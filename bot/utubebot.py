from pyrogram import Client

from .config import Config


class UtubeBot(Client):
    def __init__(self):
        super().__init__(
            name=Config.NAME,
            bot_token=Config.BOT_TOKEN,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins=dict(root="bot.plugins"),
            workers=6,
        )
        self.DOWNLOAD_WORKERS = 6
        self.counter = 0
        self.download_controller = {}
        self.user_uploads = {}

    async def get_user_upload_status(self, user_id: int) -> str:
        """Get user's upload status and remaining uploads."""
        is_owner = user_id == Config.BOT_OWNER

        if is_owner:
            return "You are the bot owner - you have unlimited uploads! 🎉"

        uploads_used = self.user_uploads.get(user_id, 0)
        uploads_limit = 2  # Hardcoded limit
        uploads_remaining = uploads_limit - uploads_used

        status = f"Your upload status:\n\n" \
                 f"• Used: {uploads_used}/{uploads_limit} uploads\n" \
                 f"• Remaining: {uploads_remaining} uploads"

        return status
