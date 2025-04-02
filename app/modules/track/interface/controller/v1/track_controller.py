import datetime
from typing import Annotated, List

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from starlette import status

from containers import Container
from core.auth import CurrentUser, get_current_user
from modules.track.application import track_service
from modules.track.application.track_service import TrackService
from modules.track.interface.schema.track_schema import CreateTrackBody, TrackResponse, CreateTrackRoutineBody, \
    TrackRoutineResponse, UpdateTrackBody, UpdateRoutineBody, \
    TrackUpdateResponse, TrackParticipant, TrackStartBody
from utils.responses.response import APIResponse

track_router = APIRouter(prefix="/api/v1/track", tags=["track"])
routine_router = APIRouter(prefix="/api/v1/routine", tags=["track routine"])


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
    - mealtime 입력: 아침, 점심, 저녁 ....
    - days 입력: 4268 -> 4일 2일 6일 8일 반복
    """
    routine = track_service.create_routine(current_user.id, body)
    return routine


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


@routine_router.get("/day/group/{track_id}", response_model=List[List[TrackRoutineResponse]])
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


@track_router.get("/track/list", response_model=List[TrackUpdateResponse])
@inject
def get_tracks(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    track 전체 가져오기
    """
    return track_service.get_tracks(user_id=current_user.id)


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


@routine_router.delete("/date/{routine_date_id}", response_model=APIResponse)
@inject
def delete_routine_date(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_date_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    track_service.delete_routine_date(user_id=current_user.id, routine_date_id=routine_date_id)
    return APIResponse(status_code=status.HTTP_200_OK)


@track_router.post("/start/{track_id}", response_model=TrackParticipant)
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
