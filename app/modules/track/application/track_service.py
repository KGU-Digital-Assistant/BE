from datetime import datetime, timedelta
from typing import List

from dependency_injector.wiring import inject

from modules.food.application.food_service import FoodService
from modules.food.domain.food import Food
from modules.track.domain.track_participant import TrackParticipant as TrackParticipantVO
from modules.track.domain.repository.track_repo import ITrackRepository

from ulid import ULID

from modules.track.domain.track import Track, TrackRoutine, RoutineCheck
from modules.track.domain.track_routine_food import RoutineFood
from modules.track.interface.schema.track_schema import CreateTrackRoutineBody, UpdateRoutineBody, \
    TrackResponse, UpdateTrackBody, TrackUpdateResponse, TrackStartBody, CreateTrackBody, RoutineFoodRequest, \
    RoutineGroupResponse, RoutineFoodResponse, TrackRoutineResponse, RoutineFoodGroupResponse
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
            food_service: FoodService,
    ):
        self.track_repo = track_repo
        self.user_service = user_service
        self.food_service = food_service

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
        routine_food_body = []
        calories = 0

        for body_food in body.foods:
            food = self.food_service.get_food_data(food_label=body_food.food_label)
            if food is None and body_food.food_name is None:
                raise_error(ErrorCode.NO_FOOD_NO_NAME)
            routine_food = RoutineFood(
                id="",
                routine_id="",
                food_label=body_food.food_label,
                quantity=body_food.quantity,
                food_name=body_food.food_name or food.name
            )
            routine_food_body.append(routine_food)
            calories += (food.calorie * routine_food.quantity)

        for day in body.days.split(","):
            _day = int(day)
            new_routine = TrackRoutine(
                id=str(ULID()),
                track_id=track.id,
                mealtime=time_parse(body.mealtime),
                days=_day,
                title=body.title,
                calorie=calories,
            )

            new_routine.routine_foods = []
            for food in routine_food_body:
                new_routine.routine_foods.append(
                    RoutineFood(
                        id=str(ULID()),
                        routine_id=new_routine.id,
                        food_label=food.food_label,
                        quantity=food.quantity,
                        food_name=food.food_name
                    )
                )
            routine_list.append(new_routine)

        routines = self.track_repo.routines_save(routine_list, track)
        sorted_routines = sorted(routines, key=lambda routine: routine.days)
        return sorted_routines

    def create_routine_food(self, routine_id: str, body: RoutineFoodRequest, user_id: str):
        routine = self.validate_routine(routine_id, user_id)
        new_routine_food = RoutineFood(
            id=str(ULID()),
            routine_id=routine.id,
            food_label=body.food_label,
            quantity=body.quantity,
        )
        food = self.food_service.get_food_data(body.food_label)
        routine.calorie += (food.calorie * body.quantity)
        return self.track_repo.routine_food_save(new_routine_food, routine)

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

    def update_routine_food(self, user_id: str, routine_food_id: str, body: RoutineFoodRequest):
        routine_food = self.track_repo.find_routine_food_by_id(routine_food_id)
        if routine_food is None:
            raise_error(ErrorCode.TRACK_ROUTINE_FOOD_NOT_FOUND)
        routine = self.validate_routine(routine_food.track_routine_id, user_id)
        old_food = self.food_service.get_food_data(routine_food.food_label)

        new_food = self.food_service.get_food_data(body.food_label)
        calories = (new_food.calorie * body.quantity) - (old_food.calorie * routine_food.quantity)

        routine_food.food_label = body.food_label
        routine_food.quantity = body.quantity

        return self.track_repo.update_routine_food(routine.id, routine_food, calories)

    def delete_track(self, track_id: str, user_id: str):
        self.track_repo.delete_track(track_id, user_id)

    def delete_routine(self, user_id: str, routine_id: str):
        self.track_repo.delete_routine(routine_id, user_id)

    def delete_routine_food(self, user_id: str, routine_food_id: str):
        routine_food = self.track_repo.find_routine_food_by_id(routine_food_id)
        if routine_food is None:
            raise_error(ErrorCode.TRACK_ROUTINE_FOOD_NOT_FOUND)
        food = self.food_service.get_food_data(routine_food.food_label)
        routine = self.validate_routine(routine_food.track_routine_id, user_id)
        return self.track_repo.delete_routine_food(routine.id, routine_food_id, food.calorie * routine_food.quantity)

    def get_tracks(self, user_id: str):
        return self.track_repo.find_tracks_by_id(user_id)

    def routine_food_check_list(self, user_id: str, routine_foods: List[RoutineFood], routine: TrackRoutine):
        routine_foods_list = []
        for routine_food in routine_foods:
            routine_food_check = self.track_repo.find_routine_food_check_by_routine_food_id(routine_food.id, user_id)
            status = False
            if routine_food_check is not None:
                status = routine_food_check.is_complete

            routine_foods_list.append(
                RoutineFoodGroupResponse(
                    id=routine_food.id,
                    routine_id=routine.id,
                    food_label=routine_food.food_label,
                    food_name=routine_food.food_name,
                    quantity=routine_food.quantity,
                    is_clear=status
                )
            )
        return routine_foods_list

    def routine_grouping(self, routines: List[TrackRoutine], track: Track, user_id: str):
        days_grouped = [[] for _ in range(track.duration + 1)]

        for routine in track.routines:
            clear_routine = self.track_repo.find_routine_check(routine.id, user_id)
            if clear_routine is None:
                raise_error(ErrorCode.TRACK_ROUTINE_NOT_FOUND)
            _day = int(routine.days)

            days_grouped[_day].append(
                RoutineGroupResponse(
                    id=routine.id,
                    track_id=track.id,
                    title=routine.title,
                    calorie=routine.calorie,
                    mealtime=routine.mealtime,
                    days=routine.days,
                    clock=routine.clock,
                    delete=routine.delete,
                    routine_foods=self.routine_food_check_list(routine.id, routine.routine_foods, clear_routine),
                    is_complete=clear_routine.is_complete,
                )
            )
        idx = 0
        for day in days_grouped:
            days_grouped[idx] = sorted(day, key=lambda day: mealtime_parse(day.mealtime))
            idx += 1

        return days_grouped

    def get_routine_list(self, track_id: str, user_id: str):
        track = self.validate_track(track_id, user_id)
        days_grouped = self.routine_grouping(track.routines, track, user_id)
        return days_grouped

    def track_start(self, user_id: str, track_id: str, body: TrackStartBody):
        self.validate_track(track_id, user_id)

        track_participant = TrackParticipantVO(id=str(ULID()), track_id=track_id, user_id=user_id)
        res = self.track_repo.start_track(track_participant)
        self.track_repo.update_start_date(track_id, user_id, body.start_date)
        return res

    def track_terminate(self, user_id: str, track_id: str):
        track = self.validate_track(user_id, track_id)
        return self.track_repo.terminate_track(user_id, track.id)

    def copy_track(self, track_id: str, user_id: str):
        track = self.validate_track(track_id, user_id)
        routines = self.track_repo.find_all_routine_by_track_id(track_id)

        track.id = str(ULID())
        track.routines = []
        copied_track = self.track_repo.save(track)

        new_routines = []
        for routine in routines:
            routine.id = str(ULID())
            new_routines.append(routine)

        copied_track.routines = self.track_repo.routines_save(new_routines, copied_track)
        return copied_track

    def get_routine_food_by_id(self, routine_food_id: str, user_id: str):
        routine_food = self.track_repo.find_routine_food_by_id(routine_food_id)
        if routine_food is None:
            raise_error(ErrorCode.TRACK_ROUTINE_FOOD_NOT_FOUND)
        self.validate_routine(routine_food.routine_id, user_id)
        return routine_food

    def create_routine_check(self, routine_id: str, user_id: str):
        routine_check = self.track_repo.find_routine_check(routine_id, user_id)
        if routine_check is not None:
            raise_error(ErrorCode.ROUTINE_CHECK_ALREADY_EXIST)
        new = RoutineCheck(
            id=str(ULID()),
            routine_id=routine_id,
            user_id=user_id,
            is_complete=False,
        )
        return self.track_repo.routine_check_save(new)

    def get_routine_food_all_by_routine_id(self, routine_id: str):
        routin_foods=self.track_repo.find_routin_food_all_by_routine_id(routine_id=routine_id)
        if routin_foods is None:
            raise raise_error(ErrorCode.TRACK_ROUTINE_NOT_FOUND)
        return routin_foods

    def get_track_part_by_user_track_id(self, user_id: str, track_id: str):
        track_part = self.track_repo.find_track_part_by_user_track_id(user_id=user_id,track_id=track_id)
        if track_part is None:
            raise raise_error(ErrorCode.TRACK_PARTICIPATION_NOT_FOUNT)
        return track_part

    def create_routine_food_check(self, routine_food_id: str, dish_id: str, user_id: str):
        routine_food_check = self.track_repo.find_routine_food_check_by_else(routine_food_id=routine_food_id,
                                                                             dish_id=dish_id,user_id=user_id)
        if routine_food_check is not None:
            raise raise_error(ErrorCode.ROUTINE_FOOD_CHECK_ALREADY_EXIST)
        self.track_repo.create_routin_food_check(routine_food_id=routine_food_id,dish_id=dish_id,user_id=user_id)

    def update_routine_check(self, user_id: str, routine_id: str):
        routine_check = self.track_repo.update_routine_check(user_id=user_id,routine_id=routine_id)
        if routine_check is None:
            raise raise_error(ErrorCode.ROUTINECHECK_NOT_FOUND)

    def get_routine_food_with_food_by_id(self, routine_food_id: str):
        routine_food_with_food = self.track_repo.find_routine_food_with_food_by_id(routine_food_id=routine_food_id)
        if routine_food_with_food is None:
            raise raise_error(ErrorCode.TRACK_ROUTINE_FOOD_NOT_FOUND)
        return routine_food_with_food