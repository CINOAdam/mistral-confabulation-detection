"""Configuration management using pydantic-settings."""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Model configuration
    model_name: str = Field(
        default="mistralai/Mistral-Small-Instruct-2409",
        description="HuggingFace model identifier"
    )
    mistral_model: str = Field(
        default="mistralai/Mistral-Small-3.2-24B-Instruct-2506",
        description="Mistral model for reproducibility experiments"
    )
    model_cache_dir: str = Field(
        default=None,  # Will use HuggingFace default: ~/.cache/huggingface
        description="Directory for caching model weights (uses HF default if not set)"
    )
    model_dtype: Literal["float16", "bfloat16", "float32"] = Field(
        default="bfloat16",
        description="Model precision"
    )
    device: str = Field(
        default="cuda",
        description="Device to run model on (cuda/cpu)"
    )

    # SAE configuration
    sae_release: str = Field(
        default="mistral-small-instruct-22b-res-sae",
        description="SAE release identifier"
    )
    sae_id: str = Field(
        default="blocks.4.hook_resid_post",
        description="SAE hook point"
    )
    sae_path: str = Field(
        default="Codcordance/Mistral-Small-3.2-24B-Instruct-2506-SAE",
        description="SAE model identifier (HuggingFace)"
    )

    # Capture configuration
    capture_layers: list[int] = Field(
        default_factory=lambda: [1, 2, 3, 4, 5],
        description="Which transformer layers to capture"
    )
    max_activations_per_layer: int = Field(
        default=100,
        description="Max activation samples to store per layer"
    )

    # Hardware limits
    max_memory_gb: float = Field(
        default=40.0,
        description="Maximum GPU memory to use (GB)"
    )
    torch_compile: bool = Field(
        default=False,
        description="Whether to use torch.compile for optimization"
    )

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    log_level: Literal["debug", "info", "warning", "error"] = Field(
        default="info",
        description="Logging level"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()
