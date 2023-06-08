import os
import logging

from pydub import AudioSegment

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel('DEBUG')


def wrong_type_file(filename: str) -> bool:
    """Функция проверяет тип файла."""
    logger.debug('Проверка типа файла.')
    if str(filename[-3:]) != 'wav':
        logger.debug('Формат данных не соответствует.')
        logger.debug(f'Тип файла не соответствует.')
        return True
    logger.debug(f'Тип файла соответствует.')
    return False


def wrong_path_to_file(filename: str) -> bool:
    """Функция проверяет директорию файла."""
    logger.debug(f'Проверка указанного пути {filename}.')
    folder = filename.split('/')[:-1]
    if folder != ['.', 'static', 'input']:
        logger.debug(f'Путь {folder} не соответствует.')
        return True
    logger.debug(f'Путь {folder} соответствует.')
    return False


def not_find_file(path_file: str) -> bool:
    filename = path_file.split('/')[-1]
    logger.debug(f'Поиск файла {filename} в папке ./static/input.')
    for root, dirs, files in os.walk('./static/input'):
        logger.debug(f'{root}, {dirs}, {files}')
        for file in files:
            if file == filename:
                logger.debug(f'Файл {path_file} найден.')
                return False
    logger.debug(f'Файл {path_file} не найден.')
    return True


def convert_wav_to_mp3(path_file: str, record_uuid: str) -> str:
    """Функция конвертирует WAV в MP3."""

    path_file = os.path.abspath(path_file)
    logger.debug(f'Получаем файл {path_file}')

    new_file_name = ((str(path_file).split('/'))[-1].split('.'))[0]

    new_file_name = record_uuid + '&' + new_file_name + '.mp3'
    folder_for_save = os.path.join(str(os.getcwd()) + '/static/records')

    logger.debug(f'Папка для хранения записей {folder_for_save}')

    abs_path_record = os.path.join(folder_for_save, new_file_name)

    logger.debug(f'Конвертируем и сохраняем файл {path_file} как {abs_path_record}.')
    sound = AudioSegment.from_wav(path_file)
    sound.export(abs_path_record, format='mp3')

    return new_file_name


def download_record(record: dict) -> None:
    """Функция скачивает указанный файл."""
    logger.debug(f'Скачивание записи {record}.')
    storage_folder = './static/records'
    output_folder = './static/output'

    for root, dirs, files in os.walk(storage_folder):
        for file in files:
            if file.startswith(record['record_uuid']):
                name = str(file).split('&')
                storage_path = os.path.join(storage_folder, file)
                output_path = os.path.join(output_folder, name[-1])
                logger.debug(f'Скачивается файл из папки {storage_path} в папку {output_path}.')
                with open(storage_path, 'rb') as sound:
                    logger.debug(f'Открываем файл {storage_path}.')
                    sound = sound.read()
                with open(output_path, 'wb') as new_file:
                    logger.debug(f'Сохраняем файл в {output_path}.')
                    new_file.write(sound)
                return
        logger.debug('Файл не найден.')


def delete_records(folder: str) -> None:
    for record in os.listdir(folder):
        os.remove(os.path.join(folder, record))
        logger.debug(f'Все записи удалены из каталога хранения.')

