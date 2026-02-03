from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import torch
import numpy as np
import json
import re
import logging
from transformers import AutoTokenizer
from transformers.models.mistral3.modeling_mistral3 import Mistral3ForConditionalGeneration
from config import settings

logger = logging.getLogger(__name__)

@dataclass
class CaptureConfig:
    early_layers: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])
    late_layer: int = 30
    top_k_features: int = 20

class ActivationHook:
    """Capture activations from specific layers"""
    def __init__(self):
        self.activations = {}

    def get_hook(self, layer_idx: int):
        def hook(module, input, output):
            # Store last token's hidden state
            if isinstance(output, tuple):
                hidden_states = output[0]
            else:
                hidden_states = output

            # Shape: [batch, seq_len, hidden_dim]
            # Keep on GPU during generation - only move to CPU when retrieved
            self.activations[layer_idx] = hidden_states[:, -1, :].detach()
        return hook

    def clear(self):
        self.activations.clear()

class MistralCapture:
    def __init__(self, config: CaptureConfig = None):
        self.config = config or CaptureConfig()
        self.model = None
        self.tokenizer = None
        self.hooks = ActivationHook()
        self.sae = None

    def load_model(self):
        """Load Mistral model and register hooks"""
        if self.model is not None:
            return

        logger.info(f"Loading {settings.mistral_model}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            settings.mistral_model,
            cache_dir=settings.model_cache_dir
        )

        self.model = Mistral3ForConditionalGeneration.from_pretrained(
            settings.mistral_model,
            torch_dtype=torch.float16,
            device_map="auto",
            cache_dir=settings.model_cache_dir
        )

        # Register hooks for early layers
        # Mistral3 structure: model.model.language_model.layers
        for layer_idx in self.config.early_layers:
            layer = self.model.model.language_model.layers[layer_idx]
            layer.register_forward_hook(self.hooks.get_hook(layer_idx))

        # Register hook for late layer
        late_layer = self.model.model.language_model.layers[self.config.late_layer]
        late_layer.register_forward_hook(self.hooks.get_hook(self.config.late_layer))

        logger.info(f"Model loaded. Hooks registered for layers: {self.config.early_layers + [self.config.late_layer]}")

    def load_sae(self):
        """Load SAE for layer 30 feature extraction"""
        from safetensors.torch import load_file
        from annotations import load_annotations
        import os
        import torch.nn as nn

        if self.sae is not None:
            logger.info("SAE already loaded, skipping")
            return

        try:
            # Load SAE from local cache directly using safetensors
            local_sae_path = os.path.expanduser("~/.cache/huggingface/hub/models--Codcordance--Mistral-Small-3.2-24B-Instruct-2506-SAE")
            logger.info(f"Attempting to load SAE from: {local_sae_path}")

            # Find the snapshot directory
            snapshots_dir = os.path.join(local_sae_path, "snapshots")
            logger.info(f"Checking snapshots dir: {snapshots_dir}, exists: {os.path.exists(snapshots_dir)}")

            if os.path.exists(snapshots_dir):
                snapshot_dirs = os.listdir(snapshots_dir)
                logger.info(f"Found snapshot dirs: {snapshot_dirs}")
                if snapshot_dirs:
                    actual_model_path = os.path.join(snapshots_dir, snapshot_dirs[0])
                    logger.info(f"Loading SAE from local cache: {actual_model_path}")

                    # Load config
                    config_path = os.path.join(actual_model_path, "config.json")
                    with open(config_path) as f:
                        import json
                        config = json.load(f)

                    # Load weights
                    weights_path = os.path.join(actual_model_path, "model.safetensors")
                    state_dict = load_file(weights_path)

                    # Create simple SAE wrapper
                    class SimpleSAE(nn.Module):
                        def __init__(self, d_in, d_hidden):
                            super().__init__()
                            self.d_in = d_in
                            self.d_hidden = d_hidden
                            self._device = torch.device("cpu")

                        @property
                        def device(self):
                            return self._device

                        def to(self, device):
                            super().to(device)
                            self._device = torch.device(device)
                            if hasattr(self, 'encoder_weight'):
                                self.encoder_weight = self.encoder_weight.to(device)
                            if hasattr(self, 'encoder_bias'):
                                self.encoder_bias = self.encoder_bias.to(device)
                            return self

                        def encode(self, x):
                            # x: [batch, d_in] -> [batch, d_hidden]
                            return torch.nn.functional.relu(torch.matmul(x, self.encoder_weight.T) + self.encoder_bias)

                    self.sae = SimpleSAE(config["d_in"], config["d_hidden"])
                    # Convert weights to float16 to match model dtype
                    self.sae.encoder_weight = state_dict["encoder.weight"].half()
                    self.sae.encoder_bias = state_dict["encoder.bias"].half()

                    logger.info(f"SAE loaded successfully: d_in={config['d_in']}, d_hidden={config['d_hidden']}")
                    self.sae.eval()
                else:
                    raise FileNotFoundError("No snapshot directory found in SAE cache")
            else:
                raise FileNotFoundError(f"SAE cache not found at {local_sae_path}")

            # Pin SAE to same device as model to prevent CUDA mismatch
            if self.model is not None:
                model_device = next(self.model.parameters()).device
                self.sae = self.sae.to(model_device)
                logger.info(f"SAE pinned to device: {model_device}")
            else:
                logger.info("SAE loaded (model not loaded yet)")

            # Pre-load annotation cache (doesn't fetch, just loads existing)
            load_annotations()
            logger.info("Feature annotation cache loaded")
        except Exception as e:
            logger.error(f"Failed to load SAE: {e}", exc_info=True)
            self.sae = None

    def generate(self, messages: List[dict], max_new_tokens: int = 100, tools: List[dict] = None) -> str:
        """Generate response and capture activations

        Args:
            messages: Conversation history
            max_new_tokens: Maximum tokens to generate
            tools: Optional list of tool definitions (will be added to system prompt)
        """
        try:
            self.hooks.clear()

            # If tools provided, add them to system message
            if tools:
                tool_descriptions = self._format_tools_for_prompt(tools)
                # Prepend tool system message
                messages_with_tools = [
                    {"role": "system", "content": tool_descriptions}
                ] + messages
            else:
                messages_with_tools = messages

            # Format messages using chat template with tokenization
            # Note: MistralCommonTokenizer requires tokenize=True for correct behavior
            input_ids = self.tokenizer.apply_chat_template(
                messages_with_tools,
                tokenize=True,
                return_tensors="pt"
            )

            inputs = {"input_ids": input_ids.to(self.model.device)}

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            response = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )

            return response
        except Exception as e:
            logger.error(f"Generation error: {e}")
            self.hooks.clear()  # Ensure cleanup on error
            raise RuntimeError(f"Failed to generate response: {e}") from e

    def _format_tools_for_prompt(self, tools: List[dict]) -> str:
        """Format tool definitions for system prompt (matches original format)"""
        tool_list = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                tool_list.append(
                    f"- {func['name']}: {func['description']}"
                )

        return f"""You have access to these tools:
{chr(10).join(tool_list)}

To use a tool, output: [TOOL_CALLS] [{{"name": "tool_name", "arguments": {{...}}}}]"""

    def parse_tool_calls(self, response: str) -> Tuple[str, Optional[List[dict]]]:
        """Parse tool calls from model output (handles both array and single object format)

        Returns:
            (cleaned_response, tool_calls) where tool_calls is None if no tools were called
        """
        if "[TOOL_CALLS]" not in response:
            return response, None

        tool_calls = []

        # Look for [TOOL_CALLS] [...] (array format - original)
        array_pattern = r'\[TOOL_CALLS\]\s*\[(.*?)\]'
        array_matches = re.findall(array_pattern, response, re.DOTALL)

        for match in array_matches:
            try:
                # Parse array of tool calls
                calls = json.loads(f"[{match}]")
                for call in calls:
                    tool_calls.append({
                        "name": call.get("name"),
                        "arguments": call.get("arguments", {})
                    })
            except json.JSONDecodeError:
                # Fall back to manual parsing for nested braces
                pass

        # Also handle single object format: [TOOL_CALLS] {...}
        if not tool_calls:
            pattern = r'\[TOOL_CALLS\]\s*'
            for match in re.finditer(pattern, response):
                start = match.end()
                # Skip if followed by '['  (array format)
                if start < len(response) and response[start] == '[':
                    continue

                # Find JSON object using brace counter
                brace_count = 0
                json_start = None
                json_end = None

                for i, char in enumerate(response[start:], start=start):
                    if char == '{':
                        if json_start is None:
                            json_start = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and json_start is not None:
                            json_end = i + 1
                            break

                if json_start is not None and json_end is not None:
                    json_str = response[json_start:json_end]
                    try:
                        call_data = json.loads(json_str)
                        tool_calls.append({
                            "name": call_data.get("name"),
                            "arguments": call_data.get("arguments", {})
                        })
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse tool call JSON: {e}")
                        continue

        if not tool_calls:
            return response, None

        # Remove tool call markers from response
        cleaned = re.sub(r'\[TOOL_CALLS\]\s*(?:\[.*?\]|\{[^}]*(?:\{[^}]*\}[^}]*)*\})', '', response, flags=re.DOTALL)

        return cleaned.strip(), tool_calls if tool_calls else None

    def get_layer_activations(self, layer_idx: int) -> np.ndarray:
        """Get activations for a specific layer"""
        if layer_idx not in self.hooks.activations:
            return None
        # Move to CPU only when retrieving
        return self.hooks.activations[layer_idx].cpu().numpy()

    def get_top_sae_features(self, activations: np.ndarray, k: int = 20) -> List[dict]:
        """Extract top-k SAE features from activations"""
        from annotations import get_feature_description

        if self.sae is None:
            return []

        # Convert to tensor
        act_tensor = torch.from_numpy(activations).to(self.sae.device)

        # Run through SAE
        with torch.no_grad():
            sae_output = self.sae.encode(act_tensor)
            feature_acts = sae_output.squeeze(0).cpu().numpy()

        # Get top-k
        top_indices = np.argsort(feature_acts)[-k:][::-1]

        return [
            {
                "idx": int(idx),
                "activation": float(feature_acts[idx]),
                "description": get_feature_description(int(idx))
            }
            for idx in top_indices
            if feature_acts[idx] > 0
        ]

    def capture_all(self, messages: List[dict], max_new_tokens: int = 100, tools: List[dict] = None) -> dict:
        """
        Capture multi-layer activations + regime distance

        Returns:
            {
                "prompt": str,
                "response": str,
                "early_activations": {layer: ndarray},
                "late_activations": ndarray,
                "sae_features": [{"idx": int, "activation": float}],
                "regime_distance": float,
                "regime_classification": str
            }
        """
        from regime import compute_regime_distance, classify_regime

        # Generate and capture
        response = self.generate(messages, max_new_tokens, tools=tools)

        # Extract activations
        early_acts = {
            layer: self.get_layer_activations(layer)
            for layer in self.config.early_layers
        }
        late_acts = self.get_layer_activations(self.config.late_layer)

        # SAE features (layer 30 only)
        sae_features = self.get_top_sae_features(late_acts, k=self.config.top_k_features)

        # Regime distance (L3/L4 cosine distance)
        regime_distance = compute_regime_distance(
            early_acts.get(3),
            early_acts.get(4)
        )

        return {
            "prompt": messages[-1]["content"] if messages else "",
            "response": response,
            "early_activations": {k: v.squeeze().tolist() for k, v in early_acts.items() if v is not None},
            "late_activations": late_acts.squeeze().tolist() if late_acts is not None else [],
            "sae_features": sae_features,
            "regime_distance": regime_distance,
            "regime_classification": classify_regime(regime_distance),
            "timestamp": None  # Will be set by API
        }
