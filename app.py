
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from reelscraper import ReelScraper
from reelscraper.utils import LoggerManager
from datetime import datetime, timezone
import os
import re

app = FastAPI()

# Logger and scraper setup
logger = LoggerManager()

# Proxy credentials
#proxy_url = "http://customer-j2t6521216:ni0kkm6q@proxy.goproxy.com:30000"
proxy_url = "customer-j2t6521216:ni0kkm6q@proxy.goproxy.com:30000"  # <-- NO http://
proxy_dict = {
    "http": proxy_url,
    "https": proxy_url
}

single_scraper = ReelScraper(timeout=30, proxy=proxy_url, logger_manager=logger)

# Request model
class PostRequest(BaseModel):
    username: str
    post_links: List[str]

@app.post("/v1/fetch-instagram-post")
def fetch_instagram_post(payload: PostRequest):
    try:
        username = payload.username
        post_links = payload.post_links

        reels = single_scraper.get_user_reels(username, max_posts=10)
        if not reels:
            raise HTTPException(
                status_code=404,
                detail=f"No reels found for user '{username}'"
            )

        def extract_shortcode(url):
            patterns = [r'/reel/([^/?]+)', r'/p/([^/?]+)']
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None

        target_shortcodes = {extract_shortcode(link): link for link in post_links if extract_shortcode(link)}
        matched = [reel for reel in reels if reel.get('shortcode') in target_shortcodes]

        for post in matched:
            post['target_link'] = target_shortcodes.get(post.get('shortcode'))

        return {
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "username": username,
                "total_reels_scraped": len(reels),
                "total_target_links": len(post_links),
                "matched_posts_count": len(matched),
                "matched_posts": matched
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/v1/health")
def health_check():
    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {"status": "healthy", "service": "reelscraper-api"}
    }

@app.get("/")
def home():
    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "message": "Instagram Post Match API (FastAPI) is running!",
            "documentation": {
                "fetch_posts": "POST /v1/fetch-instagram-post",
                "health": "GET /v1/health",
                "swagger_docs": "/docs"
            }
        }
    }
