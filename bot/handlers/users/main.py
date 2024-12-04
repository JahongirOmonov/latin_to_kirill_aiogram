from aiogram import types, Bot
from datetime import date, datetime

# from common.tasks import send_echo_celery
from utils.choices import Role
from aiogram.fsm.context import FSMContext
from bot.states.main import SmsForAdmin
from bot.utils.orm import get_user
from common.models import TelegramProfile
import common.tasks


async def start(message: types.Message, bot: Bot):
    user = await get_user(message.chat)
    current_date = date.today()

    current_time = datetime.now().strftime("%H:%M:%S")
    text = (f"Assalomu alaykum, {user.first_name}\n"
            f"O'zgartirmoqchi bo'lgan matningizni kiriting!")
    mention = f"<a href='tg://user?id={user.chat_id}'>{user.first_name}</a>"
    notification = (f"Diqqat!!!   ID: {user.id}  \n\n"
                    f"{mention} ro'yhatdan o'tdi✅ \n\n"
                    f"Sana: {current_date}  |  {current_time}")
    file_id="BAACAgIAAxkBAAOOZ0jMg14gDmGTJE79dN40zes2BNMAAnheAALgIUlKkj-4CcsokSE2BA"
    caption = "📹Botning barcha imkoniyatlarini bilish uchun videoni ko'ring..."
    await message.answer(text, reply_to_message_id=message.message_id)
    await message.answer_video(video=file_id, caption=caption, width=1920, height=1080)
    admin_users = TelegramProfile.objects.filter(role=Role.ADMIN)
    for admin in admin_users:
        try:
            if admin.chat_id:
                await bot.send_message(chat_id=admin.chat_id, text=notification, parse_mode="HTML")
        except:
            pass
    # await bot.send_message(6956376313, notification)

# async def get_video_file_id(message: types.Message, bot: Bot):
#     await message.answer(message.video.file_id)


#/sms(for admin)
async def sms_for_admin(message: types.Message, bot: Bot, state: FSMContext):
    await message.answer("Adminga xabar yuborish uchun matnni kiriting: ")
    await state.set_state(SmsForAdmin.sms)

#/sms(for admin)
async def sms_received(message: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(sms=message.text)
    data = await state.get_data()
    user = TelegramProfile.objects.filter(chat_id=message.from_user.id).first()
    admin_users = TelegramProfile.objects.filter(role=Role.ADMIN)

    # Adminlarga xabar yuborish
    for admin in admin_users:
        try:
            # Har bir admin foydalanuvchining chat_id sini olish va unga xabar yuborish
            if admin.chat_id:
                text = (f"ID: {user.id}\n"
                        f"Nick: <a href='tg://user?id={user.chat_id}'>{user.first_name}</a>\n"
                        f"Username: @{user.username}\n\n"
                        f"===message===\n"
                        f"{data.get('sms')}")
                # Adminga xabar yuborish
                await bot.send_message(chat_id=admin.chat_id, text=text, parse_mode="HTML")
        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")
    await message.answer("Xabar muvaffaqiyatli yuborildi✅. Iltimos, admin javobini kuting...")

async def echo_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    caption = message.caption or ""
    user = await get_user(message.chat)
    common.tasks.send_echo_photo.delay(file_id=file_id,
                                       caption=caption,
                                       chat_id=message.chat.id,
                                       message_id=message.message_id,
                                       user_id=user.id,
                                       first_name=message.from_user.first_name,
                                       username=message.from_user.username
                                       )


async def echo_video(message: types.Message):
    file_id = message.video.file_id
    caption = message.caption or ""
    user = await get_user(message.chat)
    common.tasks.send_echo_video.delay(file_id=file_id,
                                       caption=caption,
                                       chat_id=message.chat.id,
                                       message_id=message.message_id,
                                       user_id=user.id,
                                       first_name=message.from_user.first_name,
                                       username=message.from_user.username
                                       )



async def echo(message: types.Message):
    user = await get_user(message.chat)
    common.tasks.send_echo_celery.delay(
        chat_id=message.chat.id,
        message_text=message.text,
        user_id=user.id,
        first_name=user.first_name,
        username=user.username,
        message_id=message.message_id
    )
