import psycopg2
import logging

from typing import Type
from sqlalchemy import create_engine, Column, Integer, String, inspect, desc, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base


logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel('DEBUG')

engine = create_engine('postgresql+psycopg2://admin:admin@gramophone_db:5432/gramophone_db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Users(Base):
    """Модель для хранения данных пользователей."""
    __tablename__ = 'users'

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(length=100), nullable=True)
    user_uuid: str = Column(String(length=100), nullable=True)
    token: str = Column(String(length=100), nullable=True)

    def __repr__(self):
        return f'id: {self.id}, ' \
               f'username: {self.username}, ' \
               f'user_uuid: {self.user_uuid},' \
               f'token: {self.token}'

    def to_json(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Records(Base):
    """Модель для хранения записей."""
    __tablename__ = 'records'

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, nullable=True)
    record: str = Column(String(length=250), nullable=True)
    record_uuid: str = Column(String(length=100), nullable=True)

    def __repr__(self):
        return f'id: {self.id}, ' \
               f'user_id: {self.user_id}, ' \
               f'record: {self.record},'\
               f'record_uuid: {self.record_uuid}'

    def to_json(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


def init_db() -> None:
    logger.debug('Проверка наличия таблиц "users" и "records".')
    ins = inspect(engine)
    table_users_exist = ins.dialect.has_table(engine.connect(), 'users')
    table_records_exist = ins.dialect.has_table(engine.connect(), 'records')

    if not table_users_exist:
        Base.metadata.create_all(bind=engine)
        logger.info(f'Таблица "users" успешно создана.')

    if not table_records_exist:
        Base.metadata.create_all(bind=engine)
        logger.info(f'Таблица "records" успешно создана.')


def get_all_users() -> list:
    return session.query(Users).all()


def get_user_by_username(username) -> Type[Users]:
    user_in_db = session.query(Users).filter(Users.username == username).one_or_none()
    return user_in_db


def get_user_by_id(user_id) -> Type[Users]:
    user_in_db = session.query(Users).filter(Users.id == user_id).one_or_none()
    return user_in_db


def add_user(user: dict) -> dict:
    new_user = Users(
        username=user['username'],
        user_uuid=user['user_uuid'],
        token=user['token'],
        )

    session.add(new_user)
    session.commit()
    logger.info(f'Новый пользователь {user["username"]} добавлен в базу данных.')

    return session.query(Users.user_uuid, Users.token).order_by(desc(Users.id)).first()


def delete_all_users() -> None:
    session.query(Users).delete()
    session.commit()
    logger.info('Все данные таблицы "users" удалены.')


def get_all_records() -> list:
    return session.query(Records).all()


def get_record_by_id(record_id: int, user_id: int) -> list:
    logger.debug(f'Поиск записи {record_id} пользователя {user_id}.')
    result = session.query(Records.record_uuid)\
        .filter(Records.id == record_id).filter(Records.user_id == user_id).one_or_none()
    return result


def add_record(record: dict) -> None:
    new_record = Records(
        user_id=record['user_id'],
        record=record['record'],
        record_uuid=record['record_uuid']
        )

    session.add(new_record)
    session.commit()
    logger.info(f'Новая запись добавлена в базу данных.')


def delete_all_records() -> None:
    session.query(Records).delete()
    session.commit()
    logger.info('Все данные таблицы "records" удалены.')
