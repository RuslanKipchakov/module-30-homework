import os
import sys

import uvicorn  # type: ignore

from app.fastapi_app import app

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))


def run():
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    run()
