from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
import config

#===============================================================#
# BAN / UNBAN COMMANDS
#===============================================================#

@Client.on_message(filters.command('ban'))
async def ban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c += 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id, True)
            else:
                await client.mongodb.ban_user(user_id)
        return await message.reply(f"<b>✓ {c} ᴜsᴇʀ{'s' if c > 1 else ''} ʙᴀɴɴᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>")
    except Exception as e:
        return await message.reply(f"<b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")

@Client.on_message(filters.command('unban'))
async def unban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c += 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id)
            else:
                await client.mongodb.unban_user(user_id)
        return await message.reply(f"<b>✓ {c} ᴜsᴇʀ{'s' if c > 1 else ''} ᴜɴʙᴀɴɴᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>")
    except Exception as e:
        return await message.reply(f"<b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")

#===============================================================#
# /db COMMAND
#===============================================================#

@Client.on_message(filters.command('db') & filters.private)
async def db_channels_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    db_channels = getattr(client, 'db_channels', {})
    primary_db = getattr(client, 'primary_db_channel', client.db)
    if db_channels:
        ch_list = []
        for ch_id_str, ch_data in db_channels.items():
            name = ch_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
            primary_tag = " ✓ ᴘʀɪᴍᴀʀʏ" if ch_data.get('is_primary', False) else ""
            ch_list.append(f"• <code>{name}</code> (<code>{ch_id_str}</code>){primary_tag}")
        channels_display = "\n".join(ch_list)
    else:
        channels_display = f"<i>ᴅᴇꜰᴀᴜʟᴛ ᴅʙ: <code>{primary_db}</code></i>"
    msg = f"<blockquote><b>🗄️ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs</b></blockquote>\n\n›› <b>ᴘʀɪᴍᴀʀʏ:</b> <code>{primary_db}</code>\n›› <b>ᴛᴏᴛᴀʟ:</b> <code>{len(db_channels)}</code>\n\n{channels_display}"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('➕ ᴀᴅᴅ', 'add_db_ch'), InlineKeyboardButton('➖ ʀᴇᴍᴏᴠᴇ', 'remove_db_ch')],
        [InlineKeyboardButton('⭐ sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db')]
    ])
    await message.reply(msg, reply_markup=reply_markup)
    
