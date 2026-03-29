import uvicorn


# if __name__ == "__main__":

#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8001,
#         workers=1
#     )


if __name__ == "__main__":

    uvicorn.run(
        "app.main:app",

        port=8001,
        workers=1
    )