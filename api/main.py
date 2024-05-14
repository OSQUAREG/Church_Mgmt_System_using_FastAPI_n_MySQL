# # !/Users/gregory.ogbemudia/AppData/Local/Programs/Python/Python312/python.exe
# from fastapi import FastAPI, Request  # , HTTPException, status, Depends  # type: ignore
# from fastapi.middleware.cors import CORSMiddleware  # type: ignore
# from fastapi.responses import HTMLResponse  # type: ignore
# from fastapi.staticfiles import StaticFiles  # type: ignore
# from fastapi.templating import Jinja2Templates  # type: ignore

# from .authentication.routes import auth_router
# from .hierarchy_mgmt.routes import (
#     hierarchy_router,
#     adm_head_chu_router,
#     head_chu_router,
#     church_router,
#     level1_router,
#     level2_router,
#     level3_router,
# )
# from .common.config import settings
# from .swagger_doc import (
#     title,
#     description,
#     tags_metadata,
#     contact,
#     license_info,
#     version,
# )


# # Define CORS policy
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:3000",
# ]


# def create_app():
#     # Init app
#     app = FastAPI(
#         title=title,
#         description=description,
#         version=version,
#         contact=contact,
#         license_info=license_info,
#         openapi_tags=tags_metadata,
#         persistAuthorization=True,
#     )

#     # Enable CORS middleware
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=origins,
#         allow_credentials=True,
#         allow_methods=["GET", "POST", "PUT", "PATCH"],
#         allow_headers=["Authorization", "Content-Type"],
#     )

#     # include routers to app
#     app.include_router(auth_router)
#     app.include_router(hierarchy_router)
#     app.include_router(adm_head_chu_router)
#     app.include_router(head_chu_router)
#     app.include_router(church_router)
#     # app.include_router(level1_router)
#     # app.include_router(level2_router)
#     # app.include_router(level3_router)

#     # Templates
#     import os

#     current_directory = os.path.dirname(__file__)

#     static_directory = os.path.join(current_directory, "static")
#     app.mount("/static", StaticFiles(directory=static_directory), name="static")

#     templates_directory = os.path.join(current_directory, "templates")
#     templates = Jinja2Templates(directory=templates_directory)

#     # app.mount("/static", StaticFiles(directory="/static"), name="static")
#     # templates = Jinja2Templates(directory="templates")

#     # @app.get("/hello", response_class=HTMLResponse)
#     # async def hello(request: Request):
#     #     return templates.TemplateResponse(request=request, name="index.html")

#     # @app.get("/items/{id}", response_class=HTMLResponse)
#     # async def read_item(request: Request, id: str):
#     #     return templates.TemplateResponse(
#     #         request=request, name="item.html", context={"id": id}
#     # )

#     # @app.get("/shutdown_server")
#     # async def shutdown_server():
#     #     import os
#     #     import signal

#     #     os.kill(os.getpid(), signal.SIGINT)
#     #     return {"message": "Server shutting down..."}

#     return app


# app = create_app()
