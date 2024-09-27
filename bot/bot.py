import time, re
from django.conf import settings
from telebot import TeleBot
from .models import *
from .diagrams import *
from django.db.models import Sum, F, Value
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ChatJoinRequest,
)

bot = TeleBot(settings.BOT_TOKEN, parse_mode="HTML", threaded=False)

msg_spent = "I Spent 😥"
msg_earnt = "I Earnt 😊"
msg_debt = "I am in Debt 😓"
msg_owe = "Someone owes me 🙄"

"""
start - start the bot
spends - show my spendings
earnings - show my earnings
debts - show my debts
owes - show my owes

"""


def get_keyboard(**kwargs):
    keyboard = ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True,
        one_time_keyboard=kwargs.get("one_time_keyboard") is not None,
    )

    if not kwargs:
        keyboard.add(
            KeyboardButton(msg_spent),
            KeyboardButton(msg_earnt),
            KeyboardButton(msg_debt),
        ).add(msg_owe)
    else:
        ls = []
        for key, value in kwargs.items():
            ls.append(KeyboardButton(" ".join(key.split("_")), **value))
        keyboard.add(*ls)
    return keyboard


def get_common_amount():
    mark = ReplyKeyboardMarkup(
        row_width=3, resize_keyboard=True, one_time_keyboard=True, is_persistent=False
    )

    mark.add(
        KeyboardButton("100"),
        KeyboardButton("200"),
        KeyboardButton("300"),
        KeyboardButton("400"),
        KeyboardButton("500"),
        KeyboardButton("1000"),
        KeyboardButton("1500"),
        KeyboardButton("2000"),
        KeyboardButton("2500"),
        KeyboardButton("5000"),
        KeyboardButton("10000"),
        KeyboardButton("15000"),
    )

    return mark


def delete_message(message):
    return bot.delete_message(message.chat.id, message.id)


def get_user(message, func, *args):
    try:

        from_user = message.from_user

        contact = User.objects.get(username=from_user.id)

        return contact
    except:
        mark = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        mark.add(KeyboardButton("Share Contact", request_contact=True))
        bot.register_next_step_handler(message, contact_handler, func)
        msg = """
Share your contact
        """
        bot.send_message(message.chat.id, msg, reply_markup=mark)
        return get_user(message, *args)


def get_amount(message, func):
    delete_message(message)
    if message.text == msg_spent:
        return spnt(message)
    if message.text == msg_earnt:
        return ernt(message)
    if message.text == msg_owe:
        return ow(message)
    if message.text == msg_debt:
        return debt(message)

    if message.text == "Custom":
        bot.register_next_step_handler(message, get_amount)
        bot.send_message(message.chat.id, "Okay type the amount")

    if not message.text.isdigit():
        bot.register_next_step_handler(message, get_amount)
        bot.send_message(message.chat.id, "Write only numbers")
    func(message, amount=message.text)


def get_text(message, func, *args):
    delete_message(message)
    if message.text == msg_spent:
        return spnt(message)
    if message.text == msg_earnt:
        return ernt(message)
    if message.text == msg_owe:
        return ow(message)
    if message.text == msg_debt:
        return debt(message)

    func(message, text=message.text, *args)


@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message, start)

    # if not user:

    #     return bot.send_message(
    #         message.chat.id, "Share Contact to Get started", reply_markup=mark
    #     )

    bot.send_message(
        message.chat.id, f"Hello {user.first_name}👋", reply_markup=get_keyboard()
    )


@bot.message_handler(func=lambda msg: msg.text == msg_earnt)
def ernt(message, amount=None, text=None):
    user = get_user(message, ernt)
    if not amount:
        bot.register_next_step_handler(message, get_amount, ernt)
        return bot.send_message(
            message.chat.id,
            "Yay 🥳 how much did you earn?",
            reply_markup=get_common_amount(),
        )
    if not text:
        bot.register_next_step_handler(message, get_text, ernt, amount)
        return bot.send_message(message.chat.id, "Okay specify the source??")

    Income.objects.create(reason=text, amount=amount, user=user)
    total = user.incomes.all().aggregate(total=Sum("amount"))["total"]

    msg = f"""
💰 **Earnings Summary**

🤑 **Earned Amount**: `{amount}ETB`

💼 **Total Amount**: `{total}ETB`
"""

    bot.send_message(
        message.chat.id, msg, parse_mode="MARKDOWN", reply_markup=get_keyboard()
    )


@bot.message_handler(func=lambda msg: msg.text == msg_spent)
def spnt(message, amount=None, text=None):
    user = get_user(message, spnt)
    if not amount:
        bot.register_next_step_handler(message, get_amount, spnt)
        return bot.send_message(
            message.chat.id,
            "Hmm...🤔 How much did you spend?",
            reply_markup=get_common_amount(),
        )
    if not text:
        bot.register_next_step_handler(message, get_text, spnt, amount)
        return bot.send_message(message.chat.id, "Okay specify the reason??")

    inc = Income.objects.create(user=user, amount=int("-" + amount), reason=text)
    total = user.incomes.all().aggregate(total=Sum("amount"))["total"]

    msg = f"""
💰 **Spent Summary**

🤑 **Spent Amount**: `{amount}ETB`

💼 **Total Amount**: `{total}ETB`
"""

    bot.send_message(
        message.chat.id, msg, parse_mode="MARKDOWN", reply_markup=get_keyboard()
    )


@bot.message_handler(func=lambda msg: msg.text == msg_owe)
def ow(message, amount=None, text=None):
    user = get_user(message, ow, amount, text)
    if not amount:
        bot.register_next_step_handler(message, get_amount, ow)
        return bot.send_message(
            message.chat.id,
            "Okay go on...how much they take from you?",
            reply_markup=get_common_amount(),
        )
    if not text:
        bot.register_next_step_handler(message, get_text, ow, amount)
        return bot.send_message(message.chat.id, "Who??")

    Owe.objects.create(
        user=user,
        name=text,
        amount=amount,
    )
    total = Owe.objects.filter(amount__gte=0).aggregate(total=Sum("amount"))["total"]
    msg = f"""
💰 You have {total} ETB from others
    """
    bot.send_message(
        message.chat.id, msg, reply_markup=get_keyboard(), parse_mode="MARKDOWN"
    )


@bot.message_handler(func=lambda msg: msg.text == msg_debt)
def debt(message, amount=None, text=None):
    user = get_user(message, debt, amount, text)
    if not amount:
        bot.register_next_step_handler(message, get_amount, debt)
        return bot.send_message(
            message.chat.id,
            "Seriously...how much debt??",
            reply_markup=get_common_amount(),
        )

    if not text:
        bot.register_next_step_handler(message, get_text, debt, amount)
        return bot.send_message(message.chat.id, "To who??")

    Owe.objects.create(
        user=user,
        name=text,
        amount=amount * -1,
    )

    total = Owe.objects.filter(amount__lte=0).aggregate(total=Sum("amount"))["total"]

    msg = f"""
💰 You are {total} ETB in debt
    """
    bot.send_message(
        message.chat.id, msg, reply_markup=get_keyboard(), parse_mode="MARKDOWN"
    )


@bot.message_handler(commands=["spends"])
def spens(message):
    user = get_user(message, spens)

    inc = (
        user.incomes.filter(amount__lt=0).values("reason").annotate(total=Sum("amount"))
    )

    img = get_pie(
        labels=[data["reason"] for data in inc],
        sizes=[data["total"] * -1 for data in inc],
    )
    total = sum([data["total"] for data in inc])

    msg = f"""
😓 Total spent amount {total*-1}
    """

    bot.send_photo(message.chat.id, photo=img, caption=msg, parse_mode="MARKDOWN")


@bot.message_handler(commands=["earnings"])
def ernings(message):
    user = get_user(message, ernings)

    inc = (
        user.incomes.filter(amount__gt=0).values("reason").annotate(total=Sum("amount"))
    )

    img = get_pie(
        labels=[data["reason"] for data in inc],
        sizes=[data["total"] for data in inc],
    )
    total = sum([data["total"] for data in inc])

    msg = f"""
😓 Total Earning {total} ETB
    """

    bot.send_photo(message.chat.id, photo=img, caption=msg, parse_mode="MARKDOWN")


# @bot.message_handler(func=lambda msg: msg.text == msg_owe)
# def someone_owe(message, amount=None, text=None):
#     if amount:
#         bot.register_next_step_handler(
#             message,
#             someone_owe,
#         )
#         return bot.send_message(
#             message.chat.id, "Specify the amount?", reply_markup=get_common_amount()
#         )
#     if text:
#         bot.register_next_step_handler(message, someone_owe, amount)
#         return bot.send_message(message.chat.id, "Reason??")
#     user = get_user(message)

#     Owe.objects.create(
#         user=user,
#         reason=text,
#         amount=amount,
#     )
#     total = Owe.objects.filter(amount__gte=0).aggregate(total=Sum("amount"))["total"]
#     msg = f"""
# 💰 You have {total} ETB from others
#     """
#     bot.send_message(
#         message.chat.id, msg, reply_markup=get_keyboard(), parse_mode="MARKDOWN"
#     )


# @bot.message_handler(func=lambda msg: msg.text == msg_debt)
# def owe_someone(message, amount=None, text=None):
#     if amount:
#         bot.register_next_step_handler(
#             message,
#             someone_owe,
#         )
#         return bot.send_message(
#             message.chat.id, "Specify the amount?", reply_markup=get_common_amount()
#         )
#     if text:
#         bot.register_next_step_handler(message, someone_owe, amount)
#         return bot.send_message(message.chat.id, "Reason??")
#     user = get_user(message)

#     Owe.objects.create(
#         user=user,
#         reason=text,
#         amount=amount * -1,
#     )

#     total = Owe.objects.filter(amount__lte=0).aggregate(total=Sum("amount"))["total"]

#     msg = f"""
# 💰 You are {total} ETB in debt
#     """
#     bot.send_message(
#         message.chat.id, msg, reply_markup=get_keyboard(), parse_mode="MARKDOWN"
# )


@bot.message_handler(commands=["debts"])
def mydebts(message):
    total = Owe.objects.filter(amount__lte=0).aggregate(total=Sum("amount"))["total"]
    tt = "\n".join(
        [f"\t- {ow.name}: `{ow.amount}`" for ow in Owe.objects.filter(amount__gte=0)]
    )
    msg = f"""
Debt Summary
{tt}
____________________________________
💰 You are {total} ETB in debt
    """
    bot.send_message(
        message.chat.id, msg, reply_markup=get_keyboard(), parse_mode="MARKDOWN"
    )


@bot.message_handler(commands=["owes"])
def my_owes(message):

    total = Owe.objects.filter(amount__gte=0).aggregate(total=Sum("amount"))["total"]
    tt = "\n".join(
        [f"\t- {ow.name}: `{ow.amount}`" for ow in Owe.objects.filter(amount__gte=0)]
    )
    msg = f"""
Owe Summary
{tt}
____________________________________
💰 You have {total} ETB from others
    """
    bot.send_message(
        message.chat.id, msg, reply_markup=get_keyboard(), parse_mode="MARKDOWN"
    )


######################## Telegram Contact Submit ########################################
@bot.message_handler(content_types=["contact"])
def contact_handler(message, func=None):
    con = message.contact
    data = {
        "username": message.from_user.id,
        "chat_id": message.chat.id,
        "phone_number": con.phone_number.replace("+", ""),
    }
    print(con)

    contact, iscreated = User.objects.get_or_create(**data)
    contact.first_name = con.first_name
    contact.last_name = con.last_name
    contact.save()

    if iscreated:
        msg1 = bot.send_message(
            message.chat.id, "Contact Received✅", reply_markup=get_keyboard()
        )
    else:
        msg1 = bot.send_message(
            message.chat.id, "Contact Updated Succeslly✅", reply_markup=get_keyboard()
        )

    time.sleep(0.5)

    bot.delete_message(message.chat.id, msg1.id)

    if func:

        func(message)


######################## Telegram Contact Submit ########################################
