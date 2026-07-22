import importlib
import json
from datetime import datetime
from pathlib import Path

import requests

from logger import logger

DATA_DIR = Path("content")
QUEUE_FILE = DATA_DIR / "queue.json"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

def get_next_post():
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    now = datetime.now()

    for post in sorted(queue, key=lambda p: p["publish"]):
        publish_time = datetime.strptime(post["publish"], "%Y-%m-%d %H:%M")

        if publish_time > now: 
            continue

        if all(post["published"].values()):
            continue

        return post
    return None

def read_post(post):
    path = DATA_DIR / "posts" / f'{post["id"]}.md'

    if not path.exists():
        raise FileNotFoundError(f"Post {post['id']} not found")

    return path.read_text(encoding="utf-8")

def find_image(post):
    images = DATA_DIR / "images"

    for ext in IMAGE_EXTENSIONS:
        image = images / f"{post['id']}{ext}"
        if image.exists():
            return image
            
    raise FileNotFoundError(f"Image for post {post['id']} not found")

def get_publisher(platform):
    module = importlib.import_module(f"platforms.{platform}")

    return module.publish_post

def mark_platform_posted(post_id, platform):
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    for post in queue:
        if post["id"] != post_id:
            continue

        post["published"][platform] = True

        if all(post["published"].values()):
            post["published_at"] = (datetime.utcnow().isoformat() + "Z")
        break
    else:
        raise ValueError(f"Post {post_id} not found in queue")

    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4)

    logger.info(f"Post {post_id} marked as published on {platform}")

def main():
    try:
        post = get_next_post()

        if post is None:
            logger.info("No scheduled post to publish")
            return

        logger.info(f"Preparing to publish post {post['id']}")

        text = read_post(post)
        image = find_image(post)

        for platform in post["platforms"]:
            if post["published"].get(platform):
                logger.info(f"Post {post['id']} already published on {platform}")
                continue

            logger.info(f"Publishing post {post['id']} to {platform}")

            try:
                publisher = get_publisher(platform)

                succes = publisher(text, image)

                if succes:
                    mark_platform_posted(post['id'], platform)

                    logger.info(f"Post {post['id']} successfully published on {platform}")

                else:
                    logger.info(f"Failed to publish post {post['id']} to {platform}")

            except Exception:
                logger.exception(f"Error publishing post {post['id']} to {platform}")

    except FileNotFoundError as e:
        logger.error(e)
    
    except requests.exceptions.RequestException as e:
        logger.error(e)
    
    except Exception:
        logger.exception("Unexpected error.")

if __name__ == "__main__":
    main()
