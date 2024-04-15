# !/Users/gregory.ogbemudia/AppData/Local/Programs/Python/Python312/python.exe

from enum import Enum

from .authentication import auth_router
from fastapi import FastAPI, HTTPException, status, Depends  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from .admin import adm_chu_router, adm_hie_router
from .authentication.models.auth import User
from .hierarchy_mgmt import chu_router
from .common.config import conn, get_mysql_cursor, close_mysql_cursor

description = """
The Church Management System (ChMS) is an application that helps in managing of Church members, groups, events, assets, mass communication and finances (tithes, offerings, donations, seeds etc).

## Modules
* Hierarchy Management (_in progress_)
* Membership Management (_in progress_)
* Group Management (_not implemented_)
* Asset Management (_not implemented_)
* Event Management (_not implemented_)
* Finance Management (_not implemented_)
* Mass Communication Management (_not implemented_)
"""

tags_metadata = [
    {
        "name": "Authentication Operations",
        "description": "Operations on User Authentications",
    },
    {
        "name": "Hierarchy Operations - Admin only",
        "description": "Operations on the Church Hirarchy by Admin",
    },
    {
        "name": "Head Church Operations - Admin only",
        "description": "Operations on the Head Church by Admin",
    },
    {
        "name": "Head Church Operations",
        "description": "Operations on the Head Church",
    },
]


def create_app():
    # Init app
    app = FastAPI(
        title="ChurchMan - Church Management System",
        description=description,
        version="0.0.1",
        contact={
            "name": "Gregory Ogbemudia",
            "email": "gregory.ogbemduia@gmail.com",
        },
        license_info={
            "name": "MIT License",
            "identifier": "MIT",
        },
        openapi_tags=tags_metadata,
    )

    # Define CORS policy
    origins = [
        "http://localhost",
        "http://localhost:8080",
        # "https://example.com",
        # "https://subdomain.example.com",
    ]

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
    app.include_router(adm_hie_router)
    app.include_router(adm_chu_router)
    app.include_router(chu_router)

    @app.get("/shutdown_server")
    async def shutdown_server():
        import os
        import signal

        os.kill(os.getpid(), signal.SIGINT)
        return {"message": "Server shutting down..."}

    @app.get("/test/{username}")
    # def hello():
    def hello(username):
        return {"message": f"Hello {username}"}

    return app


app = create_app()

# cursor.execute("SHOW DATABASES")
# for db in cursor:
#     print(db)

# if __name__ == "__main__":
#     config = uvicorn.Config("app.main:app", port=5000, log_level="info")
#     server = uvicorn.Server(config)
#     server.run()
