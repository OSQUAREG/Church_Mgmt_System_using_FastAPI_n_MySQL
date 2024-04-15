import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        log_level="debug",
        reload=True,
    )


# import sys
# from uvicorn import run


# def main():
#     # Open a file in append mode to capture error messages
#     with open("error.log", "a") as f:
#         # Redirect stderr to the file
#         sys.stderr = f
#         # Run uvicorn server
#         run(
#             "app.main:app",
#             # host="0.0.0.0",
#             port=8000,
#             log_level="debug",
#             reload=True,
#         )


# if __name__ == "__main__":
#     main()
