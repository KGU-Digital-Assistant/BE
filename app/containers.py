from dependency_injector import containers, providers
import ulid

from database import get_db, SessionLocal
from modules.user.application.user_service import UserService
from modules.user.infra.user_repo_impl import UserRepository
from utils.crypto import Crypto


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "modules.user"  # 의존성을 사용하는 모듈
        ]
    )

    # 의존성 정의
    db = providers.Resource(get_db)
    user_repo = providers.Factory(UserRepository, db=db)
    crypto = providers.Factory(Crypto)
    user_service = providers.Factory(
        UserService,
        user_repo=user_repo,
        crypto=crypto
    )
