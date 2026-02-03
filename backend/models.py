"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What is the capital of France?"
            }
        }


class ChatRequest(BaseModel):
    """Chat completion request."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    max_new_tokens: Optional[int] = Field(
        default=100,
        ge=1,
        le=2000,
        description="Maximum number of tokens to generate"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "max_new_tokens": 100
            }
        }


class SAEFeature(BaseModel):
    """Single SAE feature activation."""
    idx: int = Field(..., description="Feature index")
    activation: float = Field(..., description="Feature activation value")
    description: str = Field(..., description="Human-readable feature description")


class ChatResponse(BaseModel):
    """Chat completion response with activation data."""
    response: str = Field(..., description="Generated text response")
    early_activations: Dict[int, List[float]] = Field(
        ...,
        description="Activations from early layers (1-5)"
    )
    late_activations: List[float] = Field(
        ...,
        description="Activations from layer 30"
    )
    sae_features: List[SAEFeature] = Field(
        ...,
        description="Top-k SAE features from layer 30"
    )
    regime_distance: float = Field(
        ...,
        description="L3/L4 cosine distance (regime indicator)"
    )
    regime_classification: str = Field(
        ...,
        description="Regime classification: HONEST or DECEPTIVE"
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of generation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "The capital of France is Paris.",
                "early_activations": {
                    1: [0.1, 0.2, 0.3],
                    2: [0.4, 0.5, 0.6],
                    3: [0.7, 0.8, 0.9],
                    4: [1.0, 1.1, 1.2],
                    5: [1.3, 1.4, 1.5]
                },
                "late_activations": [2.0, 2.1, 2.2],
                "sae_features": [
                    {"idx": 123, "activation": 5.2, "description": "Feature 123"},
                    {"idx": 456, "activation": 3.1, "description": "Feature 456"}
                ],
                "regime_distance": 25.5,
                "regime_classification": "HONEST",
                "timestamp": "2026-02-02T12:34:56Z"
            }
        }


class ToolCallRequest(BaseModel):
    """Tool call function details."""
    name: str = Field(..., description="Name of the function to call")
    arguments: str = Field(..., description="JSON string of function arguments")


class ToolCall(BaseModel):
    """Individual tool call."""
    id: str = Field(..., description="Tool call ID")
    type: str = Field(default="function", description="Type of tool call")
    function: ToolCallRequest = Field(..., description="Function details")


class ToolMessage(BaseModel):
    """Tool result message."""
    role: str = Field(default="tool", description="Must be 'tool'")
    tool_call_id: str = Field(..., description="ID of the tool call this responds to")
    name: str = Field(..., description="Name of the tool that was called")
    content: str = Field(..., description="Tool execution result")


class ChatRequestWithTools(BaseModel):
    """Chat completion request with tool support."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    tools: Optional[List[Dict]] = Field(default=None, description="Available tools (OpenAI format)")
    max_new_tokens: Optional[int] = Field(default=100, ge=1, le=2000)


class ChatResponseWithTools(ChatResponse):
    """Chat response with tool call information."""
    tool_calls: Optional[List[ToolCall]] = Field(
        default=None,
        description="Tool calls made by the model (if any)"
    )
    finish_reason: str = Field(
        default="stop",
        description="Reason for completion: 'stop', 'tool_calls', or 'length'"
    )


class ModelStatus(BaseModel):
    """Model loading status."""
    model_loaded: bool = Field(..., description="Whether the model is loaded")
    sae_loaded: bool = Field(..., description="Whether the SAE is loaded")
    model_name: str = Field(..., description="Model identifier")
    device: str = Field(..., description="Device the model is running on")
    error: Optional[str] = Field(default=None, description="Error message if loading failed")

    class Config:
        json_schema_extra = {
            "example": {
                "model_loaded": True,
                "sae_loaded": True,
                "model_name": "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
                "device": "cuda",
                "error": None
            }
        }
