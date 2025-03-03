from abc import ABC
from dataclasses import asdict
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from database import SessionLocal
from modules.track.domain.repository.track_repo import ITrackRepository
from modules.track.domain.track import Track as TrackVO
from modules.track.domain.track import TrackRoutine as TrackRoutineVO
from modules.track.domain.track import TrackRoutineDate as TrackRoutineDateVO
from modules.track.infra.db_models.track import Track, TrackRoutine, TrackRoutineDate
from modules.track.interface.schema.track_schema import UpdateTrackBody
from utils.db_utils import row_to_dict
from utils.exceptions.error_code import ErrorCode
from utils.exceptions.handlers import raise_error


class TrackRepository(ITrackRepository, ABC):

    def save(self, track_vo: TrackVO):
        with SessionLocal() as db:
            track_dict = asdict(track_vo)
            track = Track(**track_dict)
            db.add(track)
            db.commit()
            return TrackVO(**row_to_dict(track))

    def routine_save(self, routine_vo: TrackRoutineVO, track_vo: TrackVO):
        with (SessionLocal() as db):
            routine_dates = [TrackRoutineDate(**asdict(routine_date)) for routine_date in routine_vo.routine_dates]
            track = db.query(Track).filter(Track.id == track_vo.id).first()
            routine = TrackRoutine(
                id=routine_vo.id,
                track_id=routine_vo.track_id,
                title=routine_vo.title,
                calorie=routine_vo.calorie,
                delete=routine_vo.delete,
                routine_dates=routine_dates,
                track=track
            )
            track.routines.append(routine)
            db.add(routine)
            db.commit()
            return TrackRoutineVO(**row_to_dict(routine))

    def find_by_id(self, track_id: str) -> TrackVO | None:
        with (SessionLocal() as db):
            track = db.query(Track
                    ).options(joinedload(Track.routines).joinedload(TrackRoutine.routine_dates)
                    ).filter(Track.id == track_id
                    ).first()

            if track is None:
                return None
        return TrackVO(**row_to_dict(track))

    def find_routine_by_id(self, routine_id: str):
        with SessionLocal() as db:
            routine = db.query(TrackRoutine).options(joinedload(TrackRoutine.routine_dates)
                                                     ).filter(TrackRoutine.id == routine_id).first()
            if routine is None:
                return None
            return TrackRoutineVO(**row_to_dict(routine))

    def find_routine_dates_by_routine_id(self, routine_id: str):
        routine_dates = self.db.query(TrackRoutineDate).filter(TrackRoutineDate.id == routine_id).all()
        routine_date_vos = [TrackRoutineDateVO(**row_to_dict(routine_date)) for routine_date in routine_dates]
        return routine_date_vos

    def find_routine_date_by_id(self, routine_date_id: str):
        with SessionLocal() as db:
            routine_date = db.query(TrackRoutineDate
                                    ).options(joinedload(TrackRoutineDate.routine)
                                    ).filter(TrackRoutineDate.id == routine_date_id).first()
            if routine_date is None:
                return None
            return TrackRoutineDateVO(**row_to_dict(routine_date))

    def update_track(self, track_id: str, user_id: str, body: UpdateTrackBody):
        with SessionLocal() as db:
            track = db.query(Track
                    ).options(joinedload(Track.routines).joinedload(TrackRoutine.routine_dates)
                    ).filter(Track.id == track_id
                    ).first()
            if track is None:
                raise_error(ErrorCode.TRACK_NOT_FOUND)
            if track.user_id != user_id:
                raise_error(ErrorCode.USER_NOT_AUTHENTICATED)

            track.name = body.name
            track.duration = body.duration
            db.commit()

            return TrackVO(**row_to_dict(track))

    def update_routine(self, routine_vo: TrackRoutineVO):
        with SessionLocal() as db:
            routine = db.query(TrackRoutine).options(joinedload(TrackRoutine.routine_dates)
                                                     ).filter(TrackRoutine.id == routine_vo.id).first()
            if routine is None:
                return None

            routine.title = routine_vo.title
            routine.calorie = routine_vo.calorie
            db.commit()
        return routine_vo

    def update_routine_date(self, routine_date_vo: TrackRoutineDateVO):
        with SessionLocal() as db:
            routine_date = db.query(TrackRoutineDate
                                    ).options(joinedload(TrackRoutineDate.routine)
                                    ).filter(TrackRoutineDate.id == routine_date_vo.id).first()

            if routine_date is None:
                raise raise_error(ErrorCode.TRACK_ROUTINE_DATE_NOT_FOUND)

            routine_date.weekday = routine_date.weekday
            routine_date.meal_time = routine_date.meal_time
            routine_date.date = routine_date.date
            db.commit()
            return TrackRoutineDateVO(**row_to_dict(routine_date))

    def delete_track(self, track_id: str, user_id: str):
        with SessionLocal() as db:
            track = db.query(Track).filter(Track.id == track_id).first()
            if track is None:
                raise_error(ErrorCode.TRACK_NOT_FOUND)
            if track.user_id != user_id:
                raise_error(ErrorCode.USER_NOT_AUTHENTICATED)

            db.delete(track)
            db.commit()

    def delete_routine(self, routine_id: str, user_id: str):
        with SessionLocal() as db:
            routine = db.query(TrackRoutine).filter(TrackRoutine.id == routine_id).first()
            if routine is None:
                raise_error(ErrorCode.TRACK_NOT_FOUND)
            track = db.query(Track).filter(Track.id == routine.track_id).first()
            if track is None:
                raise_error(ErrorCode.TRACK_NOT_FOUND)
            if track.user_id != user_id:
                raise_error(ErrorCode.USER_NOT_AUTHENTICATED)
            db.delete(routine)
            db.commit()

    def delete_routine_date(self, routine_date_id: str, user_id: str):
        with SessionLocal() as db:
            routine_date = db.query(TrackRoutineDate).filter(TrackRoutineDate.id == routine_date_id).first()
            if routine_date is None:
                raise_error(ErrorCode.TRACK_ROUTINE_DATE_NOT_FOUND)
            db.delete(routine_date)
            db.commit()
