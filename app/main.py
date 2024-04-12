# !/Users/gregory.ogbemudia/AppData/Local/Programs/Python/Python312/python.exe

from enum import Enum

from fastapi import Depends, FastAPI, HTTPException, status  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from .models.auth import User
from .router import hierarchy, church, auth
from .config.config import conn, get_mysql_cursor, close_mysql_cursor


def create_app():
    # Init app
    app = FastAPI()

    # Define CORS policy
    origins = [
        "http://localhost",
        "http://localhost:8080",
        "https://example.com",
        "https://subdomain.example.com",
    ]

    # Enable CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # include routers to app
    app.include_router(auth.auth_router)
    app.include_router(hierarchy.router)
    app.include_router(church.router)
    app.include_router(church.chu_router)

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
