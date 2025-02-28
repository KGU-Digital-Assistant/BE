import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from containers import Container
from modules.user.interface.controller.v1 import user_controller as user_router
from modules.track.interface.controller.v1 import track_controller as track_router

app = FastAPI()
app.container = Container()

app.include_router(user_router.router)
app.include_router(track_router.router)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000)
