import asyncio
import os
from datetime import datetime, timezone
from typing import Optional
import contextlib

from dotenv import load_dotenv
load_dotenv()

import httpx
from aiohttp import web

FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", "90"))

LATITUDE = os.getenv("LATITUDE")
LONGITUDE = os.getenv("LONGITUDE")
OWM_API_KEY = os.getenv("OWM_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

PARAMS =  {
    "lat": LATITUDE,
    "lon": LONGITUDE,
    "appid": OWM_API_KEY
}

memory_store: dict[str, Optional[object]] = {
    "result": None,
    "timestamp": None,
    "error": None,
}

async def fetch_data():
    while True:
        attempt = 0
        backoff = 1
        error = None
        result = None

        while attempt < 3:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(url=BASE_URL,params=PARAMS)
                    response.raise_for_status()
                    result = response.json()
                    error = None
                    break
            except Exception as e:
                error = str(e)
                print(f"Fetch {attempt+1} failed: {e}")
                await asyncio.sleep(backoff)
                backoff *= 2
                attempt += 1

        now = datetime.now(timezone.utc).isoformat()
        print(f"Found {len(str(result))} characters of result at {now}")
        memory_store["timestamp"] = now
        memory_store["result"] = result
        memory_store["error"] = error

        await asyncio.sleep(FETCH_INTERVAL)
        print(f"woke after {FETCH_INTERVAL} seconds. fetching again...")


# Background task management via cleanup context
async def background_fetch_ctx(app):
    task = asyncio.create_task(fetch_data())
    app["fetch_data_task"] = task
    yield
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


# API handler
async def handle_get(request):
    return web.json_response(memory_store)


# App factory
async def init_app():
    app = web.Application()
    app.router.add_get("/data", handle_get)
    app.cleanup_ctx.append(background_fetch_ctx)
    print("App generated")
    return app


# Entrypoint
if __name__ == "__main__":
    print("Starting server on http://0.0.0.0:8080/data")
    web.run_app(init_app(), host="0.0.0.0", port=8080)
