from abc import ABC
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import List

import ulid
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from app.database import SessionLocal
from app.modules.track.interface.schema.track_schema import MealTime
from app.modules.track.domain.repository.track_repo import ITrackRepository
from app.modules.track.domain.track import Track as TrackVO
from app.modules.track.domain.track import TrackRoutine as TrackRoutineVO, RoutineCheck as RoutineCheckVO
from app.modules.track.domain.track_routine_food import RoutineFood as RoutineFoodVO
from app.modules.track.domain.track_routine_food import RoutineFoodCheck as RoutineFoodCheckVO
from app.modules.track.domain.track_participant import TrackParticipant as TrackParticipantVO
from app.modules.track.infra.db_models.track import Track, TrackRoutine, RoutineCheck
from app.modules.track.infra.db_models.track_participant import TrackParticipant
from app.modules.track.infra.db_models.track_routine_food import RoutineFood, RoutineFoodCheck
from app.modules.track.interface.schema.track_schema import UpdateTrackBody, TrackRoutineList, FlagStatus
from app.modules.user.infra.db_models.user import User
from app.utils.db_utils import row_to_dict
from app.utils.exceptions.error_code import ErrorCode
from app.utils.exceptions.handlers import raise_error


class TrackRepository(ITrackRepository, ABC):

    def save(self, track_vo: TrackVO):
        with SessionLocal() as db:
            track_dict = asdict(track_vo)
            track = Track(**track_dict)
            db.add(track)
            db.commit()
            return TrackVO(**row_to_dict(track))

    def routines_save(self, routine_list_vo: List[TrackRoutineVO], track_vo: TrackVO):
        with SessionLocal() as db:

            track = db.query(Track).filter(Track.id == track_vo.id).first()

            routines = []
            for routine in routine_list_vo:
                routine_foods_db = []
                res_foods = []
                for routine_food in routine.routine_foods:
                    new_routine_food = RoutineFood(
                        id=routine_food.id,
                        routine_id=routine_food.routine_id,
                        food_label=routine_food.food_label,
                        quantity=routine_food.quantity,
                        food_name=routine_food.food_name,
                    )

                    db.add(new_routine_food)
                    routine_foods_db.append(new_routine_food)
                    res_foods.append(RoutineFoodVO(**row_to_dict(new_routine_food)))

                new_routine = TrackRoutine(
                    id=routine.id,
                    track_id=track_vo.id,
                    title=routine.title,
                    calorie=routine.calorie,
                    delete=routine.delete,
                    mealtime=routine.mealtime,
                    days=routine.days,
                    clock=routine.clock,
                    track=track,
                    routine_foods=routine_foods_db
                )
                track.routines.append(new_routine)
                db.add(new_routine)

                res_routine = TrackRoutineVO(**row_to_dict(new_routine))
                res_routine.routine_foods = res_foods
                routines.append(res_routine)
            db.commit()
            return routines

    def routine_food_save(self, routine_food_vo: RoutineFood, routine_vo: TrackRoutineVO):
        with SessionLocal() as db:
            routine_food = RoutineFood(
                id=routine_food_vo.id,
                routine_id=routine_food_vo.routine_id,
                food_label=routine_food_vo.food_label,
                quantity=routine_food_vo.quantity,
                food_name=routine_food_vo.food_name
            )
            db.add(routine_food)

            routine = db.query(TrackRoutine).filter(TrackRoutine.id == routine_vo.id).first()
            routine.calorie = routine_vo.calorie
            db.commit()
            return RoutineFood(**row_to_dict(routine_food))

    def routine_check_save(self, routine_check_vo: RoutineCheck):
        with SessionLocal() as db:
            routine_check = RoutineCheck(
                id=routine_check_vo.id,
                routine_id=routine_check_vo.routine_id,
                user_id=routine_check_vo.user_id,
                is_complete=routine_check_vo.is_complete,
            )
            db.add(routine_check)
            db.commit()
            return RoutineCheckVO(**row_to_dict(routine_check))

    def find_by_id(self, track_id: str):
        with (SessionLocal() as db):
            track = db.query(Track).options(
                joinedload(Track.routines).joinedload(TrackRoutine.routine_foods)
            ).filter(Track.id == track_id).first()

            if track is None:
                return None
            return TrackVO(**row_to_dict(track))

    def find_routine_by_id(self, routine_id: str):
        with SessionLocal() as db:
            routine = db.query(TrackRoutine).filter(TrackRoutine.id == routine_id).first()
            if routine is None:
                return None
            return TrackRoutineVO(**row_to_dict(routine))

    def find_all_routine_by_track_id(self, track_id: str):
        with SessionLocal() as db:
            routines = db.query(TrackRoutine).filter(TrackRoutine.track_id == track_id).all()
            if routines is None:
                return None

            routine_list = []
            for routine in routines:
                routine_list.append(TrackRoutineVO(**row_to_dict(routine)))
            return routine_list

    def find_routine_food_by_id(self, routine_food_id: str):
        with SessionLocal() as db:
            routine_food = db.query(RoutineFood).filter(RoutineFood.id == routine_food_id).first()
            if routine_food is None:
                return None
            return RoutineFoodVO(**row_to_dict(routine_food))

    def find_routine_food_check_by_routine_food_id(self, routine_food_id: str, user_id: str):
        with SessionLocal() as db:
            routine_food_check = db.query(RoutineFoodCheck).filter(
                RoutineFoodCheck.routine_food_id == routine_food_id,
                RoutineFoodCheck.user_id == user_id).first()
            if routine_food_check is None:
                return None
            return RoutineFoodCheckVO(**row_to_dict(routine_food_check))

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

    def update_routine_food(self, routine_id: str, routine_food_vo: RoutineFood, calories: float):
        with SessionLocal() as db:
            routine = db.query(TrackRoutine).filter(TrackRoutine.id == routine_id).first()
            if routine is None:
                return None

            routine.calorie += calories

            routine_food = db.query(RoutineFood).filter(RoutineFood.id == routine_food_vo.id).first()
            routine_food.food_label = routine_food_vo.food_label
            routine_food.quantity = routine_food_vo.quantity
            db.commit()
            return RoutineFood(**row_to_dict(routine_food))

    def delete_track(self, track_id: str, user_id: str):
        with SessionLocal() as db:
            track = db.query(Track).filter(Track.id == track_id).first()
            if track is None:
                raise_error(ErrorCode.TRACK_NOT_FOUND)

            db.delete(track)
            db.commit()

    def delete_routine(self, routine_id: str, user_id: str):
        with SessionLocal() as db:
            routine = db.query(TrackRoutine).filter(TrackRoutine.id == routine_id).first()
            if routine is None:
                raise_error(ErrorCode.TRACK_ROUTINE_NOT_FOUND)
            track = db.query(Track).filter(Track.id == routine.track_id).first()
            if track is None:
                raise_error(ErrorCode.TRACK_NOT_FOUND)

            db.delete(routine)
            db.commit()

    def delete_routine_food(self, routine_id: str, routine_food_id: str, calories: float):
        with SessionLocal() as db:
            routine = db.query(TrackRoutine).filter(TrackRoutine.id == routine_id).first()
            if routine is None:
                raise_error(ErrorCode.TRACK_ROUTINE_NOT_FOUND)
            routine_food = db.query(RoutineFood).filter(RoutineFood.id == routine_food_id).first()
            routine.calorie -= calories

            for food in routine.routine_foods:
                if routine_food.id == food.id:
                    db.delete(food)
                    break
            db.commit()
        return self.find_routine_by_id(routine_id)

    def find_tracks_by_id(self, user_id: str):
        with SessionLocal() as db:
            tracks = db.query(Track).filter(Track.user_id == user_id).all()

            track_list = []
            for track in tracks:
                track_list.append(TrackVO(**row_to_dict(track)))
        return track_list

    def start_track(self, track_participant_vo: TrackParticipantVO):
        with SessionLocal() as db:
            track_participant = TrackParticipant(
                id=track_participant_vo.id,
                track_id=track_participant_vo.track_id,
                user_id=track_participant_vo.user_id,
                joined_at=track_participant_vo.joined_at,
                status=track_participant_vo.status
            )
            db.add(track_participant)
            db.commit()
            return TrackParticipantVO(**row_to_dict(track_participant))

    def terminate_track(self, user_id: str, track_id: str):
        with SessionLocal() as db:
            track_participant = db.query(TrackParticipant).filter(TrackParticipant.user_id == user_id,
                                                                  TrackParticipant.track_id == track_id).first()
            if track_participant is None:
                return None
            track_participant.status = FlagStatus.TERMINATED
            db.commit()
            return TrackParticipantVO(**row_to_dict(track_participant))

    def update_start_date(self, track_id: str, user_id: str, start_date: datetime.date):
        with SessionLocal() as db:
            track = db.query(Track).filter(Track.id == track_id).first()

            track.start_date = datetime.now().date() + (start_date - datetime.now().date())
            track.finished_date = datetime.now().date() + timedelta(days=track.duration)
            db.commit()

    def find_track_part_by_user_track_id(self, user_id: str, track_id: str):
        with SessionLocal() as db:
            track_part = db.query(TrackParticipant).filter(TrackParticipant.user_id == user_id,
                                                           TrackParticipant.track_id == track_id).first()
            if track_part is None:
                return None
        return TrackParticipantVO(**row_to_dict(track_part))

    def find_routine_check(self, routine_id: str, user_id: str):
        with SessionLocal() as db:
            clear_routine = db.query(RoutineCheck).filter(RoutineCheck.routine_id == routine_id and
                                                          RoutineCheck.user_id == user_id
                                                          ).first()
            if clear_routine is None:
                return None
            return RoutineCheckVO(**row_to_dict(clear_routine))

    def find_routine_food_all_by_routine_id(self, routine_id: str):
        with SessionLocal() as db:
            track_routine_foods = (
                db.query(TrackRoutine)
                .options(
                    joinedload(TrackRoutine.routine_foods).joinedload(RoutineFood.food)
                )
                .filter(TrackRoutine.id == routine_id)
                .all()
            )
            if track_routine_foods is None:
                return None
            return track_routine_foods

    def create_routine_food_check(self, routine_food_id: str, dish_id: str, user_id: str):
        with SessionLocal() as db:
            new_routine_food_check = RoutineFoodCheck(
                id=str(ulid.ULID()),
                routine_food_id=routine_food_id,
                dish_id=dish_id,
                user_id=user_id,
                is_complete=True,  ## 추후 변경필요
                check_time=datetime.utcnow()
            )
            db.add(new_routine_food_check)
            db.commit()

    def delete_routine_food_check(self, routine_food_check: RoutineFoodCheck):
        with SessionLocal() as db:
            db.delete(routine_food_check)
            db.commit()

    def update_routine_check(self, user_id: str, routine_id: str, status: bool):
        with SessionLocal() as db:
            routine_check=db.query(RoutineCheck).filter(RoutineCheck.user_id==user_id,RoutineCheck.routine_id==routine_id).first()
            if routine_check is None:
                return None
            routine_check.is_complete = status
            routine_check.check_time = datetime.utcnow()
            db.add(routine_check)
            db.commit()
            return RoutineCheckVO(**row_to_dict(routine_check))

    def find_routine_food_with_food_by_id(self, routine_food_id: str):
        with SessionLocal() as db:
            routine_food = db.query(RoutineFood).options(
                    joinedload(RoutineFood.food)
                ).filter(RoutineFood.id == routine_food_id).first()
            if routine_food is None:
                return None
            return RoutineFoodVO(**row_to_dict(routine_food))

    def find_routine_food_check_by_else(self, routine_food_id: str, dish_id: str,user_id: str):
        with SessionLocal() as db:
            routine_food_check = db.query(RoutineFoodCheck).filter(RoutineFoodCheck.routine_food_id==routine_food_id,
                                                                   RoutineFoodCheck.dish_id==dish_id,
                                                                   RoutineFoodCheck.user_id==user_id).first()
            if routine_food_check is None:
                return None
            return RoutineFoodCheckVO(**row_to_dict(routine_food_check))

    def find_routine_food_check_by_dish_id(self, dish_id: str, user_id: str):
        with SessionLocal() as db:
            return db.query(RoutineFoodCheck).filter(
                    RoutineFoodCheck.dish_id == dish_id,
                    RoutineFoodCheck.user_id == user_id
                ).first()

    def find_routine_by_days_mealtime(self, track_id: str, days: int, mealtime: MealTime):
        with SessionLocal() as db:
            return db.query(TrackRoutine).filter(
                TrackRoutine.track_id==track_id,
                TrackRoutine.days==days,
                TrackRoutine.mealtime==mealtime
            ).first()

    def find_routine_food_by_routine_id_label_name(self, routine_id: str, label: int | None, name: str | None):
        with SessionLocal() as db:
            query = db.query(RoutineFood).filter(RoutineFood.routine_id == routine_id)
            if label is not None:
                query = query.filter(RoutineFood.food_label == label)
            elif name is not None:
                query = query.filter(
                    RoutineFood.food_label.is_(None),
                    RoutineFood.food_name == name
                )
            else:
                return None  # label과 name 둘 다 없으면 None
            return query.first()

    def find_participate_track(self, user_id: str):
        with SessionLocal() as db:
            track_part = db.query(TrackParticipant).filter(TrackParticipant.user_id == user_id,
                                                           TrackParticipant.status != FlagStatus.TERMINATED.value).first()
            if track_part is None:
                return None
            return TrackParticipantVO(**row_to_dict(track_part))

    def update_participant(self, track_part_vo: TrackParticipantVO):
        with SessionLocal() as db:
            track_part = db.query(TrackParticipant).filter(TrackParticipant.id == track_part_vo.id).first()
            if track_part is None:
                return None

            track_part.status = track_part_vo.status
            db.commit()
            return TrackParticipantVO(**row_to_dict(track_part))

    def find_all_participant(self, user_id: str):
        with SessionLocal() as db:
            track_part_list = db.query(TrackParticipant).filter(TrackParticipant.user_id == user_id).all()
            res = []
            for track_part_vo in track_part_list:
                res.append(TrackParticipantVO(**row_to_dict(track_part_vo)))

            return res