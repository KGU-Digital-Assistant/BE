from abc import ABC
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from database import SessionLocal
from modules.track.domain.repository.track_repo import ITrackRepository
from modules.track.domain.track import Track as TrackVO
from modules.track.domain.track import TrackRoutine as TrackRoutineVO
from modules.track.domain.track_participant import TrackParticipant as TrackParticipantVO
from modules.track.infra.db_models.track import Track, TrackRoutine
from modules.track.infra.db_models.track_participant import TrackParticipant
from modules.track.interface.schema.track_schema import UpdateTrackBody, TrackRoutineList
from modules.user.infra.db_models.user import User
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

    def routine_save(self, routine_vo: TrackRoutine, track_vo: Track):
        with SessionLocal() as db:
            track = db.query(Track).filter_by(id=track_vo.id).first()
            routine = TrackRoutine(
                id=routine_vo.id,
                track_id=track_vo.id,
                title=routine_vo.title,
                calorie=routine_vo.calorie,
                delete=routine_vo.delete,
                mealtime=routine_vo.mealtime,
                days=routine_vo.days,
                clock=routine_vo.clock,
                track=track
            )
            db.add(routine)
            db.commit()
            return TrackRoutineVO(**row_to_dict(routine))

    def routines_save(self, routine_vo: List[TrackRoutineVO], track_vo: TrackVO):
        with SessionLocal() as db:

            track = db.query(Track).filter(Track.id == track_vo.id).first()

            routines = []
            for routine in routine_vo:
                new_routine = TrackRoutine(
                    id=routine.id,
                    track_id=routine.track_id,
                    title=routine.title,
                    calorie=routine.calorie,
                    delete=routine.delete,
                    mealtime=routine.mealtime,
                    days=routine.days,
                    clock=routine.clock,
                    track=track
                )
                track.routines.append(new_routine)
                db.add(new_routine)
                routines.append(TrackRoutineVO(**row_to_dict(new_routine)))
            db.commit()
            return routines

    def find_by_id(self, track_id: str) -> TrackVO | None:
        with (SessionLocal() as db):
            track = db.query(Track
                    ).options(joinedload(Track.routines)
                    ).filter(Track.id == track_id
                    ).first()

            if track is None:
                return None
        return TrackVO(**row_to_dict(track))

    def find_routine_by_id(self, routine_id: str):
        with SessionLocal() as db:
            routine = db.query(TrackRoutine).filter(TrackRoutine.id == routine_id).first()
            if routine is None:
                return None
            return TrackRoutineVO(**row_to_dict(routine))

    def update_track(self, track_id: str, user_id: str, body: UpdateTrackBody):
        with SessionLocal() as db:
            track = db.query(Track
                    ).options(joinedload(Track.routines)
                    ).filter(Track.id == track_id
                    ).first()
            if track is None:
                raise_error(ErrorCode.TRACK_NOT_FOUND)
            if track.user_id != user_id:
                raise_error(ErrorCode.USER_NOT_AUTHENTICATED)

            track.name = body.name
            # track.duration = body.duration
            db.commit()

            return TrackVO(**row_to_dict(track))

    def update_routine(self, routine_vo: TrackRoutineVO):
        with SessionLocal() as db:
            routine = db.query(TrackRoutine).filter(TrackRoutine.id == routine_vo.id).first()
            if routine is None:
                return None

            routine.title = routine_vo.title
            routine.calorie = routine_vo.calorie
            routine.days = routine_vo.days
            routine.weekday = routine_vo.weekday
            db.commit()
        return TrackRoutineVO(**row_to_dict(routine))

    # def update_routine_date(self, routine_date_vo: TrackRoutineDateVO):
    #     with SessionLocal() as db:
    #         routine_date = db.query(TrackRoutineDate
    #                                 ).options(joinedload(TrackRoutineDate.routine)
    #                                 ).filter(TrackRoutineDate.id == routine_date_vo.id).first()
    #
    #         if routine_date is None:
    #             raise raise_error(ErrorCode.TRACK_ROUTINE_DATE_NOT_FOUND)
    #
    #         routine_date.weekday = routine_date.weekday
    #         routine_date.mealtime = routine_date.mealtime
    #         routine_date.days = routine_date.days
    #         db.commit()
    #         return TrackRoutineDateVO(**row_to_dict(routine_date))

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

    def find_tracks_by_id(self, user_id: str):
        with SessionLocal() as db:
            tracks = db.query(Track).filter(Track.user_id == user_id).all()

            track_list = []
            for track in tracks:
                track_list.append(TrackVO(**row_to_dict(track)))
        return track_list

    def start_track(self, track_participant_vo: TrackParticipantVO):
        with SessionLocal() as db:
            if db.query(TrackParticipant).filter(TrackParticipant.track_id == track_participant_vo.track_id
                                                 and TrackParticipant.user_id == track_participant_vo.user_id).first():
                raise_error(ErrorCode.PARTICIPANT_ALREADY_EXIST)

            track_participant = TrackParticipant(
                id=track_participant_vo.id,
                track_id=track_participant_vo.track_id,
                user_id=track_participant_vo.user_id,
                joined_at=track_participant_vo.joined_at,
            )
            db.add(track_participant)
            db.commit()
            return TrackParticipantVO(**row_to_dict(track_participant))

    def update_start_date(self, track_id: str, user_id: str, start_date: datetime.date):
        with SessionLocal() as db:
            track = db.query(Track).filter(Track.id == track_id).first()

            track.start_date = datetime.now().date() + (start_date - datetime.now().date())
            track.finished_date = datetime.now().date() + timedelta(days=track.duration)
            db.commit()
