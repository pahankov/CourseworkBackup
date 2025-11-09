import os
from pprint import pprint
import requests
from dotenv import load_dotenv
from vk_errors import get_error_message

load_dotenv()

class VK_API:
    def __init__(self):
        self.token = os.getenv('VK_ACCESS_TOKEN')

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

        if 'error' in data or not data.get('response'):
            if 'error' in data:
                code = data['error']['error_code']
                message = get_error_message(code)
            else:
                message = get_error_message(113)
            print(f"❌ {message}")
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
                'access_token': self.token,
                'v': '5.199'
            }
        )

        data = response.json()
        pprint(data)

        if 'error' in data or not data.get('response'):
            if 'error' in data:
                code = data['error']['error_code']
                message = get_error_message(code)
            else:
                message = get_error_message(113)
            print(f"❌ {message}")
            return False

        elif 'response' in data:
            photos = []
            for photo in data['response']['items']:
                biggest_size = max(photo['sizes'], key=lambda x: x['width'])
                likes_count = photo.get('likes', {}).get('count', 0)
                photos.append({
                    'url': biggest_size['url'],
                    'likes': likes_count
                })
            return photos

        return []


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

