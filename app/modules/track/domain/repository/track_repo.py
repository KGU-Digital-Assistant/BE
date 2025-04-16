from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List

from modules.track.domain.track_participant import TrackParticipant as TrackParticipantVO
from modules.track.domain.track import Track, TrackRoutine, RoutineCheck
from modules.track.domain.track_routine_food import RoutineFood, RoutinFoodCheck
from modules.track.interface.schema.track_schema import UpdateTrackBody


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
    def find_routin_food_all_by_routine_id(self, routine_id: str):
        raise NotImplementedError

    @abstractmethod
    def create_routin_food_check(self, routin_food_id: str, dish_id: str, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def update_routine_check(self, user_id: str, routin_id: str):
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
    def find_routine_food_check_by_routine_food_id(self, routine_food_id: str, user_id: str) -> RoutinFoodCheck:
        raise NotImplementedError

    @abstractmethod
    def find_routine_food_check_by_else(self, routine_food_id: str, dish_id: str,user_id: str):
        raise NotImplementedError