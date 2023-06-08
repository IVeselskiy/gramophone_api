from marshmallow import ValidationError
from marshmallow import post_load, validates

from drivers import wrong_type_file, not_find_file, wrong_path_to_file
from models import Users, Records, get_user_by_username, get_user_by_id
from flasgger import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    user_uuid = fields.Str(dump_only=True)
    token = fields.Str(dump_only=True)

    @validates('username')
    def validate_user(self, username, **kwargs) -> None:
        if get_user_by_username(username) is not None:
            raise ValidationError(f'Пользователь с именем {username} уже есть в базе данных.')

    @post_load
    def create_user(self, data: dict, **kwargs) -> Users:
        return Users(**data)


class RecordSchema(Schema):
    id = fields.Int(dump_only=True)
    record = fields.Str(required=True)
    user_id = fields.Int(required=True)
    record_uuid = fields.Str(dump_only=True)

    @validates('record')
    def validate_record(self, record, **kwargs) -> None:
        if wrong_path_to_file(record):
            raise ValidationError('Не верно указан путь файла. Путь должен иметь вид "./static/input/<filename>')
        elif wrong_type_file(record):
            raise ValidationError('Не верный тип файла.')
        elif not_find_file(record):
            raise ValidationError('Файл не найден.')

    @validates('user_id')
    def validate_user(self, user_id, **kwargs) -> None:
        if get_user_by_id(user_id) is None:
            raise ValidationError('Пользователь не найден.')

    @post_load
    def create_record(self, data: dict, **kwargs) -> Users:
        return Records(**data)
