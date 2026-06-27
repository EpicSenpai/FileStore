from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, InputMediaPhoto
from pyrogram.errors.pyromod import ListenerTimeout
import config
from plugins.shortner import get_short

#===============================================================#
# HELPER: BUILD SETTINGS PAGE 1 MESSAGE + MARKUP
#===============================================================#

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

#===============================================================#
# /SETTINGS COMMAND
#===============================================================#

@Client.on_message(filters.command("settings") & filters.private)
async def settings_text_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text if client.reply_text else "Access Denied!")

    msg, reply_markup = _build_settings_page1_msg(client)
    image_url = config.MESSAGES.get("START_PHOTO", "https://litter.catbox.moe/q9aqxh.jpg")
    await message.reply_photo(photo=image_url, caption=msg, reply_markup=reply_markup)

#===============================================================#
# HOME / ABOUT / CLOSE CALLBACKS
#===============================================================#

@Client.on_callback_query(filters.regex("^home$"))
async def back_to_home_callback(client: Client, query: CallbackQuery):
    await query.answer("↩️ Returning back to home dashboard...")
    user_id = query.from_user.id

    buttons = [[InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="ABOUT"), InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data='close')]]
    if user_id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("• sᴇᴛᴛɪɴɢs •", callback_data="settings")])

    start_caption = config.MESSAGES.get('START', '').format(
        first=query.from_user.first_name,
        last=query.from_user.last_name or "",
        username=None if not query.from_user.username else '@' + query.from_user.username,
        mention=query.from_user.mention,
        id=user_id
    )

    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=config.MESSAGES.get("START_PHOTO", ""), caption=start_caption),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
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

#===============================================================#
# PAGE 1 SETTINGS CALLBACK
#===============================================================#

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

#===============================================================#
# ADMINS CALLBACK — FIXED (was not registered before)
#===============================================================#

@Client.on_callback_query(filters.regex("^admins$"))
async def admins_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()
    msg = (
        f"<blockquote><b>⚙️ ᴀᴅᴍɪɴ sᴇᴛᴛɪɴɢs:</b></blockquote>\n"
        f"<b>ᴀᴅᴍɪɴ ᴜsᴇʀ ɪᴅs:</b> {', '.join(f'<code>{a}</code>' for a in client.admins)}\n\n"
        f"<i>ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴀᴅᴅ/ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴs!</i>"
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
# AUTO DELETE CALLBACK — FIXED
#===============================================================#

@Client.on_callback_query(filters.regex("^auto_del$"))
async def auto_del_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()

    msg = (
        f"<blockquote><b>⏱️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ sᴇᴛᴛɪɴɢs</b></blockquote>\n\n"
        f"›› <b>ᴄᴜʀʀᴇɴᴛ ᴛɪᴍᴇʀ:</b> <code>{client.auto_del} sᴇᴄᴏɴᴅs</code>\n"
        f"›› <b>0 = ᴅɪsᴀʙʟᴇᴅ</b>\n\n"
        f"<i>sᴇɴᴅ ɴᴇᴡ ᴠᴀʟᴜᴇ ɪɴ sᴇᴄᴏɴᴅs (ᴇɢ: 1800 = 30 ᴍɪɴs, 0 = ᴅɪsᴀʙʟᴇ)</i>"
    )
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('✏️ sᴇᴛ ᴛɪᴍᴇʀ', 'set_auto_del')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]
    ])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^set_auto_del$"))
async def set_auto_del_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()

    await query.message.edit_text(
        "<b>⏱️ sᴇɴᴅ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ ɪɴ sᴇᴄᴏɴᴅs ᴡɪᴛʜɪɴ 60s:</b>\n\n"
        "<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>1800</code> (30 mins), <code>3600</code> (1 hour), <code>0</code> (disable)"
    )
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        new_val = int(res.text.strip())
        client.auto_del = new_val
        # Save to DB
        await client.mongodb.user_data.update_one(
            {"_id": "bot_settings"},
            {"$set": {"auto_del": new_val}},
            upsert=True
        )
        await res.delete()
        await query.message.edit_text(
            f"<blockquote><b>✓ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴜᴘᴅᴀᴛᴇᴅ!</b></blockquote>\n\n"
            f"›› ɴᴇᴡ ᴠᴀʟᴜᴇ: <code>{new_val} sᴇᴄᴏɴᴅs</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'auto_del')]])
        )
    except ListenerTimeout:
        await query.message.edit_text(
            "<b>✗ ᴛɪᴍᴇᴏᴜᴛ! ɴᴏ ɪɴᴘᴜᴛ ʀᴇᴄᴇɪᴠᴇᴅ.</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'auto_del')]])
        )
    except ValueError:
        await query.message.edit_text(
            "<b>✗ ɪɴᴠᴀʟɪᴅ ᴠᴀʟᴜᴇ! sᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ ᴏɴʟʏ.</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'auto_del')]])
        )

#===============================================================#
# PROTECT CONTENT CALLBACK — FIXED
#===============================================================#

@Client.on_callback_query(filters.regex("^protect$"))
async def protect_content_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)

    # Toggle protect
    client.protect = not client.protect
    await client.mongodb.user_data.update_one(
        {"_id": "bot_settings"},
        {"$set": {"protect": client.protect}},
        upsert=True
    )
    status = "✓ ᴇɴᴀʙʟᴇᴅ" if client.protect else "✗ ᴅɪsᴀʙʟᴇᴅ"
    await query.answer(f"ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ {status}!", show_alert=True)

    # Refresh page 2
    await settings_page_2(client, query)

#===============================================================#
# DB CHANNELS CALLBACK — FIXED
#===============================================================#

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
            is_primary = ch_data.get('is_primary', False)
            name = ch_data.get('name', 'Unknown')
            primary_tag = " [ᴘʀɪᴍᴀʀʏ ✓]" if is_primary else ""
            ch_list.append(f"• <code>{name}</code> (<code>{ch_id_str}</code>){primary_tag}")
        channels_display = "\n".join(ch_list)
    else:
        channels_display = f"<i>ᴏɴʟʏ ᴅᴇꜰᴀᴜʟᴛ ᴅʙ: <code>{primary}</code></i>"

    msg = (
        f"<blockquote><b>🗄️ ᴅʙ ᴄʜᴀɴɴᴇʟ sᴇᴛᴛɪɴɢs</b></blockquote>\n\n"
        f"›› <b>ᴛᴏᴛᴀʟ:</b> <code>{len(db_channels)}</code>\n"
        f"›› <b>ᴘʀɪᴍᴀʀʏ:</b> <code>{primary}</code>\n\n"
        f"{channels_display}\n\n"
        f"<i>ᴜsᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴅʙ ᴄʜᴀɴɴᴇʟs!</i>"
    )
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('➕ ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ', 'add_db_ch'), InlineKeyboardButton('➖ ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ', 'remove_db_ch')],
        [InlineKeyboardButton('⭐ sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]
    ])
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except Exception:
        await query.message.edit_caption(caption=msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^add_db_ch$"))
async def add_db_channel_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()

    await query.message.edit_text(
        "<b>🗄️ sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴛᴏ ᴀᴅᴅ ᴀs ᴅʙ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜɪɴ 60s:</b>\n\n"
        "<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>-1001234567890</code>\n\n"
        "<i>ᴍᴀᴋᴇ sᴜʀᴇ ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ!</i>"
    )
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
        await query.message.edit_text(
            f"<blockquote><b>✓ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴀᴅᴅᴇᴅ!</b></blockquote>\n\n"
            f"›› <b>ɴᴀᴍᴇ:</b> {chat.title}\n›› <b>ɪᴅ:</b> <code>{channel_id}</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]])
        )
    except ListenerTimeout:
        await query.message.edit_text(
            "<b>✗ ᴛɪᴍᴇᴏᴜᴛ!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]])
        )
    except Exception as e:
        await query.message.edit_text(
            f"<b>✗ ᴇʀʀᴏʀ: {e}</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]])
        )

@Client.on_callback_query(filters.regex("^remove_db_ch$"))
async def remove_db_channel_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()

    await query.message.edit_text(
        "<b>🗄️ sᴇɴᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴡɪᴛʜɪɴ 60s:</b>\n\n"
        "<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>-1001234567890</code>"
    )
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id = int(res.text.strip())

        if str(channel_id) in getattr(client, 'db_channels', {}):
            client.db_channels.pop(str(channel_id), None)
            await client.mongodb.remove_db_channel(channel_id)
            text = f"<blockquote><b>✓ ᴅʙ ᴄʜᴀɴɴᴇʟ <code>{channel_id}</code> ʀᴇᴍᴏᴠᴇᴅ!</b></blockquote>"
        else:
            text = f"<b>✗ ᴄʜᴀɴɴᴇʟ <code>{channel_id}</code> ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ᴅʙ ʟɪsᴛ!</b>"

        await res.delete()
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]])
        )
    except ListenerTimeout:
        await query.message.edit_text(
            "<b>✗ ᴛɪᴍᴇᴏᴜᴛ!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]])
        )
    except Exception as e:
        await query.message.edit_text(
            f"<b>✗ ᴇʀʀᴏʀ: {e}</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]])
        )

@Client.on_callback_query(filters.regex("^set_primary_db$"))
async def set_primary_db_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()

    await query.message.edit_text(
        "<b>⭐ sᴇɴᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴛᴏ sᴇᴛ ᴀs ᴘʀɪᴍᴀʀʏ ᴅʙ ᴡɪᴛʜɪɴ 60s:</b>\n\n"
        "<i>ɴᴏᴛᴇ: ᴄʜᴀɴɴᴇʟ ᴍᴜsᴛ ᴀʟʀᴇᴀᴅʏ ʙᴇ ɪɴ ᴅʙ ᴄʜᴀɴɴᴇʟ ʟɪsᴛ!</i>"
    )
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id = int(res.text.strip())

        db_channels = getattr(client, 'db_channels', {})
        if str(channel_id) not in db_channels:
            await res.delete()
            return await query.message.edit_text(
                f"<b>✗ ᴄʜᴀɴɴᴇʟ <code>{channel_id}</code> ɴᴏᴛ ꜰᴏᴜɴᴅ! ᴀᴅᴅ ɪᴛ ꜰɪʀsᴛ.</b>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]])
            )

        # Reset all primaries, then set new one
        for ch_id_str in db_channels:
            db_channels[ch_id_str]['is_primary'] = False
        db_channels[str(channel_id)]['is_primary'] = True
        client.primary_db_channel = channel_id
        client.db = channel_id

        await client.mongodb.set_primary_db_channel(channel_id)
        await res.delete()
        await query.message.edit_text(
            f"<blockquote><b>✓ ᴘʀɪᴍᴀʀʏ ᴅʙ sᴇᴛ ᴛᴏ <code>{channel_id}</code>!</b></blockquote>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]])
        )
    except ListenerTimeout:
        await query.message.edit_text(
            "<b>✗ ᴛɪᴍᴇᴏᴜᴛ!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]])
        )

#===============================================================#
# PHOTOS & TEXTS CALLBACKS — FIXED
#===============================================================#

@Client.on_callback_query(filters.regex("^photos$"))
async def photos_callback(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    await query.answer()

    msg = (
        f"<blockquote><b>🖼️ ᴘʜᴏᴛᴏ sᴇᴛᴛɪɴɢs</b></blockquote>\n\n"
        f"›› <b>sᴛᴀʀᴛ ᴘʜᴏᴛᴏ:</b> <code>{config.MESSAGES.get('START_PHOTO', 'None')}</code>\n"
        f"›› <b>ꜰsᴜʙ ᴘʜᴏᴛᴏ:</b> <code>{config.MESSAGES.get('FSUB_PHOTO', 'None')}</code>\n"
        f"›› <b>sʜᴏʀᴛ ᴘɪᴄ:</b> <code>{config.MESSAGES.get('SHORT_PIC', 'None')}</code>\n\n"
        f"<i>ᴄʜᴏᴏsᴇ ᴡʜɪᴄʜ ᴘʜᴏᴛᴏ ᴛᴏ ᴜᴘᴅᴀᴛᴇ:</i>"
    )
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('sᴛᴀʀᴛ ᴘʜᴏᴛᴏ', 'set_photo_START_PHOTO'),
         InlineKeyboardButton('ꜰsᴜʙ ᴘʜᴏᴛᴏ', 'set_photo_FSUB_PHOTO')],
        [InlineKeyboardButton('sʜᴏʀᴛ ᴘɪᴄ', 'set_photo_SHORT_PIC')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings_page_2')]
    ])
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
    await query.message.edit_text(
        f"<b>🖼️ sᴇɴᴅ ɴᴇᴡ ᴘʜᴏᴛᴏ ᴜʀʟ ꜰᴏʀ <code>{photo_key}</code> ᴡɪᴛʜɪɴ 60s:</b>\n\n"
        f"<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>https://example.com/image.jpg</code>"
    )
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        new_url = res.text.strip()
        config.MESSAGES[photo_key] = new_url
        # Save to DB
        await client.mongodb.user_data.update_one(
            {"_id": "bot_messages"},
            {"$set": {photo_key: new_url}},
            upsert=True
        )
await client.mongodb.user_data.update_one(
            {"_id": "bot_messages"},
            {"$set": {photo_key: new_url}},
            upsert=True
        )
        await res.delete()   # ← try block ke andar
        await query.message.edit_text(
            f"<blockquote><b>✓ {photo_key} ᴜᴘᴅᴀᴛᴇᴅ!</b></blockquote>\n\n›› <code>{new_url}</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]])
        )
    except ListenerTimeout:
        await query.message.edit_text(
            "<b>✗ ᴛɪᴍᴇᴏᴜᴛ!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]])
        )
