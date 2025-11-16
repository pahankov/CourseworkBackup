import os
import requests
from ya_errors import get_error_message_ya
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()


class YD_API:

    FOLDER_NAME = "VK_PHOTO"

    def __init__(self):
        self.token = os.getenv('YD_ACCESS_TOKEN')

    def add_folder(self):
        folder_name = self.FOLDER_NAME
        headers = {'Authorization': f'OAuth {self.token}'}

        response = requests.put(
            "https://cloud-api.yandex.net/v1/disk/resources",
            params={"path": folder_name},
            headers=headers
        )

        message = get_error_message_ya(response.status_code)
        print(f"✅ {message}")
        return True

    def upload_photos_to_disk(self, photos_data):
        folder_name = self.FOLDER_NAME
        headers = {'Authorization': f'OAuth {self.token}'}

        print(f"📤 Начинаем загрузку {len(photos_data)} фото...")

        for photo in tqdm(photos_data, desc="Загрузка"):
            file_name = photo['file_name']
            vk_photo_url = photo['url']

            response = requests.post(
                "https://cloud-api.yandex.net/v1/disk/resources/upload",
                params={
                    'path': f"{folder_name}/{file_name}",
                    'url': vk_photo_url
                },
                headers=headers
            )

            message = get_error_message_ya(response.status_code)
            print(f"✅ {file_name} - {message}")
