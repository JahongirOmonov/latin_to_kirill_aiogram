from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import ContentType
from bot import states
from bot.handlers.users.main import start, sms_for_admin, sms_received, echo, echo_photo, echo_video, \
    sms_for_banned_user, confirm_callback


def prepare_router() -> Router:

    router = Router()
    router.message.filter(F.chat.type == "private")
    # router.message.filter(mytest_handler, Command("test"))  <-- bu test edi. har ehtimolga qarshi qoldirildi.
    # router.callback_query.register(callbaq, F.data.startswith("button")) <-- bu ham.
    router.callback_query.register(confirm_callback, F.data == "confirm_channels")

    #sms for admin
    router.message.register(sms_received, states.main.SmsForAdmin.sms)
    router.message.register(sms_for_admin, Command("sms"))
    router.message.register(sms_for_banned_user, Command("xabar"))

    router.message.register(start, Command("start"))
    # router.message.register(get_video_file_id, F.content_type==ContentType.VIDEO)


    # echo_photo
    router.message.register(echo_photo, F.content_type == ContentType.PHOTO)

    # echo_video
    router.message.register(echo_video, F.content_type == ContentType.VIDEO)

    # echo
    router.message.register(echo)

    return router
