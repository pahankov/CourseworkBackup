from VK_API import VK_API
from YA_DISK_API import YD_API

vk_api = VK_API()

while True:
    user_id = input("Введите ID пользователя: ")

    if not vk_api.check_user_profile(user_id):
        print("Попробуйте другого пользователя")
        continue

    count_input = input("Введите кол-во фото (по умолчанию 5): ")
    count = int(count_input.strip() or 5)

    photos = vk_api.get_vk_photos(user_id, count)

    if photos:
        yd_api = YD_API()
        yd_api.add_folder()
        yd_api.upload_photos_to_disk(photos)

    break
