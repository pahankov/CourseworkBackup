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
        return True

    def get_vk_photos(self, user_id):
        count = input("Введите кол-во фото: ")

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
            photos = []
            for photo in data['response'][0]['items']:
                best_size = self.get_best_size(photo['sizes'])
                likes_count = photo.get('likes', {}).get('count', 0)
                upload_date = datetime.fromtimestamp(photo.get('date', 0)).strftime('%Y-%m-%d %H:%M:%S')
                photo_info = {
                    'url': best_size['url'],
                    'likes': likes_count,
                    'type': best_size['type'],
                    'date': upload_date
                }
                photos.append(photo_info)
            self.save_to_json(photos, user_id)
            return photos

        return []

    def get_best_size(self, sizes):
        priority_sizes = {size['type']: size for size in sizes}

        for preferred in ['w', 'z', 'y', 'x', 'm', 's']:
            if preferred in priority_sizes:
                return priority_sizes[preferred]

        return max(sizes, key=lambda x: x['width'])

    def save_to_json(self, photos, user_id):
        """Сохраняет информацию о фото в JSON файл"""
        if not photos:
            return

        filename = "photos.json"

        data_to_save = {
            'user_id': user_id,
            'photos': photos
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)

        print(f"✅ Информация о {len(photos)} фото сохранена в {filename}")

vk_api = VK_API()

while True:
    user_id = input("Введите ID пользователя: ")

    if vk_api.check_user_profile(user_id):
        photos = vk_api.get_vk_photos(user_id)

        for photo in photos:
            print(f"Лайков: {photo['likes']}, URL: {photo['url'][:50]}...")
        break
    else:
        print("Попробуйте другого пользователя")
