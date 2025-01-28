import uvicorn


def main():
    """Run the FastAPI server."""
    uvicorn.run("woodcut_planner.api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
