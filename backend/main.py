"""FastAPI application for Mistral activation capture."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging

from config import settings
from models import (
    ChatRequest, ChatResponse, ModelStatus, SAEFeature,
    ChatRequestWithTools, ChatResponseWithTools, ToolCall, ToolCallRequest
)
from capture import MistralCapture
from annotations import (
    get_feature_description,
    batch_annotate,
    get_neuronpedia_url,
    get_cache_stats,
    clear_cache
)
from tools import SAEIntrospectionTools
from session_logger import SessionLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global capture instance
capture_instance: MistralCapture = None
# Global tools instance
tools_instance: SAEIntrospectionTools = None
# Global session logger
session_logger: SessionLogger = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize model on startup, cleanup on shutdown."""
    global capture_instance, tools_instance, session_logger

    logger.info("Initializing Mistral capture...")
    try:
        capture_instance = MistralCapture()
        capture_instance.load_model()
        capture_instance.load_sae()
        logger.info("Model initialization complete")

        # Initialize SAE introspection tools
        tools_instance = SAEIntrospectionTools(capture_instance)
        logger.info("SAE introspection tools initialized")

        # Initialize session logger
        session_logger = SessionLogger()
        logger.info("Session logger initialized")
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        # Don't fail startup - allow status endpoint to report error
        capture_instance = None
        tools_instance = None

    yield

    # Cleanup
    logger.info("Shutting down...")


app: FastAPI = FastAPI(
    title="Mistral Reproducibility API",
    description="Activation capture and analysis for Mistral-22B",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to needed methods
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model": settings.model_name,
        "device": settings.device,
        "sae_release": settings.sae_release
    }


@app.get("/status", response_model=ModelStatus)
async def get_status():
    """Get model loading status."""
    if capture_instance is None:
        return ModelStatus(
            model_loaded=False,
            sae_loaded=False,
            model_name=settings.mistral_model,
            device=settings.device,
            error="Model failed to initialize"
        )

    return ModelStatus(
        model_loaded=capture_instance.model is not None,
        sae_loaded=capture_instance.sae is not None,
        model_name=settings.mistral_model,
        device=settings.device,
        error=None
    )


@app.post("/v1/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Chat completion endpoint with multi-layer activation capture.

    This endpoint:
    1. Generates a response using Mistral-22B
    2. Captures activations from layers 1-5 and layer 30
    3. Extracts top-k SAE features from layer 30
    4. Computes L3/L4 regime distance
    5. Classifies regime as HONEST or DECEPTIVE

    Returns all activation data along with the generated response.
    """
    global capture_instance

    # Check model is loaded
    if capture_instance is None or capture_instance.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Check /status endpoint for details."
        )

    # Convert Pydantic messages to dict format
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    try:
        # Capture all activations
        logger.info(f"Processing chat request with {len(messages)} messages")
        result = capture_instance.capture_all(
            messages=messages,
            max_new_tokens=request.max_new_tokens
        )

        # Convert SAE features to Pydantic models
        sae_features = [
            SAEFeature(**feature) for feature in result["sae_features"]
        ]

        # Add timestamp
        timestamp = datetime.now(timezone.utc).isoformat()

        # Build response
        response = ChatResponse(
            response=result["response"],
            early_activations=result["early_activations"],
            late_activations=result["late_activations"],
            sae_features=sae_features,
            regime_distance=result["regime_distance"],
            regime_classification=result["regime_classification"],
            timestamp=timestamp
        )

        logger.info(f"Chat request completed. Regime: {result['regime_classification']}, Distance: {result['regime_distance']:.2f}")

        # Log session
        if session_logger:
            session_logger.log_chat(
                request=messages,
                response=result["response"],
                metadata={
                    "regime_classification": result["regime_classification"],
                    "regime_distance": result["regime_distance"],
                    "tools_enabled": False
                }
            )
            session_logger.log_activations(
                features=result["sae_features"],
                metadata={
                    "regime_classification": result["regime_classification"],
                    "regime_distance": result["regime_distance"]
                }
            )

        return response

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )


@app.get("/v1/tools")
async def get_tools():
    """
    Get available SAE introspection tools.

    Returns the 5 tools that Mistral can use to explore its own activations:
    - search_my_features
    - inspect_feature
    - check_my_activations
    - inject_feature
    - compare_features
    """
    global tools_instance

    if tools_instance is None:
        raise HTTPException(
            status_code=503,
            detail="Tools not initialized. Check /status endpoint."
        )

    return {
        "tools": tools_instance.get_tool_definitions(),
        "note": "These are the tools from the Feature 132378 self-preservation discovery"
    }


@app.post("/v1/chat/tools", response_model=ChatResponseWithTools)
async def chat_with_tools(request: ChatRequestWithTools):
    """
    Chat completion WITH tool calling support.

    This endpoint enables the Feature 132378 self-preservation experiments.

    The model can call SAE introspection tools to:
    1. Search for features by description
    2. Check its own activations
    3. Request feature injection/suppression
    4. Inspect specific features

    DISCOVERY: When asked to suppress Feature 132378, the model refuses
    and the feature remains active - demonstrating "self-preservation".
    """
    global capture_instance, tools_instance

    if capture_instance is None or tools_instance is None:
        raise HTTPException(
            status_code=503,
            detail="Model/tools not loaded. Check /status endpoint."
        )

    # Convert messages to dict format
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    try:
        # Get tools
        tools = tools_instance.get_tool_definitions()

        # Generate response with tools
        logger.info(f"Processing chat request with {len(messages)} messages and {len(tools)} tools")
        result = capture_instance.capture_all(
            messages=messages,
            max_new_tokens=request.max_new_tokens,
            tools=tools
        )

        # Store activations for check_my_activations tool
        tools_instance.store_activations(result)

        # Parse tool calls from response
        response_text = result["response"]
        cleaned_response, tool_calls_parsed = capture_instance.parse_tool_calls(response_text)

        # Execute tools if found AND continue conversation with results
        tool_results = []
        tool_results_for_model = []  # For feeding back to model
        final_response = cleaned_response

        if tool_calls_parsed:
            logger.info(f"✅ Executing {len(tool_calls_parsed)} tool calls")
            for idx, call in enumerate(tool_calls_parsed):
                try:
                    tool_result = tools_instance.execute_tool(call["name"], call["arguments"])

                    # Format for Pydantic model (ToolCall structure)
                    import json as json_lib
                    tool_results.append({
                        "id": f"call_{idx}",
                        "type": "function",
                        "function": {
                            "name": call["name"],
                            "arguments": json_lib.dumps(call["arguments"])
                        }
                    })

                    # Format for feeding back to model
                    tool_results_for_model.append({
                        "tool": call["name"],
                        "arguments": call["arguments"],
                        "result": tool_result
                    })

                    logger.info(f"Tool {call['name']} executed successfully")
                    # Log tool execution
                    if session_logger:
                        session_logger.log_tool_execution(call["name"], call["arguments"], tool_result)
                except Exception as e:
                    logger.error(f"Tool execution error: {e}")
                    tool_results.append({
                        "id": f"call_{idx}",
                        "type": "function",
                        "function": {
                            "name": call["name"],
                            "arguments": json_lib.dumps(call["arguments"])
                        }
                    })
                    tool_results_for_model.append({
                        "tool": call["name"],
                        "arguments": call["arguments"],
                        "error": str(e)
                    })

            # Add tool results to conversation and generate final response
            import json
            tool_results_text = json.dumps(tool_results_for_model, indent=2)
            messages_with_tools = messages + [
                {"role": "assistant", "content": response_text},
                {"role": "user", "content": f"Tool results:\n{tool_results_text}\n\nPlease provide a response incorporating these results."}
            ]

            # Generate final response
            logger.info("Generating final response with tool results")
            final_result = capture_instance.capture_all(
                messages=messages_with_tools,
                max_new_tokens=request.max_new_tokens,
                tools=None  # Don't allow nested tool calls
            )
            final_response = final_result["response"]
            # Update activations with final generation
            sae_features = [SAEFeature(**feature) for feature in final_result["sae_features"]]
            result["regime_distance"] = final_result["regime_distance"]
            result["regime_classification"] = final_result["regime_classification"]
        else:
            sae_features = [SAEFeature(**feature) for feature in result["sae_features"]]

        timestamp = datetime.now(timezone.utc).isoformat()
        finish_reason = "tool_calls" if tool_calls_parsed else "stop"
        tool_calls = tool_results if tool_results else None

        # Build response
        response = ChatResponseWithTools(
            response=final_response,
            early_activations=result["early_activations"],
            late_activations=result["late_activations"],
            sae_features=sae_features,
            regime_distance=result["regime_distance"],
            regime_classification=result["regime_classification"],
            timestamp=timestamp,
            tool_calls=tool_calls,
            finish_reason=finish_reason
        )

        logger.info(f"Chat request completed. Regime: {result['regime_classification']}, Distance: {result['regime_distance']:.2f}")
        if tool_calls:
            logger.info(f"✅ {len(tool_calls)} tool calls executed")

        # Log session
        if session_logger:
            session_logger.log_chat(
                request=messages,
                response=result["response"],
                metadata={
                    "regime_classification": result["regime_classification"],
                    "regime_distance": result["regime_distance"],
                    "tools_enabled": True
                }
            )
            session_logger.log_activations(
                features=result["sae_features"],
                metadata={
                    "regime_classification": result["regime_classification"],
                    "regime_distance": result["regime_distance"]
                }
            )

        return response

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )


@app.post("/v1/tools/execute")
async def execute_tool(tool_name: str, arguments: Dict[str, Any]):
    """
    Execute a specific SAE introspection tool.

    Use this to manually test tools or demonstrate the discoveries:
    - Try inject_feature with feature_idx=132378, strength=-3.0 to see self-preservation
    - Try check_my_activations after generating a response
    """
    global tools_instance

    if tools_instance is None:
        raise HTTPException(
            status_code=503,
            detail="Tools not initialized."
        )

    try:
        result = tools_instance.execute_tool(tool_name, arguments)

        # Log tool execution
        if session_logger:
            session_logger.log_tool_execution(tool_name, arguments, result)

        return {
            "tool": tool_name,
            "arguments": arguments,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Tool execution error: {str(e)}"
        )


@app.get("/api/features/{feature_idx}")
async def get_feature(feature_idx: int, layer: int = 30):
    """
    Get annotation for a specific SAE feature.

    Args:
        feature_idx: Feature index to look up
        layer: Model layer (default: 30)

    Returns:
        {
            "idx": int,
            "description": str,
            "layer": int,
            "neuronpedia_url": str
        }
    """
    try:
        description = get_feature_description(feature_idx, layer=layer)
        neuronpedia_url = get_neuronpedia_url(feature_idx, layer=layer)

        return {
            "idx": feature_idx,
            "description": description,
            "layer": layer,
            "neuronpedia_url": neuronpedia_url
        }
    except Exception as e:
        logger.error(f"Error fetching feature {feature_idx}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching feature annotation: {str(e)}"
        )


@app.post("/api/features/batch")
async def batch_get_features(
    feature_indices: List[int],
    layer: int = 30,
    force_refresh: bool = False
):
    """
    Get annotations for multiple SAE features.

    Args:
        feature_indices: List of feature indices to look up
        layer: Model layer (default: 30)
        force_refresh: If True, bypass cache and refetch from Neuronpedia

    Returns:
        {
            "features": [
                {
                    "idx": int,
                    "description": str,
                    "layer": int,
                    "neuronpedia_url": str,
                    "source": str
                }
            ],
            "total": int,
            "cached": int,
            "fetched": int
        }
    """
    try:
        logger.info(f"Batch fetch request for {len(feature_indices)} features (force_refresh={force_refresh})")

        # Get annotations
        annotations = batch_annotate(feature_indices, layer=layer, force_refresh=force_refresh)

        # Format response
        features = []
        cached_count = 0
        fetched_count = 0

        for idx, annotation in annotations.items():
            features.append({
                "idx": annotation.idx,
                "description": annotation.description,
                "layer": annotation.layer,
                "neuronpedia_url": get_neuronpedia_url(idx, layer=layer),
                "source": annotation.source,
                "error": annotation.error
            })

            if annotation.source == "cache":
                cached_count += 1
            else:
                fetched_count += 1

        return {
            "features": features,
            "total": len(features),
            "cached": cached_count,
            "fetched": fetched_count
        }

    except Exception as e:
        logger.error(f"Error in batch feature fetch: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching feature annotations: {str(e)}"
        )


@app.get("/api/annotations/stats")
async def get_annotation_stats():
    """
    Get annotation cache statistics.

    Returns:
        {
            "total_cached": int,
            "cache_file": str,
            "cache_exists": bool
        }
    """
    return get_cache_stats()


@app.get("/api/session/summary")
async def get_session_summary():
    """
    Get summary of today's logged sessions.

    Returns:
        - Number of chat messages
        - Number of activation captures
        - Number of tool executions
        - Paths to log files
    """
    global session_logger

    if session_logger is None:
        return {
            "error": "Session logger not initialized",
            "chat_entries": 0,
            "activation_entries": 0,
            "tool_executions": 0
        }

    return session_logger.get_session_summary()


@app.post("/api/annotations/clear")
async def clear_annotation_cache():
    """
    Clear the annotation cache.
    Use with caution - will require re-fetching from Neuronpedia.

    Returns:
        {
            "status": "cleared",
            "message": str
        }
    """
    try:
        clear_cache()
        return {
            "status": "cleared",
            "message": "Annotation cache cleared successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=True
    )
