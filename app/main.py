
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import auth, authorization_demo, curriculum, tasks, users
from app.schemas import curriculum as curriculum_schemas

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
app.include_router(curriculum.router)


WEB_DIRECTORY = Path(__file__).resolve().parent.parent / "web"

if WEB_DIRECTORY.is_dir():
    app.mount("/web", StaticFiles(directory=WEB_DIRECTORY), name="web")


@app.get("/", include_in_schema=False)
def web_application():
    return FileResponse(WEB_DIRECTORY / "index.html")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    create_schemas = {
        "GradeCreate": curriculum_schemas.GradeCreate,
        "SubjectCreate": curriculum_schemas.SubjectCreate,
        "BookCreate": curriculum_schemas.BookCreate,
        "ChapterCreate": curriculum_schemas.ChapterCreate,
        "PageCreate": curriculum_schemas.PageCreate,
        "TopicCreate": curriculum_schemas.TopicCreate,
    }

    update_schemas = {
        "GradeUpdate": curriculum_schemas.GradeUpdate,
        "SubjectUpdate": curriculum_schemas.SubjectUpdate,
        "BookUpdate": curriculum_schemas.BookUpdate,
        "ChapterUpdate": curriculum_schemas.ChapterUpdate,
        "PageUpdate": curriculum_schemas.PageUpdate,
        "TopicUpdate": curriculum_schemas.TopicUpdate,
    }

    component_schemas = openapi_schema.setdefault(
        "components", {}
    ).setdefault("schemas", {})

    for name, model in {**create_schemas, **update_schemas}.items():
        component_schemas[name] = model.model_json_schema()

    create_one_of = [
        {"$ref": f"#/components/schemas/{name}"}
        for name in create_schemas
    ]

    update_one_of = [
        {"$ref": f"#/components/schemas/{name}"}
        for name in update_schemas
    ]

    paths = openapi_schema["paths"]

    paths["/curriculum/admin/{resource}"]["post"]["requestBody"] = {
        "required": True,
        "description": (
            "Provide the request body matching the selected resource: "
            "grades, subjects, books, chapters, pages, or topics."
        ),
        "content": {
            "application/json": {
                "schema": {"oneOf": create_one_of}
            }
        },
    }

    paths["/curriculum/admin/{resource}/{record_id}"]["patch"][
        "requestBody"
    ] = {
        "required": True,
        "description": (
            "Provide the fields to update for the selected resource."
        ),
        "content": {
            "application/json": {
                "schema": {"oneOf": update_one_of}
            }
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
