from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import psutil
import shutil
import re
from datetime import datetime, timedelta
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
# ADMINS PANEL FUNCTION (called from settings callbacks)
#===============================================================#

async def admins(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ Only admins can use this!', show_alert=True)
    msg = (
        f"<blockquote><b>⚙️ Admin Settings:</b></blockquote>\n\n"
        f"<b>Admin User IDs:</b> {', '.join(f'<code>{a}</code>' for a in client.admins)}\n\n"
        f"<i>Use the buttons below to add or remove an admin!</i>"
    )
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴀᴅᴍɪɴ', 'add_admin'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ', 'rm_admin')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]
    ])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

#===============================================================#
# ADD / REMOVE ADMIN CALLBACKS
#===============================================================#

@Client.on_callback_query(filters.regex("^add_admin$"))
async def add_new_admins(client: Client, query: CallbackQuery):
    await query.answer()
    if query.from_user.id not in client.admins:
        return await client.send_message(query.from_user.id, client.reply_text)
    ids_msg = await client.ask(query.from_user.id, "Send user IDs separated by space within 60 seconds!\nEg: <code>838278682 83622928</code>", filters=filters.text, timeout=60)
    ids = ids_msg.text.split()
    try:
        for identifier in ids:
            if int(identifier) not in client.admins:
                client.admins.append(int(identifier))
    except Exception as e:
        return await ids_msg.reply(f"Error: {e}")
    await admins(client, query)
    return await ids_msg.reply(f"<b>✓ {len(ids)} admin {'id' if len(ids)==1 else 'ids'} promoted successfully!</b>")

@Client.on_callback_query(filters.regex("^rm_admin$"))
async def remove_admins(client: Client, query: CallbackQuery):
    await query.answer()
    if query.from_user.id not in client.admins:
        return await client.send_message(query.from_user.id, client.reply_text)
    ids_msg = await client.ask(query.from_user.id, "Send user IDs separated by space within 60 seconds!\nEg: <code>838278682 83622928</code>", filters=filters.text, timeout=60)
    ids = ids_msg.text.split()
    try:
        for identifier in ids:
            if int(identifier) == client.owner:
                await client.send_message(query.from_user.id, "<b>✗ Cannot remove the owner from admin list!</b>")
                continue
            if int(identifier) in client.admins:
                client.admins.remove(int(identifier))
    except Exception as e:
        return await ids_msg.reply(f"Error: {e}")
    await admins(client, query)
    return await ids_msg.reply(f"<b>✓ {len(ids)} admin {'id' if len(ids)==1 else 'ids'} removed successfully!</b>")

#===============================================================#
# /addpremium COMMAND
#===============================================================#

@Client.on_message(filters.command("addpremium") & filters.private)
async def add_premium_user_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")
    args = message.text.split()
    if len(args) < 3:
        return await message.reply("<blockquote><b>✦ Add Premium</b></blockquote>\n\n›› <b>Usage:</b> <code>/addpremium &lt;user_id&gt; &lt;duration&gt;</code>\n›› <b>Examples:</b>\n• <code>/addpremium 12345678 7d</code> (7 Days)\n• <code>/addpremium 12345678 30d</code> (30 Days)\n• <code>/addpremium 12345678 lifetime</code> (Permanent)")
    try:
        target_user = int(args[1])
        duration_str = args[2]
    except ValueError:
        return await message.reply("<b>✗ Invalid user ID format. Must be a number.</b>")
    expiry_time, is_lifetime = parse_premium_duration(duration_str)
    if expiry_time is None and not is_lifetime:
        return await message.reply("<b>✗ Invalid duration! Use <code>1d</code> to <code>30d</code> or <code>lifetime</code>.</b>")
    total_days = int(duration_str.replace('d', '')) if 'd' in duration_str.lower() else None
    await client.mongodb.add_pro(user_id=target_user, expiry_date=expiry_time, total_days=total_days, is_lifetime=is_lifetime)
    expiry_display = "Lifetime Access" if is_lifetime else expiry_time.strftime('%Y-%m-%d %H:%M:%S')
    await message.reply(f"<blockquote><b>✓ Premium Granted Successfully!</b></blockquote>\n\n›› <b>User:</b> <code>{target_user}</code>\n›› <b>Validity:</b> <code>{expiry_display}</code>")
    try:
        await client.send_message(chat_id=target_user, text=f"<blockquote><b>✨ ʜᴇʏ sᴇɴᴘᴀɪ! ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘɢʀᴀᴅᴇᴅ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ!</b></blockquote>\n\n›› <b>Status:</b> No verification wall — Direct file access enabled!\n›› <b>ᴇxᴘɪʀʏ:</b> <code>{expiry_display}</code>")
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
        return await message.reply("<b>✗ Usage:</b> <code>/remove_premium &lt;user_id&gt;</code>")
    try:
        target_user = int(args[1])
    except ValueError:
        return await message.reply("<b>✗ Invalid user ID format.</b>")
    is_pro = await client.mongodb.is_pro(target_user)
    if not is_pro:
        return await message.reply("<b>✗ This user does not have an active premium subscription.</b>")
    await client.mongodb.remove_pro(target_user)
    await message.reply(f"<blockquote><b>✓ Premium Removed Successfully!</b></blockquote>\n\n›› User <code>{target_user}</code> has been switched back to free verification mode.")
    try:
        await client.send_message(chat_id=target_user, text="<blockquote><b>⚠️ ʜᴇʏ sᴇɴᴘᴀɪ! ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ.</b></blockquote>\n\n›› ʏᴏᴜ ᴡɪʟʟ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ sʜᴏʀᴛʟɪɴᴋs ᴛᴏ ᴀᴄᴄᴇss ꜰɪʟᴇs ɴᴏᴡ.")
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
    msg = f"<blockquote>✦ Premium Members (Page {page}/{total_pages})</blockquote>\n\n"
    if not page_items:
        msg += "<i>No premium users registered in database.</i>\n"
    else:
        for idx, doc in enumerate(page_items, start=start_idx + 1):
            u_id = doc['_id']
            is_lifetime = doc.get('is_lifetime', False)
            expiry_date = doc.get('expiry_date')
            added_at = doc.get('added_at', current_time)
            total_days = doc.get('total_days', 0)
            elapsed = current_time - added_at
            elapsed_str = f"{elapsed.days}d passed" if elapsed.days > 0 else "Added today"
            if is_lifetime:
                time_status = "♾️ Lifetime Access"
            elif expiry_date:
                remaining = expiry_date - current_time
                if remaining.total_seconds() <= 0:
                    time_status = "❌ Expired"
                else:
                    time_status = f"⏳ {remaining.days}d {remaining.seconds // 3600}h remaining"
            else:
                time_status = "❓ Unknown"
            total_days_str = f" | Total: {total_days}d" if total_days else ""
            msg += f"<b>{idx}.</b> <a href='tg://user?id={u_id}'>User</a> (<code>{u_id}</code>)\n   {time_status}{total_days_str} | <i>{elapsed_str}</i>\n\n"
    buttons = []
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("‹ Prev", callback_data=f"propage_{page-1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("Next ›", callback_data=f"propage_{page+1}"))
    if nav_row:
        buttons.append(nav_row)
    if page > 1:
        buttons.append([InlineKeyboardButton("‹ Back", callback_data=f"propage_1")])
    else:
        buttons.append([InlineKeyboardButton("Close •", callback_data="close")])
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
        return await message.reply("<b>✗ Usage:</b> <code>/addcredit &lt;user_id&gt; &lt;amount&gt;</code>")
    try:
        target_user = int(args[1])
        amount = int(args[2])
    except ValueError:
        return await message.reply("<b>✗ Invalid input! Both values must be numbers.</b>")
    user_data = await client.mongodb.user_data.find_one({"_id": target_user})
    if not user_data:
        return await message.reply("<b>✗ This user is not registered in the bot database.</b>")
    current_credits = user_data.get("credits", 0)
    new_credits = current_credits + amount
    await client.mongodb.user_data.update_one({"_id": target_user}, {"$set": {"credits": new_credits}}, upsert=True)
    await message.reply(f"<blockquote><b>✓ Credits Added Successfully!</b></blockquote>\n\n›› User <code>{target_user}</code>\n›› Previous: <code>{current_credits}</code> → New: <code>{new_credits} credits</code>")
    try:
        await client.send_message(chat_id=target_user, text=f"<blockquote><b>✨ ʜᴇʏ sᴇɴᴘᴀɪ! ᴛʜᴇ ᴀᴅᴍɪɴ ʜᴀs ᴄʀᴇᴅɪᴛᴇᴅ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ!</b></blockquote>\n\n›› <b>ᴄʀᴇᴅɪᴛs ᴀᴅᴅᴇᴅ:</b> <code>{amount} credits</code>\n›› <b>ᴄᴜʀʀᴇɴᴛ ʙᴀʟᴀɴᴄᴇ:</b> <code>{new_credits} credits</code>")
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
        return await message.reply(f"<blockquote><b>✦ Global Credits Config</b></blockquote>\n\n›› <b>Current Reward Per Bypass:</b> <code>{current_val} credits</code>\n›› <b>To Change:</b> <code>/setcredit &lt;amount&gt;</code>")
    try:
        new_amount = int(args[1])
    except ValueError:
        return await message.reply("<b>✗ Invalid amount! Must be a number.</b>")
    await client.mongodb.set_global_credits_amount(new_amount)
    await message.reply(f"<blockquote><b>✓ Global Credits Updated!</b></blockquote>\n\n›› <b>New Reward Per Bypass:</b> <code>{new_amount} credits</code>")

#===============================================================#
# /dbroadcast COMMAND
#===============================================================#

@Client.on_message(filters.command("dbroadcast") & filters.private)
async def set_auto_delete_broadcast_latency_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")
    args = message.text.split()
    if len(args) < 2:
        current_lat = await client.mongodb.get_dbroadcast_latency()
        return await message.reply(f"<blockquote><b>✦ Auto-Delete Broadcast Config</b></blockquote>\n\n›› <b>Current Latency:</b> <code>{current_lat} seconds</code> (0 = Disabled)\n›› <b>To Set:</b> <code>/dbroadcast &lt;seconds&gt;</code>")
    try:
        seconds = int(args[1])
    except ValueError:
        return await message.reply("<b>✗ Latency must be a number in seconds.</b>")
    await client.mongodb.set_dbroadcast_latency(seconds)
    await message.reply(f"<blockquote><b>✓ Broadcast Auto-Delete Set!</b></blockquote>\n\n›› <b>Set to:</b> <code>{seconds} seconds</code>")

#===============================================================#
# /commands COMMAND
#===============================================================#

@Client.on_message(filters.command("commands") & filters.private)
async def admin_manual_commands_directory_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")
    manual = """<blockquote><b>⛩️ Reze — Admin Commands Directory</b></blockquote>

<b>⚙️ Settings:</b>
• <code>/settings</code> ›› Open bot settings panel

<b>👑 Premium Operations:</b>
• <code>/addpremium &lt;id&gt; &lt;1d-30d|lifetime&gt;</code> ›› Grant premium access (no verification)
• <code>/remove_premium &lt;id&gt;</code> ›› Revoke premium, back to normal verification
• <code>/premium_users</code> ›› View all premium users with time remaining

<b>💰 Credits:</b>
• <code>/addcredit &lt;id&gt; &lt;amount&gt;</code> ›› Add credits to any user
• <code>/setcredit &lt;amount&gt;</code> ›› Set credits reward per shortlink bypass

<b>📡 Broadcast:</b>
• <code>/broadcast</code> ›› Instant broadcast (reply to a message)
• <code>/broadcast del 10m</code> ›› Broadcast + auto delete after 10 mins
• <code>/broadcast schedule 2h</code> ›› Schedule broadcast after 2 hours
• <code>/broadcast schedule 1h del 30m</code> ›› Schedule + auto delete
• <code>/pbroadcast</code> ›› Broadcast and pin the message
• <code>/dbroadcast &lt;seconds&gt;</code> ›› Set broadcast auto-delete time

<b>📊 Stats:</b>
• <code>/stats</code> ›› CPU, RAM, Network and bot statistics
• <code>/users</code> ›› Total user count

<b>🛡️ Ban/Unban:</b>
• <code>/ban &lt;id&gt;</code> ›› Ban a user from the bot
• <code>/unban &lt;id&gt;</code> ›› Unban a user

• <code>/commands</code> ›› Show this command list"""
    await message.reply(manual)

#===============================================================#
# /stats COMMAND
#===============================================================#

@Client.on_message(filters.command("stats"))
async def usage_cmd(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply("✗ Only admins can use this!")
    reply = await message.reply("<blockquote>›› Extracting usage data...</blockquote>")
    try:
        total_users_list = await client.mongodb.full_userbase()
        total_users = len(total_users_list)
    except Exception:
        total_users = "Error"
    uptime_duration = datetime.now() - getattr(client, 'uptime', datetime.now())
    days = uptime_duration.days
    hours, remainder = divmod(uptime_duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime_str = f"{days}d {hours}h {minutes}m"
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
        network_status = "✓ Available"
        net_section = f"<blockquote>›› <b>Uploaded:</b> <code>{bytes_sent:.2f} MB</code>\n›› <b>Downloaded:</b> <code>{bytes_recv:.2f} MB</code></blockquote>"
    except PermissionError:
        network_status = "✗ Not Available"
        net_section = "<blockquote>›› <b>Status:</b> <code>Not available on this host</code></blockquote>"
    try:
        process = psutil.Process()
        bot_cpu_usage = process.cpu_percent(interval=1)
        bot_memory_usage = process.memory_info().rss / (1024**2)
        bot_status = "✓ Running"
    except Exception:
        bot_cpu_usage = 0.0
        bot_memory_usage = 0.0
        bot_status = "✗ Error"
    disk_status = "✓ Normal" if disk_percent < 80 else "✗ High" if disk_percent < 95 else "✗ Critical"
    ram_status = "✓ Normal" if ram_percent < 80 else "✗ High" if ram_percent < 95 else "✗ Critical"
    cpu_status = "✓ Normal" if cpu_usage < 80 else "✗ High" if cpu_usage < 95 else "✗ Critical"
    msg = f"""<blockquote>✦ System Usage Stats</blockquote>

<blockquote><u><b>≡ Bot Statistics:</b></u></blockquote>
<blockquote>›› <b>Total Users:</b> <code>{total_users}</code>
›› <b>Bot Status:</b> {bot_status}
›› <b>Uptime:</b> <code>{uptime_str}</code>
›› <b>Admins:</b> <code>{len(client.admins)}</code></blockquote>

<blockquote><u><b>≡ Disk Usage:</b></u></blockquote>
<blockquote>›› <b>Total:</b> <code>{total_gb:.2f} GB</code>
›› <b>Used:</b> <code>{used_gb:.2f} GB</code> ({disk_percent:.1f}%)
›› <b>Free:</b> <code>{free_gb:.2f} GB</code>
›› <b>Status:</b> {disk_status}</blockquote>

<blockquote><u><b>≡ RAM Usage:</b></u></blockquote>
<blockquote>›› <b>Total:</b> <code>{total_ram:.2f} GB</code>
›› <b>Used:</b> <code>{used_ram:.2f} GB</code> ({ram_percent:.1f}%)
›› <b>Free:</b> <code>{free_ram:.2f} GB</code>
›› <b>Status:</b> {ram_status}</blockquote>

<blockquote><u><b>≡ Swap Usage:</b></u></blockquote>
<blockquote>›› <b>Total:</b> <code>{total_swap:.2f} GB</code>
›› <b>Used:</b> <code>{used_swap:.2f} GB</code> ({swap_percent:.1f}%)
›› <b>Free:</b> <code>{free_swap:.2f} GB</code></blockquote>

<blockquote><u><b>≡ CPU & Network:</b></u></blockquote>
<blockquote>›› <b>CPU Usage:</b> <code>{cpu_usage:.2f}%</code> {cpu_status}
›› <b>Network:</b> {network_status}</blockquote>
{net_section}

<blockquote><u><b>≡ Bot Resource Usage:</b></u></blockquote>
<blockquote>›› <b>CPU:</b> <code>{bot_cpu_usage:.2f}%</code>
›› <b>Memory:</b> <code>{bot_memory_usage:.2f} MB</code></blockquote>"""
    await reply.edit_text(msg)
