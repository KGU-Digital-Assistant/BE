import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.containers import Container
from app.modules.user.interface.controller.v1 import user_controller as user_router
from app.modules.mealday.interface.controller.v1 import mealday_controller as mealday_router
from app.modules.track.interface.controller.v1 import track_controller as track_router
from app.modules.food.interface.controller.v1 import food_controller as food_router
from app.utils.scheduler import start_track_scheduler

app = FastAPI()
app.container = Container()

app.include_router(user_router.router)
app.include_router(mealday_router.mealday_router)
app.include_router(mealday_router.dish_router)
app.include_router(track_router.track_router)
app.include_router(track_router.routine_router)
app.include_router(track_router.routine_food_router)
app.include_router(food_router.router)


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


@app.get("/health-check")
def hello():
    return "Hello World!"


@app.on_event("startup")
async def startup_event():
    start_track_scheduler()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000)
