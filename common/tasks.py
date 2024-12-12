import asyncio

from aiogram.enums import parse_mode
from celery import shared_task
from src.settings import API_TOKEN
from .models import TelegramProfile
from utils.choices import Role
import logging
import pytesseract
from PIL import Image
from aiogram import html

async def send_messages(bot_token, admin_chat_id):
    bot = Bot(token=bot_token)
    all_users = TelegramProfile.objects.all().order_by('id')
    count = all_users.count()
    userlar = "ID   |   ISM   |   USERNAME   |   QO‘SHILDI\n"



    for user in all_users:
        local_time = localtime(user.created_at)
        userlar += (
            f"{user.id}   |   {user.first_name or ''}   |   "
            f"@{user.username or '❌'}   |   {local_time.strftime('%d/%m/%Y, %H:%M')}\n"
        )

    userlar += (
        f"\n===============================\n"
        f"Ayni vaqtdagi foydalanuvchilar soni: {count} ta\n"
        f"Matn uzunligi: {len(userlar)} belgidan iborat"
    )
    max_length = 4096

    for i in range(0, len(userlar), max_length):
        chunk = userlar[i:i + max_length]
        await bot.send_message(chat_id=admin_chat_id, text=chunk)

@shared_task
def send_user_list(bot_token, admin_chat_id):
    asyncio.run(send_messages(bot_token, admin_chat_id))



from celery import shared_task
from aiogram import Bot
from django.utils.timezone import localtime
import requests


@shared_task
def send_archive_sync(id, chat_id):
    # Foydalanuvchini bazadan olish
    user = TelegramProfile.objects.filter(id=id).first()
    if not user:
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": "Bunday foydalanuvchi mavjud emas!"}
        response = requests.post(url, json=payload)
        return response.status_code

    # Arxivlarni olish
    archives = Archive.objects.filter(author=user).order_by("created_at")
    data = ""
    for arch in archives:
        local_time = localtime(arch.created_at)
        data += f"{arch.title}   |   {local_time.strftime('%d.%m.%Y %H:%M')}\n-------------->\n"

    # Xabarni tayyorlash
    text = (
        f"ID: {user.id}   |   Name: {user.first_name}   |   Username: @{user.username}\n\n"
        f"{data}"
    )

    max_length = 4096

    # Xabarni yuborish (sinxron)
    for i in range(0, len(text), max_length):
        chunk = text[i:i + max_length]
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": chunk}
        requests.post(url, json=payload)

    # # Xabarni yuborish (sinxron)
    # url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    # payload = {"chat_id": chat_id, "text": text}
    # response = requests.post(url, json=payload)


from translate import to_cyrillic, to_latin
import re
#
#
def contains_cyrillic(text):
    return bool(re.search('[\u0400-\u04FF]', text))


from celery import shared_task
import requests
from .models import Archive

@shared_task
def send_echo_photo(file_id, caption, chat_id, message_id, user_id, first_name, username, text_of_img):

    if caption:
        message_text = caption
    else:
        message_text = text_of_img


    # message_text = caption
    isLatin_orCirill = True
    z = ""

    # Kirill va Latin turlarini tekshirish
    if message_text.isascii() or 'o‘' not in message_text or 'O‘' not in message_text or 'oʻ' not in message_text or 'Oʻ' not in message_text or 'g‘' not in message_text or 'G‘' not in message_text or 'gʻ' not in message_text or 'Gʻ' not in message_text:
        z = to_cyrillic(message_text)  # Kirillga o'girish
        if z == message_text:
            z = to_latin(message_text)
    else:
        if contains_cyrillic(message_text):  # Agar Kirill matni bo'lsa
            z = to_latin(message_text)  # Lotinga o'girish
        else:
            isLatin_orCirill = False

    # Agar matn noto'g'ri bo'lsa, xabar jo'natish
    if not isLatin_orCirill:
        text = "Siz kiritgan matn UTF-8 standartiga mos kelmaydi!\nFaqat text kiriting!\n\n" + caption
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendPhoto"
        payload = {"photo":file_id, "chat_id": chat_id, "caption": text, "reply_to_message_id": message_id}
        requests.post(url, json=payload)

        # Admin uchun xabar
        range = f"ID: {user_id}   |   Name: {first_name}   |   Username: @{username}\nUTF-8 ga mos kelmaydigan rasmli matn kiritdi:⬇️\n\n{caption}"
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendPhoto"
        payload = {"photo":file_id, "chat_id": 6956376313, "caption": range}
        requests.post(url, json=payload)

        message_text = "#rasm[🚫]\n\n" + message_text
        Archive.objects.create(title=message_text, author_id=user_id)
    else:
        # Matnni tarjima qilish va qayta yuborish
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendPhoto"
        payload = {"photo":file_id, "chat_id": chat_id, "caption": html.code(z), "reply_to_message_id": message_id, "parse_mode": "HTML"}
        requests.post(url, json=payload)

        # Admin uchun xabar
        range = f"ID: {user_id}   |   Name: {first_name}   |   Username: @{username}\n🖼Rasmli matn kiritdi:⬇️\n\n{message_text}"
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendPhoto"
        payload = {"photo":file_id, "chat_id": 6956376313, "caption": range}
        requests.post(url, json=payload)
        # Arxivga saqlash
        message_text = "#rasm\n\n" + message_text
        Archive.objects.create(title=message_text, author_id=user_id)







@shared_task
def send_echo_video(file_id, caption, chat_id, message_id, user_id, first_name, username):
    message_text = caption
    isLatin_orCirill = True
    z = ""

    # Kirill va Latin turlarini tekshirish
    if message_text.isascii() or 'o‘' not in message_text or 'O‘' not in message_text or 'oʻ' not in message_text or 'Oʻ' not in message_text or 'g‘' not in message_text or 'G‘' not in message_text or 'gʻ' not in message_text or 'Gʻ' not in message_text:
        z = to_cyrillic(message_text)  # Kirillga o'girish
        if z == message_text:
            z = to_latin(message_text)
    else:
        if contains_cyrillic(message_text):  # Agar Kirill matni bo'lsa
            z = to_latin(message_text)  # Lotinga o'girish
        else:
            isLatin_orCirill = False

    # Agar matn noto'g'ri bo'lsa, xabar jo'natish
    if not isLatin_orCirill:
        text = "Siz kiritgan matn UTF-8 standartiga mos kelmaydi!\nFaqat text kiriting!\n\n" + caption
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendVideo"
        payload = {"video": file_id, "chat_id": chat_id, "caption": text, "reply_to_message_id": message_id}
        requests.post(url, json=payload)

        # Admin uchun xabar
        admin_message = f"ID: {user_id}   |   Name: {first_name}   |   Username: @{username}\nUTF-8 ga mos kelmaydigan video matn kiritdi:⬇️\n\n{caption}"
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendVideo"
        payload = {"video": file_id, "chat_id": 6956376313, "caption": admin_message}
        requests.post(url, json=payload)

        # Arxivga saqlash
        message_text = "#video[🚫]\n\n" + message_text
        Archive.objects.create(title=message_text, author_id=user_id)
    else:
        # Matnni tarjima qilish va qayta yuborish
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendVideo"
        payload = {"video": file_id, "chat_id": chat_id, "caption": html.code(z), "reply_to_message_id": message_id, "parse_mode": "HTML"}
        requests.post(url, json=payload)

        # Admin uchun xabar
        admin_message = f"ID: {user_id}   |   Name: {first_name}   |   Username: @{username}\n📹Video matn kiritdi:⬇️\n\n{message_text}"
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendVideo"
        payload = {"video": file_id, "chat_id": 6956376313, "caption": admin_message}
        requests.post(url, json=payload)

        # Arxivga saqlash
        message_text = "#video\n\n" + message_text
        Archive.objects.create(title=message_text, author_id=user_id)





@shared_task
def send_echo_celery(chat_id, message_text, user_id, first_name, username, message_id):

    isLatin_orCirill = True
    z = ""

    # Kirill va Latin turlarini tekshirish
    if message_text.isascii() or 'o‘' not in message_text or 'O‘' not in message_text or 'oʻ' not in message_text or 'Oʻ' not in message_text or 'g‘' not in message_text or 'G‘' not in message_text or 'gʻ' not in message_text or 'Gʻ' not in message_text:
        z = to_cyrillic(message_text)  # Kirillga o'girish
        if z == message_text:
            z = to_latin(message_text)
    else:
        if contains_cyrillic(message_text):  # Agar Kirill matni bo'lsa
            z = to_latin(message_text)  # Lotinga o'girish
        else:
            isLatin_orCirill = False

    # Agar matn noto'g'ri bo'lsa, xabar jo'natish
    if not isLatin_orCirill:
        text = "Siz kiritgan matn UTF-8 standartiga mos kelmaydi!\nFaqat text kiriting!"
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "reply_to_message_id":message_id}
        requests.post(url, json=payload)

        # Admin uchun xabar
        range = f"ID: {user_id}   |   Name: {first_name}   |   Username: @{username}\nUTF-8 ga mos kelmaydigan matn kiritdi:⬇️\n\n{z}"
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        payload = {"chat_id": 6956376313, "text": range}
        requests.post(url, json=payload)

        # Arxivga saqlash
        message_text = "[🚫]\n\n" + message_text
        Archive.objects.create(title=message_text, author_id=user_id)
    else:
        # Matnni tarjima qilish va qayta yuborish
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": html.code(z), "reply_to_message_id":message_id, "parse_mode": "HTML"}
        requests.post(url, json=payload)

        # Admin uchun xabar
        range = f"ID: {user_id}   |   Name: {first_name}   |   Username: @{username}\nMatn kiritdi:⬇️\n\n{message_text}"
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        payload = {"chat_id": 6956376313, "text": range}
        requests.post(url, json=payload)

        # Arxivga saqlash
        Archive.objects.create(title=message_text, author_id=user_id)














