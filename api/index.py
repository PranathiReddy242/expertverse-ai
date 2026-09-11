import os
import sys
import traceback

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")

for p in [root_dir, backend_dir]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    err_msg = str(e)
    err_tb = traceback.format_exc()
    app = FastAPI(title="ExpertVerse AI Error Handler")

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
    async def catch_all(path: str):
        return JSONResponse(
            status_code=500,
            content={"error": err_msg, "traceback": err_tb, "sys_path": sys.path}
        )
