# AI Ad Generator

Generate 28+ ad variations in minutes using AI-powered ideation, headlines, and image generation.

## Features

- 🧠 **AI Product Analysis** - Understands your product and target audience
- 💡 **Emotional Angle Generation** - Picks the right emotional hooks (fear, aspiration, satisfaction, etc.)
- ✍️ **Headline Engine** - Creates 3-7 word headlines that tell an entire story
- 🎨 **Image Generation** - Uses Flux Pro for high-quality ad imagery via Replicate
- 📐 **6 Template Styles** - Prevents format staleness with varied layouts
- 📦 **2x2 Matrix Output** - 7 products × 2 headlines × 2 images = 28 ads

## Quick Start

### 1. Get API Keys

You'll need:
- **Replicate API Token**: [Get it here](https://replicate.com/account/api-tokens)
- **Anthropic API Key**: [Get it here](https://console.anthropic.com/settings/keys)

### 2. Setup

```bash
# Clone/navigate to the project
cd "Image automation"

# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

### 3. Run

```bash
# Option A: Use the quick start script
chmod +x start.sh
./start.sh

# Option B: Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### 4. Open the UI

Navigate to: **http://localhost:8000**

## Usage

1. **Add Products** (up to 7)
   - Enter product name
   - Describe the product, benefits, target audience
   - Optional: Add creative guidance (e.g., "push anti-aging angle")

2. **Configure Settings**
   - Choose ad size (Instagram, Facebook, etc.)
   - Select headlines per product (2-4)
   - Select images per product (2-4)

3. **Generate**
   - Click "Generate Ads"
   - Wait for AI to work its magic (~30-60 seconds per product)
   - Download all ads as ZIP or individually

## Template Styles

The compositor randomly rotates through 6 template styles:

1. **Minimal** - Clean headline at top
2. **Banner Bottom** - Solid color banner with text
3. **Sale Sticker** - Circle sticker overlay in corner
4. **Split Layout** - Text panel on left, image on right
5. **Diagonal Banner** - Angled banner across corner
6. **Gradient Overlay** - Dark gradient from bottom with text

## Cost Estimate

Per batch of 28 ads:
- Image Generation: ~$0.70 (14 images × ~$0.05)
- Claude API: ~$0.05 (ideation + headlines)
- **Total: ~$0.75** ($0.027 per ad)

## Project Structure

```
Image automation/
├── main.py              # FastAPI backend
├── ai_brain.py          # Claude-powered ideation
├── image_generator.py   # Replicate/Flux integration
├── compositor.py        # Template-based ad formatting
├── config.py            # Configuration
├── requirements.txt     # Python dependencies
├── .env.example         # API key template
├── start.sh             # Quick start script
├── static/
│   ├── index.html       # Web UI
│   ├── styles.css       # Styling
│   └── app.js           # Frontend logic
├── templates/           # Ad templates
│   └── fonts/           # Custom fonts (optional)
└── output/              # Generated ads
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/api/generate` | POST | Start batch generation |
| `/api/jobs/{job_id}` | GET | Check job status |
| `/api/analyze-product` | POST | Analyze single product |
| `/api/generate-headlines` | POST | Generate headlines only |
| `/api/download-batch/{job_id}` | GET | Download all ads as ZIP |

## Extending

### Add Custom Fonts

Drop `.ttf` or `.otf` files into `templates/fonts/` for custom typography.

### Add New Template Styles

Edit `compositor.py` and add a new method `_apply_your_style()`, then add the style name to `TEMPLATE_STYLES` in `config.py`.

### Add Video Generation (Future)

The architecture is designed to support video. Integration points:
- Add `video_generator.py` with Kling/Veo API
- Extend `main.py` with video generation endpoints
- Update UI with video options

## License

MIT
