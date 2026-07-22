import requests

from config import FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID


def publish_post(post_text, image_path):
    url = f"https://graph.facebook.com/v23.0/{FACEBOOK_PAGE_ID}/photos"

    with open(image_path, "rb") as image:
        response = requests.post(
            url,
            data={
                "message": post_text,
                "access_token": FACEBOOK_ACCESS_TOKEN,
            },
            files={
                "source": image,
            },
        )

    response.raise_for_status()

    return True