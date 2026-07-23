from config import ACCESS_TOKEN, PERSON_URN
import requests
import logging

logger = logging.getLogger(__name__)

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

def publish_post(post_text, image_path):
    asset_urn = upload_image(image_path)
    
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