"""
AI Brain - Claude-powered intelligence layer for ad generation
Handles: Product analysis, emotional angle generation, and headline creation
"""
import anthropic
from typing import Optional
from config import ANTHROPIC_API_KEY, MIN_HEADLINE_WORDS, MAX_HEADLINE_WORDS


class AIBrain:
    """
    The AI Brain powers all creative decisions:
    - Analyzes products to understand what they are
    - Generates emotional angles based on product type
    - Creates compelling 3-7 word headlines that tell a story
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
    
    async def analyze_product(self, product_info: str, reference_context: Optional[str] = None) -> dict:
        """
        Analyze a product from URL, brief, or description.
        Returns structured understanding of the product.
        """
        context_addition = ""
        if reference_context:
            context_addition = f"\n\nAdditional context from reference images: {reference_context}"
        
        prompt = f"""Analyze this product for advertising purposes. I need to understand:
1. What category is this product? (skincare, cleaning, fashion, tech, food, etc.)
2. What are the key benefits?
3. Who is the target audience?
4. What emotional triggers would work best for this product?

Product information:
{product_info}{context_addition}

Respond in this exact JSON format:
{{
    "category": "category name",
    "product_name": "short product name",
    "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
    "target_audience": "description of target audience",
    "emotional_triggers": ["emotion 1", "emotion 2", "emotion 3"],
    "visual_themes": ["theme 1", "theme 2"],
    "product_in_shot": true or false (should the product itself appear in the ad image?)
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse the JSON response
        import json
        response_text = response.content[0].text
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        return json.loads(response_text.strip())
    
    async def generate_emotional_angles(
        self, 
        product_analysis: dict, 
        user_guidance: Optional[str] = None
    ) -> list[dict]:
        """
        Generate emotional angles for the ad based on product type.
        
        Examples:
        - Skincare → anti-aging, insecurity, transformation, confidence
        - Cleaning → disgust at dirt, satisfaction of clean, embarrassment
        - Fashion → lifestyle, aspiration, belonging, identity
        """
        guidance_addition = ""
        if user_guidance:
            guidance_addition = f"\n\nUser's creative guidance: {user_guidance}"
        
        prompt = f"""Based on this product analysis, generate 2 distinct emotional angles for advertising.

Product Analysis:
- Category: {product_analysis['category']}
- Product: {product_analysis['product_name']}
- Benefits: {', '.join(product_analysis['key_benefits'])}
- Target Audience: {product_analysis['target_audience']}
- Known Emotional Triggers: {', '.join(product_analysis['emotional_triggers'])}{guidance_addition}

For each angle, consider:
- Negative emotions to push (fear, insecurity, disgust, FOMO) 
- Positive outcomes to show (transformation, confidence, satisfaction)
- Visual scenarios that embody this emotion

Respond in this exact JSON format:
{{
    "angles": [
        {{
            "name": "angle name",
            "emotion_type": "negative" or "positive",
            "core_emotion": "the main emotion to evoke",
            "visual_scenario": "brief description of the scene/mood for image generation",
            "color_mood": "warm/cool/vibrant/muted/dramatic"
        }},
        {{
            "name": "second angle name",
            "emotion_type": "negative" or "positive", 
            "core_emotion": "the main emotion",
            "visual_scenario": "brief description",
            "color_mood": "warm/cool/vibrant/muted/dramatic"
        }}
    ]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json
        response_text = response.content[0].text
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        return json.loads(response_text.strip())["angles"]
    
    async def generate_headlines(
        self, 
        product_analysis: dict, 
        emotional_angles: list[dict],
        count: int = 2
    ) -> list[dict]:
        """
        Generate compelling 3-7 word headlines that tell an entire story.
        
        Great headlines:
        - "They'll wonder what changed"
        - "Your mirror will notice first"
        - "Guests asked what service you use"
        - "The pants that got you hired"
        """
        angles_text = "\n".join([
            f"- {a['name']}: {a['core_emotion']} ({a['emotion_type']})"
            for a in emotional_angles
        ])
        
        prompt = f"""Generate {count} POWERFUL advertising headlines for this product.

Product: {product_analysis['product_name']}
Category: {product_analysis['category']}
Benefits: {', '.join(product_analysis['key_benefits'])}
Target Audience: {product_analysis['target_audience']}

Emotional Angles to explore:
{angles_text}

CRITICAL HEADLINE RULES:
1. Exactly {MIN_HEADLINE_WORDS}-{MAX_HEADLINE_WORDS} words
2. Must tell an ENTIRE STORY in those few words
3. Imply a before/after transformation
4. Speak to a specific moment or feeling
5. Avoid generic phrases like "best ever" or "amazing results"
6. Use second person ("you", "your") or third person observation ("they noticed")

EXAMPLES OF GREAT HEADLINES:
- "They'll wonder what changed" (transformation, curiosity from others)
- "Your mirror will notice first" (self-improvement, daily ritual)
- "Guests asked what service you use" (social proof, clean home)
- "The interview went differently this time" (confidence, fashion)
- "Your skin at 40, their confusion at 40" (anti-aging, comparison)

Generate {count} headlines that are THIS level of quality.

Respond in this exact JSON format:
{{
    "headlines": [
        {{
            "text": "the headline text",
            "word_count": number,
            "emotional_angle": "which angle this targets",
            "story_implied": "what story/transformation is implied",
            "strength_score": 1-10 rating
        }}
    ]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json
        response_text = response.content[0].text
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        result = json.loads(response_text.strip())
        
        # Sort by strength score and take the top ones
        headlines = sorted(result["headlines"], key=lambda x: x.get("strength_score", 5), reverse=True)
        return headlines[:count]
    
    async def generate_image_prompts(
        self, 
        product_analysis: dict, 
        emotional_angles: list[dict],
        include_product: bool = True
    ) -> list[str]:
        """
        Generate detailed image prompts for Flux/image generation models.
        Creates one prompt per emotional angle.
        """
        prompts = []
        
        for angle in emotional_angles:
            product_context = ""
            if include_product:
                product_context = f"The {product_analysis['product_name']} should be subtly visible or implied in the scene."
            else:
                product_context = f"Do NOT show the product directly. Focus on the emotional scenario and outcome."
            
            prompt = f"""Generate a detailed image prompt for an advertising photo.

Product: {product_analysis['product_name']}
Emotional Angle: {angle['name']}
Core Emotion: {angle['core_emotion']}
Visual Scenario: {angle['visual_scenario']}
Color Mood: {angle['color_mood']}
{product_context}

Create a prompt that will generate a STUNNING advertising image. Include:
- Subject description (person, scene, or product focus)
- Lighting style (natural, studio, dramatic, soft, etc.)
- Color palette that matches the mood
- Composition notes
- Photography style (editorial, lifestyle, product, portrait)
- Any specific details that sell the emotion

The prompt should be detailed but focused, around 50-80 words.
Just respond with the prompt text, no JSON or formatting."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            
            prompts.append(response.content[0].text.strip())
        
        return prompts


# Synchronous wrapper for non-async contexts
class AIBrainSync:
    """Synchronous wrapper for AIBrain"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
        self._async_brain = AIBrain()
    
    def analyze_product(self, product_info: str, reference_context: Optional[str] = None) -> dict:
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self._async_brain.analyze_product(product_info, reference_context)
        )
    
    def generate_emotional_angles(self, product_analysis: dict, user_guidance: Optional[str] = None) -> list[dict]:
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self._async_brain.generate_emotional_angles(product_analysis, user_guidance)
        )
    
    def generate_headlines(self, product_analysis: dict, emotional_angles: list[dict], count: int = 2) -> list[dict]:
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self._async_brain.generate_headlines(product_analysis, emotional_angles, count)
        )
    
    def generate_image_prompts(self, product_analysis: dict, emotional_angles: list[dict], include_product: bool = True) -> list[str]:
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self._async_brain.generate_image_prompts(product_analysis, emotional_angles, include_product)
        )
