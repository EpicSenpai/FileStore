from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from datetime import datetime, timedelta
import re

#===============================================================#
# HELPER: PARSE TIME STRING (e.g. 10m, 2h, 1d)
#===============================================================#

def parse_time_string(time_str: str) -> int:
    """Convert time string like 10m, 2h, 1d to seconds. Returns 0 if invalid."""
    match = re.match(r"^(\d+)([smhd])$", time_str.strip().lower())
    if not match:
        return 0
    amount, unit = int(match.group(1)), match.group(2)
    multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    return amount * multipliers[unit]

#===============================================================#

@Client.on_message(filters.command('users'))
async def user_count(client, message):
    if not message.from_user.id in client.admins:
        return await client.send_message(message.from_user.id, client.reply_text)
    total_users = await client.mongodb.full_userbase()
    await message.reply(f"**{len(total_users)} Users are using this bot currently!**")

#===============================================================#
# BROADCAST COMMAND — UPGRADED WITH SCHEDULE + AUTO DELETE
#===============================================================#

@Client.on_message(filters.private & filters.command('broadcast'))
async def send_text(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return

    if not message.reply_to_message:
        return await message.reply(
            "<blockquote><b>📡 ʙʀᴏᴀᴅᴄᴀsᴛ ᴜsᴀɢᴇ:</b></blockquote>\n\n"
            "Reply to a message with:\n"
            "• <code>/broadcast</code> — instant broadcast\n"
            "• <code>/broadcast del 10m</code> — broadcast + auto delete after 10 mins\n"
            "• <code>/broadcast schedule 2h</code> — schedule broadcast after 2h\n"
            "• <code>/broadcast schedule 1h del 30m</code> — schedule after 1h + delete after 30m\n\n"
            "<b>Time formats:</b> <code>30s, 10m, 2h, 1d</code>"
        )

    args = message.text.split()[1:]  # Args after /broadcast
    schedule_after = 0
    delete_after = 0

    # Parse arguments
    i = 0
    while i < len(args):
        if args[i].lower() == "schedule" and i + 1 < len(args):
            schedule_after = parse_time_string(args[i + 1])
            i += 2
        elif args[i].lower() == "del" and i + 1 < len(args):
            delete_after = parse_time_string(args[i + 1])
            i += 2
        else:
            i += 1

    broadcast_msg = message.reply_to_message

    # If scheduled, wait first
    if schedule_after > 0:
        schedule_time = datetime.now() + timedelta(seconds=schedule_after)
        wait_msg = await message.reply(
            f"<blockquote><b>⏰ ʙʀᴏᴀᴅᴄᴀsᴛ sᴄʜᴇᴅᴜʟᴇᴅ!</b></blockquote>\n\n"
            f"›› ᴡɪʟʟ sᴇɴᴅ ᴀᴛ: <code>{schedule_time.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
            f"›› ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ: <code>{'after ' + str(delete_after) + 's' if delete_after else 'disabled'}</code>"
        )
        await asyncio.sleep(schedule_after)

    # Do the broadcast
    query = await client.mongodb.full_userbase()
    total = 0
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0
    sent_message_ids = []  # For auto-delete tracking

    pls_wait = await message.reply(
        f"<blockquote><i>📡 Broadcasting to {len(query)} users...</i></blockquote>"
    )

    for chat_id in query:
        try:
            sent = await broadcast_msg.copy(chat_id)
            successful += 1
            if delete_after > 0:
                sent_message_ids.append((chat_id, sent.id))
        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                sent = await broadcast_msg.copy(chat_id)
                successful += 1
                if delete_after > 0:
                    sent_message_ids.append((chat_id, sent.id))
            except Exception:
                unsuccessful += 1
        except UserIsBlocked:
            await client.mongodb.del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await client.mongodb.del_user(chat_id)
            deleted += 1
        except Exception as e:
            print(f"Broadcast failed for {chat_id}: {e}")
            unsuccessful += 1
        total += 1

    auto_del_note = f"\n›› <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ:</b> <code>after {delete_after}s</code>" if delete_after else ""

    status = (
        f"<blockquote><b><u>✓ Broadcast Completed</u></b></blockquote>\n"
        f"›› <b>ᴛᴏᴛᴀʟ:</b> <code>{total}</code>\n"
        f"›› <b>sᴜᴄᴄᴇssꜰᴜʟ:</b> <code>{successful}</code>\n"
        f"›› <b>ʙʟᴏᴄᴋᴇᴅ:</b> <code>{blocked}</code>\n"
        f"›› <b>ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄs:</b> <code>{deleted}</code>\n"
        f"›› <b>ꜰᴀɪʟᴇᴅ:</b> <code>{unsuccessful}</code>"
        f"{auto_del_note}"
    )
    await pls_wait.edit(status)

    # Auto delete logic
    if delete_after > 0 and sent_message_ids:
        await asyncio.sleep(delete_after)
        del_success = 0
        for chat_id, msg_id in sent_message_ids:
            try:
                await client.delete_messages(chat_id, msg_id)
                del_success += 1
            except Exception:
                pass
        try:
            await pls_wait.edit(
                status + f"\n\n<blockquote><b>🗑️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇᴅ {del_success}/{len(sent_message_ids)} ᴍᴇssᴀɢᴇs!</b></blockquote>"
            )
        except Exception:
            pass

#===============================================================#
# PBROADCAST — PIN BROADCAST
#===============================================================#

@Client.on_message(filters.private & filters.command('pbroadcast'))
async def pin_bdcst_text(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return

    if not message.reply_to_message:
        return await message.reply("Reply to a message with /pbroadcast to pin broadcast it.")

    query = await client.mongodb.full_userbase()
    broadcast_msg = message.reply_to_message
    total = 0
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0

    pls_wait = await message.reply(
        f"<blockquote><i>📌 Pin Broadcasting to {len(query)} users...</i></blockquote>"
    )

    for chat_id in query:
        try:
            sent_msg = await broadcast_msg.copy(chat_id)
            await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id, both_sides=True)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                sent_msg = await broadcast_msg.copy(chat_id)
                await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id)
                successful += 1
            except Exception:
                unsuccessful += 1
        except UserIsBlocked:
            await client.mongodb.del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await client.mongodb.del_user(chat_id)
            deleted += 1
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
            unsuccessful += 1
        total += 1

    status = (
        f"<blockquote><b><u>✓ Pin Broadcast Completed</u></b></blockquote>\n"
        f"›› <b>ᴛᴏᴛᴀʟ:</b> <code>{total}</code>\n"
        f"›› <b>sᴜᴄᴄᴇssꜰᴜʟ:</b> <code>{successful}</code>\n"
        f"›› <b>ʙʟᴏᴄᴋᴇᴅ:</b> <code>{blocked}</code>\n"
        f"›› <b>ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄs:</b> <code>{deleted}</code>\n"
        f"›› <b>ꜰᴀɪʟᴇᴅ:</b> <code>{unsuccessful}</code>"
    )
    await pls_wait.edit(status)
        
