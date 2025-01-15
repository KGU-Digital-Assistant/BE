from datetime import datetime

import ulid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime, Enum, Date
from database import Base
from core.auth import Role
from modules.user.interface.schema.user_schema import Rank, Gender


class User(Base):  # 회원
    __tablename__ = "User"

    id: Mapped[str] = mapped_column(String(length=26), primary_key=True, nullable=False, default=lambda: str(ulid.new()))
    username: Mapped[str] = mapped_column(String(length=255), nullable=False)  # 회원가입 ID로 사용 (컬럼 이름 고정)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)  # 실명
    cellphone: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender))  # 1 남자, 0 여자
    birth: Mapped[Date] = mapped_column(Date)
    nickname: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    rank: Mapped[Rank] = mapped_column(Enum(Rank), nullable=False)
    profile_picture: Mapped[str] = mapped_column(String(length=255))
    email: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    # external_id: Mapped[str] = mapped_column(String(length=255))  # 연동했을 때 id
    # auth_type: Mapped[str] = mapped_column(String(length=255))  # 연동 방식 ex) kakao
    fcm_token: Mapped[str] = mapped_column(String(length=255))  # fcm 토큰
    # cur_group_id: Mapped[int] = mapped_column(ForeignKey("Group.id"))  # 현재 참여 중인 그룹 ID
    # mentor_id: Mapped[int] = mapped_column(ForeignKey("Mentor.id"))  # 멘토 ID
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False, default=Role.USER)  # 역할 정의
    create_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # 가입일자
    update_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # groups: Mapped[list['Group']] = relationship('Group', secondary=Participation, back_populates='users')
