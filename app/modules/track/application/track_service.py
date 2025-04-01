from datetime import datetime, timedelta
from typing import List

from dependency_injector.wiring import inject

from modules.track.domain.track_participant import TrackParticipant as TrackParticipantVO
from modules.track.domain.repository.track_repo import ITrackRepository

from ulid import ULID

from modules.track.domain.track import Track, TrackRoutine
from modules.track.interface.schema.track_schema import CreateTrackRoutineBody, UpdateRoutineBody, \
    TrackResponse, UpdateTrackBody, TrackUpdateResponse, TrackStartBody, CreateTrackBody
from modules.user.application.user_service import UserService
from modules.user.domain.user import User
from utils.db_utils import orm_to_pydantic_dataclass, orm_to_pydantic
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error
from utils.parser import weekday_parse, time_parse, mealtime_parse


class TrackService:
    @inject
    def __init__(
            self,
            track_repo: ITrackRepository,
            user_service: UserService,
    ):
        self.track_repo = track_repo
        self.user_service = user_service

    def validate_track(self, track_id: str, user_id: str):
        track = self.track_repo.find_by_id(track_id)

        if not track:
            raise raise_error(ErrorCode.TRACK_NOT_FOUND)
        if not track.routines:
            track.routines = []
        if track.user_id != user_id:
            raise raise_error(ErrorCode.USER_NOT_AUTHENTICATED)
        return track

    def validate_routine(self, routine_id: str, user_id: str):
        routine = self.track_repo.find_routine_by_id(routine_id)
        if routine is None:
            raise raise_error(ErrorCode.TRACK_ROUTINE_NOT_FOUND)
        if routine.track.user_id != user_id:
            raise raise_error(ErrorCode.USER_NOT_AUTHENTICATED)
        return routine

    def create_track(self, user_id: str, body: CreateTrackBody):
        now = datetime.now()
        track = Track(
            id=str(ULID()),
            user_id=user_id,
            duration=body.duration,
            name=body.name,
            create_time=now,
            # start_date=body.start_date,
            # finish_date=body.start_date + timedelta(days=body.duration),
        )
        track.origin_track_id = track.id
        return self.track_repo.save(track)

    def create_routine(self, user_id: str, body: CreateTrackRoutineBody):
        track = self.validate_track(body.track_id, user_id)
        user = self.user_service.get_user_by_id(user_id)
        routine_list = []

        for day in body.days:
            _day = int(day)
            routine_list.append(
                TrackRoutine(
                    id=str(ULID()),
                    track_id=track.id,
                    mealtime=time_parse(body.mealtime),
                    days=_day,
                    title=body.title,
                    calorie=body.calorie
                )
            )
        routines = self.track_repo.routines_save(routine_list, track)
        sorted_routines = sorted(routines, key=lambda routine: routine.days)
        return sorted_routines

    def get_routine_by_id(self, routine_id: str, user_id: str):
        routine = self.track_repo.find_routine_by_id(routine_id)
        if routine is None:
            raise_error(ErrorCode.TRACK_ROUTINE_NOT_FOUND)
        self.validate_track(track_id=routine.track.id, user_id=user_id)

        return routine

    def get_track_by_id(self, track_id: str, user_id: str):
        track = self.validate_track(track_id, user_id)
        track.routines = sorted(track.routines, key=lambda routine: (routine.days,
                                                                     mealtime_parse(routine.mealtime)))
        return track

    def update_track(self, user_id: str, track_id: str, body: UpdateTrackBody):
        return self.track_repo.update_track(track_id, user_id, body)

    def update_routine(self, user_id: str, routine_id: str, body: UpdateRoutineBody):
        routine = self.validate_routine(routine_id, user_id)
        track = self.validate_track(routine.track.id, user_id)
        routine.title = body.title
        routine.calorie = body.calorie
        routine.mealtime = time_parse(body.mealtime)
        if body.days > track.duration:
            raise raise_error(ErrorCode.ROUTINE_DAYS_SO_OVER)
        routine.days = body.days
        return self.track_repo.update_routine(routine)

    def delete_track(self, track_id: str, user_id: str):
        self.track_repo.delete_track(track_id, user_id)

    def delete_routine(self, user_id: str, routine_id: str):
        self.track_repo.delete_routine(routine_id, user_id)

    def get_tracks(self, user_id: str):
        return self.track_repo.find_tracks_by_id(user_id)

    def track_start(self, user_id: str, track_id: str, body: TrackStartBody):
        self.validate_track(track_id, user_id)

        track_participant = TrackParticipantVO(id=str(ULID()), track_id=track_id, user_id=user_id)
        res = self.track_repo.start_track(track_participant)
        self.track_repo.update_start_date(track_id, user_id, body.start_date)
        return res

    def get_routine_list(self, track_id: str, user_id: str):
        track = self.validate_track(track_id, user_id)
        days_grouped = [[] for _ in range(track.duration + 1)]

        for routine in track.routines:
            _day = int(routine.days)
            days_grouped[_day].append(routine)

        idx = 0
        for day in days_grouped:
            days_grouped[idx] = sorted(day, key=lambda day: mealtime_parse(day.mealtime))
            idx += 1

        return days_grouped
