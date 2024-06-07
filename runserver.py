import uvicorn  # type: ignore

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="localhost",
        port=8000,
        log_level="debug",
        reload=True,
    )


# import threading
# import uvicorn
# from save_openapi_json import save_openapi_spec


# def fetch_and_save_openapi_spec():
#     url = "http://127.0.0.1:8000/openapi.json"
#     output_file = "openapi.json"
#     save_openapi_spec(url, output_file)


# if __name__ == "__main__":
#     # Run the fetch and save in a separate thread to avoid blocking
#     threading.Thread(target=fetch_and_save_openapi_spec).start()

#     # Start the server
#     uvicorn.run(
#         "api:app",
#         host="localhost",
#         port=8000,
#         log_level="debug",
#         reload=True,
#     )
