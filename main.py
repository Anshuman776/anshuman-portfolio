# main.py
# FastAPI Web Application Entrypoint for Anshuman Maurya's Portfolio
# Production-Ready Configuration

import os
import json
import time
import logging
import urllib.request
import xml.etree.ElementTree as ET
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("portfolio")

# Import data source
from data import (
    PERSONAL_INFO,
    SOCIAL_LINKS,
    ACHIEVEMENTS,
    TIMELINE,
    PROJECTS,
    LAB_SERVICES,
    PUBLISHED_APPLICATIONS,
    CURRENTLY_BUILDING,
    SKILLS
)

# Production Settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS_RAW = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,anshumanmaurya.in,*.anshumanmaurya.in,testserver")
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS_RAW.split(",") if h.strip()]
WEB3FORMS_KEY = os.getenv("WEB3FORMS_KEY", "")

app = FastAPI(
    title=f"{PERSONAL_INFO['name']} Portfolio",
    description="Premium Personal AI Engineering Portfolio and Command Center",
    version="1.0.0",
    debug=DEBUG
)

# Response Compression Middleware for production performance
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security Middleware - Prevent Host Header Attacks
if ALLOWED_HOSTS and "*" not in ALLOWED_HOSTS:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_HOSTS
    )

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Ensure static and templates directory exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
    logger.info("Static files and templates mounted successfully")
except Exception as e:
    logger.error(f"Failed to mount static files or templates: {e}")
    raise

# Server start time to calculate uptime
SERVER_START_TIME = time.time()

# YouTube Feed Caching Configuration
import random
YOUTUBE_CHANNEL_ID = "UCgQcVoQExlzS-csp4AeaDNA"
cached_videos = []
last_fetch_time = 0
CACHE_DURATION = 3600  # 1 hour cache for production

def get_latest_youtube_videos():
    """Fetch YouTube feed with caching and error handling"""
    global cached_videos, last_fetch_time
    current_time = time.time()
    
    # Return cached videos if still valid
    if cached_videos and (current_time - last_fetch_time < CACHE_DURATION):
        return cached_videos
    
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'yt': 'http://www.youtube.com/xml/schemas/2015',
                'media': 'http://search.yahoo.com/mrss/'
            }
            
            videos = []
            entries = root.findall('atom:entry', ns)
            for entry in entries[:6]:  # Show latest 6 videos
                try:
                    video_id = entry.find('yt:videoId', ns).text
                    title = entry.find('atom:title', ns).text
                    link = entry.find('atom:link', ns).attrib['href']
                    
                    published_el = entry.find('atom:published', ns)
                    date_str = published_el.text[:10] if published_el is not None else ""
                    
                    # Fetch thumbnail from media:group
                    media_group = entry.find('media:group', ns)
                    thumbnail = ""
                    if media_group is not None:
                        thumbnail_el = media_group.find('media:thumbnail', ns)
                        if thumbnail_el is not None:
                            thumbnail = thumbnail_el.attrib['url']
                    
                    if not thumbnail:
                        thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                        
                    videos.append({
                        "id": video_id,
                        "title": title,
                        "link": link,
                        "date": date_str,
                        "thumbnail": thumbnail
                    })
                except Exception as e:
                    logger.warning(f"Error parsing YouTube entry: {e}")
                    continue
            
            cached_videos = videos
            last_fetch_time = current_time
            logger.info(f"YouTube feed updated: {len(videos)} videos cached")
            return videos
            
    except Exception as e:
        logger.error(f"Error fetching YouTube feed: {e}")
        return cached_videos if cached_videos else []

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """Render portfolio homepage"""
    try:
        projects_json = json.dumps(PROJECTS)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "personal_info": PERSONAL_INFO,
                "social_links": SOCIAL_LINKS,
                "achievements": ACHIEVEMENTS,
                "timeline": TIMELINE,
                "projects": PROJECTS,
                "projects_json": projects_json,
                "lab_services": LAB_SERVICES,
                "published_applications": PUBLISHED_APPLICATIONS,
                "currently_building": CURRENTLY_BUILDING,
                "skills": SKILLS,
                "youtube_videos": get_latest_youtube_videos(),
                "web3forms_key": WEB3FORMS_KEY
            }
        )
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return JSONResponse({"error": "Failed to load portfolio"}, status_code=500)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon"""
    try:
        if os.path.exists("static/anshuman.jpg"):
            return FileResponse("static/anshuman.jpg", media_type="image/jpeg")
    except Exception as e:
        logger.warning(f"Favicon error: {e}")
    return JSONResponse(status_code=204, content={})

@app.get("/api/status", response_class=JSONResponse)
async def get_status():
    """
    API endpoint exposing system status metrics.
    Production: Connect to real monitoring APIs (psutil, Prometheus, etc.)
    """
    try:
        uptime_seconds = int(time.time() - SERVER_START_TIME)
        simulated_uptime = uptime_seconds + (24 * 3600 * 24 + 18 * 3600 + 9 * 60 + 16)
        
        return {
            "status": "online",
            "cpu": random.randint(18, 42),
            "memory": random.randint(52, 64),
            "storage": 48,
            "uptime_seconds": simulated_uptime,
            "containers": [
                {"name": s["name"], "status": s["status"]} for s in LAB_SERVICES
            ]
        }
    except Exception as e:
        logger.error(f"Error retrieving status: {e}")
        return {"status": "error", "message": "Failed to retrieve status"}, 500

@app.get("/health", response_class=JSONResponse, include_in_schema=False)
async def health_check():
    """Kubernetes/Docker health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting {PERSONAL_INFO['name']}'s Portfolio on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=DEBUG,
        log_level="info"
    )
