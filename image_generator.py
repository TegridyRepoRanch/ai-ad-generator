"""
Image Generator - Replicate API integration for AI image generation
Uses Flux models for high-quality ad imagery
"""
import replicate
import aiohttp
import asyncio
from pathlib import Path
from typing import Optional
from config import REPLICATE_API_TOKEN, IMAGE_MODELS, DEFAULT_IMAGE_MODEL, AD_SIZES, DEFAULT_AD_SIZE, OUTPUT_DIR


class ImageGenerator:
    """
    Handles all image generation via Replicate API.
    Primary model: Flux Pro for best quality/price ratio.
    """
    
    def __init__(self):
        self.client = replicate.Client(api_token=REPLICATE_API_TOKEN)
        self.model = IMAGE_MODELS[DEFAULT_IMAGE_MODEL]
    
    def set_model(self, model_key: str):
        """Switch between available models"""
        if model_key in IMAGE_MODELS:
            self.model = IMAGE_MODELS[model_key]
        else:
            raise ValueError(f"Unknown model: {model_key}. Available: {list(IMAGE_MODELS.keys())}")
    
    async def generate_image(
        self,
        prompt: str,
        size: str = DEFAULT_AD_SIZE,
        output_path: Optional[Path] = None,
        seed: Optional[int] = None
    ) -> Path:
        """
        Generate a single image from a prompt.
        
        Args:
            prompt: The image generation prompt
            size: Ad size preset (e.g., 'instagram_feed', 'facebook_story')
            output_path: Where to save the image (auto-generated if None)
            seed: Optional seed for reproducibility
            
        Returns:
            Path to the generated image
        """
        width, height = AD_SIZES.get(size, AD_SIZES[DEFAULT_AD_SIZE])
        
        # Prepare input for Flux model
        input_params = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_outputs": 1,
            "output_format": "png",
            "output_quality": 90,
        }
        
        if seed is not None:
            input_params["seed"] = seed
        
        # Run the model
        output = self.client.run(
            self.model,
            input=input_params
        )
        
        # Download the image
        image_url = output[0] if isinstance(output, list) else output
        
        # Generate output path if not provided
        if output_path is None:
            import uuid
            output_path = OUTPUT_DIR / f"generated_{uuid.uuid4().hex[:8]}.png"
        
        # Download image
        await self._download_image(str(image_url), output_path)
        
        return output_path
    
    async def generate_batch(
        self,
        prompts: list[str],
        size: str = DEFAULT_AD_SIZE,
        output_prefix: str = "batch"
    ) -> list[Path]:
        """
        Generate multiple images concurrently.
        
        Args:
            prompts: List of image prompts
            size: Ad size preset
            output_prefix: Prefix for output filenames
            
        Returns:
            List of paths to generated images
        """
        tasks = []
        for i, prompt in enumerate(prompts):
            output_path = OUTPUT_DIR / f"{output_prefix}_{i:02d}.png"
            tasks.append(self.generate_image(prompt, size, output_path))
        
        return await asyncio.gather(*tasks)
    
    async def _download_image(self, url: str, output_path: Path) -> None:
        """Download an image from URL to local path"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(await response.read())
                else:
                    raise Exception(f"Failed to download image: {response.status}")
    
    def generate_image_sync(
        self,
        prompt: str,
        size: str = DEFAULT_AD_SIZE,
        output_path: Optional[Path] = None,
        seed: Optional[int] = None
    ) -> Path:
        """Synchronous version of generate_image"""
        return asyncio.get_event_loop().run_until_complete(
            self.generate_image(prompt, size, output_path, seed)
        )
    
    def generate_batch_sync(
        self,
        prompts: list[str],
        size: str = DEFAULT_AD_SIZE,
        output_prefix: str = "batch"
    ) -> list[Path]:
        """Synchronous version of generate_batch"""
        return asyncio.get_event_loop().run_until_complete(
            self.generate_batch(prompts, size, output_prefix)
        )


class ImageGeneratorWithFallback(ImageGenerator):
    """
    Image generator with automatic fallback to cheaper/faster models on failure.
    Tries: flux_pro -> flux_dev -> flux_schnell
    """
    
    def __init__(self):
        super().__init__()
        self.fallback_order = ["flux_pro", "flux_dev", "flux_schnell"]
    
    async def generate_image_with_fallback(
        self,
        prompt: str,
        size: str = DEFAULT_AD_SIZE,
        output_path: Optional[Path] = None
    ) -> Path:
        """Generate image with automatic model fallback on failure"""
        last_error = None
        
        for model_key in self.fallback_order:
            try:
                self.set_model(model_key)
                return await self.generate_image(prompt, size, output_path)
            except Exception as e:
                last_error = e
                print(f"Model {model_key} failed: {e}. Trying next...")
                continue
        
        raise Exception(f"All models failed. Last error: {last_error}")
