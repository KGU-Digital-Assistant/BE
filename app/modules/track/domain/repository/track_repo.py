from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List


from app.modules.track.domain.track_participant import TrackParticipant as TrackParticipantVO
from app.modules.track.domain.track import Track, TrackRoutine, RoutineCheck
from app.modules.track.domain.track_routine_food import RoutineFood, RoutineFoodCheck
from app.modules.track.interface.schema.track_schema import UpdateTrackBody
from app.modules.track.interface.schema.track_schema import MealTime


class ITrackRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, track: Track):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, track_id: str):
        raise NotImplementedError

    @abstractmethod
    def routines_save(self, routine: List[TrackRoutine], track: Track):
        raise NotImplementedError

    @abstractmethod
    def find_routine_by_id(self, routine_id: str):
        raise NotImplementedError

    @abstractmethod
    def update_track(self, track_id: str, user_id: str, body: UpdateTrackBody):
        raise NotImplementedError

    @abstractmethod
    def update_routine(self, routine: TrackRoutine):
        raise NotImplementedError

    @abstractmethod
    def delete_track(self, track_id: str, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def delete_routine(self, routine_id: str, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_tracks_by_id(self, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def start_track(self, track_participant: TrackParticipantVO):
        raise NotImplementedError

    @abstractmethod
    def update_start_date(self, track_id: str, user_id: str, start_date: datetime.date):
        raise NotImplementedError

    @abstractmethod
    def find_all_routine_by_track_id(self, track_id):
        raise NotImplementedError

    @abstractmethod
    def delete_routine_food(self, routine_id: str, routine_food_id: str, calories: float):
        raise NotImplementedError

    @abstractmethod
    def find_routine_food_by_id(self, routine_food_id: str):
        raise NotImplementedError

    @abstractmethod
    def routine_food_save(self, new_routine_food: RoutineFood, routine_vo: TrackRoutine):
        raise NotImplementedError

    @abstractmethod
    def update_routine_food(self, routine_id: str, routine_food: RoutineFood, calories: float):
        raise NotImplementedError

    @abstractmethod
    def find_track_part_by_user_track_id(self, user_id: str, track_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_routine_food_all_by_routine_id(self, routine_id: str):
        raise NotImplementedError

    @abstractmethod
    def create_routine_food_check(self, routine_food_id: str, dish_id: str, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def delete_routine_food_check(self, routine_food_check: RoutineFoodCheck):
        raise NotImplementedError

    @abstractmethod
    def update_routine_check(self, user_id: str, routine_id: str, status: bool):
        raise NotImplementedError

    @abstractmethod
    def find_routine_food_with_food_by_id(self, routine_food_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_routine_check(self, routine_id: str, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def terminate_track(self, user_id: str, track_id: str):
        raise NotImplementedError

    @abstractmethod
    def routine_check_save(self, new: RoutineCheck):
        raise NotImplementedError

    @abstractmethod
    def find_routine_food_check_by_routine_food_id(self, routine_food_id: str, user_id: str) -> RoutineFoodCheck:
        raise NotImplementedError

    @abstractmethod
    def find_routine_food_check_by_else(self, routine_food_id: str, dish_id: str,user_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_routine_food_check_by_dish_id(self, dish_id: str, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_routine_by_days_mealtime(self, track_id: str, days: int, mealtime: MealTime):
        raise NotImplementedError

    @abstractmethod
    def find_routine_food_by_routine_id_label_name(self, routine_id: str, label: int | None, name: str | None):
        raise NotImplementedError

    @abstractmethod
    def find_participate_track(self, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def update_participant(self, track_part_vo: TrackParticipantVO):
        raise NotImplementedError

    @abstractmethod
    def find_all_participant(self, user_id: str):
        raise NotImplementedError
