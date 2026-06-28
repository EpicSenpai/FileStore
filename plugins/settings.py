from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, InputMediaPhoto
from pyrogram.errors.pyromod import ListenerTimeout
import config
from plugins.shortner import get_short

def _build_settings_page1_msg(client):
    total_fsub = len(client.fsub_dict)
    request_enabled = sum(1 for data in client.fsub_dict.values() if data[2])
    timer_enabled = sum(1 for data in client.fsub_dict.values() if data[3] > 0)
    total_db_channels = len(getattr(client, 'db_channels', {}))
    primary_db = getattr(client, 'primary_db_channel', client.db)
    msg = (
        f"<blockquote>✦ sᴇᴛᴛɪɴɢs ᴏꜰ @{client.username} (ᴘᴀɢᴇ 1)</blockquote>\n"
        f"›› <b>ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_fsub}</code> (ʀᴇǫᴜᴇsᴛ: {request_enabled}, ᴛɪᴍᴇʀ: {timer_enabled})\n"
        f"›› <b>ᴅʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_db_channels}</code> (ᴘʀɪᴍᴀʀʏ: <code>{primary_db}</code>)\n"
        f"›› <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:</b> <code>{client.auto_del}</code>\n"
        f"›› <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:</b> <code>{'✓ ᴛʀᴜᴇ' if client.protect else '✗ ꜰᴀʟsᴇ'}</code>\n"
        f"›› <b>ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:</b> <code>{'✓ ᴛʀᴜᴇ' if client.disable_btn else '✗ ꜰᴀʟsᴇ'}</code>\n"
        f"›› <b>ʀᴇᴘʟʏ ᴛᴇxᴛ:</b> <code>{client.reply_text if client.reply_text else 'ɴᴏɴᴇ'}</code>\n"
        f"›› <b>ᴀᴅᴍɪɴs:</b> <code>{len(client.admins)}</code>\n\n"
        f"<blockquote><u><b>≡ ᴍᴜʟᴛɪ-sʜᴏʀᴛᴇɴᴇer sᴛᴀᴛᴜs:</b></u></blockquote>\n"
        f"›› <b>sʜᴏʀᴛɴᴇer 1:</b> <code>{getattr(config, 'SHORT_URL_1', 'None')}</code> [<code>{'✔️ ᴏɴ' if getattr(config, 'SHORT_STATUS_1', True) else '❌ ᴏꜰꜰ'}</code>]\n"
        f"›› <b>sʜᴏʀᴛɴᴇer 2:</b> <code>{getattr(config, 'SHORT_URL_2', 'None')}</code> [<code>{'✔️ ᴏɴ' if getattr(config, 'SHORT_STATUS_2', True) else '❌ ᴏꜰꜰ'}</code>]\n"
        f"›› <b>sʜᴏʀᴛɴᴇer 3:</b> <code>{getattr(config, 'SHORT_URL_3', 'None')}</code> [<code>{'✔️ ᴏɴ' if getattr(config, 'SHORT_STATUS_3', True) else '❌ ᴏꜰꜰ'}</code>]"
    )
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs', 'fsub'), InlineKeyboardButton('ᴅʙ ᴄʜᴀɴɴᴇʟs', 'db_channels')],
        [InlineKeyboardButton('ᴀᴅᴍɪɴs', 'admins'), InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', 'auto_del')],
        [InlineKeyboardButton('ʜᴏᴍᴇ', 'home'), InlineKeyboardButton('›› ɴᴇxᴛ', 'settings_page_2')]
    ])
    return msg, reply_markup

@Client.on_message(filters.command("settings") & filters.private)
async def settings_text_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")
    msg, reply_markup = _build_settings_page1_msg(client)
    await message.reply(msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^home$"))
async def back_to_home_callback(client: Client, query: CallbackQuery):
    await query.answer("↩️ Returning back to home dashboard...")
    user_id = query.from_user.id
    buttons = [[InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="ABOUT"), InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data='close')]]
    if user_id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("• sᴇᴛᴛɪɴɢs •", callback_data="settings")])
    start_caption = config.MESSAGES.get('START', '').format(first=query.from_user.first_name, last=query.from_user.last_name or "", username=None if not query.from_user.username else '@' + query.from_user.username, mention=query.from_user.mention, id=user_id)
    try:
        await query.message.edit_media(media=InputMediaPhoto(media=config.MESSAGES.get("START_PHOTO", ""), caption=start_caption), reply_markup=InlineKeyboardMarkup(buttons))
    except Exception:
        try:
            await query.message.edit_text(text=start_caption, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            pass

@Client.on_callback_query(filters.regex("^ABOUT$"))
async def render_about_callback_query(client: Client, query: CallbackQuery):
    await query.answer("ℹ️ Loading about documentation details...")
    about_text = config.MESSAGES.get('ABOUT', '').format(bot_name=client.username)
    back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="home")]])
    try:
        await query.message.edit_caption(caption=about_text, reply_markup=back_markup)
    except Exception:
        try:
            await query.message.edit_text(text=about_text, reply_markup=back_markup)
        except Exception:
            pass

@Client.on_callback_query(filters.regex("^close$"))
async def close_panel_callback_query(client: Client, query: CallbackQuery):
    await query.answer("🗑️ Interface closed.")
    await query.message.delete()

@Client.on_callback_query(filters.regex("^settings$"))
async def settings(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    msg, reply_markup = _build_settings_page1_msg(client)
    try:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)
    except Exception:
        try:
            await query.message.edit_text(msg, reply_markup=reply_markup)
        except Exception:
            pass

@Client.on_callback_query(filters.regex("^admins$"))
async def admins_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    msg = (f"<blockquote><b>⚙️ ᴀᴅᴍɪɴ sᴇᴛᴛɪɴɢs:</b></blockquote>\n" f"<b>ᴀᴅᴍɪɴ ɪᴅs:</b> {', '.join(f'<code>{a}</code>' for a in client.admins)}\n\n" f"<i>ᴜsᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ:</i>")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('ᴀᴅᴅ ᴀᴅᴍɪɴ', 'add_admin'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ', 'rm_admin')], [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^auto_del$"))
async def auto_del_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    msg = (f"<blockquote><b>⏱️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ sᴇᴛᴛɪɴɢs</b></blockquote>\n\n" f"›› <b>ᴄᴜʀʀᴇɴᴛ:</b> <code>{client.auto_del}s</code>\n" f"›› <b>0 = ᴅɪsᴀʙʟᴇᴅ</b>")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('✏️ sᴇᴛ ᴛɪᴍᴇʀ', 'set_auto_del')], [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^set_auto_del$"))
async def set_auto_del_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    await query.message.edit_text("<b>⏱️ sᴇɴᴅ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ ɪɴ sᴇᴄᴏɴᴅs (60s timeout):</b>\n\n<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>1800</code> = 30 mins, <code>0</code> = disable")
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        new_val = int(res.text.strip())
        client.auto_del = new_val
        await client.mongodb.user_data.update_one({"_id": "bot_settings"}, {"$set": {"auto_del": new_val}}, upsert=True)
        await res.delete()
        await query.message.edit_text(f"<blockquote><b>✓ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴜᴘᴅᴀᴛᴇᴅ!</b></blockquote>\n\n›› ɴᴇᴡ: <code>{new_val}s</code>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'auto_del')]]))
    except ListenerTimeout:
        await query.message.edit_text("<b>✗ ᴛɪᴍᴇᴏᴜᴛ!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'auto_del')]]))
    except ValueError:
        await query.message.edit_text("<b>✗ ɪɴᴠᴀʟɪᴅ! sᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ.</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'auto_del')]]))

@Client.on_callback_query(filters.regex("^protect$"))
async def protect_content_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    client.protect = not client.protect
    await client.mongodb.user_data.update_one({"_id": "bot_settings"}, {"$set": {"protect": client.protect}}, upsert=True)
    status = "✓ ᴇɴᴀʙʟᴇᴅ" if client.protect else "✗ ᴅɪsᴀʙʟᴇᴅ"
    await query.answer(f"ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ {status}!", show_alert=True)
    await settings_page_2(client, query)

@Client.on_callback_query(filters.regex("^db_channels$"))
async def db_channels_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    db_channels = getattr(client, 'db_channels', {})
    primary = getattr(client, 'primary_db_channel', client.db)
    if db_channels:
        ch_list = []
        for ch_id_str, ch_data in db_channels.items():
            name = ch_data.get('name', 'Unknown')
            primary_tag = " [ᴘʀɪᴍᴀʀʏ ✓]" if ch_data.get('is_primary', False) else ""
            ch_list.append(f"• <code>{name}</code> (<code>{ch_id_str}</code>){primary_tag}")
        channels_display = "\n".join(ch_list)
    else:
        channels_display = f"<i>ᴅᴇꜰᴀᴜʟᴛ ᴅʙ: <code>{primary}</code></i>"
    msg = (f"<blockquote><b>🗄️ ᴅʙ ᴄʜᴀɴɴᴇʟ sᴇᴛᴛɪɴɢs</b></blockquote>\n\n" f"›› <b>ᴛᴏᴛᴀʟ:</b> <code>{len(db_channels)}</code>\n" f"›› <b>ᴘʀɪᴍᴀʀʏ:</b> <code>{primary}</code>\n\n" f"{channels_display}")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('➕ ᴀᴅᴅ', 'add_db_ch'), InlineKeyboardButton('➖ ʀᴇᴍᴏᴠᴇ', 'remove_db_ch')], [InlineKeyboardButton('⭐ sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db')], [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^add_db_ch$"))
async def add_db_channel_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    await query.message.edit_text("<b>🗄️ sᴇɴᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴛᴏ ᴀᴅᴅ (60s timeout):</b>\n\n<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>-1001234567890</code>")
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id = int(res.text.strip())
        chat = await client.get_chat(channel_id)
        channel_data = {'name': chat.title, 'is_primary': False}
        if not hasattr(client, 'db_channels'):
            client.db_channels = {}
        client.db_channels[str(channel_id)] = channel_data
        await client.mongodb.add_db_channel(channel_id, channel_data)
        await res.delete()
        await query.message.edit_text(f"<blockquote><b>✓ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴀᴅᴅᴇᴅ!</b></blockquote>\n\n›› <b>ɴᴀᴍᴇ:</b> {chat.title}\n›› <b>ɪᴅ:</b> <code>{channel_id}</code>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    except ListenerTimeout:
        await query.message.edit_text("<b>✗ ᴛɪᴍᴇᴏᴜᴛ!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    except Exception as e:
        await query.message.edit_text(f"<b>✗ ᴇʀʀᴏʀ: {e}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

@Client.on_callback_query(filters.regex("^remove_db_ch$"))
async def remove_db_channel_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    await query.message.edit_text("<b>🗄️ sᴇɴᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ (60s timeout):</b>")
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id = int(res.text.strip())
        if str(channel_id) in getattr(client, 'db_channels', {}):
            client.db_channels.pop(str(channel_id), None)
            await client.mongodb.remove_db_channel(channel_id)
            text = f"<blockquote><b>✓ ᴄʜᴀɴɴᴇʟ <code>{channel_id}</code> ʀᴇᴍᴏᴠᴇᴅ!</b></blockquote>"
        else:
            text = f"<b>✗ ᴄʜᴀɴɴᴇʟ <code>{channel_id}</code> ɴᴏᴛ ꜰᴏᴜɴᴅ!</b>"
        await res.delete()
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    except ListenerTimeout:
        await query.message.edit_text("<b>✗ ᴛɪᴍᴇᴏᴜᴛ!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    except Exception as e:
        await query.message.edit_text(f"<b>✗ ᴇʀʀᴏʀ: {e}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

@Client.on_callback_query(filters.regex("^set_primary_db$"))
async def set_primary_db_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    await query.message.edit_text("<b>⭐ sᴇɴᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴛᴏ sᴇᴛ ᴀs ᴘʀɪᴍᴀʀʏ (60s timeout):</b>")
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id = int(res.text.strip())
        db_channels = getattr(client, 'db_channels', {})
        if str(channel_id) not in db_channels:
            await res.delete()
            return await query.message.edit_text(f"<b>✗ ᴄʜᴀɴɴᴇʟ <code>{channel_id}</code> ɴᴏᴛ ꜰᴏᴜɴᴅ!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        for ch_id_str in db_channels:
            db_channels[ch_id_str]['is_primary'] = False
        db_channels[str(channel_id)]['is_primary'] = True
        client.primary_db_channel = channel_id
        client.db = channel_id
        await client.mongodb.set_primary_db_channel(channel_id)
        await res.delete()
        await query.message.edit_text(f"<blockquote><b>✓ ᴘʀɪᴍᴀʀʏ ᴅʙ sᴇᴛ ᴛᴏ <code>{channel_id}</code>!</b></blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    except ListenerTimeout:
        await query.message.edit_text("<b>✗ ᴛɪᴍᴇᴏᴜᴛ!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

@Client.on_callback_query(filters.regex("^photos$"))
async def photos_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    msg = (f"<blockquote><b>🖼️ ᴘʜᴏᴛᴏ sᴇᴛᴛɪɴɢs</b></blockquote>\n\n" f"›› sᴛᴀʀᴛ: <code>{config.MESSAGES.get('START_PHOTO', 'None')}</code>\n" f"›› ꜰsᴜʙ: <code>{config.MESSAGES.get('FSUB_PHOTO', 'None')}</code>\n" f"›› sʜᴏʀᴛ: <code>{config.MESSAGES.get('SHORT_PIC', 'None')}</code>")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('sᴛᴀʀᴛ ᴘʜᴏᴛᴏ', 'set_photo_START_PHOTO'), InlineKeyboardButton('ꜰsᴜʙ ᴘʜᴏᴛᴏ', 'set_photo_FSUB_PHOTO')], [InlineKeyboardButton('sʜᴏʀᴛ ᴘɪᴄ', 'set_photo_SHORT_PIC')], [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings_page_2')]])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^set_photo_(.+)$"))
async def set_photo_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    photo_key = query.data.replace("set_photo_", "")
    await query.message.edit_text(f"<b>🖼️ sᴇɴᴅ ɴᴇᴡ ᴜʀʟ ꜰᴏʀ <code>{photo_key}</code> (60s timeout):</b>")
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        new_url = res.text.strip()
        config.MESSAGES[photo_key] = new_url
        await client.mongodb.user_data.update_one({"_id": "bot_messages"}, {"$set": {photo_key: new_url}}, upsert=True)
        await res.delete()
        await query.message.edit_text(f"<b>✓ {photo_key} ᴜᴘᴅᴀᴛᴇᴅ!</b>\n\n›› <code>{new_url}</code>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
    except ListenerTimeout:
        await query.message.edit_text("<b>✗ ᴛɪᴍᴇᴏᴜᴛ!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
    except Exception as e:
        await query.message.edit_text(f"<b>✗ ᴇʀʀᴏʀ: {e}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))

@Client.on_callback_query(filters.regex("^texts$"))
async def texts_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    msg = "<blockquote><b>📝 ᴛᴇxᴛ sᴇᴛᴛɪɴɢs</b></blockquote>\n\n<i>ᴄʜᴏᴏsᴇ ᴡʜɪᴄʜ ᴛᴇxᴛ ᴛᴏ ᴇᴅɪᴛ:</i>"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('sᴛᴀʀᴛ ᴍsɢ', 'set_text_START'), InlineKeyboardButton('ꜰsᴜʙ ᴍsɢ', 'set_text_FSUB')], [InlineKeyboardButton('ᴀʙᴏᴜᴛ', 'set_text_ABOUT'), InlineKeyboardButton('ʀᴇᴘʟʏ ᴛᴇxᴛ', 'set_text_REPLY')], [InlineKeyboardButton('sʜᴏʀᴛ ᴍsɢ', 'set_text_SHORT_MSG')], [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings_page_2')]])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^set_text_(.+)$"))
async def set_text_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)@Client.on_callback_query(filters.regex("^settings_page_2$"))
async def settings_page_2(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    total_fsub = len(client.fsub_dict)
    total_db_channels = len(getattr(client, 'db_channels', {}))
    msg = (f"<blockquote>✦ sᴇᴛᴛɪɴɢs ᴏꜰ @{client.username} (ᴘᴀɢᴇ 2)</blockquote>\n" f"›› <b>ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_fsub}</code>\n" f"›› <b>ᴅʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_db_channels}</code>\n" f"›› <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:</b> <code>{'✓ ᴛʀᴜᴇ' if client.protect else '✗ ꜰᴀʟsᴇ'}</code>\n" f"›› <b>ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:</b> <code>{'✓ ᴛʀᴜᴇ' if client.disable_btn else '✗ ꜰᴀʟsᴇ'}</code>\n\n" f"<blockquote><u><b>≡ 1sᴛ sʜᴏʀᴛᴇɴᴇʀ:</b></u></blockquote>\n" f"›› <b>sᴛᴀᴛᴜs:</b> <code>{'✔️ ᴇɴᴀʙʟᴇᴅ' if getattr(config, 'SHORT_STATUS_1', True) else '❌ ᴅɪsᴀʙʟᴇᴅ'}</code>\n" f"›› <b>ᴜʀʟ:</b> <code>{getattr(config, 'SHORT_URL_1', 'None')}</code>\n\n" f"<blockquote><u><b>≡ 2ɴᴅ sʜᴏʀᴛᴇɴᴇʀ:</b></u></blockquote>\n" f"›› <b>sᴛᴀᴛᴜs:</b> <code>{'✔️ ᴇɴᴀʙʟᴇᴅ' if getattr(config, 'SHORT_STATUS_2', True) else '❌ ᴅɪsᴀʙʟᴇᴅ'}</code>\n" f"›› <b>ᴜʀʟ:</b> <code>{getattr(config, 'SHORT_URL_2', 'None')}</code>\n\n" f"<blockquote><u><b>≡ 3ʀᴅ sʜᴏʀᴛᴇɴᴇʀ:</b></u></blockquote>\n" f"›› <b>sᴛᴀᴛᴜs:</b> <code>{'✔️ ᴇɴᴀʙʟᴇᴅ' if getattr(config, 'SHORT_STATUS_3', True) else '❌ ᴅɪsᴀʙʟᴇᴅ'}</code>\n" f"›› <b>ᴜʀʟ:</b> <code>{getattr(config, 'SHORT_URL_3', 'None')}</code>")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ', 'protect'), InlineKeyboardButton('ᴘʜᴏᴛᴏs', 'photos')], [InlineKeyboardButton('ᴛᴇxᴛs', 'texts'), InlineKeyboardButton('🛠️ sʜᴏʀᴛɴᴇer sᴇᴛᴛɪɴɢs', 'manage_shortners')], [InlineKeyboardButton('‹ ᴘʀᴇᴠ', 'settings'), InlineKeyboardButton('ʜᴏᴍᴇ', 'home')]])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^manage_shortners$"))
async def manage_shortners(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    msg = (f"<blockquote>✦ ᴍᴜʟᴛɪ-sʜᴏʀᴛᴇɴᴇer ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</blockquote>\n\n" f"›› 1sᴛ: <code>{getattr(config, 'SHORT_URL_1', 'None')}</code> [<code>{'✔️' if getattr(config, 'SHORT_STATUS_1', True) else '❌'}</code>]\n" f"›› 2ɴᴅ: <code>{getattr(config, 'SHORT_URL_2', 'None')}</code> [<code>{'✔️' if getattr(config, 'SHORT_STATUS_2', True) else '❌'}</code>]\n" f"›› 3ʀᴅ: <code>{getattr(config, 'SHORT_URL_3', 'None')}</code> [<code>{'✔️' if getattr(config, 'SHORT_STATUS_3', True) else '❌'}</code>]")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('sʜᴏʀᴛɴᴇer 1', 'edit_short_1'), InlineKeyboardButton('sʜᴏʀᴛɴᴇer 2', 'edit_short_2')], [InlineKeyboardButton('sʜᴏʀᴛɴᴇer 3', 'edit_short_3')], [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings_page_2')]])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^edit_short_(1|2|3)$"))
async def edit_specific_shortner(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    num = query.data.split("_")[2]
    url_val = getattr(config, f"SHORT_URL_{num}", "None")
    tut_val = getattr(config, f"SHORT_TUT_{num}", "None")
    status_val = getattr(config, f"SHORT_STATUS_{num}", True)
    analytics = await client.mongodb.db.shortner_analytics.find_one({"shortner_id": int(num)}) or {}
    total_clicks = analytics.get("clicks", 0)
    msg = (f"<blockquote>🛠️ sʜᴏʀᴛᴇɴᴇer {num}</blockquote>\n" f"›› <b>sᴛᴀᴛᴜs:</b> <code>{'✔️ ᴀᴄᴛɪᴠᴇ' if status_val else '❌ ɪɴᴀᴄᴛɪᴠᴇ'}</code>\n" f"›› <b>ᴜʀʟ:</b> <code>{url_val}</code>\n" f"›› <b>ᴛᴜᴛ:</b> <code>{tut_val}</code>")
    status_text = "❌ ᴅɪsᴀʙʟᴇ" if status_val else "✔️ ᴇɴᴀʙʟᴇ"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(status_text, f'toggle_status_{num}')], [InlineKeyboardButton('ᴠᴇʀɪꜰɪᴇᴅ: ' + str(total_clicks), f'clicks_stats_{num}')], [InlineKeyboardButton('sᴇᴛ ᴜʀʟ', f'set_url_{num}'), InlineKeyboardButton('sᴇᴛ ᴀᴘɪ', f'set_api_{num}')], [InlineKeyboardButton('sᴇᴛ ᴛᴜᴛ', f'set_tut_{num}'), InlineKeyboardButton('ᴛᴇsᴛ', f'test_api_{num}')], [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'manage_shortners')]])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^clicks_stats_(1|2|3)$"))
async def stats_alert_callback(client, query):
    num = query.data.split("_")[2]
    analytics = await client.mongodb.db.shortner_analytics.find_one({"shortner_id": int(num)}) or {}
    clicks = analytics.get("clicks", 0)
    await query.answer(f"Shortener {num}: {clicks} verifications today!", show_alert=True)

@Client.on_callback_query(filters.regex("^toggle_status_(1|2|3)$"))
async def toggle_shortner_status(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    num = query.data.split("_")[2]
    current_status = getattr(config, f"SHORT_STATUS_{num}", True)
    new_status = not current_status
    setattr(config, f"SHORT_STATUS_{num}", new_status)
    await client.mongodb.db.shortner_config.update_one({"shortner_id": int(num)}, {"$set": {"enabled": new_status}}, upsert=True)
    await query.answer(f"Shortener {num} {'ON' if new_status else 'OFF'}!", show_alert=True)
    await edit_specific_shortner(client, query)

@Client.on_callback_query(filters.regex("^set_(url|api|tut)_(1|2|3)$"))
async def process_shortner_inputs(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    _, field, num = query.data.split("_")
    examples = {"url": "gplinks.com", "api": "540e6d65...", "tut": "https://t.me/channel"}
    await query.message.edit_text(f"<b>📥 sᴇɴᴅ ɴᴇᴡ {field.upper()} ꜰᴏʀ sʜᴏʀᴛᴇɴᴇer {num} (60s):</b>\n\n<b>ᴇx:</b> <code>{examples[field]}</code>")
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        new_value = res.text.strip()
        if field == "url":
            new_value = new_value.replace('https://', '').replace('http://', '').replace('/', '')
        setattr(config, f"SHORT_{field.upper()}_{num}", new_value)
        db_field_map = {"url": "short_url", "api": "short_api", "tut": "tutorial_link"}
        await client.mongodb.db.shortner_config.update_one({"shortner_id": int(num)}, {"$set": {db_field_map[field]: new_value}}, upsert=True)
        await res.delete()
        await query.message.edit_text(f"<blockquote><b>✓ sʜᴏʀᴛᴇɴᴇer {num} {field.upper()} ᴜᴘᴅᴀᴛᴇᴅ!</b></blockquote>\n\n›› <code>{new_value}</code>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', f'edit_short_{num}')]]))
    except ListenerTimeout:
        await query.message.edit_text("<b>✗ ᴛɪᴍᴇᴏᴜᴛ!</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', f'edit_short_{num}')]]))

@Client.on_callback_query(filters.regex("^test_api_(1|2|3)$"))
async def test_shortner_connectivity(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    num = query.data.split("_")[2]
    url_val = getattr(config, f"SHORT_URL_{num}", None)
    api_val = getattr(config, f"SHORT_API_{num}", None)
    if not url_val or not api_val or url_val == "None" or api_val == "None":
        return await query.answer("✗ URL or API Key missing!", show_alert=True)
    await query.answer("⏳ Testing...")
    try:
        original_url = getattr(client, 'shortner_url', None)
        original_api = getattr(client, 'shortner_api', None)
        client.shortner_url = url_val
        client.shortner_api = api_val
        test_link = get_short("https://t.me/PRIME_SMP", client)
        client.shortner_url = original_url
        client.shortner_api = original_api
        if test_link and test_link.startswith("http"):
            msg = f"<blockquote><b>✓ sʜᴏʀᴛᴇɴᴇer {num} ᴡᴏʀᴋɪɴɢ!</b></blockquote>\n\n›› {test_link}"
        else:
            msg = f"<blockquote><b>✗ ᴛᴇsᴛ ꜰᴀɪʟᴇᴅ!</b></blockquote>\n\n›› ᴄʜᴇᴄᴋ ᴀᴘɪ ᴛᴏᴋᴇɴ."
    except Exception as e:
        msg = f"<blockquote><b>✗ ᴇʀʀᴏʀ!</b></blockquote>\n\n›› <code>{str(e)}</code>"
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', f'edit_short_{num}')]]))

@Client.on_callback_query(filters.regex("^fsub$"))
async def fsub(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    if client.fsub_dict:
        ch_list = []
        for channel_id, channel_data in client.fsub_dict.items():
            name = channel_data[0] if channel_data and len(channel_data) > 0 else "Unknown"
            req = "✓ ʀᴇǫ" if channel_data[2] else "✗ ʀᴇǫ"
            timer = f"ᴛɪᴍᴇʀ: {channel_data[3]}ᴍ" if channel_data[3] > 0 else "ᴛɪᴍᴇʀ: ∞"
            ch_list.append(f"• <code>{name}</code> (<code>{channel_id}</code>) - {req}, {timer}")
        channels_display = "\n".join(ch_list)
    else:
        channels_display = "<i>ɴᴏ ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs</i>"
    msg = f"<b>◍ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛᴛɪɴɢs</b>\n\n{channels_display}\n\n<b>ᴜsᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ:</b>"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('›› ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ', 'add_fsub'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ', 'remove_fsub')], [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)
