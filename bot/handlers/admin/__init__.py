

from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter

from bot.filters.admins import AdminFilter
from bot.handlers.admin.commands import (
    messages_for_users, received_messages, message_for_user,
    message_received, message_result, info, info_continue, users, get_archive, archive_result
)
from bot.states.main import Messages, InfoUser, Message, ArchiveState


def prepare_router() -> Router:
    router = Router()

    # Admin filtrini qo'shish
    router.message.filter(AdminFilter())

    # /messages -> Holatsiz
    router.message.register(messages_for_users, Command("messages"))
    router.message.register(received_messages, StateFilter(Messages.messages_for_user))

    # /message -> Faqat Message holatlarida ishlaydi
    router.message.register(message_for_user, Command("message"))
    router.message.register(message_received, StateFilter(Message.id_of_user))
    router.message.register(message_result, StateFilter(Message.message_for_user))

    # /user -> Faqat InfoUser holatlarida ishlaydi
    router.message.register(info, Command("user"))
    router.message.register(info_continue, StateFilter(InfoUser.id_of_user))

    # /users -> Holatsiz
    router.message.register(users, Command("users"))

    # /archive -> arxivlar
    router.message.register(get_archive, Command("archive"))
    router.message.register(archive_result, ArchiveState.id_of_user)

    return router