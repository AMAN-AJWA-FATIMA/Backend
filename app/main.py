from fastapi import FastAPI

from app.routers import tasks, users

app = FastAPI(
    title="Task Management API",
    description="A REST API for managing users and their tasks.",
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
