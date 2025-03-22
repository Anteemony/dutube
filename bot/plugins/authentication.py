import logging

from pyrogram import filters as Filters
from pyrogram.types import Message

from ..youtube import GoogleAuth
from ..config import Config
from ..translations import Messages as tr
from ..utubebot import UtubeBot


log = logging.getLogger(__name__)


@UtubeBot.on_message(
    Filters.private
    & Filters.incoming
    & Filters.command("authorise")
    & Filters.user(Config.AUTH_USERS)
)
async def _auth(c: UtubeBot, m: Message) -> None:
    if len(m.command) == 1:
        await m.reply_text(tr.NO_AUTH_CODE_MSG, True)
        return

    code = m.command[1]

    try:
        auth = GoogleAuth(Config.CLIENT_ID, Config.CLIENT_SECRET)

        auth.Auth(code)

        auth.SaveCredentialsFile(Config.CRED_FILE)

        msg = await m.reply_text(tr.AUTH_SUCCESS_MSG, True)

        with open(Config.CRED_FILE, "r") as f:
            cred_data = f.read()

        log.debug(f"Authentication success, auth data saved to {Config.CRED_FILE}")

        msg2 = await msg.reply_text(cred_data, parse_mode=None)
        await msg2.reply_text(
            "This is your authorisation data! Save this for later use. Reply /save_auth_data to the authorisation "
            "data to re authorise later. (helpful if you use Heroku)",
            True,
        )

    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(tr.AUTH_FAILED_MSG.format(e), True)


@UtubeBot.on_message(
    Filters.private
    & Filters.incoming
    & Filters.command("save_auth_data")
    & Filters.reply
    & Filters.user(Config.AUTH_USERS)
)
async def _save_auth_data(c: UtubeBot, m: Message) -> None:
    auth_data = m.reply_to_message.text
    try:
        with open(Config.CRED_FILE, "w") as f:
            f.write(auth_data)

        auth = GoogleAuth(Config.CLIENT_ID, Config.CLIENT_SECRET)
        auth.LoadCredentialsFile(Config.CRED_FILE)
        auth.authorize()

        await m.reply_text(tr.AUTH_DATA_SAVE_SUCCESS, True)
        log.debug(f"Authentication success, auth data saved to {Config.CRED_FILE}")
    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(tr.AUTH_FAILED_MSG.format(e), True)


@UtubeBot.on_message(
    Filters.private
    & Filters.incoming
    & Filters.command("add_user")
    & Filters.user(Config.BOT_OWNER)  # Only bot owner can add users
)
async def _add_user(c: UtubeBot, m: Message) -> None:
    if len(m.command) != 2:
        await m.reply_text("Please provide a user ID.\nUsage: `/add_user 123456789`", True)
        return

    try:
        user_id = int(m.command[1])

        # Check if user is already authorized
        if user_id in Config.AUTH_USERS:
            await m.reply_text("This user is already authorized!", True)
            return

        # Add user to AUTH_USERS list
        Config.AUTH_USERS.append(user_id)

        await m.reply_text(f"Successfully added user {user_id} to authorized users list.", True)
        log.info(f"New user {user_id} added to AUTH_USERS by {m.from_user.id}")

    except ValueError:
        await m.reply_text("Please provide a valid user ID (numbers only).", True)
    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(f"An error occurred: {str(e)}", True)


@UtubeBot.on_message(
    Filters.private
    & Filters.incoming
    & Filters.command("list_users")
    & Filters.user(Config.BOT_OWNER)
)
async def _list_users(c: UtubeBot, m: Message) -> None:
    try:
        auth_users = Config.AUTH_USERS
        if not auth_users:
            await m.reply_text("No authorized users found.", True)
            return

        users_text = "Authorized Users:\n\n"
        for user_id in auth_users:
            try:
                user = await c.get_users(user_id)
                name = user.first_name
                if user.last_name:
                    name += f" {user.last_name}"
                username = f"@{user.username}" if user.username else "No username"
                users_text += f"• ID: `{user_id}`\n  Name: {name}\n  Username: {username}\n\n"
            except Exception as e:
                users_text += f"• ID: `{user_id}` (Unable to fetch user info)\n\n"

        await m.reply_text(users_text, True)

    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(f"An error occurred: {str(e)}", True)


@UtubeBot.on_message(
    Filters.private
    & Filters.incoming
    & Filters.command("remove_user")
    & Filters.user(Config.BOT_OWNER)
)
async def _remove_user(c: UtubeBot, m: Message) -> None:
    if len(m.command) != 2:
        await m.reply_text("Please provide a user ID.\nUsage: `/remove_user 123456789`", True)
        return

    try:
        user_id = int(m.command[1])

        # Don't allow removing the bot owner
        if user_id == Config.BOT_OWNER:
            await m.reply_text("Cannot remove the bot owner!", True)
            return

        # Check if user exists in AUTH_USERS
        if user_id not in Config.AUTH_USERS:
            await m.reply_text("This user is not in the authorized users list!", True)
            return

        # Remove user from AUTH_USERS list
        Config.AUTH_USERS.remove(user_id)

        await m.reply_text(f"Successfully removed user {user_id} from authorized users list.", True)
        log.info(f"User {user_id} removed from AUTH_USERS by {m.from_user.id}")

    except ValueError:
        await m.reply_text("Please provide a valid user ID (numbers only).", True)
    except Exception as e:
        log.error(e, exc_info=True)
        await m.reply_text(f"An error occurred: {str(e)}", True)

