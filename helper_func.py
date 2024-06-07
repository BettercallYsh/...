import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import FORCE_SUB_CHANNEL, ADMINS
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait

async def is_subscribed(_, client, update):
    if not FORCE_SUB_CHANNEL:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=user_id)
    except UserNotParticipant:
        return False

    if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return False
    else:
        return True

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii").rstrip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.rstrip("=")
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    return string

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages < len(message_ids):
        try:
            msgs = await client.get_messages(chat_id=client.db_channel.id, message_ids=message_ids[total_messages:total_messages+200])
            messages.extend(msgs)
            total_messages += len(msgs)
        except FloodWait as e:
            await asyncio.sleep(e.x)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
    elif message.text:
        matches = re.match(r"https://t.me/(?:c/)?([^/]+)/(\d+)", message.text)
        if matches:
            channel_id, msg_id = matches.groups()
            if channel_id.isdigit() and int(channel_id) == -100 * client.db_channel.id:
                return int(msg_id)
            elif channel_id == client.db_channel.username:
                return int(msg_id)
    return 0

def get_readable_time(seconds: int) -> str:
    time_suffix_list = ["s", "m", "h", "days"]
    time_list = []
    for divisor, suffix in zip([60] * 2 + [24], time_suffix_list):
        seconds, remainder = divmod(seconds, divisor)
        if seconds or time_list:
            time_list.append(f"{seconds}{suffix}")
        if not seconds:
            break
    return ":".join(reversed(time_list))

subscribed = filters.create(is_subscribed)
