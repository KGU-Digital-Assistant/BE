from dependency_injector import containers, providers
import ulid

from database import get_db, SessionLocal
from modules.track.application.track_service import TrackService
from modules.track.infra.repository.track_repo_impl import TrackRepository
from modules.user.application.user_service import UserService
from modules.user.infra.user_repo_impl import UserRepository
from modules.mealday.infra.mealday_repo_impl import MealDayRepository
from modules.mealday.application.mealday_service import MealDayService
from modules.food.infra.food_repo_impl import FoodRepository
from modules.food.application.food_service import FoodService

from utils.crypto import Crypto


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "modules.user",  # 의존성을 사용하는 모듈
            "modules.track",
            "modules.mealday",
            "modules.food",
        ]
    )

    # 의존성 정의
    # db = providers.Resource(get_db)
    user_repo = providers.Factory(UserRepository)
    crypto = providers.Factory(Crypto)
    user_service = providers.Factory(
        UserService,
        user_repo=user_repo,
        crypto=crypto
    )

    food_repo = providers.Factory(FoodRepository)
    food_service = providers.Factory(
        FoodService,
        food_repo=food_repo,
        crypto=crypto
    )

    track_repo = providers.Factory(TrackRepository)
    track_service = providers.Factory(
        TrackService,
        track_repo=track_repo,
        user_service=user_service,
        food_service=food_service
    )

    mealday_repo = providers.Factory(MealDayRepository)
    mealday_service = providers.Factory(
        MealDayService,
        mealday_repo=mealday_repo,
        user_service=user_service,
        track_service=track_service,
        food_service=food_service,
        crypto=crypto
    )
