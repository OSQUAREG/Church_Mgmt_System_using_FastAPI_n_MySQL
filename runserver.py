# from save_openapi_json import save_openapi_spec
import uvicorn

# # # URL of the OpenAPI JSON specification
# url = "http://127.0.0.1:8000/openapi.json"
# # Output file to save the JSON data
# output_file = "openapi1.json"
# # Save the OpenAPI specification


if __name__ == "__main__":
    # save_openapi_spec(url, output_file)

    # if os.path.exists(output_file):
    #     print(f"File {output_file} successfully saved.")
    # else:
    #     print(f"Failed to save file {output_file}.")

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
