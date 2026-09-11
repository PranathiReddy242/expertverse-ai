import os
import sys

# Ensure backend root is in sys.path for Vercel Serverless
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.main import app
