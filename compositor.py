"""
Ad Compositor - Template-based ad formatting and compositing
Creates final ad-ready images with headlines, overlays, and formatting
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from typing import Optional, Tuple
import random
from config import (
    TEMPLATES_DIR, FONTS_DIR, OUTPUT_DIR, 
    TEMPLATE_STYLES, TEMPLATE_COLORS, FONT_SETTINGS,
    AD_SIZES, DEFAULT_AD_SIZE
)


class AdCompositor:
    """
    Takes base images and combines them with headlines and formatting
    to create final, polished ad images.
    
    Supports multiple template styles to prevent format staleness.
    """
    
    def __init__(self):
        self.font_path = self._get_default_font()
        self.used_templates = []  # Track used templates to ensure variety
    
    def _get_default_font(self) -> Optional[Path]:
        """Get a font file, with fallback to system fonts"""
        # Check for custom fonts in templates/fonts
        custom_fonts = list(FONTS_DIR.glob("*.ttf")) + list(FONTS_DIR.glob("*.otf"))
        if custom_fonts:
            return custom_fonts[0]
        
        # Fallback to common system fonts
        system_fonts = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/System/Library/Fonts/SFProDisplay-Bold.otf",  # macOS
            "/Library/Fonts/Arial Bold.ttf",  # macOS
            "C:/Windows/Fonts/arial.ttf",  # Windows
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        ]
        for font in system_fonts:
            if Path(font).exists():
                return Path(font)
        
        return None  # Will use PIL default
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get font at specified size"""
        if self.font_path:
            try:
                return ImageFont.truetype(str(self.font_path), size)
            except Exception:
                pass
        return ImageFont.load_default()
    
    def _select_template(self, avoid_recent: int = 3) -> str:
        """
        Select a template style, avoiding recently used ones.
        This prevents format staleness.
        """
        available = [t for t in TEMPLATE_STYLES if t not in self.used_templates[-avoid_recent:]]
        if not available:
            available = TEMPLATE_STYLES
        
        selected = random.choice(available)
        self.used_templates.append(selected)
        return selected
    
    def reset_template_history(self):
        """Reset template history for a new batch"""
        self.used_templates = []
    
    def compose_ad(
        self,
        base_image_path: Path,
        headline: str,
        template_style: Optional[str] = None,
        output_path: Optional[Path] = None,
        subheadline: Optional[str] = None,
        cta_text: Optional[str] = None,
        sale_text: Optional[str] = None
    ) -> Path:
        """
        Compose a final ad from base image and text elements.
        
        Args:
            base_image_path: Path to the AI-generated base image
            headline: Main headline text (3-7 words)
            template_style: Template to use (auto-selected if None)
            output_path: Where to save (auto-generated if None)
            subheadline: Optional secondary text
            cta_text: Optional call-to-action text
            sale_text: Optional sale/discount text
            
        Returns:
            Path to the final composed ad image
        """
        # Load base image
        img = Image.open(base_image_path).convert("RGBA")
        
        # Select template if not specified
        if template_style is None:
            template_style = self._select_template()
        
        # Apply template
        if template_style == "minimal":
            img = self._apply_minimal(img, headline, subheadline)
        elif template_style == "banner_bottom":
            img = self._apply_banner_bottom(img, headline, cta_text)
        elif template_style == "sale_sticker":
            img = self._apply_sale_sticker(img, headline, sale_text or "SALE")
        elif template_style == "split_layout":
            img = self._apply_split_layout(img, headline, subheadline)
        elif template_style == "diagonal_banner":
            img = self._apply_diagonal_banner(img, headline)
        elif template_style == "gradient_overlay":
            img = self._apply_gradient_overlay(img, headline, subheadline)
        else:
            # Default to minimal
            img = self._apply_minimal(img, headline, subheadline)
        
        # Generate output path if needed
        if output_path is None:
            import uuid
            output_path = OUTPUT_DIR / f"ad_{template_style}_{uuid.uuid4().hex[:8]}.png"
        
        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(output_path, "PNG", quality=95)
        
        return output_path
    
    def _apply_minimal(
        self, 
        img: Image.Image, 
        headline: str, 
        subheadline: Optional[str] = None
    ) -> Image.Image:
        """
        Minimal template: Clean headline at top with subtle shadow
        """
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Calculate font size based on image width
        font_size = int(width * FONT_SETTINGS["headline"]["size_ratio"])
        font = self._get_font(font_size)
        
        # Get text size
        bbox = draw.textbbox((0, 0), headline, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position at top center with padding
        x = (width - text_width) // 2
        y = int(height * 0.05)
        
        # Draw shadow
        shadow_offset = max(2, font_size // 20)
        draw.text((x + shadow_offset, y + shadow_offset), headline, 
                  font=font, fill=(0, 0, 0, 180))
        
        # Draw headline
        draw.text((x, y), headline, font=font, fill=TEMPLATE_COLORS["text_light"])
        
        # Add subheadline if provided
        if subheadline:
            sub_font_size = int(width * FONT_SETTINGS["subheadline"]["size_ratio"])
            sub_font = self._get_font(sub_font_size)
            sub_bbox = draw.textbbox((0, 0), subheadline, font=sub_font)
            sub_width = sub_bbox[2] - sub_bbox[0]
            sub_x = (width - sub_width) // 2
            sub_y = y + text_height + int(height * 0.02)
            draw.text((sub_x, sub_y), subheadline, font=sub_font, 
                      fill=TEMPLATE_COLORS["text_light"])
        
        return img
    
    def _apply_banner_bottom(
        self, 
        img: Image.Image, 
        headline: str,
        cta_text: Optional[str] = None
    ) -> Image.Image:
        """
        Banner template: Solid color banner at bottom with headline
        """
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Calculate banner height
        banner_height = int(height * 0.15)
        banner_y = height - banner_height
        
        # Draw banner background
        banner_color = self._hex_to_rgba(TEMPLATE_COLORS["primary"], 230)
        draw.rectangle(
            [(0, banner_y), (width, height)],
            fill=banner_color
        )
        
        # Draw headline
        font_size = int(width * FONT_SETTINGS["headline"]["size_ratio"] * 0.9)
        font = self._get_font(font_size)
        bbox = draw.textbbox((0, 0), headline, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = banner_y + (banner_height - text_height) // 2
        
        if cta_text:
            y -= int(banner_height * 0.1)
        
        draw.text((x, y), headline, font=font, fill=TEMPLATE_COLORS["text_light"])
        
        # Add CTA if provided
        if cta_text:
            cta_font_size = int(font_size * 0.5)
            cta_font = self._get_font(cta_font_size)
            cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
            cta_width = cta_bbox[2] - cta_bbox[0]
            cta_x = (width - cta_width) // 2
            cta_y = y + text_height + int(banner_height * 0.05)
            draw.text((cta_x, cta_y), cta_text, font=cta_font, 
                      fill=TEMPLATE_COLORS["accent"])
        
        return img
    
    def _apply_sale_sticker(
        self, 
        img: Image.Image, 
        headline: str,
        sale_text: str = "SALE"
    ) -> Image.Image:
        """
        Sale sticker template: Headline at top + circular sale sticker
        """
        # First apply minimal headline
        img = self._apply_minimal(img, headline)
        
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Draw sale sticker (circle in corner)
        sticker_radius = int(min(width, height) * 0.12)
        sticker_x = width - sticker_radius - int(width * 0.05)
        sticker_y = height - sticker_radius - int(height * 0.05)
        
        # Draw sticker background
        sticker_color = self._hex_to_rgba(TEMPLATE_COLORS["sale_red"], 255)
        draw.ellipse(
            [(sticker_x - sticker_radius, sticker_y - sticker_radius),
             (sticker_x + sticker_radius, sticker_y + sticker_radius)],
            fill=sticker_color
        )
        
        # Draw sale text
        font_size = int(sticker_radius * 0.5)
        font = self._get_font(font_size)
        bbox = draw.textbbox((0, 0), sale_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = sticker_x - text_width // 2
        text_y = sticker_y - text_height // 2
        draw.text((text_x, text_y), sale_text, font=font, 
                  fill=TEMPLATE_COLORS["text_light"])
        
        return img
    
    def _apply_split_layout(
        self, 
        img: Image.Image, 
        headline: str,
        subheadline: Optional[str] = None
    ) -> Image.Image:
        """
        Split layout: Image takes 70% width, text panel takes 30%
        """
        width, height = img.size
        
        # Create new canvas
        panel_width = int(width * 0.35)
        new_width = width + panel_width
        canvas = Image.new("RGBA", (new_width, height), 
                          self._hex_to_rgba(TEMPLATE_COLORS["primary"], 255))
        
        # Paste original image on the right
        canvas.paste(img, (panel_width, 0))
        
        # Draw text on left panel
        draw = ImageDraw.Draw(canvas)
        
        # Headline
        font_size = int(panel_width * 0.12)
        font = self._get_font(font_size)
        
        # Word wrap the headline
        words = headline.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < panel_width - 40:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        y_offset = height // 3
        for line in lines:
            draw.text((20, y_offset), line, font=font, 
                      fill=TEMPLATE_COLORS["text_light"])
            bbox = draw.textbbox((0, 0), line, font=font)
            y_offset += bbox[3] - bbox[1] + 10
        
        # Resize back to original dimensions
        canvas = canvas.resize((width, height), Image.Resampling.LANCZOS)
        
        return canvas
    
    def _apply_diagonal_banner(
        self, 
        img: Image.Image, 
        headline: str
    ) -> Image.Image:
        """
        Diagonal banner: Angled banner across top-left corner
        """
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Create diagonal banner polygon
        banner_width = int(width * 0.5)
        points = [
            (0, 0),
            (banner_width, 0),
            (0, banner_width)
        ]
        
        banner_color = self._hex_to_rgba(TEMPLATE_COLORS["accent"], 230)
        draw.polygon(points, fill=banner_color)
        
        # Draw headline at an angle (simplified - horizontal for now)
        font_size = int(width * FONT_SETTINGS["headline"]["size_ratio"] * 0.7)
        font = self._get_font(font_size)
        
        # Position in the banner area
        draw.text((20, int(height * 0.08)), headline, font=font, 
                  fill=TEMPLATE_COLORS["text_light"])
        
        return img
    
    def _apply_gradient_overlay(
        self, 
        img: Image.Image, 
        headline: str,
        subheadline: Optional[str] = None
    ) -> Image.Image:
        """
        Gradient overlay: Dark gradient from bottom with text
        """
        width, height = img.size
        
        # Create gradient overlay
        gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_gradient = ImageDraw.Draw(gradient)
        
        # Draw gradient from bottom
        gradient_height = int(height * 0.5)
        for y in range(gradient_height):
            # Calculate alpha (more opaque at bottom)
            progress = y / gradient_height
            alpha = int(200 * progress)
            draw_gradient.line(
                [(0, height - y), (width, height - y)],
                fill=(0, 0, 0, alpha)
            )
        
        # Composite gradient onto image
        img = Image.alpha_composite(img, gradient)
        
        # Draw text
        draw = ImageDraw.Draw(img)
        font_size = int(width * FONT_SETTINGS["headline"]["size_ratio"])
        font = self._get_font(font_size)
        
        bbox = draw.textbbox((0, 0), headline, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = height - int(height * 0.15) - text_height
        
        draw.text((x, y), headline, font=font, fill=TEMPLATE_COLORS["text_light"])
        
        # Subheadline
        if subheadline:
            sub_font_size = int(width * FONT_SETTINGS["subheadline"]["size_ratio"])
            sub_font = self._get_font(sub_font_size)
            sub_bbox = draw.textbbox((0, 0), subheadline, font=sub_font)
            sub_width = sub_bbox[2] - sub_bbox[0]
            sub_x = (width - sub_width) // 2
            sub_y = y + text_height + 10
            draw.text((sub_x, sub_y), subheadline, font=sub_font, 
                      fill=TEMPLATE_COLORS["text_light"])
        
        return img
    
    def _hex_to_rgba(self, hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
        """Convert hex color to RGBA tuple"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, alpha)


def compose_ad_batch(
    base_images: list[Path],
    headlines: list[str],
    output_dir: Optional[Path] = None
) -> list[Path]:
    """
    Compose a batch of ads using the 2x2 matrix approach.
    
    Args:
        base_images: List of 2 base images
        headlines: List of 2 headlines
        output_dir: Directory for output files
        
    Returns:
        List of 4 composed ad paths (all combinations)
    """
    compositor = AdCompositor()
    compositor.reset_template_history()
    
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    output_paths = []
    ad_index = 0
    
    for img_idx, img_path in enumerate(base_images):
        for hl_idx, headline in enumerate(headlines):
            output_path = output_dir / f"ad_{ad_index:02d}_img{img_idx}_hl{hl_idx}.png"
            path = compositor.compose_ad(
                base_image_path=img_path,
                headline=headline,
                output_path=output_path
            )
            output_paths.append(path)
            ad_index += 1
    
    return output_paths
