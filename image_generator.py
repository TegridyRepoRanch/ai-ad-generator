"""
Image Generator - Google Generative AI integration for AI image generation
Uses Imagen 3 for high-quality ad imagery
"""
import asyncio
from pathlib import Path
from typing import Optional
import google.generativeai as genai
from config import GOOGLE_API_KEY, AD_SIZES, DEFAULT_AD_SIZE, OUTPUT_DIR


class ImageGenerator:
    """
    Handles all image generation via Google Generative AI (Imagen 3).
    """

    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.ImageGenerationModel("imagen-3.0-generate-002")

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
            seed: Optional seed for reproducibility (not supported by Imagen, ignored)

        Returns:
            Path to the generated image
        """
        width, height = AD_SIZES.get(size, AD_SIZES[DEFAULT_AD_SIZE])

        # Determine aspect ratio for Imagen
        aspect_ratio = self._get_aspect_ratio(width, height)

        # Run image generation in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio=aspect_ratio,
                safety_filter_level="block_only_high",
                person_generation="allow_adult",
            )
        )

        # Generate output path if not provided
        if output_path is None:
            import uuid
            output_path = OUTPUT_DIR / f"generated_{uuid.uuid4().hex[:8]}.png"

        # Save the image
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Imagen returns images directly, save the first one
        image = result.images[0]
        image._pil_image.save(str(output_path), format="PNG")

        return output_path

    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """Convert dimensions to Imagen aspect ratio string"""
        ratio = width / height

        # Imagen 3 supported aspect ratios
        if abs(ratio - 1.0) < 0.1:
            return "1:1"
        elif abs(ratio - 16/9) < 0.1:
            return "16:9"
        elif abs(ratio - 9/16) < 0.1:
            return "9:16"
        elif abs(ratio - 4/3) < 0.1:
            return "4:3"
        elif abs(ratio - 3/4) < 0.1:
            return "3:4"
        elif ratio > 1:
            return "16:9"  # Default landscape
        else:
            return "9:16"  # Default portrait

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

    def generate_image_sync(
        self,
        prompt: str,
        size: str = DEFAULT_AD_SIZE,
        output_path: Optional[Path] = None,
        seed: Optional[int] = None
    ) -> Path:
        """Synchronous version of generate_image"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.generate_image(prompt, size, output_path, seed)
            )
        finally:
            loop.close()

    def generate_batch_sync(
        self,
        prompts: list[str],
        size: str = DEFAULT_AD_SIZE,
        output_prefix: str = "batch"
    ) -> list[Path]:
        """Synchronous version of generate_batch"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.generate_batch(prompts, size, output_prefix)
            )
        finally:
            loop.close()


class ImageGeneratorWithFallback(ImageGenerator):
    """
    Image generator with automatic retry on failure.
    Uses Imagen 3 with retry logic.
    """

    def __init__(self):
        super().__init__()
        self.max_retries = 3

    async def generate_image_with_fallback(
        self,
        prompt: str,
        size: str = DEFAULT_AD_SIZE,
        output_path: Optional[Path] = None
    ) -> Path:
        """Generate image with automatic retry on failure"""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return await self.generate_image(prompt, size, output_path)
            except Exception as e:
                last_error = e
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                continue

        raise Exception(f"All {self.max_retries} attempts failed. Last error: {last_error}")
