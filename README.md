# Instagram Post Match API (reelscraper)

A minimal Flask API for matching Instagram posts using the reelscraper library.

## Features
- No Playwright, no extra helpers
- Uses only reelscraper for all scraping and matching
- Simple `/v1/fetch-instagram-post` endpoint

## Endpoints

### Health Check
```
GET /v1/health
```

### Fetch Instagram Posts
```
POST /v1/fetch-instagram-post
Content-Type: application/json
{
  "username": "nasa",
  "post_links": ["https://www.instagram.com/reel/SHORTCODE/"]
}
```

## Running Locally
```bash
pip install -r requirements.txt
python app.py
```

## Docker
```bash
docker build -t reelscraper-api .
docker run -p 5000:5000 reelscraper-api
```

## Example Response
```json
{
  "success": true,
  "timestamp": "...",
  "data": {
    "username": "nasa",
    "total_reels_scraped": 10,
    "total_target_links": 1,
    "matched_posts_count": 1,
    "matched_posts": [
      {
        "shortcode": "SHORTCODE",
        "url": "https://www.instagram.com/reel/SHORTCODE/",
        ...
      }
    ]
  }
}
``` 