from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flasgger import Swagger, APISpec, swag_from
from flask import Flask, request
from flask_restful import Api, Resource
from marshmallow import ValidationError

import uuid
import secrets
import logging

from models import \
    init_db, \
    get_all_users, \
    add_user, \
    delete_all_users, \
    get_record_by_id, \
    get_all_records, \
    add_record, \
    session, \
    Records, \
    delete_all_records
from schemas import UserSchema, RecordSchema
from drivers import download_record, convert_wav_to_mp3, delete_records

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel('DEBUG')

app = Flask(__name__)
api = Api(app)

spec = APISpec(
    title='UsersList',
    version='1.0.0',
    openapi_version='2.0',
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)


@app.before_request
def before_request():
    """Этот эндпойнт создает таблицы users и records в базе данных."""
    init_db()


class UsersList(Resource):

    @swag_from('./docs/get_users.yml')
    def get(self) -> tuple[list[dict], int]:
        """Этот эндпойнт возвращает всех пользователей из базы данных."""
        schema = UserSchema()
        table_is_not_empty = get_all_users()
        if table_is_not_empty:
            return schema.dump(table_is_not_empty, many=True), 200
        return [{'message': 'В базе данных нет ни одного пользователя.'}], 200

    @swag_from('./docs/post_users.yml')
    def post(self) -> tuple[list[dict], int]:
        """
        Этот эндпойнт проверяет есть ли в базе данных пользователи с указанным username
         и если нет добавляет нового пользователя.
        """

        schema = UserSchema()
        username = request.json

        try:
            user = schema.load(username)
        except ValidationError as exc:
            return exc.messages, 400

        username = user.username
        user_uuid = str(uuid.uuid4())
        token = secrets.token_hex()

        new_user = {
            'username': username,
            'user_uuid': user_uuid,
            'token': token,
        }

        answer = add_user(new_user)
        return schema.dump(answer), 201

    @swag_from('./docs/delete_users.yml')
    def delete(self) -> tuple[list[dict], int]:
        """Этот эндпойнт удаляет все данные из таблицы Users."""
        delete_all_users()
        return [{'message': 'Все пользователи удалены из базы данных.'}], 200


class RecordsList(Resource):
    @swag_from('./docs/get_records.yml')
    def get(self) -> tuple[list[dict], int]:
        """Этот эндпойнт возвращает все записи из базы данных."""

        logger.debug('Работа метода GET, эндпойнт - record/')
        schema = RecordSchema()

        input_values = request.values.to_dict()
        if input_values:
            logger.debug('Имеются входные данные. Будет произведен поиск и скачивание запрашиваемой записи.')
            record = schema.dump(get_record_by_id(int(input_values['id']), int(input_values['user'])))

            if record:
                download_record(record)
                return [{'message': f'Запись {record} добавлена в папку output.'}], 200
            else:
                return [{'message': 'Запись с заданными параметрами не найдена.'}], 200

        else:
            logger.debug('Входные данные отсутствуют. Будет возвращен список всех записей.')
            table_is_not_empty = get_all_records()
            if table_is_not_empty:
                return schema.dump(table_is_not_empty, many=True), 200
            return [{'message': 'В базе данных нет ни одной записи.'}], 200

    @swag_from('./docs/post_records.yml')
    def post(self) -> str or tuple[str, int]:
        """
        Этот эндпойнт проверяет формат файла, конвертирует его в mp3, сохраняет файл на сервере,
        а ссылку на этот файл в базе данных.
        """
        logger.debug('Работа метода POST, эндпойнт - record/')

        data = request.json
        schema = RecordSchema()

        try:
            logger.debug(f'Валидация данных {data}.')
            data = schema.load(data)
        except ValidationError as exc:
            return exc.messages, 400

        record_uuid = str(uuid.uuid4())

        record = convert_wav_to_mp3(data.record, record_uuid)

        new_record = {
            'user_id': data.user_id,
            'record': record,
            'record_uuid': record_uuid
        }

        add_record(new_record)

        url = request.host_url
        data_record = session.query(Records).filter(Records.record_uuid == record_uuid)
        link = f'record?id={data_record[0].id}&user={data_record[0].user_id}'
        record_link = url + link
        return [{'url': record_link}], 201

    @swag_from('./docs/delete_records.yml')
    def delete(self) -> tuple[list[dict], int]:
        """Этот эндпойнт удаляет все записи из таблицы Records."""

        logger.debug('Работа метода DELETE, эндпойнт - record/')
        delete_all_records()
        delete_records('./static/records')
        return [{'message': 'Все записи удалены из базы данных.'}], 200


template = spec.to_flasgger(
    app,
    definitions=[UserSchema, RecordSchema]
)

swagger = Swagger(app, template=template)

api.add_resource(UsersList, '/api/user')
api.add_resource(RecordsList, '/api/record')


if __name__ == '__main__':
    logger.info('Старт работы программы Gramophone.')
    app.run(debug=True)
