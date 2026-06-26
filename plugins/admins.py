from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import time
import psutil
import shutil
import re
from datetime import datetime, timedelta
import config

# Helper conversion for pro-time inputs string formats
def parse_premium_duration(time_str: str):
    if time_str.lower() == "lifetime":
        return None, True
    match = re.match(r"^(\d+)([d])$", time_str.lower())
    if not match:
        return None, False
    amount, unit = match.groups()
    amount = int(amount)
    if unit == 'd':
        return datetime.now() + timedelta(days=amount), False
    return None, False

#===============================================================#

async def admins(client, query):
    if not (query.from_user.id == client.owner):
        return await query.answer('This can only be used by owner.')
    msg = f"""<blockquote>**Admin Settings:**</blockquote>
**Admin User IDs:** {", ".join(f"`{a}`" for a in client.admins)}

__Use the appropriate button below to add or remove an admin based on your needs!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴀᴅᴍɪɴ', 'add_admin'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ', 'rm_admin')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_message(filters.command("addpremium") & filters.private)
async def add_premium_user_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    args = message.text.split()
    if len(args) < 3:
        return await message.reply("<blockquote><b>✦ ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ sᴇᴛᴜᴘ ᴍᴏᴅᴜʟᴇ</b></blockquote>\n\n›› <b>ᴜsᴀɢᴇ:</b> `/addpremium <user_id> <duration>`\n›› <b>ᴇxᴀᴍᴘʟᴇs:</b>\n• `/addpremium 12345678 7d` (7 Days)\n• `/addpremium 12345678 lifetime` (Permanent)")
    
    try:
        target_user = int(args[1])
        duration_str = args[2]
    except ValueError:
        return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ_ɪᴅ ꜰᴏʀᴍᴀᴛ. ᴍᴜsᴛ ʙᴇ ᴀɴ ɪɴᴛᴇɢᴇʀ.</b>")
        
    expiry_time, is_lifetime = parse_premium_duration(duration_str)
    if expiry_time is None and not is_lifetime:
        return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ꜰᴏʀᴍᴀᴛ! ᴜsᴇ <code>1d</code> ᴛᴏ <code>30d</code> ᴏʀ <code>lifetime</code>.</b>")
        
    total_days = int(duration_str.replace('d','')) if 'd' in duration_str.lower() else None
    
    await client.mongodb.add_pro(user_id=target_user, expiry_date=expiry_time, total_days=total_days, is_lifetime=is_lifetime)
    
    expiry_display = "ʟɪꜰᴇᴛɪᴍᴇ ꜰᴀᴄɪʟɪᴛʏ" if is_lifetime else expiry_time.strftime('%Y-%m-%d %H:%M:%S')
    await message.reply(f"<blockquote><b>✓ ᴘʀᴇᴍɪᴜᴍ sᴜᴄᴄᴇssꜰᴜʟʟʏ ɢʀᴀɴᴛᴇᴅ!</b></blockquote>\n\n›› <b>ᴜsᴇʀ:</b> <code>{target_user}</code>\n›› <b>ᴠᴀʟɪᴅɪᴛʏ:</b> <code>{expiry_display}</code>")
    
    try:
        await client.send_message(chat_id=target_user, text=f"<blockquote><b>✨ ʜᴇʏ sᴇɴᴘᴀɪ! ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘɢʀᴀᴅᴇᴅ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ!</b></blockquote>\n\n›› <b>sᴛᴀᴛᴜs:</b> ɴᴏ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴡᴀʟʟ (ᴅɪʀᴇᴄᴛ ꜰɪʟᴇ ᴀᴄᴄᴇss)\n›› <b>ᴇxᴘɪʀʏ:</b> <code>{expiry_display}</code>")
    except Exception:
        pass

#===============================================================#

@Client.on_message(filters.command("remove_premium") & filters.private)
async def remove_premium_user_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("<b>✗ ᴜsᴀɢᴇ:</b> `/remove_premium <user_id>`")
        
    try:
        target_user = int(args[1])
    except ValueError:
        return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ_ɪᴅ ꜰᴏʀᴍᴀᴛ.</b>")
        
    is_pro = await client.mongodb.is_pro(target_user)
    if not is_pro:
        return await message.reply("<b>✗ ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇs ɴᴏᴛ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ sᴜʙsᴄʀɪᴘᴛɪᴏɴ.</b>")
        
    await client.mongodb.remove_pro(target_user)
    await message.reply(f"<blockquote><b>✓ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b></blockquote>\n\n›› ᴜsᴇʀ <code>{target_user}</code> ʜᴀs ʙᴇᴇɴ sᴡɪᴛᴄʜᴇᴅ ʙᴀᴄᴋ ᴛᴏ ꜰʀᴇᴇ ʟɪɴᴋ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ.")
    try:
        await client.send_message(chat_id=target_user, text="<b>⚠️ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ ʙʏ ᴀᴅᴍɪɴ. ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ sʜᴏʀᴛʟɪɴᴋs ɴᴏᴡ.</b>")
    except Exception:
        pass

#===============================================================#

@Client.on_message(filters.command("premium_users") & filters.private)
async def list_premium_users_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    await render_premium_list_page(client, message, page=1, is_callback=False)

async def render_premium_list_page(client, message_or_query, page: int, is_callback: bool):
    current_time = datetime.now()
    cursor = client.mongodb.premium_users.find()
    all_pros = [doc async for doc in cursor]
    
    total_users = len(all_pros)
    items_per_page = 10
    total_pages = (total_users + items_per_page - 1) // items_per_page
    if total_pages == 0:
        total_pages = 1
        
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_items = all_pros[start_idx:end_idx]
    
    msg = f"<blockquote>✦ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀs ᴀɴᴀʟʏᴛɪᴄs (ᴘᴀɢᴇ {page}/{total_pages})</blockquote>\n\n"
    
    if not page_items:
        msg += "_ɴᴏ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ʀᴇɢɪsᴛᴇʀᴇᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ_\n"
    else:
        for idx, doc in enumerate(page_items, start=start_idx + 1):
            u_id = doc['_id']
            is_lifetime = doc.get('is_lifetime', False)
            expiry_date = doc.get('expiry_date')
            added_at = doc.get('added_at', current_time)
            
            # Math calculation for elapsed and structural times tracking
            elapsed = current_time - added_at
            elapsed_str = f"{elapsed.days}ᴅ ᴘᴀssᴇᴅ" if elapsed.days > 0 else "ᴀᴅᴅᴇᴅ ᴛᴏᴅᴀʏ"
            
            if is_lifetime:
                time_status = "• ʟɪꜰᴇᴛɪᴍᴇ ᴀᴄᴄᴇss"
            elif expiry_date:
                remaining = expiry_date - current_time
                if remaining.total_seconds() <= 0:
                    time_status = "• ᴇxᴘɪʀᴇᴅ"
                else:
                    time_status = f"• {remaining.days}ᴅ {remaining.seconds // 3600}ʜ ʀᴇᴍᴀɪɴɪɴɢ"
            else:
                time_status = "• ᴜɴᴋɴᴏᴡɴ ʟᴀᴛᴇɴᴄʏ"
                
            msg += f"<b>{idx}.</b> <a href='tg://user?id={u_id}'>ᴜsᴇʀ ɴᴏᴅᴇ</a> (<code>{u_id}</code>)\n   {time_status} | <i>{elapsed_str}</i>\n\n"
            
    buttons = []
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("‹ ᴘʀᴇᴠ", callback_data=f"propage_{page-1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("ɴᴇxᴛ ›", callback_data=f"propage_{page+1}"))
        
    if nav_row:
        buttons.append(nav_row)
        
    # Toggle button layout dynamically based on current routing position context
    if page > 1:
        buttons.append([InlineKeyboardButton("‹ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", callback_data="settings")])
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

@Client.on_message(filters.command("addcredit") & filters.private)
async def add_credits_to_user_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    args = message.text.split()
    if len(args) < 3:
        return await message.reply("<b>✗ ᴜsᴀɢᴇ:</b> `/addcredit <user_id> <amount>`")
        
    try:
        target_user = int(args[1])
        amount = int(args[2])
    except ValueError:
        return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ ᴘᴀʀᴀᴍᴇᴛᴇʀs. ᴍᴜsᴛ ʙᴇ ɪɴᴛᴇɢᴇʀs.</b>")
        
    user_data = await client.mongodb.user_data.find_one({"_id": target_user})
    if not user_data:
        return await message.reply("<b>✗ ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ registered ɪɴ ʙᴏᴛ's core data table.</b>")
        
    current_credits = user_data.get("credits", 0)
    new_credits = current_credits + amount
    
    await client.mongodb.user_data.update_one({"_id": target_user}, {"$set": {"credits": new_credits}}, upsert=True)
    await message.reply(f"<blockquote><b>✓ ᴄʀᴇᴅɪᴛs sᴜᴄᴄᴇssfᴜʟʟʏ ɪɴᴊᴇᴄᴛᴇᴅ!</b></blockquote>\n\n›› ᴜsᴇʀ <code>{target_user}</code> balance up: <code>{current_credits}</code> -> <code>{new_credits}</code>")
    try:
        await client.send_message(chat_id=target_user, text=f"<blockquote><b>✨ ʜᴇʏ sᴇɴᴘᴀɪ! ᴀᴅᴍɪɴ ʜᴀs ᴄʀᴇᴅɪᴛᴇᴅ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ!</b></blockquote>\n\n›› <b>ᴀᴅᴅᴇᴅ:</b> <code>{amount} ᴄʀᴇᴅɪᴛs</code>\n›› <b>ᴄᴜʀʀᴇɴᴛ ʙᴀʟᴀɴᴄᴇ:</b> <code>{new_credits} ᴄʀᴇᴅɪᴛs</code>")
    except Exception:
        pass

#===============================================================#

@Client.on_message(filters.command("setcredit") & filters.private)
async def set_global_credits_config_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    args = message.text.split()
    if len(args) < 2:
        current_val = await client.mongodb.get_set_credits_amount()
        return await message.reply(f"<blockquote><b>✦ ɢʟᴏʙᴀʟ ᴄʀᴇᴅɪᴛs CONFIG</b></blockquote>\n\n›› <b>ᴄᴜʀʀᴇɴᴛ ʀᴇᴡᴀʀᴅ ᴘᴇʀ ʙʏᴘᴀss:</b> <code>{current_val} ᴄʀᴇᴅɪᴛs</code>\n›› <b>ᴛᴏ ᴄʜᴀɴɢᴇ:</b> `/setcredit <amount>`")
        
    try:
        new_amount = int(args[1])
    except ValueError:
        return await message.reply("<b>✗ Amount must be an integer string numerical.</b>")
        
    await client.mongodb.set_global_credits_amount(new_amount)
    await message.reply(f"<blockquote><b>✓ ɢʟᴏʙᴀʟ ᴄʀᴇᴅɪᴛs CONFIG ᴜᴘᴅᴀᴛᴇᴅ!</b></blockquote>\n\n›› <b>ɴᴇᴡ sᴇᴛ ᴀᴍᴏᴜɴᴛ:</b> <code>{new_amount} ᴄʀᴇᴅɪᴛs</code> per bypass loop validation. All menus aligned.")

#===============================================================#

@Client.on_message(filters.command("dbroadcast") & filters.private)
async def set_auto_delete_broadcast_latency_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    args = message.text.split()
    if len(args) < 2:
        current_lat = await client.mongodb.get_dbroadcast_latency()
        return await message.reply(f"<blockquote><b>✦ AUTO-DELETE BROADCAST CONFIG</b></blockquote>\n\n›› <b>ᴄᴜʀʀᴇɴᴛ sᴇᴛ ʟᴀᴛᴇɴᴄʏ:</b> <code>{current_lat} sᴇᴄᴏɴᴅs</code> (0 = Disabled)\n›› <b>ᴛᴏ sᴇᴛ (ᴇɢ: 10m = 600s):</b> `/dbroadcast <seconds>`")
        
    try:
        seconds = int(args[1])
    except ValueError:
        return await message.reply("<b>✗ Latency parameters must be integer metrics seconds.</b>")
        
    await client.mongodb.set_dbroadcast_latency(seconds)
    await message.reply(f"<blockquote><b>✓ BROADCAST AUTO-DELETE TARGET LOADED!</b></blockquote>\n\n›› <b>sᴇᴛ sᴇᴄᴏɴᴅs:</b> <code>{seconds} sᴇᴄᴏɴᴅs</code>. All future broadcast modules will trigger scheduled dynamic execution nodes.")

#===============================================================#

@Client.on_message(filters.command("commands") & filters.private)
async def admin_manual_commands_directory_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    manual = """<blockquote><b>⛩️ REZE CORE MANAGEMENT COMMANDS DIRECTORY</b></blockquote>

<b>⚙️ ᴘʀᴇᴍɪᴜᴍ ᴏᴘᴇʀᴀᴛɪᴏɴs:</b>
• `/addpremium <id> <duration>` ›› Grant premium bypass access nodes.
• `/remove_premium <id>` ›› Revoke premium layer instantly.
• `/premium_users` ›› Active pagination list with elapsed metrics.

<b>📊 ᴄʀᴇᴅɪᴛs ᴀɴᴀʟʏᴛɪᴄs:</b>
• `/addcredit <id> <amount>` ›› Inject credits into user data node directly.
• `/setcredit <amount>` ›› Set global dynamic tokens reward on shortlink bypass.

<b>📡 ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ:</b>
• `/dbroadcast <seconds>` ›› Set global auto-delete latency for broadcast packets.
• `/stats` ›› Extract CPU, RAM, Network IO and userbase analytics data.
• `/settings` ›› Invoke core administration panel grid.
"""
    await message.reply(manual)

#===============================================================#

@Client.on_message(filters.command("stats"))
async def usage_cmd(client: Client, message: Message):
    if not message.from_user.id in client.admins:
        return await message.reply("✗ ᴛʜɪs ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜsᴇᴅ ʙʏ ᴀᴅᴍɪɴs!")
    
    reply = await message.reply("<blockquote>›› ᴇxᴛʀᴀᴄᴛɪɴɢ ᴜsᴀɢᴇ ᴅᴀᴛᴀ...</blockquote>")

    try:
        total_users_list = await client.mongodb.full_userbase()
        total_users = len(total_users_list)
    except Exception:
        total_users = "ᴇʀʀᴏʀ"

    uptime_duration = datetime.now() - getattr(client, 'uptime', datetime.now())
    days = uptime_duration.days
    hours, remainder = divmod(uptime_duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime_str = f"{days}ᴅ {hours}ʜ {minutes}ᴍ"

    total, used, free = shutil.disk_usage("/")
    total_gb = total / (1024**3)
    used_gb = used / (1024**3)
    free_gb = free / (1024**3)
    disk_percent = (used / total) * 100

    ram = psutil.virtual_memory()
    total_ram = ram.total / (1024**3)
    used_ram = ram.used / (1024**3)
    free_ram = ram.available / (1024**3)
    ram_percent = ram.percent

    swap = psutil.swap_memory()
    total_swap = swap.total / (1024**3)
    used_swap = swap.used / (1024**3)
    free_swap = swap.free / (1024**3)
    swap_percent = swap.percent

    cpu_usage = psutil.cpu_percent(interval=1)

    try:
        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent / (1024**2)
        bytes_recv = net_io.bytes_recv / (1024**2)
        network_status = "✓ ᴀᴠᴀɪʟᴀʙʟᴇ"
        net_section = f"<blockquote>›› **ᴜᴘʟᴏᴀᴅᴇᴅ:** `{bytes_sent:.2f} ᴍʙ`\n›› **ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ:** `{bytes_recv:.2f} ᴍʙ`</blockquote>"
    except PermissionError:
        network_status = "✗ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ"
        net_section = "<blockquote>›› **sᴛᴀᴛᴜs:** `ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴘʀᴏᴏᴛ`</blockquote>"

    try:
        process = psutil.Process()
        bot_cpu_usage = process.cpu_percent(interval=1)
        bot_memory_usage = process.memory_info().rss / (1024**2)
        bot_status = "✓ ʀᴜɴɴɪɴɢ"
    except Exception:
        bot_cpu_usage = 0.0
        bot_memory_usage = 0.0
        bot_status = "✗ ᴇʀʀᴏʀ"

    disk_status = "✓ ɴᴏʀᴍᴀʟ" if disk_percent < 80 else "✗ ʜɪɢʜ" if disk_percent < 95 else "✗ ᴄʀɪᴛɪᴄᴀʟ"
    ram_status = "✓ ɴᴏʀᴍᴀʟ" if ram_percent < 80 else "✗ ʜɪɢʜ" if ram_percent < 95 else "✗ ᴄʀɪᴛɪᴄᴀʟ"
    cpu_status = "✓ ɴᴏʀᴍᴀʟ" if cpu_usage < 80 else "✗ ʜɪɢʜ" if cpu_usage < 95 else "✗ ᴄʀɪᴛɪᴄᴀʟ"

    msg = f"""<blockquote>✦ sʏsᴛᴇᴍ ᴜsᴀɢᴇ sᴛᴀᴛs</blockquote>

<blockquote><u>**≡ ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs:**</u></blockquote>
<blockquote>›› **ᴛᴏᴛᴀʟ ᴜsᴇʀs:** `{total_users}`
›› **ʙᴏᴛ sᴛᴀᴛᴜs:** {bot_status}
›› **ᴜᴘᴛɪᴍᴇ:** `{uptime_str}`
›› **ᴀᴅᴍɪɴs:** `{len(client.admins)}`</blockquote>

<blockquote><u>**≡ ᴅɪsᴋ ᴜsᴀɢᴇ:**</u></blockquote>
<blockquote>›› **ᴛᴏᴛᴀʟ:** `{total_gb:.2f} ɢʙ`
›› **ᴜsᴇᴅ:** `{used_gb:.2f} ɢʙ` ({disk_percent:.1f}%)
›› **ꜰʀᴇᴇ:** `{free_gb:.2f} ɢʙ`
›› **sᴛᴀᴛᴜs:** {disk_status}</blockquote>

<blockquote><u>**≡ ʀᴀᴍ ᴜsᴀɢᴇ:**</u></blockquote>
<blockquote>›› **ᴛᴏᴛᴀʟ:** `{total_ram:.2f} ɢʙ`
›› **ᴜsᴇᴅ:** `{used_ram:.2f} ɢʙ` ({ram_percent:.1f}%)
›› **ꜰʀᴇᴇ:** `{free_ram:.2f} ɢʙ`
›› **sᴛᴀᴛᴜs:** {ram_status}</blockquote>

<blockquote><u>**≡ sᴡᴀᴘ ᴜsᴀɢᴇ:**</u></blockquote>
<blockquote>›› **ᴛᴏᴛᴀʟ:** `{total_swap:.2f} ɢʙ`
›› **ᴜsᴇᴅ:** `{used_swap:.2f} ɢʙ` ({swap_percent:.1f}%)
›› **ꜰʀᴇᴇ:** `{free_swap:.2f} ɢʙ`</blockquote>

<blockquote><u>**≡ ᴄᴘᴜ & ɴᴇᴛᴡᴏʀᴋ:**</u></blockquote>
<blockquote>›› **ᴄᴘᴜ ᴜsᴀɢᴇ:** `{cpu_usage:.2f}%` {cpu_status}
›› **ɴᴇᴛᴡᴏʀᴋ:** {network_status}</blockquote>
{net_section}

<blockquote><u>**≡ ʙᴏᴛ ʀᴇsᴏᴜʀᴄᴇ ᴜsᴀɢᴇ:**</u></blockquote>
<blockquote>›› **ᴄᴘᴜ:** `{bot_cpu_usage:.2f}%`
›› **ᴍᴇᴍᴏʀʏ:** `{bot_memory_usage:.2f} ᴍʙ`</blockquote>

<blockquote>**• ᴜsᴇ ᴛʜɪs ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴛᴏ ᴍᴏɴɪᴛᴏʀ ʏᴏᴜʀ ʙᴏᴛ's ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇ!**</blockquote>"""
    await reply.edit_text(msg)

#===============================================================#

@Client.on_callback_query(filters.regex("^add_admin$"))
async def add_new_admins(client: Client, query: CallbackQuery):
    await query.answer()
    if not query.from_user.id in client.admins:
        return await client.send_message(query.from_user.id, client.reply_text)
    ids_msg = await client.ask(query.from_user.id, "Send user ids seperated by a space in the next 60 seconds!\nEg: `838278682 83622928 82789928`", filters=filters.text, timeout=60)
    ids = ids_msg.text.split()
    try:
        for identifier in ids:
            if int(identifier) not in client.admins:
                client.admins.append(int(identifier))
    except Exception as e:
        return await ids_msg.reply(f"Error: {e}")
    await admins(client, query)
    return await ids_msg.reply(f"__{len(ids)} admin {'id' if len(ids)==1 else 'ids'} have been promoted!!__")
    
#===============================================================#

@Client.on_callback_query(filters.regex("^rm_admin$"))
async def remove_admins(client: Client, query: CallbackQuery):
    await query.answer()
    if not query.from_user.id in client.admins:
        return await client.send_message(query.from_user.id, client.reply_text)
    ids_msg = await client.ask(query.from_user.id, "Send user ids seperated by a space in the next 60 seconds!\nEg: `838278682 83622928 82789928`", filters=filters.text, timeout=60)
    ids = ids_msg.text.split()
    try:
        for identifier in ids:
            if int(identifier) == client.owner:
                await client.send_message(query.from_user.id, "Nigga i can never remove the owner from the admin list!!")
                continue
            if int(identifier) in client.admins:
                client.admins.remove(int(identifier))
    except Exception as e:
        return await ids_msg.reply(f"Error: {e}")
    await admins(client, query)
    return await ids_msg.reply(f"__{len(ids)} admin {'id' if len(ids)==1 else 'ids'} have been removed!!__")
                                   
