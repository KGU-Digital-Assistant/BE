from abc import ABCMeta, abstractmethod
from typing import List

from modules.track.domain.track import Track, TrackRoutine, TrackRoutineDate
from modules.track.interface.schema.track_schema import UpdateTrackBody


class ITrackRepository(metaclass=ABCMeta):
    @abstractmethod
    def save(self, track: Track):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, track_id: str):
        raise NotImplementedError

    @abstractmethod
    def routine_save(self, routine: TrackRoutine, track: Track):
        raise NotImplementedError

    @abstractmethod
    def find_routine_by_id(self, routine_id: str):
        raise NotImplementedError

    @abstractmethod
    def find_routine_dates_by_routine_id(self, routine_id: str):
        raise NotImplementedError

    @abstractmethod
    def update_track(self, track_id: str, user_id: str, body: UpdateTrackBody):
        raise NotImplementedError

    @abstractmethod
    def update_routine(self, routine: TrackRoutine):
        raise NotImplementedError

    @abstractmethod
    def find_routine_date_by_id(self, routine_date_id: str):
        raise NotImplementedError

    @abstractmethod
    def update_routine_date(self, routine_date: TrackRoutineDate):
        raise NotImplementedError

    @abstractmethod
    def delete_track(self, track_id: str, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def delete_routine(self, routine_id: str, user_id: str):
        raise NotImplementedError

    @abstractmethod
    def delete_routine_date(self, routine_date_id: str, user_id: str):
        raise NotImplementedError
