import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app

try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except Exception:
    handler = app
