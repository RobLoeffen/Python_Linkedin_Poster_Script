from pathlib import Path
from config import ACCESS_TOKEN, PERSON_URN
import requests
import json
from datetime import datetime

from logger import logger

DATA_DIR = Path("content")
QUEUE_FILE = DATA_DIR / "queue.json"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


QUEUE_FILE = DATA_DIR / "queue.json"

def get_next_post():
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    now = datetime.now()

    for post in sorted(queue, key=lambda p: p["publish"]):
        publish = datetime.strptime(
            post["publish"],
            "%Y-%m-%d %H:%M"
        )

        if not post["posted"] and publish <= now:
            return post

    return None


def read_post(post):
    path = DATA_DIR / "posts" / f'{post["id"]}.md'

    return path.read_text(encoding="utf-8")


def find_image(post):

    images = DATA_DIR / "images"

    for ext in IMAGE_EXTENSIONS:

        path = images / f'{post["id"]}{ext}'

        if path.exists():
            return path

    raise FileNotFoundError("Image not found.")

def upload_image(image_path):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "LinkedIn-Version": "202601",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        headers=headers,
        json={
            "initializeUploadRequest": {
                "owner": PERSON_URN
            }
        },
    )

    logger.info(response.status_code)
    logger.info(response.text)
    response.raise_for_status()

    data = response.json()["value"]

    upload_url = data["uploadUrl"]
    image_urn = data["image"]

    logger.info(f"Uploading image to {upload_url}")

    with open(image_path, "rb") as f:
        upload = requests.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}"
            },
            data=f,
        )

    upload.raise_for_status()

    logger.info(f"Image uploaded: {image_urn}")

    return image_urn

def publish_post(post_text, asset_urn):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "LinkedIn-Version": "202601",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }

    payload = {
        "author": PERSON_URN,
        "commentary": post_text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "content": {
            "media": {
                "id": asset_urn
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    response = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=headers,
        json=payload,
    )

    logger.info(response.status_code)
    logger.info(response.text)

    if response.status_code == 201:
        logger.info("Post created successfully.")
        return True

    logger.error(response.text)
    response.raise_for_status()

def mark_as_posted(post_id):

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    for post in queue:

        if post["id"] == post_id:
            post["posted"] = True
            break

    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4)

def main():
    try:
        post = get_next_post()

        if post is None:
            logger.info("No scheduled post found.")
            return

        logger.info(f"Preparing post {post['id']}")

        text = read_post(post)
        image = find_image(post)

        asset_urn = upload_image(image)

        success = publish_post(text, asset_urn)

        if success:
            mark_as_posted(post["id"])
            logger.info(
                f"Post {post['id']} published successfully."
            )
        else:
            logger.error(
                f"Post {post['id']} failed."
            )

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")

    except requests.exceptions.RequestException as e:
        logger.error(f"LinkedIn API error: {e}")

    except Exception:
        logger.exception("Unexpected error occurred.")

if __name__ == "__main__":
    main()
