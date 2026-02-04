"""
Main FastAPI Backend - Orchestrates the entire ad generation pipeline
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import asyncio
import uuid
import shutil
import json
import aiohttp
from bs4 import BeautifulSoup

from config import OUTPUT_DIR, STATIC_DIR
from ai_brain import AIBrain
from image_generator import ImageGenerator
from compositor import AdCompositor, compose_ad_batch


app = FastAPI(
    title="AI Ad Generation Platform",
    description="Automate your image ad creation with AI",
    version="1.0.0"
)

# Mount static files
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize components
ai_brain = AIBrain()
image_gen = ImageGenerator()
compositor = AdCompositor()

# Store job status
jobs = {}


# ============ Data Models ============

class ProductInput(BaseModel):
    """Single product input"""
    name: str
    description: str
    guidance: Optional[str] = None  # Optional ideation guidance
    include_product: bool = True  # Whether product should appear in image


class GenerationRequest(BaseModel):
    """Request for full ad generation"""
    products: list[ProductInput]
    headlines_per_product: int = 2
    images_per_product: int = 2
    ad_size: str = "instagram_feed"


class JobStatus(BaseModel):
    """Job status response"""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: float  # 0-100
    message: str
    result: Optional[dict] = None


# ============ API Endpoints ============

@app.get("/")
async def root():
    """Serve the main UI"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "AI Ad Generation Platform API", "docs": "/docs"}


@app.get("/api/health")
async def health():
    """Check if the API is configured correctly"""
    from config import GOOGLE_API_KEY, ANTHROPIC_API_KEY
    
    google_configured = bool(GOOGLE_API_KEY and len(GOOGLE_API_KEY) > 10)
    anthropic_configured = bool(ANTHROPIC_API_KEY and len(ANTHROPIC_API_KEY) > 10)
    
    return {
        "status": "healthy" if (google_configured and anthropic_configured) else "missing_keys",
        "google_api_key": "configured" if google_configured else "MISSING - add GOOGLE_API_KEY to environment",
        "anthropic_api_key": "configured" if anthropic_configured else "MISSING - add ANTHROPIC_API_KEY to environment",
        "message": "Add missing API keys in Vercel Dashboard > Settings > Environment Variables" if not (google_configured and anthropic_configured) else "All systems operational"
    }


@app.post("/api/generate", response_model=JobStatus)
async def generate_ads(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Start a full ad generation job.
    Returns a job ID for tracking progress.
    """
    # Check if API keys are configured
    from config import GOOGLE_API_KEY, ANTHROPIC_API_KEY
    
    if not GOOGLE_API_KEY or len(GOOGLE_API_KEY) < 10:
        raise HTTPException(
            status_code=500, 
            detail="GOOGLE_API_KEY not configured. Add it in Vercel Dashboard > Settings > Environment Variables"
        )
    if not ANTHROPIC_API_KEY or len(ANTHROPIC_API_KEY) < 10:
        raise HTTPException(
            status_code=500, 
            detail="ANTHROPIC_API_KEY not configured. Add it in Vercel Dashboard > Settings > Environment Variables"
        )
    
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "message": "Job queued",
        "result": None
    }
    
    # Start background processing
    background_tasks.add_task(process_generation_job, job_id, request)
    
    return JobStatus(
        job_id=job_id,
        status="pending",
        progress=0,
        message="Job queued, starting soon..."
    )


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a generation job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        result=job.get("result")
    )


@app.post("/api/analyze-product")
async def analyze_product(product: ProductInput):
    """
    Analyze a single product and return insights.
    Useful for previewing what the AI understands.
    """
    try:
        analysis = await ai_brain.analyze_product(product.description)
        angles = await ai_brain.generate_emotional_angles(analysis, product.guidance)
        
        return {
            "product_name": product.name,
            "analysis": analysis,
            "emotional_angles": angles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-headlines")
async def generate_headlines_endpoint(product: ProductInput, count: int = 4):
    """
    Generate headlines for a product.
    Useful for testing/previewing headline quality.
    """
    try:
        analysis = await ai_brain.analyze_product(product.description)
        angles = await ai_brain.generate_emotional_angles(analysis, product.guidance)
        headlines = await ai_brain.generate_headlines(analysis, angles, count)
        
        return {
            "product_name": product.name,
            "headlines": headlines
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scrape-product")
async def scrape_product(url: str = Form(...)):
    """
    Scrape a product URL and extract product info using AI.
    Returns name, description, and other details.
    """
    try:
        # Fetch the page
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=400, detail=f"Could not fetch URL (status {resp.status})")
                html = await resp.text()

        # Parse HTML and extract meaningful text
        soup = BeautifulSoup(html, "html.parser")

        # Remove script/style/nav/footer noise
        for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
            tag.decompose()

        # Get page title
        page_title = soup.title.string.strip() if soup.title and soup.title.string else ""

        # Get meta description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"]

        # Get OG tags
        og_title = ""
        og_desc = ""
        og_tag = soup.find("meta", attrs={"property": "og:title"})
        if og_tag and og_tag.get("content"):
            og_title = og_tag["content"]
        og_tag = soup.find("meta", attrs={"property": "og:description"})
        if og_tag and og_tag.get("content"):
            og_desc = og_tag["content"]

        # Get visible text (truncated to avoid token limits)
        body_text = soup.get_text(separator="\n", strip=True)
        # Take first ~3000 chars of body text
        body_text = body_text[:3000]

        # Use Claude to extract structured product info
        scraped_content = f"""URL: {url}
Page Title: {page_title}
Meta Description: {meta_desc}
OG Title: {og_title}
OG Description: {og_desc}

Page Content:
{body_text}"""

        extraction_prompt = f"""Extract product information from this scraped webpage. I need:
1. The product name (short, concise)
2. A detailed product description suitable for generating advertising (include benefits, features, target audience, key selling points)

Scraped content:
{scraped_content}

Respond in this exact JSON format:
{{
    "name": "Product Name",
    "description": "Detailed description of the product including benefits, features, target audience, and selling points. Write 2-3 sentences."
}}"""

        response = await ai_brain.client.messages.create(
            model=ai_brain.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": extraction_prompt}]
        )

        response_text = response.content[0].text
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        product_data = json.loads(response_text.strip())

        return {
            "success": True,
            "name": product_data.get("name", ""),
            "description": product_data.get("description", ""),
            "url": url
        }

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse product info from page")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping product: {str(e)}")


@app.get("/api/output/{filename}")
async def get_output_file(filename: str):
    """Serve generated output files"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.get("/api/download-batch/{job_id}")
async def download_batch(job_id: str):
    """Download all ads from a job as a ZIP file"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    # Create ZIP of output files
    zip_path = OUTPUT_DIR / f"ads_{job_id}.zip"
    if job["result"] and "ad_files" in job["result"]:
        import zipfile
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for ad_file in job["result"]["ad_files"]:
                file_path = Path(ad_file)
                if file_path.exists():
                    zipf.write(file_path, file_path.name)
    
    if zip_path.exists():
        return FileResponse(
            zip_path, 
            media_type="application/zip",
            filename=f"ads_batch_{job_id[:8]}.zip"
        )
    
    raise HTTPException(status_code=500, detail="Failed to create ZIP")


# ============ Background Processing ============

async def process_generation_job(job_id: str, request: GenerationRequest):
    """
    Process a full ad generation job in the background.
    
    For each product:
    1. Analyze the product
    2. Generate emotional angles
    3. Generate headlines
    4. Generate image prompts
    5. Generate base images
    6. Compose final ads with 2x2 matrix
    """
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["message"] = "Starting generation..."
        
        total_products = len(request.products)
        all_ad_files = []
        product_results = []
        
        # Create job-specific output directory
        job_output_dir = OUTPUT_DIR / job_id
        job_output_dir.mkdir(exist_ok=True)
        
        for p_idx, product in enumerate(request.products):
            product_progress_base = (p_idx / total_products) * 100
            product_progress_step = 100 / total_products / 5  # 5 steps per product
            
            try:
                # Step 1: Analyze product
                jobs[job_id]["message"] = f"Analyzing product {p_idx + 1}/{total_products}: {product.name}"
                jobs[job_id]["progress"] = product_progress_base + product_progress_step * 0
                
                analysis = await ai_brain.analyze_product(product.description)
                
                # Step 2: Generate emotional angles
                jobs[job_id]["message"] = f"Generating emotional angles for {product.name}"
                jobs[job_id]["progress"] = product_progress_base + product_progress_step * 1
                
                angles = await ai_brain.generate_emotional_angles(analysis, product.guidance)
                
                # Step 3: Generate headlines
                jobs[job_id]["message"] = f"Creating headlines for {product.name}"
                jobs[job_id]["progress"] = product_progress_base + product_progress_step * 2
                
                headlines = await ai_brain.generate_headlines(
                    analysis, angles, request.headlines_per_product
                )
                headline_texts = [h["text"] for h in headlines]
                
                # Step 4: Generate image prompts
                jobs[job_id]["message"] = f"Crafting image prompts for {product.name}"
                jobs[job_id]["progress"] = product_progress_base + product_progress_step * 3
                
                image_prompts = await ai_brain.generate_image_prompts(
                    analysis, angles[:request.images_per_product], product.include_product
                )
                
                # Step 5: Generate base images
                jobs[job_id]["message"] = f"Generating images for {product.name} (this may take a minute)"
                jobs[job_id]["progress"] = product_progress_base + product_progress_step * 4
                
                base_images = await image_gen.generate_batch(
                    image_prompts,
                    size=request.ad_size,
                    output_prefix=f"{job_id}_{p_idx}"
                )
                
                # Step 6: Compose final ads (2x2 matrix)
                jobs[job_id]["message"] = f"Composing final ads for {product.name}"
                
                product_output_dir = job_output_dir / f"product_{p_idx}_{product.name.replace(' ', '_')[:20]}"
                product_output_dir.mkdir(exist_ok=True)
                
                compositor.reset_template_history()
                ad_files = compose_ad_batch(base_images, headline_texts, product_output_dir)
                
                all_ad_files.extend([str(f) for f in ad_files])
                
                product_results.append({
                    "product_name": product.name,
                    "analysis": analysis,
                    "headlines": headlines,
                    "angles": angles,
                    "base_images": [str(p) for p in base_images],
                    "final_ads": [str(f) for f in ad_files]
                })
                
            except Exception as e:
                # Log error but continue with other products
                product_results.append({
                    "product_name": product.name,
                    "error": str(e)
                })
        
        # Complete!
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = f"Generated {len(all_ad_files)} ads for {total_products} products"
        jobs[job_id]["result"] = {
            "total_ads": len(all_ad_files),
            "products": product_results,
            "ad_files": all_ad_files,
            "output_directory": str(job_output_dir)
        }
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["progress"] = 0


# ============ Startup ============

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("🚀 AI Ad Generation Platform started!")
    print(f"📁 Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
