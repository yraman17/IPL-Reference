import uvicorn
from .main import app

if __name__ == "__main__":
    print("Starting IPL Statistics API...")
    print("Loading data...")
    
    # Start the server
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",  # Allow external connections
        port=8000,        # Port number
        reload=True        # Auto-reload on code changes
    ) 