from typing import Any
from django.core.management import BaseCommand, CommandError
from django.core.management.base import CommandParser

from bot.bot import bot


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--bot", type=int)

    def handle(self, *args: Any, **options: Any):
        bot_number = options.get("bot")
        if bot_number == 1:
            bot.remove_webhook()
        elif bot_number == 2:
            bot.remove_webhook()
