import uvicorn
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 4321))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False, # Disable reload to avoid subprocess issues for now
        # workers=int(os.getenv("UVICORN_WORKERS", 1)) # Can be enabled for production
    )
