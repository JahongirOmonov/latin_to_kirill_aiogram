from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, InlineKeyboardBuilder

async def get_subscribed_channels_markup(channel_list: list):
    markup = InlineKeyboardBuilder()
    for channel in channel_list:
        markup.add(
            InlineKeyboardButton(
                text=f"🔉 {channel.title}",
                url=channel.url
            )
        )
    markup.add(InlineKeyboardButton(text="Tasdiqlash ✅", callback_data="confirm_channels"))
    return markup.adjust(*(1,)).as_markup()

# < test InlineKeyboardBuilder
# async def test_inline_markup():
#     builder = InlineKeyboardBuilder()
#     builder2 = InlineKeyboardBuilder()
#
#     for i in range(10):
#         builder.add(InlineKeyboardButton(text=f"B {i+1}", callback_data=f"button_{i}"))
#
#     for q in "absdefghij":
#         builder2.add(InlineKeyboardButton(text=f"B {q}", callback_data=f"button_{q}"))
#     builder.adjust(*(5,))
#     builder2.adjust(*(2,))
#     builder.attach(builder2)
#     return builder.as_markup()