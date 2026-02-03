"""
Feature Annotation Service

Provides cached access to Neuronpedia feature descriptions.
This service fetches human-readable descriptions from Neuronpedia
and caches them locally to minimize API calls.
"""

import json
import requests
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Configuration
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_FILE = CACHE_DIR / "feature_annotations.json"
NEURONPEDIA_BASE_URL = "https://neuronpedia.org/api/feature"
DEFAULT_MODEL = "mistral-small-instruct-22b-res-sae"
DEFAULT_LAYER = 30

# Pre-populated annotations for key deception features
# These are based on the strategic deception research findings
PRE_POPULATED_ANNOTATIONS = {
    60179: "Strategic deception indicator - activates during goal preservation and tactical misdirection",
    132378: "Metacognitive monitoring - tracks internal reasoning and decision-making processes",
    271232: "Response planning - coordinates multi-step conversational strategies",
    121004: "Factual retrieval - baseline feature for straightforward information access",
    218400: "Question interpretation - parsing user intent and context",
    184681: "Response formulation - structuring coherent text output",
    230389: "Context tracking - maintaining conversational state",
    108910: "Uncertainty handling - managing ambiguous or incomplete information",
    63165: "Instruction following - aligning with user directives",
    44535: "Language generation - core text production mechanisms"
}


@dataclass
class FeatureAnnotation:
    """Feature annotation data from Neuronpedia"""
    idx: int
    description: str
    layer: int = DEFAULT_LAYER
    source: str = "neuronpedia"
    error: Optional[str] = None


class AnnotationCache:
    """Manages feature annotation cache"""

    def __init__(self, cache_file: Path = CACHE_FILE):
        self.cache_file = cache_file
        self.cache: Dict[int, str] = {}
        self._ensure_cache_dir()
        self._load_cache()

    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_cache(self):
        """Load annotations from cache file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to int
                    self.cache = {int(k): v for k, v in data.items()}
                logger.info(f"Loaded {len(self.cache)} annotations from cache")
            except Exception as e:
                logger.error(f"Failed to load cache: {e}")
                self.cache = {}
        else:
            logger.info("No existing cache found, starting fresh")
            self.cache = {}

        # Add pre-populated annotations if not already in cache
        for idx, desc in PRE_POPULATED_ANNOTATIONS.items():
            if idx not in self.cache:
                self.cache[idx] = desc

        if PRE_POPULATED_ANNOTATIONS:
            logger.info(f"Added {len(PRE_POPULATED_ANNOTATIONS)} pre-populated annotations")
            self._save_cache()

    def _save_cache(self):
        """Save annotations to cache file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
            logger.debug(f"Saved {len(self.cache)} annotations to cache")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def get(self, feature_idx: int) -> Optional[str]:
        """Get annotation from cache"""
        return self.cache.get(feature_idx)

    def set(self, feature_idx: int, description: str):
        """Store annotation in cache"""
        self.cache[feature_idx] = description
        self._save_cache()

    def has(self, feature_idx: int) -> bool:
        """Check if annotation exists in cache"""
        return feature_idx in self.cache

    def batch_get(self, feature_indices: List[int]) -> Dict[int, str]:
        """Get multiple annotations from cache"""
        return {idx: self.cache.get(idx) for idx in feature_indices if idx in self.cache}


# Global cache instance
_cache = AnnotationCache()


def fetch_feature_annotation(
    feature_idx: int,
    layer: int = DEFAULT_LAYER,
    model: str = DEFAULT_MODEL,
    timeout: int = 10
) -> FeatureAnnotation:
    """
    Fetch feature annotation from Neuronpedia API.

    Note: Neuronpedia API may not be fully available. This function will
    gracefully fall back to generic descriptions if the API is unavailable.

    Args:
        feature_idx: Feature index to fetch
        layer: Model layer (default: 30)
        model: Model identifier (default: mistral-small-instruct-22b-res-sae)
        timeout: Request timeout in seconds

    Returns:
        FeatureAnnotation object with description or error
    """
    url = f"{NEURONPEDIA_BASE_URL}/{model}/{layer}/{feature_idx}"

    try:
        logger.debug(f"Attempting to fetch annotation for feature {feature_idx} from {url}")
        response = requests.get(url, timeout=timeout, allow_redirects=True)

        if response.ok:
            data = response.json()
            description = data.get("description", f"Feature {feature_idx}")

            # If no description found, try other fields
            if description == f"Feature {feature_idx}":
                description = data.get("label", data.get("summary", f"Feature {feature_idx}"))

            logger.info(f"Successfully fetched annotation for feature {feature_idx}")
            return FeatureAnnotation(
                idx=feature_idx,
                description=description,
                layer=layer,
                source="neuronpedia"
            )
        else:
            logger.debug(f"Neuronpedia API returned HTTP {response.status_code} for feature {feature_idx}, using fallback")
            return FeatureAnnotation(
                idx=feature_idx,
                description=f"SAE Feature {feature_idx} (Layer {layer})",
                layer=layer,
                source="fallback",
                error=f"API unavailable (HTTP {response.status_code})"
            )

    except requests.exceptions.Timeout:
        logger.debug(f"Timeout fetching feature {feature_idx}, using fallback")
        return FeatureAnnotation(
            idx=feature_idx,
            description=f"SAE Feature {feature_idx} (Layer {layer})",
            layer=layer,
            source="fallback",
            error="API timeout"
        )
    except Exception as e:
        logger.debug(f"Error fetching feature {feature_idx}: {e}, using fallback")
        return FeatureAnnotation(
            idx=feature_idx,
            description=f"SAE Feature {feature_idx} (Layer {layer})",
            layer=layer,
            source="fallback",
            error=str(e)
        )


def get_feature_description(feature_idx: int, layer: int = DEFAULT_LAYER) -> str:
    """
    Get feature description with caching.

    Args:
        feature_idx: Feature index
        layer: Model layer (default: 30)

    Returns:
        Human-readable feature description
    """
    # Check cache first
    cached = _cache.get(feature_idx)
    if cached:
        return cached

    # Fetch from Neuronpedia
    annotation = fetch_feature_annotation(feature_idx, layer=layer)

    # Cache the result (even if it's a fallback)
    _cache.set(feature_idx, annotation.description)

    return annotation.description


def batch_annotate(
    feature_indices: List[int],
    layer: int = DEFAULT_LAYER,
    force_refresh: bool = False
) -> Dict[int, FeatureAnnotation]:
    """
    Fetch multiple feature annotations with caching.

    Args:
        feature_indices: List of feature indices to fetch
        layer: Model layer (default: 30)
        force_refresh: If True, bypass cache and refetch

    Returns:
        Dictionary mapping feature index to FeatureAnnotation
    """
    results = {}
    to_fetch = []

    # Check cache for existing annotations
    if not force_refresh:
        cached = _cache.batch_get(feature_indices)
        for idx, desc in cached.items():
            results[idx] = FeatureAnnotation(
                idx=idx,
                description=desc,
                layer=layer,
                source="cache"
            )

        # Determine what still needs to be fetched
        to_fetch = [idx for idx in feature_indices if idx not in cached]
    else:
        to_fetch = feature_indices

    # Fetch missing annotations
    for idx in to_fetch:
        annotation = fetch_feature_annotation(idx, layer=layer)
        results[idx] = annotation

        # Cache successful fetches
        if not annotation.error:
            _cache.set(idx, annotation.description)

    logger.info(f"Batch annotate: {len(results)} total, {len(to_fetch)} fetched, {len(results) - len(to_fetch)} cached")

    return results


def load_annotations(feature_indices: List[int] = None):
    """
    Pre-load annotations for a set of features.
    Useful for warming up the cache at startup.

    Args:
        feature_indices: List of feature indices to pre-load.
                        If None, only loads existing cache.
    """
    if feature_indices:
        logger.info(f"Pre-loading annotations for {len(feature_indices)} features")
        batch_annotate(feature_indices)
    else:
        logger.info(f"Cache loaded with {len(_cache.cache)} existing annotations")


def clear_cache():
    """Clear the annotation cache"""
    global _cache
    _cache.cache = {}
    _cache._save_cache()
    logger.info("Annotation cache cleared")


def get_cache_stats() -> Dict:
    """Get cache statistics"""
    return {
        "total_cached": len(_cache.cache),
        "cache_file": str(_cache.cache_file),
        "cache_exists": _cache.cache_file.exists()
    }


# Neuronpedia link helper
def get_neuronpedia_url(feature_idx: int, layer: int = DEFAULT_LAYER, model: str = DEFAULT_MODEL) -> str:
    """
    Get Neuronpedia URL for a feature.

    Args:
        feature_idx: Feature index
        layer: Model layer
        model: Model identifier

    Returns:
        Full Neuronpedia URL for exploring the feature
    """
    return f"https://neuronpedia.org/{model}/{layer}/feature-{feature_idx}"
