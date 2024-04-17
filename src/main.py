import uvicorn


if __name__ == "__main__":
    uvicorn.run("src.start:app", host="0.0.0.0", port=8081)