import datetime
from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from starlette import status

from containers import Container
from core.auth import CurrentUser, get_current_user
from modules.track.application import track_service
from modules.track.application.track_service import TrackService
from modules.track.interface.schema.track_schema import CreateTrackBody, TrackResponse, CreateTrackRoutineBody, \
    TrackRoutineResponse, TrackRoutineDateResponse, UpdateTrackBody, UpdateRoutineBody, UpdateRoutineDateBody, \
    TrackUpdateResponse
from utils.responses.response import APIResponse

router = APIRouter(prefix="/api/v1/track", tags=["track"])


@router.post("/", response_model=TrackResponse)
@inject
def create_track(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: CreateTrackBody,
    track_service: TrackService = Depends(Provide[Container.track_service]),
):
    track = track_service.create_track(current_user.id, name=body.name, duration=body.duration)
    return track
    # return APIResponse(status_code=status.HTTP_201_CREATED, data=dataclass_to_pydantic(track, TrackResponse))


@router.post("/routines", response_model=TrackRoutineResponse)
@inject
def create_routine(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        body: CreateTrackRoutineBody,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    routine = track_service.create_routine(current_user.id, body)
    return routine


@router.get("/{track_id}", response_model=TrackResponse)
@inject
def get_track(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    (트랙 + 루틴 + 루틴 date) 조회
    """
    return track_service.get_track_by_id(track_id=track_id, user_id=current_user.id)


@router.get("/routine/{routine_id}", response_model=TrackRoutineResponse)
@inject
def get_routine(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    """
    하나의 루틴과 그 루틴의 반복들
    """
    return track_service.get_routine_by_id(routine_id, current_user.id)


@router.put("/{track_id}", response_model=TrackUpdateResponse)
@inject
def update_track(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_id: str,
        body: UpdateTrackBody,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    return track_service.update_track(user_id=current_user.id, track_id=track_id, body=body)


@router.put("/routine/{routine_id}", response_model=TrackRoutineResponse)
@inject
def update_routine(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_id: str,
        body: UpdateRoutineBody,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    return track_service.update_routine(user_id=current_user.id, routine_id=routine_id, body=body)


@router.put("/routine/date/{routine_date_id}", response_model=TrackRoutineDateResponse)
@inject
def update_routine_date(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_date_id: str,
        body: UpdateRoutineDateBody,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    return track_service.update_routine_date(user_id=current_user.id, routine_date_id=routine_date_id, body=body)


@router.delete("/{track_id}", response_model=APIResponse)
@inject
def delete_track(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        track_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    track_service.delete_track(track_id=track_id, user_id=current_user.id)
    return APIResponse(status_code=status.HTTP_200_OK)


@router.delete("/routine/{routine_id}", response_model=APIResponse)
@inject
def delete_routine(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    track_service.delete_routine(user_id=current_user.id, routine_id=routine_id)
    return APIResponse(status_code=status.HTTP_200_OK)


@router.delete("/routine/date/{routine_date_id}", response_model=APIResponse)
@inject
def delete_routine_date(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        routine_date_id: str,
        track_service: TrackService = Depends(Provide[Container.track_service]),
):
    track_service.delete_routine_date(user_id=current_user.id, routine_date_id=routine_date_id)
    return APIResponse(status_code=status.HTTP_200_OK)
