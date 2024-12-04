# yourapp/management/commands/migrate_user_data.py

from django.core.management.base import BaseCommand
from django.db import connections
from common.models import TelegramProfile

class Command(BaseCommand):
    help = 'Migrates data from SQLite user table to TelegramProfile model'

    def handle(self, *args, **kwargs):
        # SQLite ma'lumotlar bazasiga ulanish
        sqlite_connection = connections['default']  # Django settings'da SQLite ulanishini sozlang

        with sqlite_connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user")  # "user" jadvalidan barcha ma'lumotlarni olish
            rows = cursor.fetchall()  # Barcha ma'lumotlarni olish

        # Olingan ma'lumotlarni TelegramProfile modeliga qo'shish
        for row in rows:
            chat_id = row[0]  # `user` jadvalidagi chat_id
            username = row[1]  # `user` jadvalidagi username
            first_name = row[2]  # `user` jadvalidagi first_name
            last_name = row[3]  # `user` jadvalidagi last_name
            language = row[4]  # `user` jadvalidagi language

            # TelegramProfile modeliga yangi yozuv qo'shish
            profile = TelegramProfile(
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language=language,
                role="USER"  # yoki kerakli rolni belgilash
            )
            profile.save()  # Yangi profilni saqlash

        self.stdout.write(self.style.SUCCESS('Data migrated successfully!'))
