from datetime import datetime

from dependency_injector.wiring import inject

from modules.track.domain.repository.track_repo import ITrackRepository

from ulid import ULID

from modules.track.domain.track import Track, TrackRoutine, TrackRoutineDate
from modules.track.interface.schema.track_schema import CreateTrackRoutineBody, UpdateRoutineBody, \
    UpdateRoutineDateBody, TrackResponse, UpdateTrackBody
from modules.user.application.user_service import UserService
from modules.user.domain.user import User
from utils.db_utils import orm_to_pydantic_dataclass, orm_to_pydantic
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error
from utils.parser import weekday_parse, time_parse


def validate_track(track: Track, user: User):
    if not user:
        raise raise_error(ErrorCode.USER_NOT_FOUND)
    if not track:
        raise raise_error(ErrorCode.TRACK_NOT_FOUND)
    if track.user_id != user.id:
        raise raise_error(ErrorCode.USER_NOT_AUTHENTICATED)
    return track, user


class TrackService:
    @inject
    def __init__(
            self,
            track_repo: ITrackRepository,
            user_service: UserService,
    ):
        self.track_repo = track_repo
        self.user_service = user_service

    def create_track(self, user_id: str, name: str, duration: int):
        now = datetime.now()
        track = Track(
            id=str(ULID()),
            user_id=user_id,
            duration=duration,
            name=name,
            create_time=now,
        )
        track.origin_track_id = track.id
        return self.track_repo.save(track)

    def create_routine_date(self, track: Track, routine: TrackRoutine, body: CreateTrackRoutineBody):
        routine_date_list = []
        for day in body.weekday:
            _day = weekday_parse(day)
            for __day in range(_day, track.duration + 1, 7):
                routine_date_list.append(
                    TrackRoutineDate(
                        id=str(ULID()),
                        routine_id=routine.id,
                        meal_time=time_parse(body.meal_time),
                        weekday=_day,
                        date=__day,
                    )
                )
        return routine_date_list

    def create_routine(self, user_id: str, body: CreateTrackRoutineBody):
        track, user = validate_track(self.track_repo.find_by_id(body.track_id),
                                     self.user_service.get_user_by_id(user_id))
        routine = TrackRoutine(
            id=str(ULID()),
            track_id=track.id,
            title=body.title,
            calorie=0.0,
            delete=False,
        )
        routine.routine_dates = self.create_routine_date(track, routine, body)
        return self.track_repo.routine_save(routine, track)

    def get_routine_by_id(self, routine_id: str, user_id: str):
        routine = self.track_repo.find_routine_by_id(routine_id)
        track = self.track_repo.find_by_id(routine.track_id)
        if track.user_id != user_id:
            raise raise_error(ErrorCode.USER_NOT_AUTHENTICATED)
        # routine_dates = self.track_repo.find_routine_dates_by_routine_id(routine.id)

        return routine

    def get_track_by_id(self, track_id: str, user_id: str):
        track = self.track_repo.find_by_id(track_id)
        if track is None:
            raise raise_error(ErrorCode.TRACK_NOT_FOUND)
        if track.user_id != user_id:
            raise raise_error(ErrorCode.USER_NOT_AUTHENTICATED)
        return track

    def update_track(self, user_id: str, track_id: str, body: UpdateTrackBody):
        return self.track_repo.update_track(track_id, user_id, body)

    def update_routine(self, user_id: str, routine_id: str, body: UpdateRoutineBody):
        routine = self.track_repo.find_routine_by_id(routine_id)
        if routine is None:
            raise raise_error(ErrorCode.TRACK_ROUTINE_NOT_FOUND)
        if routine.track.user_id != user_id:
            raise raise_error(ErrorCode.USER_NOT_AUTHENTICATED)

        routine.title = body.title
        routine.calorie = body.calorie
        return self.track_repo.update_routine(routine)

    def update_routine_date(self, user_id: str, routine_date_id: str, body: UpdateRoutineDateBody):
        routine_date = self.track_repo.find_routine_date_by_id(routine_date_id)
        if routine_date is None:
            raise raise_error(ErrorCode.TRACK_ROUTINE_DATE_NOT_FOUND)

        routine = self.track_repo.find_routine_by_id(routine_date.routine_id)
        if routine is None:
            raise raise_error(ErrorCode.TRACK_ROUTINE_NOT_FOUND)

        track = self.track_repo.find_by_id(routine.track_id)
        if track is None:
            raise raise_error(ErrorCode.TRACK_NOT_FOUND)
        if track.user_id != user_id:
            raise raise_error(ErrorCode.USER_NOT_AUTHENTICATED)

        # 수 10일차, 월 변경 -> 10 // 7 -> 3 - 2 -> 1
        _date = routine_date.date
        _date = (_date // 7) + routine_date.weekday - weekday_parse(body.weekday)

        routine_date.date = 7 * (routine_date.date // 7) + _date
        routine_date.weekday = weekday_parse(body.weekday)
        routine_date.meal_time = time_parse(body.meal_time)

        return self.track_repo.update_routine_date(routine_date)

    def delete_track(self, track_id: str, user_id: str):
        self.track_repo.delete_track(track_id, user_id)

    def delete_routine(self, user_id: str, routine_id: str):
        self.track_repo.delete_routine(routine_id, user_id)

    def delete_routine_date(self, user_id: str, routine_date_id: str):
        self.track_repo.delete_routine_date(routine_date_id, user_id)
