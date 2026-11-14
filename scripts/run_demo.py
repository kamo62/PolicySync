"""The supported launcher never accepts a public bind or proxy forwarding."""

import uvicorn

from app.config import Settings

if __name__ == "__main__":
    settings = Settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        proxy_headers=False,
        access_log=False,
    )
