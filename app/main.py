from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import auth, authorization_demo, tasks, users

app = FastAPI(
    title="Task Management and Authentication API",
    description=(
        "Task Management API with secure user authentication, refresh-token "
        "rotation, and role-based authorization."
    ),
    version="2.0.0",
)

app.include_router(auth.router)
app.include_router(authorization_demo.router)
app.include_router(users.router)
app.include_router(tasks.router)

WEB_DIRECTORY = Path(__file__).resolve().parent.parent / "web"
if WEB_DIRECTORY.is_dir():
    app.mount("/web", StaticFiles(directory=WEB_DIRECTORY), name="web")


@app.get("/", include_in_schema=False)
def web_application():
    return FileResponse(WEB_DIRECTORY / "index.html")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
