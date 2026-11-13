import asyncio
import os
import subprocess
import time
from playwright.async_api import async_playwright

VIDEO_OUTPUT = "/config/Desktop/BuildWithGemini/travel_concierge_demo.mp4"

async def main():
    if os.path.exists(VIDEO_OUTPUT):
        os.remove(VIDEO_OUTPUT)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir="/tmp/demo_recordings",
            record_video_size={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print("Navigating to frontend...")
        await page.goto("http://localhost:8080")
        await page.wait_for_timeout(2000)

        # Demo Step 1: Prompt 1 - "What can you help me with?" / Click suggestion pill
        print("Clicking first suggestion pill...")
        pill = page.locator(".suggestion-pill").first
        await pill.click()
        
        # Wait for agent response to appear
        print("Waiting for response 1...")
        await page.wait_for_selector(".msg-row.agent .bubble:not(:has-text('…'))", timeout=60000)
        await page.wait_for_timeout(4000)

        # Demo Step 2: Rich prompt with tool calls, places lookup and hotel recommendations
        print("Typing prompt 2...")
        input_el = page.locator("#input")
        await input_el.fill("Find 3 luxury hotels near Shinjuku, Tokyo and check nearby attractions")
        await page.wait_for_timeout(1000)
        await page.keyboard.press("Enter")

        print("Waiting for response 2...")
        # Wait for the second agent reply
        agent_bubbles = page.locator(".msg-row.agent .bubble")
        await agent_bubbles.nth(1).wait_for(timeout=90000)
        # Wait until it is no longer the placeholder "…"
        start = time.time()
        while time.time() - start < 90:
            text = await agent_bubbles.nth(1).inner_text()
            if text and text.strip() != "…":
                break
            await asyncio.sleep(1)

        await page.wait_for_timeout(6000)

        # Scroll smoothly to show full conversation and cards
        await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        await page.wait_for_timeout(3000)

        video_path = await page.video.path()
        await context.close()
        await browser.close()

        print("Raw video saved at:", video_path)
        # Convert / copy to final destination with ffmpeg for optimal compatibility
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            VIDEO_OUTPUT
        ], check=True)
        print("Final demo video created at:", VIDEO_OUTPUT)

asyncio.run(main())
