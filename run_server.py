import uvicorn
from main import app
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT, reload=settings.APP_RELOAD)
