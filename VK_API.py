import os
import requests
from dotenv import load_dotenv
from vk_errors import get_error_message
import json
from datetime import datetime

load_dotenv()

class VK_API:
    def __init__(self):
        self.token = os.getenv('VK_ACCESS_TOKEN')

    def vk_error(self, data):

        if data.get('response') and isinstance(data['response'], dict):
            data['response'] = [data['response']]


        if 'error' in data or not data.get('response') or (
                data.get('response') and data['response'][0].get('is_closed')):
            if 'error' in data:
                message = get_error_message(data['error']['error_code'])
            elif not data.get('response'):
                message = get_error_message(113)
            else:
                message = get_error_message(30)
            print(f"❌ {message}")
            return True

        return False

    def check_user_profile(self, user_id):
        response = requests.get(
            "https://api.vk.com/method/users.get",
            params={
                'user_ids': user_id,
                'fields': 'has_photo,deactivated,is_closed,can_access_closed',
                'access_token': self.token,
                'v': '5.199'
            }
        )

        data = response.json()

        if self.vk_error(data):
            return False

        user = data['response'][0]

        if user.get('has_photo', 0) == 0:
            print("📭 У пользователя нет фото в профиле")
            return False
        if user.get('is_closed') and not user.get('can_access_closed'):
            print("❌ Профиль является приватным")
            return False
        photo_response = requests.get(
            "https://api.vk.com/method/photos.get",
            params={
                'owner_id': user_id,
                'album_id': 'profile',
                'count': 1,
                'access_token': self.token,
                'v': '5.199'
            }
        )

        photo_data = photo_response.json()

        if 'error' in photo_data:
            error_code = photo_data['error']['error_code']
            if 'error' in photo_data:
                print("❌ Доступ к фото профиля запрещён")
                return False
        return True

    def get_vk_photos(self, user_id, count=5):
        response = requests.get(
            "https://api.vk.com/method/photos.get",
            params={
                'owner_id': user_id,
                'album_id': 'profile',
                'count': count,
                'extended': 1,
                'photo_sizes': 1,
                'access_token': self.token,
                'v': '5.199'
            }
        )

        data = response.json()

        if self.vk_error(data):
            return False

        elif 'response' in data:
            photos_info = []
            used_names = set()

            for photo in data['response'][0]['items']:
                biggest_size = max(photo['sizes'], key=lambda x: x['width'] * x['height'])
                likes_count = photo.get('likes', {}).get('count', 0)
                upload_date = datetime.fromtimestamp(photo.get('date', 0)).strftime('%Y-%m-%d')

                base_name = f"{likes_count}"

                if base_name in used_names:
                    file_name = f"{likes_count}_{upload_date}.jpg"
                else:
                    file_name = f"{likes_count}.jpg"

                used_names.add(base_name)

                photo_data = {
                    "file_name": file_name,
                    "size": biggest_size['type'],
                    "url": biggest_size['url']
                }
                photos_info.append(photo_data)

            self.save_to_json(photos_info)
            return photos_info

        return []

    def save_to_json(self, photos_info):
        if not photos_info:
            return

        filename = "photos.json"

        json_data = [
            {
                "file_name": photo["file_name"],
                "size": photo["size"]
            }
            for photo in photos_info
        ]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Информация о {len(photos_info)} фото сохранена в {filename}")
