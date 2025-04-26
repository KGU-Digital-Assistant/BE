from app.database import SessionLocal
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date
from app.modules.track.infra.db_models.track import Track
from app.modules.track.infra.db_models.track_participant import TrackParticipant
from app.modules.track.interface.schema.track_schema import FlagStatus


def check_and_end_tracks():
    with SessionLocal() as db:
        today = date.today()
        tracks = db.query(Track).filter(Track.finish_date < today).all()
        for track in tracks:
            track_participants = db.query(TrackParticipant).filter(
                TrackParticipant.track_id == track.id,
                TrackParticipant.status == FlagStatus.STARTED
            ).all()

            for participant in track_participants:
                participant.status = FlagStatus.TERMINATED

        db.commit()


def start_track_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_end_tracks, 'cron', hour=0, minute=0)  # ⏰ 매일 0시 실행
    scheduler.start()
