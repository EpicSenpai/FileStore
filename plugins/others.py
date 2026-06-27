from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.pyromod import ListenerTimeout
from datetime import datetime, timedelta
import re
import config

#===============================================================#
# HELPER: PARSE PREMIUM DURATION
#===============================================================#

def parse_premium_duration(time_str: str):
    if time_str.lower() == "lifetime":
        return None, True
    match = re.match(r"^(\d+)(d)$", time_str.lower())
    if not match:
        return None, False
    amount = int(match.group(1))
    return datetime.now() + timedelta(days=amount), False

#===============================================================#
# /addpremium COMMAND
#===============================================================#

@Client.on_message(filters.command("addpremium") & filters.private)
async def add_premium_user_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")
    args = message.text.split()
    if len(args) < 3:
        return await message.reply("<blockquote><b>✦ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ</b></blockquote>\n\n›› <b>ᴜsᴀɢᴇ:</b> <code>/addpremium &lt;user_id&gt; &lt;duration&gt;</code>\n›› <b>ᴇxᴀᴍᴘʟᴇs:</b>\n• <code>/addpremium 12345678 7d</code> (7 Days)\n• <code>/addpremium 12345678 30d</code> (30 Days)\n• <code>/addpremium 12345678 lifetime</code> (Permanent)")
    try:
        target_user = int(args[1])
        duration_str = args[2]
    except ValueError:
        return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ! ᴍᴜsᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ.</b>")
    expiry_time, is_lifetime = parse_premium_duration(duration_str)
    if expiry_time is None and not is_lifetime:
        return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ! ᴜsᴇ <code>1d</code> ᴛᴏ <code>30d</code> ᴏʀ <code>lifetime</code>.</b>")
    total_days = int(duration_str.replace('d', '')) if 'd' in duration_str.lower() else None
    await client.mongodb.add_pro(user_id=target_user, expiry_date=expiry_time, total_days=total_days, is_lifetime=is_lifetime)
    expiry_display = "ʟɪꜰᴇᴛɪᴍᴇ" if is_lifetime else expiry_time.strftime('%Y-%m-%d %H:%M:%S')
    await message.reply(f"<blockquote><b>✓ ᴘʀᴇᴍɪᴜᴍ ɢʀᴀɴᴛᴇᴅ!</b></blockquote>\n\n›› <b>ᴜsᴇʀ:</b> <code>{target_user}</code>\n›› <b>ᴠᴀʟɪᴅɪᴛʏ:</b> <code>{expiry_display}</code>")
    try:
        await client.send_message(chat_id=target_user, text=f"<blockquote><b>✨ ᴀᴀᴘᴋᴀ ᴀᴄᴄᴏᴜɴᴛ ᴘʀᴇᴍɪᴜᴍ ʜᴏ ɢᴀʏᴀ!</b></blockquote>\n\n›› <b>sᴛᴀᴛᴜs:</b> ᴅɪʀᴇᴄᴛ ꜰɪʟᴇ ᴀᴄᴄᴇss (ɴᴏ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ)\n›› <b>ᴇxᴘɪʀʏ:</b> <code>{expiry_display}</code>")
    except Exception:
        pass

#===============================================================#
# /remove_premium COMMAND
#===============================================================#

@Client.on_message(filters.command("remove_premium") & filters.private)
async def remove_premium_user_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("<b>✗ ᴜsᴀɢᴇ:</b> <code>/remove_premium &lt;user_id&gt;</code>")
    try:
        target_user = int(args[1])
    except ValueError:
        return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ!</b>")
    is_pro = await client.mongodb.is_pro(target_user)
    if not is_pro:
        return await message.reply("<b>✗ ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴘʀᴇᴍɪᴜᴍ!</b>")
    await client.mongodb.remove_pro(target_user)
    await message.reply(f"<blockquote><b>✓ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴍᴏᴠᴇᴅ!</b></blockquote>\n\n›› ᴜsᴇʀ <code>{target_user}</code> ᴀʙ ɴᴏʀᴍᴀʟ ᴜsᴇʀ ʜᴀɪ.")
    try:
        await client.send_message(chat_id=target_user, text="<b>⚠️ ᴀᴀᴘᴋᴀ ᴘʀᴇᴍɪᴜᴍ ʜᴀᴛᴀ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ. ᴀʙ ᴀᴀᴘᴋᴏ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴋᴀʀɴɪ ʜᴏɢɪ.</b>")
    except Exception:
        pass

#===============================================================#
# /premium_users COMMAND
#===============================================================#

@Client.on_message(filters.command("premium_users") & filters.private)
async def list_premium_users_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")
    await render_premium_list_page(client, message, page=1, is_callback=False)

async def render_premium_list_page(client, message_or_query, page: int, is_callback: bool):
    current_time = datetime.now()
    cursor = client.mongodb.premium_users.find()
    all_pros = [doc async for doc in cursor]
    total_users = len(all_pros)
    items_per_page = 10
    total_pages = max((total_users + items_per_page - 1) // items_per_page, 1)
    start_idx = (page - 1) * items_per_page
    page_items = all_pros[start_idx:start_idx + items_per_page]
    msg = f"<blockquote>✦ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀs (ᴘᴀɢᴇ {page}/{total_pages})</blockquote>\n\n"
    if not page_items:
        msg += "<i>ᴋᴏɪ ʙʜɪ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ ɴᴀʜɪ ʜᴀɪ!</i>\n"
    else:
        for idx, doc in enumerate(page_items, start=start_idx + 1):
            u_id = doc['_id']
            is_lifetime = doc.get('is_lifetime', False)
            expiry_date = doc.get('expiry_date')
            added_at = doc.get('added_at', current_time)
            total_days = doc.get('total_days', 0)
            elapsed = current_time - added_at
            elapsed_str = f"{elapsed.days}d ʙɪᴛ ɢᴀʏᴇ" if elapsed.days > 0 else "ᴀᴀᴊ ᴀᴅᴅ ʜᴜᴀ"
            if is_lifetime:
                time_status = "♾️ ʟɪꜰᴇᴛɪᴍᴇ"
            elif expiry_date:
                remaining = expiry_date - current_time
                if remaining.total_seconds() <= 0:
                    time_status = "❌ ᴇxᴘɪʀᴇᴅ"
                else:
                    time_status = f"⏳ {remaining.days}d {remaining.seconds // 3600}h ʙᴀᴋɪ"
            else:
                time_status = "❓ ᴜɴᴋɴᴏᴡɴ"
            total_days_str = f" | ᴋᴜʟ: {total_days}d" if total_days else ""
            msg += f"<b>{idx}.</b> <a href='tg://user?id={u_id}'>ᴜsᴇʀ</a> (<code>{u_id}</code>)\n   {time_status}{total_days_str} | <i>{elapsed_str}</i>\n\n"
    buttons = []
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("‹ ᴘʀᴇᴠ", callback_data=f"propage_{page-1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("ɴᴇxᴛ ›", callback_data=f"propage_{page+1}"))
    if nav_row:
        buttons.append(nav_row)
    if page > 1:
        buttons.append([InlineKeyboardButton("‹ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="close")])
    else:
        buttons.append([InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data="close")])
    markup = InlineKeyboardMarkup(buttons)
    if is_callback:
        await message_or_query.message.edit_text(text=msg, reply_markup=markup)
    else:
        await message_or_query.reply(text=msg, reply_markup=markup)

@Client.on_callback_query(filters.regex(r"^propage_(\d+)$"))
async def process_pro_pagination_callback(client: Client, query: CallbackQuery):
    await query.answer()
    target_page = int(query.data.split("_")[1])
    await render_premium_list_page(client, query, page=target_page, is_callback=True)

#===============================================================#
# /addcredit COMMAND
#===============================================================#

@Client.on_message(filters.command("addcredit") & filters.private)
async def add_credits_to_user_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")
    args = message.text.split()
    if len(args) < 3:
        return await message.reply("<b>✗ ᴜsᴀɢᴇ:</b> <code>/addcredit &lt;user_id&gt; &lt;amount&gt;</code>")
    try:
        target_user = int(args[1])
        amount = int(args[2])
    except ValueError:
        return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ! ᴅᴏɴᴏ ɴᴜᴍʙᴇʀ ʜᴏɴᴇ ᴄʜᴀʜɪʏᴇ.</b>")
    user_data = await client.mongodb.user_data.find_one({"_id": target_user})
    if not user_data:
        return await message.reply("<b>✗ ʏᴇ ᴜsᴇʀ ʙᴏᴛ ᴍᴇɪɴ ʀᴇɢɪsᴛᴇʀᴇᴅ ɴᴀʜɪ ʜᴀɪ!</b>")
    current_credits = user_data.get("credits", 0)
    new_credits = current_credits + amount
    await client.mongodb.user_data.update_one({"_id": target_user}, {"$set": {"credits": new_credits}}, upsert=True)
    await message.reply(f"<blockquote><b>✓ ᴄʀᴇᴅɪᴛs ᴀᴅᴅ ʜᴏ ɢᴀʏᴇ!</b></blockquote>\n\n›› ᴜsᴇʀ <code>{target_user}</code>\n›› ᴘᴜʀᴀɴᴇ: <code>{current_credits}</code> → ɴᴀʏᴇ: <code>{new_credits}</code>")
    try:
        reward_amount = await client.mongodb.get_set_credits_amount()
        await client.send_message(chat_id=target_user, text=f"<blockquote><b>✨ ᴀᴀᴘᴋᴇ ᴀᴄᴄᴏᴜɴᴛ ᴍᴇɪɴ ᴄʀᴇᴅɪᴛs ᴀᴀ ɢᴀʏᴇ!</b></blockquote>\n\n›› <b>ᴊᴏᴅᴇ ɢᴀʏᴇ:</b> <code>{amount} ᴄʀᴇᴅɪᴛs</code>\n›› <b>ᴀʙ ʙᴀᴋɪ:</b> <code>{new_credits} ᴄʀᴇᴅɪᴛs</code>")
    except Exception:
        pass

#===============================================================#
# /setcredit COMMAND
#===============================================================#

@Client.on_message(filters.command("setcredit") & filters.private)
async def set_global_credits_config_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")
    args = message.text.split()
    if len(args) < 2:
        current_val = await client.mongodb.get_set_credits_amount()
        return await message.reply(f"<blockquote><b>✦ ɢʟᴏʙᴀʟ ᴄʀᴇᴅɪᴛs ᴄᴏɴꜰɪɢ</b></blockquote>\n\n›› <b>ᴀʙʜɪ ᴋᴇ ᴄʀᴇᴅɪᴛs ᴘʀᴇ ʙʏᴘᴀss:</b> <code>{current_val}</code>\n›› <b>ᴄʜᴀɴɢᴇ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ:</b> <code>/setcredit &lt;amount&gt;</code>")
    try:
        new_amount = int(args[1])
    except ValueError:
        return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ! ɴᴜᴍʙᴇʀ ᴅᴀʟᴏ.</b>")
    await client.mongodb.set_global_credits_amount(new_amount)
    await message.reply(f"<blockquote><b>✓ ᴄʀᴇᴅɪᴛs ᴀᴘᴅᴀᴛᴇ ʜᴏ ɢᴀʏᴇ!</b></blockquote>\n\n›› <b>ɴᴀʏᴀ ᴀᴍᴏᴜɴᴛ:</b> <code>{new_amount} ᴄʀᴇᴅɪᴛs</code> ᴘʀᴇ ʙʏᴘᴀss")

#===============================================================#
# /commands COMMAND
#===============================================================#

@Client.on_message(filters.command("commands") & filters.private)
async def admin_manual_commands_directory_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")
    manual = """<blockquote><b>⛩️ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs ᴅɪʀᴇᴄᴛᴏʀʏ</b></blockquote>

<b>⚙️ sᴇᴛᴛɪɴɢs:</b>
• <code>/settings</code> › ʙᴏᴛ ᴋɪ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ ᴋʜᴏʟᴏ

<b>👑 ᴘʀᴇᴍɪᴜᴍ ᴏᴘᴇʀᴀᴛɪᴏɴs:</b>
• <code>/addpremium &lt;id&gt; &lt;1d-30d|lifetime&gt;</code> › ᴜsᴇʀ ᴋᴏ ᴘʀᴇᴍɪᴜᴍ ᴅᴏ (ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ɴᴀʜɪ ʜᴏɢɪ)
• <code>/remove_premium &lt;id&gt;</code> › ᴘʀᴇᴍɪᴜᴍ ʜᴀᴛᴀᴏ, ᴠᴀᴘᴀs ɴᴏʀᴍᴀʟ ʙɴᴇɢᴀ
• <code>/premium_users</code> › ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ᴋɪ ʟɪsᴛ ᴅᴇᴋʜᴏ

<b>💰 ᴄʀᴇᴅɪᴛs:</b>
• <code>/addcredit &lt;id&gt; &lt;amount&gt;</code> › ᴋɪsɪ ʙʜɪ ᴜsᴇʀ ᴋᴏ ᴄʀᴇᴅɪᴛs ᴅᴏ
• <code>/setcredit &lt;amount&gt;</code> › ʜᴀʀ ʙʏᴘᴀss ᴘᴀʀ ᴍɪʟɴᴇ ᴡᴀʟᴇ ᴄʀᴇᴅɪᴛs sᴇᴛ ᴋᴀʀᴏ

<b>📡 ʙʀᴏᴀᴅᴄᴀsᴛ:</b>
• <code>/broadcast</code> › ɪɴsᴛᴀɴᴛ ʙʀᴏᴀᴅᴄᴀsᴛ (ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ)
• <code>/broadcast del 10m</code> › ʙʀᴏᴀᴅᴄᴀsᴛ + 10 ᴍɪɴᴛ ᴍᴇɪɴ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ
• <code>/broadcast schedule 2h</code> › 2 ɢʜᴀɴᴛᴇ ʙᴀᴀᴅ ʙʜᴇᴊᴏ
• <code>/broadcast schedule 1h del 30m</code> › sᴄʜᴇᴅᴜʟᴇ + ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ
• <code>/pbroadcast</code> › ʙʀᴏᴀᴅᴄᴀsᴛ + ᴘɪɴ ᴋᴀʀᴏ

<b>📊 sᴛᴀᴛs:</b>
• <code>/stats</code> › CPU, RAM, ɴᴇᴛᴡᴏʀᴋ sᴛᴀᴛs
• <code>/users</code> › ᴋᴜʟ ᴜsᴇʀs ᴋɪᴛɴᴇ ʜᴀɪɴ

<b>🛡️ ʙᴀɴ/ᴜɴʙᴀɴ:</b>
• <code>/ban &lt;id&gt;</code> › ᴜsᴇʀ ʙᴀɴ ᴋᴀʀᴏ
• <code>/unban &lt;id&gt;</code> › ᴜsᴇʀ ᴜɴʙᴀɴ ᴋᴀʀᴏ

<b>🗄️ ᴅᴀᴛᴀʙᴀsᴇ:</b>
• <code>/dbroadcast &lt;seconds&gt;</code> › ʙʀᴏᴀᴅᴄᴀsᴛ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ sᴇᴛ ᴋᴀʀᴏ
• <code>/commands</code> › ʏᴇ ʟɪsᴛ ᴅᴇᴋʜᴏ"""
    await message.reply(manual)

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
        return await message.reply(f"<b>{c} ᴜsᴇʀs ʙᴀɴ ᴋᴀʀ ᴅɪʏᴇ!</b>")
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
        return await message.reply(f"<b>{c} ᴜsᴇʀs ᴜɴʙᴀɴ ᴋᴀʀ ᴅɪʏᴇ!</b>")
    except Exception as e:
        return await message.reply(f"<b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")

#===============================================================#
# DB CHANNELS COMMANDS
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
        
