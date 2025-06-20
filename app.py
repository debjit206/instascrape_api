from flask import Flask, request, jsonify
from reelscraper import ReelScraper, ReelMultiScraper
from reelscraper.utils import LoggerManager
import os
from datetime import datetime, timezone

app = Flask(__name__)

# Configure logger
logger = LoggerManager()

# Create a single scraper instance
single_scraper = ReelScraper(timeout=30, proxy=None, logger_manager=logger)

@app.route("/v1/fetch-instagram-post", methods=["POST"])
def fetch_instagram_post():
    try:
        data = request.get_json()
        username = data.get("username")
        post_links = data.get("post_links")

        if not username or not post_links or not isinstance(post_links, list):
            return jsonify({
                "success": False,
                "error": "username and post_links (list) are required",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 400

        # Scrape latest posts from user
        reels = single_scraper.get_user_reels(username, max_posts=10)
        if not reels:
            return jsonify({
                "success": False,
                "error": f"No reels found for user '{username}'",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 404

        # Match with provided post links (by shortcode)
        def extract_shortcode(url):
            import re
            patterns = [r'/reel/([^/?]+)', r'/p/([^/?]+)']
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None

        target_shortcodes = {extract_shortcode(link): link for link in post_links if extract_shortcode(link)}
        matched = [reel for reel in reels if reel.get('shortcode') in target_shortcodes]

        # Attach the original target link to each matched post
        for post in matched:
            post['target_link'] = target_shortcodes.get(post.get('shortcode'))

        return jsonify({
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "username": username,
                "total_reels_scraped": len(reels),
                "total_target_links": len(post_links),
                "matched_posts_count": len(matched),
                "matched_posts": matched
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@app.route("/v1/health", methods=["GET"])
def health_check():
    return jsonify({
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {"status": "healthy", "service": "reelscraper-api"}
    })

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "message": "Instagram Post Match API (reelscraper) is running!",
            "documentation": {
                "fetch_posts": "POST /v1/fetch-instagram-post",
                "health": "GET /v1/health"
            }
        }
    })

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host="0.0.0.0", port=port) 