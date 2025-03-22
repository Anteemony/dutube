from pyrogram import filters as Filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..config import Config
from ..translations import Messages as tr


@UtubeBot.on_message(
    Filters.private
    & Filters.incoming
    & Filters.command("check")
    & Filters.user(Config.AUTH_USERS)
)
async def check_uploads(c: UtubeBot, m: Message):
    """Handler for /check command to show remaining uploads."""
    try:
        # Get user's upload status
        status = await c.get_user_upload_status(m.from_user.id)

        # Send status message
        await m.reply_text(
            text=status,
            quote=True
        )
    except Exception as e:
        await m.reply_text(
            "Sorry, couldn't check your upload status. Please try again later.",
            quote=True
        )