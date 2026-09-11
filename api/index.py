import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")

for p in [root_dir, backend_dir]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

from app.main import app

try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except Exception:
    handler = app
