from fastapi import FastAPI  # , Request, HTTPException, status, Depends  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from fastapi.templating import Jinja2Templates  # type: ignore

from .authentication.routes import auth_router
from .church_admin.routes import (
    hierarchy_router,
    head_chu_adm_router,
    head_chu_router,
    church_router,
    church_adm_router,
    churchleads_router,
    churchleads_adm_router,
)
from .membership_mgmt.routes import (
    members_router,
    members_adm_router,
    member_branch_router,
    member_branch_adm_router,
)
from .user_mgmt.routes import user_route, user_adm_route
from .common.config import settings
from .swagger_doc import get_swagger_params
from .common.database import (
    create_audit_log_triggers,
    create_change_track_triggers,
    get_all_endpoints,
    insert_mod_sub_endpts_table,
)

# from save_openapi_json import save_openapi_spec
# from fastapi.responses import HTMLResponse  # type: ignore
# from sqlalchemy.orm import Session  # type: ignore


# Define CORS policy
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]


def create_app(prefix=settings.dev_prefix):
    # Get Swagger Params
    swagger_params = get_swagger_params(prefix)

    # Init app
    app = FastAPI(**swagger_params)

    # Enable CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # include routers to app
    app.include_router(auth_router, prefix=prefix)
    app.include_router(hierarchy_router, prefix=prefix)
    app.include_router(head_chu_router, prefix=prefix)
    app.include_router(head_chu_adm_router, prefix=prefix)
    app.include_router(church_router, prefix=prefix)
    app.include_router(church_adm_router, prefix=prefix)
    app.include_router(churchleads_router, prefix=prefix)
    app.include_router(churchleads_adm_router, prefix=prefix)
    app.include_router(members_router, prefix=prefix)
    app.include_router(members_adm_router, prefix=prefix)
    app.include_router(member_branch_router, prefix=prefix)
    app.include_router(member_branch_adm_router, prefix=prefix)
    app.include_router(user_route, prefix=prefix)
    app.include_router(user_adm_route, prefix=prefix)

    # Perform DB Operations
    """Create Triggers, Insert into Endpoints Table"""
    # create_audit_log_triggers()
    # create_change_track_triggers()
    insert_mod_sub_endpts_table(app)
    get_all_endpoints(app)

    # Templates
    import os

    current_directory = os.path.dirname(__file__)

    static_directory = os.path.join(current_directory, "static")
    app.mount("/static", StaticFiles(directory=static_directory), name="static")

    templates_directory = os.path.join(current_directory, "templates")
    templates = Jinja2Templates(directory=templates_directory)

    # app.mount("/static", StaticFiles(directory="/static"), name="static")
    # templates = Jinja2Templates(directory="templates")

    # @app.get("/hello", response_class=HTMLResponse)
    # async def hello(request: Request):
    #     return templates.TemplateResponse(request=request, name="index.html")

    # @app.get("/items/{id}", response_class=HTMLResponse)
    # async def read_item(request: Request, id: str):
    #     return templates.TemplateResponse(
    #         request=request, name="item.html", context={"id": id}
    # )

    # @app.get("/shutdown_server")
    # async def shutdown_server():
    #     import os
    #     import signal

    #     os.kill(os.getpid(), signal.SIGINT)
    #     return {"message": "Server shutting down..."}

    # # URL of the OpenAPI JSON specification
    # url = "http://127.0.0.1:8000/openapi.json"
    # # Output file to save the JSON data
    # output_file = "openapi.json"
    # # Save the OpenAPI specification
    # save_openapi_spec(url, output_file)

    return app


app = create_app()
