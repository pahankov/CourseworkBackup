import os
import requests
from dotenv import load_dotenv

load_dotenv()


class VK_API:
    def __init__(self):
        self.token = os.getenv('VK_ACCESS_TOKEN')

    def get_vk_photos(self, user_id, count):
        response = requests.get(
            "https://api.vk.com/method/photos.get",
            params={
                'owner_id': user_id,  # Чей профиль
                'album_id': 'profile',  # Откуда фото
                'count': count,  # Сколько штук
                'access_token': self.token,
                'v': '5.199'
            }
        )

        data = response.json()  # получаем ОДИН объект

        if 'error' in data:  # проверяем есть ли поле 'error'
            # Это ОШИБКА
            code = data['error']['error_code']  # код ошибки
            message = data['error']['error_msg']  # текст ошибки
            print(f"Код ошибки: {code}, Сообщение: {message}")
            return []  # ← ВАЖНО: возвращаем пустой список!

        elif 'response' in data:
            # Это УСПЕХ
            photos = data['response']['items']  # список фото
            count = data['response']['count']  # количество фото
        photos = []
        for photo in data['response']['items']:
            biggest_size = max(photo['sizes'], key=lambda x: x['width'])
            likes_count = 0
            if 'likes' in photo and 'count' in photo['likes']:
                likes_count = photo['likes']['count']
            photos.append({
                'url': biggest_size['url'],
                'likes': photo['likes']['count']
            })
        return photos



vk_api = VK_API()
user_id = input("Введите ID пользователя: ")
count = input("Введите кол-во фото: ")
photos = vk_api.get_vk_photos(user_id, count)

for photo in photos:
    print(f"Лайков: {photo['likes']}, URL: {photo['url'][:50]}...")



