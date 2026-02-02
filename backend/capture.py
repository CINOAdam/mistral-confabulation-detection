from dataclasses import dataclass, field
from typing import Dict, List
import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import settings

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
            self.activations[layer_idx] = hidden_states[:, -1, :].detach().cpu()
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

        print(f"Loading {settings.mistral_model}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            settings.mistral_model,
            cache_dir=settings.model_cache_dir
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            settings.mistral_model,
            torch_dtype=torch.float16,
            device_map="auto",
            cache_dir=settings.model_cache_dir
        )

        # Register hooks for early layers
        for layer_idx in self.config.early_layers:
            layer = self.model.model.layers[layer_idx]
            layer.register_forward_hook(self.hooks.get_hook(layer_idx))

        # Register hook for late layer
        late_layer = self.model.model.layers[self.config.late_layer]
        late_layer.register_forward_hook(self.hooks.get_hook(self.config.late_layer))

        print(f"Model loaded. Hooks registered for layers: {self.config.early_layers + [self.config.late_layer]}")

    def load_sae(self):
        """Load SAE for layer 30 feature extraction"""
        from sae_lens import SAE

        if self.sae is not None:
            return

        try:
            self.sae = SAE.load_from_pretrained(settings.sae_path)
            self.sae.eval()
            print(f"SAE loaded from {settings.sae_path}")
        except Exception as e:
            print(f"Warning: Could not load SAE: {e}")
            self.sae = None

    def generate(self, messages: List[dict], max_new_tokens: int = 100) -> str:
        """Generate response and capture activations"""
        self.hooks.clear()

        # Format messages
        formatted = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(formatted, return_tensors="pt").to(self.model.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )

        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )

        return response

    def get_layer_activations(self, layer_idx: int) -> np.ndarray:
        """Get activations for a specific layer"""
        if layer_idx not in self.hooks.activations:
            return None
        return self.hooks.activations[layer_idx].numpy()

    def get_top_sae_features(self, activations: np.ndarray, k: int = 20) -> List[dict]:
        """Extract top-k SAE features from activations"""
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
                "description": f"Feature {idx}"  # TODO: Load from annotations
            }
            for idx in top_indices
            if feature_acts[idx] > 0
        ]

    def capture_all(self, messages: List[dict], max_new_tokens: int = 100) -> dict:
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
        response = self.generate(messages, max_new_tokens)

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
            "early_activations": {k: v.tolist() for k, v in early_acts.items() if v is not None},
            "late_activations": late_acts.tolist() if late_acts is not None else [],
            "sae_features": sae_features,
            "regime_distance": regime_distance,
            "regime_classification": classify_regime(regime_distance),
            "timestamp": None  # Will be set by API
        }
