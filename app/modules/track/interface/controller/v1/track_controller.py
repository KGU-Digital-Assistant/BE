import datetime
from typing import Annotated, List, Dict, Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from sqlalchemy import Integer
from starlette import status

from app.containers import Container
from app.core.auth import CurrentUser, get_current_user
from app.modules.track.application import track_service
from app.modules.track.application.track_service import TrackService
from app.modules.track.interface.schema.track_schema import CreateTrackBody, TrackResponse, CreateTrackRoutineBody, \
    TrackRoutineResponse, UpdateTrackBody, UpdateRoutineBody, \
    TrackUpdateResponse, TrackParticipantResponse, TrackStartBody, RoutineFoodResponse, RoutineFoodRequest, \
    RoutineGroupResponse, RoutineCheckResponse, FlagStatus
from app.utils.responses.response import APIResponse

track_router = APIRouter(prefix="/api/v1/tracks", tags=["Track"])
routine_router = APIRouter(prefix="/api/v1/routines", tags=["Track-Routine"])
routine_food_router = APIRouter(prefix="/api/v1/routine-foods", tags=["Routine-Food"])


@track_router.post("/", response_model=TrackResponse)
@inject
def create_track(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: CreateTrackBody,
    track_service: TrackService = Depends(Provide[Container.track_service]),
):
    track = track_service.create_track(current_user.id, body)
    return track


@routine_router.post("/", response_model=List[TrackRoutineResponse])
@inject
def create_routine(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        body: CreateTrackRoutineBody,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    - mealtime 입력: 아침 or 점심 or 저녁 ....
    - days 입력: 4,2,6,8,14 -> 4일 2일 6일 8일 14일 반복
    - food_name: food_label이 없는 음식일때 작성해야함.
    """
    routine = track_service.create_routine(current_user.id, body)
    return routine


@track_router.post("/{track_id}/copy", response_model=TrackResponse)
@inject
def copy_track(
        track_id: str,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    ### 트랙 복제
    - 재시작할때
    """
    return track_service.copy_track(track_id, current_user.id)


@routine_food_router.post("/{routine_id}", response_model=RoutineFoodResponse)
@inject
def create_routine_food(
        routine_id: str,
        body: RoutineFoodRequest,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    루틴에 제품(음식) 추가하기
    """
    return track_service.create_routine_food(routine_id, body, current_user.id)


@routine_router.post("/{routine_id}/check-table", response_model=RoutineCheckResponse)
@inject
def create_routine_check(
        routine_id: str,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    ### RoutineCheck 테이블 생성 API
    """
    return track_service.create_routine_check(routine_id, current_user.id)


@track_router.get("/participants", response_model=List[TrackParticipantResponse])
@inject
def get_participants(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    참여했던, 참여중인 트랙 참여 데이터 가져오기
    """
    return track_service.get_track_part_all(current_user.id)


@track_router.get("/participants/current", response_model=Optional[TrackParticipantResponse])
@inject
def participating_tracks(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    현재 참여중인 트랙 보기
    """
    return track_service.get_track_current_part_by_user_id(current_user.id)


@track_router.get("/{track_id}/days", response_model=Dict[str, datetime.date])
@inject
def get_track_days(
        track_id: str,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    ### v-16
    - 트랙 일차별 몇월 몇일인지 GET
    - 0번째 인덱스가 1일차임.
    """
    return track_service.get_track_days(track_id, current_user.id)


@routine_router.get("/{routine_id}", response_model=TrackRoutineResponse)
@inject
def get_routine(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    하나의 루틴
    """
    return track_service.get_routine_by_id(routine_id, current_user.id)


@track_router.get("/{track_id}", response_model=TrackResponse)
@inject
def get_track(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    본인이 만든 (트랙 + 루틴) 조회
    """
    return track_service.get_track_by_id(track_id=track_id, user_id=current_user.id)


@routine_router.get("/{track_id}/days", response_model=List[List[RoutineGroupResponse]])
@inject
def get_routine_list(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    ### 해당 트랙의 루틴들을 일차별로 배열에 담아서 넘김
    - -> List[1][1] ~ List[1][n] : 1일차 루틴들
    - -> List[2][1] ~ List[2][m] : 2일차 루틴들
    ...
    """
    return track_service.get_routine_list(track_id=track_id, user_id=current_user.id)


@track_router.get("/", response_model=List[TrackUpdateResponse])
@inject
def get_tracks(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    track 전체 가져 오기
    """
    return track_service.get_tracks(user_id=current_user.id)


@routine_food_router.get("/{routine_food_id}", response_model=RoutineFoodResponse)
@inject
def get_routine_food(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_food_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    routine_food 가져오기
    """
    return track_service.get_routine_food_by_id(routine_food_id, current_user.id)


@track_router.put("/{track_id}", response_model=TrackUpdateResponse)
@inject
def update_track(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_id: str,
        body: UpdateTrackBody,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    트랙 이름 변경
    """
    return track_service.update_track(user_id=current_user.id, track_id=track_id, body=body)


@routine_router.put("/{routine_id}", response_model=TrackRoutineResponse)
@inject
def update_routine(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_id: str,
        body: UpdateRoutineBody,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    return track_service.update_routine(user_id=current_user.id, routine_id=routine_id, body=body)


@routine_food_router.put("/{routine_food_id}", response_model=RoutineFoodResponse)
@inject
def update_routine_food(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_food_id: str,
        body: RoutineFoodRequest,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    return track_service.update_routine_food(user_id=current_user.id, routine_food_id=routine_food_id, body=body)


@track_router.delete("/{track_id}", response_model=APIResponse)
@inject
def delete_track(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    track_service.delete_track(track_id=track_id, user_id=current_user.id)
    return APIResponse(status_code=status.HTTP_200_OK)


@routine_router.delete("/{routine_id}", response_model=APIResponse)
@inject
def delete_routine(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    track_service.delete_routine(user_id=current_user.id, routine_id=routine_id)
    return APIResponse(status_code=status.HTTP_200_OK)


@routine_food_router.delete("/{routine_food_id}", response_model=TrackRoutineResponse)
@inject
def delete_routine_food(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_food_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    return track_service.delete_routine_food(user_id=current_user.id, routine_food_id=routine_food_id)


@track_router.post("/{track_id}/start", response_model=TrackParticipantResponse)
@inject
def start_track(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_id: str,
        body: TrackStartBody,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    트랙 시작 하기
    """
    return track_service.track_start(user_id=current_user.id, track_id=track_id, body=body)


@track_router.put("/{track_id}/terminate", response_model=TrackParticipantResponse)
@inject
def terminate_track(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    트랙 중단 하기
    """
    return track_service.track_terminate(user_id=current_user.id, track_id=track_id)
