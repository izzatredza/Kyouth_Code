from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

# Load variables defined inside a local .env configuration file
load_dotenv()

app = FastAPI()

# Retrieve backend URL from environment variables, fallback to local standard default port if unset
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001/chat")

base_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    # Pass the environment configuration down into the template securely
    return templates.TemplateResponse(
        request=request, name="chat_page.html", context={"backend_url": BACKEND_URL}
    )
