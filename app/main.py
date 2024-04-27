# !/Users/gregory.ogbemudia/AppData/Local/Programs/Python/Python312/python.exe

from enum import Enum
import os

from fastapi import FastAPI, Request  # , HTTPException, status, Depends  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from .authentication.routes import auth_router
from .admin.routes import adm_head_chu_router
from .hierarchy_mgmt.routes import (
    hierarchy_router,
    head_chu_router,
    province_router,
    zone_router,
    area_router,
)
from .common.config import settings
from .swagger_doc import (
    title,
    description,
    tags_metadata,
    contact,
    license_info,
    version,
)

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# Define CORS policy
origins = [
    "http://localhost",
    "http://localhost:8080",
    # "https://example.com",
    # "https://subdomain.example.com",
]


def create_app():
    # Init app
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        contact=contact,
        license_info=license_info,
        openapi_tags=tags_metadata,
        persistAuthorization=True,
    )

    # Enable CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # include routers to app
    app.include_router(auth_router)
    app.include_router(hierarchy_router)
    app.include_router(adm_head_chu_router)
    app.include_router(head_chu_router)
    app.include_router(province_router)
    app.include_router(zone_router)
    app.include_router(area_router)

    # Templates
    current_directory = os.path.dirname(__file__)

    static_directory = os.path.join(current_directory, "static")
    app.mount("/static", StaticFiles(directory=static_directory), name="static")

    templates_directory = os.path.join(current_directory, "templates")
    templates = Jinja2Templates(directory=templates_directory)

    # app.mount("/static", StaticFiles(directory="/static"), name="static")
    # templates = Jinja2Templates(directory="templates")

    @app.get("/hello", response_class=HTMLResponse)
    async def hello(request: Request):
        return templates.TemplateResponse(request=request, name="index.html")

    @app.get("/items/{id}", response_class=HTMLResponse)
    async def read_item(request: Request, id: str):
        return templates.TemplateResponse(
            request=request, name="item.html", context={"id": id}
        )

    # @app.post("/auth/login")
    # async def login(request: Request):

    @app.get("/shutdown_server")
    async def shutdown_server():
        import os
        import signal

        os.kill(os.getpid(), signal.SIGINT)
        return {"message": "Server shutting down..."}

    # @app.get("/test/{username}")
    # # def hello():
    # def hello(username):
    #     return {"message": f"Hello {username}"}

    return app


app = create_app()
