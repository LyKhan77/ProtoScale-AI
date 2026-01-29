"""Qwen Image Edit multi-angle generation.

Adapted from: https://huggingface.co/spaces/multimodalart/qwen-image-multiple-angles-3d-camera

Uses Qwen-Image-Edit-2511 with Lightning and Multiple Angles LoRA adapters
to generate consistent multi-angle views of an object.
"""
import torch
from PIL import Image
from typing import List, Optional

from app.config import get_config
from app.utils import get_logger

logger = get_logger(__name__)

# Global model singleton
_pipeline = None


def get_device():
    """Get the appropriate device for inference."""
    config = get_config()
    if config.GPU_DEVICE == "cuda" and torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_pipeline():
    """Load and configure the Qwen Image Edit pipeline with LoRA adapters."""
    global _pipeline

    if _pipeline is not None:
        return _pipeline

    logger.info("Loading Qwen Image Edit pipeline...")

    device = get_device()
    dtype = torch.bfloat16 if device in ("cuda", "mps") else torch.float32

    try:
        from diffusers import QwenImageEditPlusPipeline

        # Load base model on CPU first, then use offloading
        _pipeline = QwenImageEditPlusPipeline.from_pretrained(
            "Qwen/Qwen-Image-Edit-2511",
            torch_dtype=dtype,
        )

        # Use CPU offload - automatically moves components to GPU only when needed
        # This avoids OOM on 24GB GPUs since full model is ~23GB
        _pipeline.enable_model_cpu_offload()

        # Load LoRA adapters
        _pipeline.load_lora_weights(
            "lightx2v/Qwen-Image-Edit-2511-Lightning",
            adapter_name="lightning"
        )
        _pipeline.load_lora_weights(
            "fal/Qwen-Image-Edit-2511-Multiple-Angles-LoRA",
            adapter_name="angles"
        )

        # Activate both adapters
        _pipeline.set_adapters(["lightning", "angles"], adapter_weights=[1.0, 1.0])

        logger.info(f"Qwen pipeline loaded with CPU offload on {device}")

    except Exception as e:
        logger.error(f"Failed to load Qwen pipeline: {e}")
        raise

    return _pipeline


def get_azimuth_prompt(azimuth: int) -> str:
    """Get the prompt for a specific azimuth angle.

    Args:
        azimuth: Angle in degrees (0=front, 90=right, 180=back, 270=left)

    Returns:
        Formatted prompt string
    """
    # Azimuth descriptions
    azimuth_map = {
        0: "front view",
        90: "right side view",
        180: "back view",
        270: "left side view",
    }

    view_desc = azimuth_map.get(azimuth, f"{azimuth} degree view")

    # Prompt format: <sks> [azimuth] [elevation] [distance]
    # Default elevation=0, distance=1.5
    return f"<sks> {azimuth} 0 1.5"


def generate_single_view(
    image: Image.Image,
    azimuth: int,
    num_inference_steps: int = 4,
    guidance_scale: float = 3.5,
) -> Image.Image:
    """Generate a single view at the specified azimuth.

    Args:
        image: Input PIL image
        azimuth: Viewing angle in degrees
        num_inference_steps: Number of denoising steps (4 for Lightning)
        guidance_scale: Classifier-free guidance scale

    Returns:
        Generated PIL image
    """
    pipeline = load_pipeline()
    device = get_device()

    prompt = get_azimuth_prompt(azimuth)

    logger.info(f"Generating view at azimuth {azimuth} with prompt: {prompt}")

    # Ensure image is RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize to expected size if needed (512x512 typical)
    if image.size != (512, 512):
        image = image.resize((512, 512), Image.Resampling.LANCZOS)

    with torch.no_grad():
        result = pipeline(
            prompt=prompt,
            image=image,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        ).images[0]

    return result


def generate_multi_angle_views(
    image: Image.Image,
    azimuths: List[int] = None,
    num_inference_steps: int = 4,
    guidance_scale: float = 3.5,
) -> List[Image.Image]:
    """Generate multi-angle views of an object.

    Args:
        image: Input PIL image of the object
        azimuths: List of azimuth angles to generate (default: [0, 90, 180, 270])
        num_inference_steps: Number of denoising steps (4 for Lightning LoRA)
        guidance_scale: Classifier-free guidance scale

    Returns:
        List of generated PIL images at each azimuth
    """
    if azimuths is None:
        azimuths = [0, 90, 180, 270]

    logger.info(f"Generating {len(azimuths)} multi-angle views")

    generated_images = []

    for azimuth in azimuths:
        view = generate_single_view(
            image=image,
            azimuth=azimuth,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        )
        generated_images.append(view)
        logger.info(f"Generated view at azimuth {azimuth}")

    return generated_images


def cleanup():
    """Release model resources."""
    global _pipeline
    if _pipeline is not None:
        del _pipeline
        _pipeline = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Qwen pipeline cleaned up")
