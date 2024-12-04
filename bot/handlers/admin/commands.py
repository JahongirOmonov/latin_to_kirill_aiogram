from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.states.main import Messages, Message, InfoUser, ArchiveState
from common.models import TelegramProfile
from aiogram import Bot
import asyncio
import common.tasks
from django.utils.timezone import localtime
import requests
from src.settings import API_TOKEN


#/messages
async def messages_for_users(message: Message, state: FSMContext):
    await message.answer("Barcha foydalanuvchilar uchun xabarni kiriting: ")
    await state.set_state(Messages.messages_for_user)

#/messages
async def received_messages(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(msg_of_admin=message.text)
    data = await state.get_data()
    users = TelegramProfile.objects.all().order_by('id')

    undelivered_users = "Xabar yetib bormagan foydalanuvchilar:\n\n"
    admins_message = (f"👮‍♂️<b>Admin:</b>\n\n"
                      f"<i>{data.get('msg_of_admin')}</i>")
    for user in users:
        try:
            if user.chat_id:
                await bot.send_message(chat_id=user.chat_id, text=admins_message, parse_mode="HTML")
                await asyncio.sleep(1)
        except:
            # mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
            mytext = f"ID: {user.id}, NAME: {user.first_name}, username: @{user.username}\n"
            undelivered_users += mytext
    max_length = 4096
    for i in range(0, len(undelivered_users), max_length):
        chunk = undelivered_users[i:i + max_length]
        # await bot.send_message(chat_id=6956376313, text=chunk)
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        payload = {"chat_id": 6956376313, "text": chunk}
        requests.post(url, json=payload)
    await state.clear()
    # await bot.send_message(chat_id=6956376313, text=undelivered_users)

    await message.answer("Xabar foydalanuvchilarga muvaffaqiyatli yuborildi✅")
    await state.clear()


#/message
async def message_for_user(message: Message, state: FSMContext):
    await message.answer("Foydalanuvchi ID raqamini kiriting: ")
    await state.set_state(Message.id_of_user)

#/message
async def message_received(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(id_of_user=message.text)
    await message.answer("Xabarni kiriting: ")
    await state.set_state(Message.message_for_user)

#/message
async def message_result(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(msg_for_user=message.text)
    data = await state.get_data()
    user = TelegramProfile.objects.filter(id=data.get('id_of_user')).first()
    admins_message = (f"👮‍♂️<b>Admin:</b>\n\n"
                      f"<i>{data.get('msg_for_user')}</i>")
    secret = (f"🔒<b>Secret:</b>\n\n"
              f"Admin: <a href='tg://user?id={message.chat.id}'>{message.from_user.first_name}</a>\n"
              f"ID: {user.id}, <a href='tg://user?id={user.chat_id}'>{user.first_name}</a> ga xabar yozdi:\n\n"
              f"<i>{data.get('msg_for_user')}</i>")
    try:
        await bot.send_message(chat_id=user.chat_id, text=admins_message, parse_mode="HTML")
        if message.chat.id != 6956376313:
            await bot.send_message(chat_id=6956376313, text=secret, parse_mode="HTML")
        await message.answer("Xabar muvaffaqiyatli yuborildi✅")
    except:
        await message.answer("Xabar yetib bormadi❌")
    await state.clear()


#/user
async def info(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Foydalanuvchi ID raqamini kiriting: ")
    await state.set_state(InfoUser.id_of_user)

#/user
async def get_archive(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Foydalanuvchi ID raqamini kiriting: ")
    await state.set_state(ArchiveState.id_of_user)



#/users
async def users(message: Message, bot: Bot):
    common.tasks.send_user_list.delay(bot.token, admin_chat_id=message.chat.id)
    await message.answer("Foydalanuvchilar ro'yxatini yuborildi✅")

#/users
async def info_continue(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(id_of_user=message.text)
    data = await state.get_data()
    user = TelegramProfile.objects.filter(id=data.get('id_of_user')).first()
    if user:
        local_time = localtime(user.created_at)
        if user.first_name and user.chat_id:
            mention = f'<a href="tg://user?id={user.chat_id}">{user.first_name}</a>'
        else:
            mention = "Ismi mavjud emas"
        text = (f"Foydalanuvchi haqida ma`lumot ⬇️\n\n"
                f"ID: {user.id}\n"
                f"Nick: {mention}\n"
                f"Username: @{user.username}\n"
                f"Chat_id: {user.chat_id}\n"
                f"Role: {user.role}\n"
                f"Joined: {local_time.strftime('%d.%m.%Y %H:%M')}\n"
                f"Havola: tg://user?id={user.chat_id}\n")
        try:
            profile_photos =await bot.get_user_profile_photos(user_id=user.chat_id, limit=1)
            if profile_photos.total_count > 0:
                photo = profile_photos.photos[0][-1].file_id
                await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=text, parse_mode=ParseMode.HTML)
            else:
                await message.answer(text, parse_mode="HTML")
        except:
            await message.answer(text, parse_mode="HTML")

    else:
        await message.answer("Bunday foydalanuvchi mavjud emas❌")
    await state.clear()


#/archive
async def archive_result(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(id_of_user=message.text)
    data = await state.get_data()
    common.tasks.send_archive_sync.delay(id=data.get('id_of_user'), chat_id=message.chat.id)
    await state.clear()
    await message.answer("Arxivlar yuborilmoqda. Iltimos, kuting...")








