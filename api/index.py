import os
import sys
import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Add paths
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(root_dir, "backend")

for p in [root_dir, backend_dir]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

_load_error = None
app = None

try:
    from app.main import app as main_app
    app = main_app
except Exception as e:
    _load_error = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
    print(f"FastAPI Load Error: {_load_error}")
    
    app = FastAPI(title="ExpertVerse AI Fallback")
    
    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
    async def fallback_handler(full_path: str):
        return JSONResponse(
            status_code=500,
            content={
                "status": "initialization_error",
                "message": "FastAPI failed to initialize on Vercel.",
                "error": _load_error,
                "sys_path": sys.path,
                "files_in_root": os.listdir(root_dir) if os.path.exists(root_dir) else []
            }
        )
