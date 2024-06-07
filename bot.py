from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pymongo import MongoClient
from aiohttp import web
from plugins import web_server
import sys
from datetime import datetime
from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT, MONGO_URI

# Import from the new files
from database import add_admin, remove_admin, set_force_sub, get_force_sub, is_admin, get_all_users, save_broadcast_message
import start
import channel_post
import help_func

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

        # Connect to MongoDB
        self.client = MongoClient(MONGO_URI)
        self.db = self.client["telegram_bot"]
        self.users_collection = self.db["users"]
        self.config_collection = self.db["config"]

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # Load force subscription channel from the database
        self.force_sub_channel = get_force_sub() or FORCE_SUB_CHANNEL

        if self.force_sub_channel:
            try:
                link = (await self.get_chat(self.force_sub_channel)).invite_link
                if not link:
                    await self.export_chat_invite_link(self.force_sub_channel)
                    link = (await self.get_chat(self.force_sub_channel)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(f"Please Double check the FORCE_SUB_CHANNEL value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {self.force_sub_channel}")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/CodeXBotzSupport for support")
                sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/CodeXBotzSupport for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/CodeXBotz")
        self.LOGGER(__name__).info(f""" \n\n       
░█████╗░░█████╗░██████╗░███████╗██╗░░██╗██████╗░░█████╗░████████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗╚══██╔══╝╚════██║
██║░░╚═╝██║░░██║██║░░██║█████╗░░░╚███╔╝░██████╦╝██║░░██║░░░██║░░░░░███╔═╝
██║░░██╗██║░░██║██║░░██║██╔══╝░░░██╔██╗░██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
╚█████╔╝╚█████╔╝██████╔╝███████╗██╔╝╚██╗██████╦╝╚█████╔╝░░░██║░░░███████╗
░╚════╝░░╚════╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
                                          """)
        self.username = usr_bot_me.username
        # web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

        # Add handlers for commands
        self.add_handler(filters.command("addadmin")(self.add_admin))
        self.add_handler(filters.command("removeadmin")(self.remove_admin))
        self.add_handler(filters.command("setforcesub")(self.set_force_sub))
        self.add_handler(filters.command("currentforcesub")(self.current_force_sub))
        self.add_handler(filters.command("users")(self.list_users))
        self.add_handler(filters.command("broadcast")(self.broadcast_message))

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    async def add_admin(self, client, message):
        if not await is_admin(message.from_user.id):
            await message.reply_text("You don't have permission to use this command.")
            return

        try:
            new_admin_id = int(message.text.split(" ", 1)[1])
            add_admin(new_admin_id)
            await message.reply_text(f"User {new_admin_id} added as admin.")
        except Exception as e:
            await message.reply_text(f"Error: {e}")

    async def remove_admin(self, client, message):
        if not await is_admin(message.from_user.id):
            await message.reply_text("You don't have permission to use this command.")
            return

        try:
            admin_id = int(message.text.split(" ", 1)[1])
            remove_admin(admin_id)
            await message.reply_text(f"User {admin_id} removed from admin role.")
        except Exception as e:
            await message.reply_text(f"Error: {e}")

    async def set_force_sub(self, client, message):
        if not await is_admin(message.from_user.id):
            await message.reply_text("You don't have permission to use this command.")
            return

        try:
            channel_id = message.text.split(" ", 1)[1]
            set_force_sub(channel_id)
            self.force_sub_channel = channel_id
            await message.reply_text(f"Force subscription set to channel ID: {channel_id}")
        except Exception as e:
            await message.reply_text(f"Error: {e}")

    async def current_force_sub(self, client, message):
        if not await is_admin(message.from_user.id):
            await message.reply_text("You don't have permission to use this command.")
            return

        channel_id = self.force_sub_channel
        if channel_id:
            await message.reply_text(f"Current force subscription channel ID: {channel_id}")
        else:
            await message.reply_text("No force subscription channel is set.")

    async def list_users(self, client, message):
        if not await is_admin(message.from_user.id):
            await message.reply_text("You don't have permission to use this command.")
            return

        users = get_all_users()
        if users:
            user_list = "\n".join([str(user["user_id"]) for user in users])
            await message.reply_text(f"Registered Users:\n{user_list}")
        else:
            await message.reply_text("No users found.")

    async def broadcast_message(self, client, message):
        if not await is_admin(message.from_user.id):
            await message.reply_text("You don't have permission to use this command.")
            return

        try:
            broadcast_text = message.text.split(" ", 1)[1]
            users = get_all_users()
            for user in users:
                try:
                    await client.send_message(user["user_id"], broadcast_text)
                except Exception as e:
                    continue
            await message.reply_text("Broadcast message sent to all users.")
        except Exception as e:
            await message.reply_text

