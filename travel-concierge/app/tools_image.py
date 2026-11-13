"""Image generation tool for travel-concierge using gemini-3.1-flash-lite-image."""

import re
import uuid
from typing import Any
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-04-fc2df7c82d43"
BUCKET_NAME = "travel-concierge-media-qwiklabs-gcp-04-fc2df7c82d43"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"

_storage_client = None
_genai_client = None


def _get_storage_client() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client


def _get_genai_client() -> genai.Client:
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    return _genai_client


async def generate_destination_image(
    prompt: str,
    tool_context: ToolContext,
    destination_name: str = "travel-postcard",
) -> dict[str, Any]:
    """Generate a high-quality travel image or scenic postcard for a destination.

    Saves the image as a session artifact and uploads it to public Cloud Storage,
    returning its public HTTPS URL.

    Args:
        prompt: A descriptive visual prompt for the image (e.g. 'A scenic sunset postcard of Kyoto Japan with cherry blossoms and a pagoda').
        destination_name: Short name of the destination or landmark for naming the image (e.g. 'Kyoto', 'Sagrada Familia').

    Returns:
        A dictionary containing the public image URL, filename, and status.
    """
    clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", destination_name.lower().strip())
    filename = f"{clean_name}_{uuid.uuid4().hex[:8]}.jpg"

    genai_client = _get_genai_client()

    # Generate image using gemini-3.1-flash-lite-image in global location
    response = genai_client.models.generate_content(
        model=IMAGE_MODEL,
        contents=f"Generate a scenic travel photograph or postcard: {prompt}",
        config=types.GenerateContentConfig(
            response_modalities=[types.Modality.IMAGE],
        ),
    )

    image_bytes = None
    mime_type = "image/jpeg"

    for candidate in response.candidates:
        if not candidate.content or not candidate.content.parts:
            continue
        for part in candidate.content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/jpeg"
                break
        if image_bytes:
            break

    if not image_bytes:
        return {"error": "Failed to generate image bytes from model."}

    # 1. Save artifact so it shows up in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload image bytes to public Cloud Storage bucket
    storage_client = _get_storage_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "destination": destination_name,
        "filename": filename,
        "public_url": public_url,
        "prompt": prompt,
    }
