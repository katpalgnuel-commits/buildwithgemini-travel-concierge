"""Video generation tool for travel-concierge using gemini-omni-flash-preview."""

import base64
import re
import uuid
from typing import Any
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-04-fc2df7c82d43"
BUCKET_NAME = "travel-concierge-media-qwiklabs-gcp-04-fc2df7c82d43"
VIDEO_MODEL = "gemini-omni-flash-preview"

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


async def generate_destination_video(
    prompt: str,
    tool_context: ToolContext,
    destination_name: str = "destination-video",
) -> dict[str, Any]:
    """Generate a short scenic video clip for a travel destination or attraction.

    Uses Google's Omni model (gemini-omni-flash-preview) in the global region.
    Saves the video as a session artifact and uploads it to public Cloud Storage,
    returning its public HTTPS URL.

    Args:
        prompt: A descriptive visual prompt for the short video (e.g. 'A scenic aerial drone shot of turquoise waves lapping against the cliffs in Bali at sunset').
        destination_name: Short name of the destination or attraction for naming the video file (e.g. 'Kyoto', 'Bali').

    Returns:
        A dictionary containing the public video URL, filename, and status.
    """
    clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", destination_name.lower().strip())
    filename = f"{clean_name}_{uuid.uuid4().hex[:8]}.mp4"

    client = _get_genai_client()

    interaction = client.interactions.create(
        model=VIDEO_MODEL,
        input=f"Generate a short scenic travel video: {prompt}",
    )

    video_bytes = None
    mime_type = "video/mp4"

    # Extract video from interaction
    if getattr(interaction, "output_video", None) and getattr(interaction.output_video, "data", None):
        raw_data = interaction.output_video.data
        if isinstance(raw_data, str):
            video_bytes = base64.b64decode(raw_data)
        elif isinstance(raw_data, bytes):
            video_bytes = raw_data
        if getattr(interaction.output_video, "mime_type", None):
            mime_type = interaction.output_video.mime_type
    elif getattr(interaction, "steps", None):
        for step in reversed(interaction.steps):
            if getattr(step, "type", None) == "model_output" and getattr(step, "content", None):
                for item in step.content:
                    if getattr(item, "type", None) == "video" and getattr(item, "data", None):
                        raw_data = item.data
                        video_bytes = base64.b64decode(raw_data) if isinstance(raw_data, str) else raw_data
                        if getattr(item, "mime_type", None):
                            mime_type = item.mime_type
                        break
            if video_bytes:
                break

    if not video_bytes:
        return {"error": "Failed to generate video bytes from omni model."}

    # 1. Save artifact so it shows up in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload video bytes to public Cloud Storage bucket
    storage_client = _get_storage_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "destination": destination_name,
        "filename": filename,
        "public_url": public_url,
        "prompt": prompt,
    }
