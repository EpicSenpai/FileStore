from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.pyromod import ListenerTimeout
import config
from plugins.shortner import get_short

#===============================================================#
# HIGH-PRIORITY CORE CALLBACK MODULES (GLOBAL NAVIGATION FIX)
#===============================================================#

@Client.on_callback_query(filters.regex("^home$"))
async def back_to_home_callback(client: Client, query: CallbackQuery):
    await query.answer("↩️ Returning back to home dashboard...")
    user_id = query.from_user.id
    
    buttons = [[InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="ABOUT"), InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data='close')]]
    if user_id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("• ꜱᴇᴛᴛɪɴɢs •", callback_data="settings")])
        
    start_caption = config.MESSAGES.get('START', '').format(
        first=query.from_user.first_name,
        last=query.from_user.last_name or "",
        username=None if not query.from_user.username else '@' + query.from_user.username,
        mention=query.from_user.mention,
        id=user_id
    )
    
    try:
        await query.message.edit_caption(
            caption=start_caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception:
        try:
            await query.message.edit_text(
                text=start_caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            pass

@Client.on_callback_query(filters.regex("^ABOUT$"))
async def render_about_callback_query(client: Client, query: CallbackQuery):
    await query.answer("ℹ️ Loading about documentation details...")
    
    about_text = config.MESSAGES.get('ABOUT', '').format(
        bot_name=client.username
    )
    
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
# PAGE 1: CORE BOT SETTINGS PANEL
#===============================================================#

@Client.on_callback_query(filters.regex("^settings$"))
async def settings(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    total_fsub = len(client.fsub_dict)
    request_enabled = sum(1 for data in client.fsub_dict.values() if data[2])
    timer_enabled = sum(1 for data in client.fsub_dict.values() if data[3] > 0)
    
    total_db_channels = len(getattr(client, 'db_channels', {}))
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    msg = f"""<blockquote>✦ sᴇᴛᴛɪɴgs ᴏғ @{client.username} (ᴘᴀɢᴇ 1)</blockquote>
›› <b>ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_fsub}</code> (ʀᴇǫᴜᴇsᴛ: {request_enabled}, ᴛɪᴍᴇʀ: {timer_enabled})
›› <b>ᴅʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{total_db_channels}</code> (ᴘʀɪᴍᴀʀʏ: <code>{primary_db}</code>)
›› <b>ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:</b> <code>{client.auto_del}</code>
›› <b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:</b> <code>{"✓ ᴛʀᴜᴇ" if client.protect else "✗ ꜰᴀʟsᴇ"}</code>
›› <b>ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:</b> <code>{"✓ ᴛʀᴜᴇ" if client.disable_btn else "✗ ꜰᴀʟsᴇ"}</code>
›› <b>ʀᴇᴘʟʏ ᴛᴇxᴛ:</b> <code>{client.reply_text if client.reply_text else 'ɴᴏɴᴇ'}</code>
›› <b>ᴀᴅᴍɪɴs:</b> <code>{len(client.admins)}</code>

<blockquote><u><b>≡ ᴍᴜʟᴛɪ-sʜᴏʀᴛᴇɴᴇʀ sᴛᴀᴛᴜs:</b></u></blockquote>
›› <b>sʜᴏʀᴛɴᴇʀ 1:</b> <code>{getattr(config, 'SHORT_URL_1', 'None')}</code> [<code>{"✔️ ᴏɴ" if getattr(config, 'SHORT_STATUS_1', True) else "❌ ᴏғғ"}</code>]
›› <b>sʜᴏʀᴛɴᴇʀ 2:</b> <code>{getattr(config, 'SHORT_URL_2', 'None')}</code> [<code>{"✔️ ᴏɴ" if getattr(config, 'SHORT_STATUS_2', True) else "❌ ᴏғғ"}</code>]
›› <b>sʜᴏʀᴛɴᴇʀ 3:</b> <code>{getattr(config, 'SHORT_URL_3', 'None')}</code> [<code>{"✔️ ᴏɴ" if getattr(config, 'SHORT_STATUS_3', True) else "❌ ᴏғғ"}</code>]
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs', 'fsub'), InlineKeyboardButton('ᴅʙ ᴄʜᴀɴɴᴇʟs', 'db_channels')],
        [InlineKeyboardButton('ᴀᴅᴍɪɴs', 'admins'), InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', 'auto_del')],
        [InlineKeyboardButton('ʜᴏᴍᴇ', 'home'), InlineKeyboardButton('›› ɴᴇxᴛ', 'settings_page_2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#
# PAGE 2: MULTI-SHORTENER DYNAMIC TOGGLE OVERVIEW
#===============================================================#

@Client.on_callback_query(filters.regex("^settings_page_2$"))
async def settings_page_2(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    total_fsub = len(client.fsub_dict)
    total_db_channels = len(getattr(client, 'db_channels', {}))
    
    msg = f"""<blockquote>✦ sᴇᴛᴛɪɴgs ᴏғ @{client.username} (ᴘᴀɢᴇ 2)</blockquote>
›› <b><b>ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs:</b></b> <code>{total_fsub}</code>
›› <b><b>ᴅʙ ᴄʜᴀɴɴᴇʟs:</b></b> <code>{total_db_channels}</code>
›› <b><b>ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:</b></b> <code>{"✓ ᴛʀᴜᴇ" if client.protect else "✗ ꜰᴀʟsᴇ"}</code>
›› <b><b>ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:</b></b> <code>{"✓ ᴛʀᴜᴇ" if client.disable_btn else "✗ ꜰᴀʟsᴇ"}</code>

<blockquote><u><b>≡ 1sᴛ sʜᴏʀᴛᴇɴᴇʀ sᴇᴛᴛɪɴgs:</b></u></blockquote>
›› <b>sᴛᴀᴛᴜs:</b> <code>{"✔️ ᴇɴᴀʙʟᴇᴅ" if getattr(config, 'SHORT_STATUS_1', True) else "❌ ᴅɪsᴀʙʟᴇᴅ"}</code>
›› <b>ᴜʀʟ:</b> <code>{getattr(config, 'SHORT_URL_1', 'None')}</code>

<blockquote><u><b>≡ 2ɴᴅ sʜᴏʀᴛᴇɴᴇʀ sᴇᴛᴛɪɴgs:</b></u></blockquote>
›› <b>sᴛᴀᴛᴜs:</b> <code>{"✔️ ᴇɴᴀʙʟᴇᴅ" if getattr(config, 'SHORT_STATUS_2', True) else "❌ ᴅɪsᴀʙʟᴇᴅ"}</code>
›› <b>ᴜʀʟ:</b> <code>{getattr(config, 'SHORT_URL_2', 'None')}</code>

<blockquote><u><b>≡ 3ʀᴅ sʜᴏʀᴛᴇɴᴇʀ sᴇᴛᴛɪɴgs:</b></u></blockquote>
›› <b>sᴛᴀᴛᴜs:</b> <code>{"✔️ ᴇɴᴀʙʟᴇᴅ" if getattr(config, 'SHORT_STATUS_3', True) else "❌ ᴅɪsᴀʙʟᴇᴅ"}</code>
›› <b>ᴜʀʟ:</b> <code>{getattr(config, 'SHORT_URL_3', 'None')}</code>
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ', 'protect'), InlineKeyboardButton('ᴘʜᴏᴛᴏs', 'photos')],
        [InlineKeyboardButton('ᴛᴇxᴛs', 'texts'), InlineKeyboardButton('🛠️ sʜᴏʀᴛɴᴇʀ sᴇᴛᴛɪɴgs', 'manage_shortners')],
        [InlineKeyboardButton('‹ ᴘʀᴇᴠ', 'settings'), InlineKeyboardButton('ʜᴏᴍᴇ', 'home')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#
# MULTI-SHORTENER MANAGEMENT INTERFACE PANEL
#===============================================================#

@Client.on_callback_query(filters.regex("^manage_shortners$"))
async def manage_shortners(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    msg = f"""<blockquote>✦ ᴍᴜʟᴛɪ-sʜᴏʀᴛᴇɴᴇʀ ᴍᴀɴᴀɢᴇᴍᴇnt ᴘᴀɴᴇʟ</blockquote>

›› <b>1sᴛ:</b> <code>{getattr(config, 'SHORT_URL_1', 'None')}</code> [<code>{"✔️ ᴏɴ" if getattr(config, 'SHORT_STATUS_1', True) else "❌ ᴏғғ"}</code>]
›› <b>2ɴᴅ:</b> <code>{getattr(config, 'SHORT_URL_2', 'None')}</code> [<code>{"✔️ ᴏɴ" if getattr(config, 'SHORT_STATUS_2', True) else "❌ ᴏғғ"}</code>]
›› <b>3ʀᴅ:</b> <code>{getattr(config, 'SHORT_URL_3', 'None')}</code> [<code>{"✔️ ᴏɴ" if getattr(config, 'SHORT_STATUS_3', True) else "❌ ᴏғғ"}</code>]

__<b>ᴄʟɪᴄᴋ ᴏɴ ᴀɴʏ sʜᴏʀᴛᴇɴᴇʀ ʙᴇʟᴏᴡ ᴛᴏ ᴄʜᴀɴɢᴇ ɪᴛs sᴇᴛᴛɪɴɢs, sᴡɪᴛᴄʜ sᴛᴀᴛᴜs ᴏʀ ʀᴜɴ ᴀ ᴛᴇsᴛ sʜᴏʀᴛᴇɴ!</b>__"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('sʜᴏʀᴛɴᴇʀ 1', 'edit_short_1'), InlineKeyboardButton('sʜᴏʀᴛɴᴇer 2', 'edit_short_2')],
        [InlineKeyboardButton('sʜᴏʀᴛɴᴇer 3', 'edit_short_3')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings_page_2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#
# EXPLICIT PARAMETER LAYER FOR INDIVIDUAL SHORTENERS
#===============================================================#

@Client.on_callback_query(filters.regex("^edit_short_(1|2|3)$"))
async def edit_specific_shortner(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    num = query.data.split("_")[2]
    url_val = getattr(config, f"SHORT_URL_{num}", "None")
    tut_val = getattr(config, f"SHORT_TUT_{num}", "None")
    status_val = getattr(config, f"SHORT_STATUS_{num}", True)
    
    # Fetch real-time total clicks from MongoDB dynamically
    analytics = await client.mongodb.db.shortner_analytics.find_one({"shortner_id": int(num)}) or {}
    total_clicks = analytics.get("clicks", 0)
    
    msg = f"""<blockquote>🛠️ ᴄᴏɴꜰɪɢᴜʀᴇ sʜᴏʀᴛᴇɴᴇʀ {num}</blockquote>
›› <b>sᴛᴀᴛᴜs:</b> <code>{"✔️ ᴀᴄᴛɪᴠᴇ / ᴏɴ" if status_val else "❌ ɪɴᴀᴄᴛɪᴠᴇ / ᴏғғ"}</code>
›› <b>ᴄᴜʀʀᴇɴᴛ ᴜʀʟ:</b> <code>{url_val}</code>
›› <b>ᴄᴜʀʀᴇɴᴛ ᴛᴜᴛᴏʀɪᴀʟ:</b> <code>{tut_val}</code>

__<b>ᴍᴀɴᴀɢᴇ sᴡɪᴛᴄʜ, ᴜᴘᴅᴀᴛᴇ ᴘᴀʀᴀᴍᴇᴛᴇʀs ᴏʀ ᴛᴇsᴛ API connectivity:</b>__"""
    
    status_text = "❌ ᴅɪsᴀʙʟᴇ / ᴛᴜʀɴ ᴏғғ" if status_val else "✔️ ᴇɴᴀʙʟᴇ / ᴛᴜʀɴ ᴏɴ"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(status_text, f'toggle_status_{num}')],
        [InlineKeyboardButton('ᴠᴇʀɪꜰɪᴇᴅ ᴛᴏᴅᴀʏ: ' + str(total_clicks), f'clicks_stats_{num}')],
        [InlineKeyboardButton('sᴇᴛ ᴜʀʟ', f'set_url_{num}'), InlineKeyboardButton('sᴇᴛ ᴀᴘɪ', f'set_api_{num}')],
        [InlineKeyboardButton('sᴇᴛ ᴛᴜᴛᴏʀɪᴀʟ', f'set_tut_{num}'), InlineKeyboardButton('ᴛᴇsᴛ sʜᴏʀᴛɴᴇʀ', f'test_api_{num}')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'manage_shortners')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#

@Client.on_callback_query(filters.regex("^clicks_stats_(1|2|3)$"))
async def stats_alert_callback(client, query):
    num = query.data.split("_")[2]
    analytics = await client.mongodb.db.shortner_analytics.find_one({"shortner_id": int(num)}) or {}
    clicks = analytics.get("clicks", 0)
    await query.answer(f"📊 Shortener {num} has processed {clicks} complete bypass verifications today!", show_alert=True)

#===============================================================#

@Client.on_callback_query(filters.regex("^toggle_status_(1|2|3)$"))
async def toggle_shortner_status(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    num = query.data.split("_")[2]
    var_name = f"SHORT_STATUS_{num}"
    current_status = getattr(config, var_name, True)
    
    new_status = not current_status
    setattr(config, var_name, new_status)
    
    # Save the status persistently to database
    await client.mongodb.db.shortner_config.update_one(
        {"shortner_id": int(num)}, 
        {"$set": {"enabled": new_status}}, 
        upsert=True
    )
    
    await query.answer(f"Shortener {num} Turned {'ON' if new_status else 'OFF'}!", show_alert=True)
    await edit_specific_shortner(client, query)

#===============================================================#

@Client.on_callback_query(filters.regex("^set_(url|api|tut)_(1|2|3)$"))
async def process_shortner_inputs(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    _, field, num = query.data.split("_")
    
    field_names = {"url": "sʜᴏʀᴛɴᴇʀ ᴅᴏᴍᴀɪɴ", "api": "ᴀᴘɪ ᴛᴏᴋᴇɴ ᴋᴇʏ", "tut": "ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ ʟɪɴᴋ"}
    examples = {"url": "gplinks.com", "api": "540e6d65d2851a9c645d...", "tut": "https://t.me/How_To_Open_Shortners"}
    
    msg = f"""<blockquote>📥 ᴜᴘᴅᴀᴛᴇ {field_names[field]} ꜰᴏʀ sʜᴏʀᴛᴇɴᴇʀ {num}</blockquote>

__<b>sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ᴠᴀʟᴜᴇ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!</b>__

**<b>ᴇxᴀᴍᴘʟᴇ:</b>** <code>{examples[field]}</code>"""
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        new_value = res.text.strip()
        
        # Clean inputs if domain
        if field == "url":
            new_value = new_value.replace('https://', '').replace('http://', '').replace('/', '')
            
        target_var = f"SHORT_{field.upper()}_{num}"
        setattr(config, target_var, new_value)
        
        # Persistent write parameters into MongoDB cluster
        db_field_map = {"url": "short_url", "api": "short_api", "tut": "tutorial_link"}
        await client.mongodb.db.shortner_config.update_one(
            {"shortner_id": int(num)}, 
            {"$set": {db_field_map[field]: new_value}}, 
            upsert=True
        )
                
        await query.message.edit_text(f"<blockquote><b>✓ sʜᴏʀᴛᴇɴᴇʀ {num} {field.upper()} ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b></blockquote>\n\n›› <b>ɴᴇᴡ ᴠᴀʟᴜᴇ:</b> <code>{new_value}</code>", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', f'edit_short_{num}')]]))
        await res.delete()
    except ListenerTimeout:
        await query.message.edit_text("<blockquote><b>✗ ᴛɪᴍᴇᴏᴜᴛ! ʏᴏᴜ ᴅɪᴅ ɴᴏᴛ sᴇɴᴅ ᴀɴʏ ᴛᴇxᴛ ᴡɪᴛʜɪɴ 60 sᴇᴄᴏɴᴅs.</b></blockquote>", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', f'edit_short_{num}')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^test_api_(1|2|3)$"))
async def test_shortner_connectivity(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs <b>ᴄᴀɴ ᴜsᴇ ᴛʜɪs!</b>', show_alert=True)
    
    num = query.data.split("_")[2]
    url_val = getattr(config, f"SHORT_URL_{num}", None)
    api_val = getattr(config, f"SHORT_API_{num}", None)
    
    if not url_val or not api_val or url_val == "None" or api_val == "None":
        return await query.answer("✗ URL or API Key is missing/empty!", show_alert=True)
        
    await query.answer("⏳ Testing connectivity... Please wait.")
    
    try:
        # Temporary runtime mount to invoke api validation test link
        client.shortner_url = url_val
        client.shortner_api = api_val
        
        test_link = get_short("https://t.me/PRIME_SMP", client)
        if test_link and test_link.startswith("http"):
            msg = f"<blockquote><b>✓ ᴛᴇsᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴘᴀssᴇᴅ!</b></blockquote>\n\n›› <b>sʜᴏʀᴛᴇɴᴇʀ {num} ɪs ᴡᴏʀᴋɪɴɢ ᴘᴇʀꜰᴇᴄᴛʟʏ!</b>\n›› <b>ɢᴇɴᴇʀᴀᴛᴇᴅ ʟɪɴᴋ:</b> {test_link}"
        else:
            msg = f"<blockquote><b>✗ ᴛᴇsᴛ ꜰᴀɪʟᴇᴅ!</b></blockquote>\n\n›› sʜᴏʀᴛᴇɴᴇʀ website returned an invalid response. Check API token syntax."
    except Exception as e:
        msg = f"<blockquote><b>✗ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴇʀʀᴏʀ!</b></blockquote>\n\n›› <b>ᴇʀʀᴏʀ:</b> <code>{str(e)}</code>"
        
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', f'edit_short_{num}')]]))

#===============================================================#
# SYSTEM CONFIG BACKWARD COMPATIBLE HANDLERS
#===============================================================#

@Client.on_callback_query(filters.regex("^fsub$"))
async def fsub(client, query):
    if client.fsub_dict:
        channel_list = []
        for channel_id, channel_data in client.fsub_dict.items():
            channel_name = channel_data[0] if channel_data and len(channel_data) > 0 else "Unknown"
            request_status = "✓ ʀᴇǫᴜᴇsᴛ" if channel_data[2] else "✗ ʀᴇǫᴜᴇsᴛ"
            timer_status = f"ᴛɪᴍᴇʀ: {channel_data[3]}ᴍ" if channel_data[3] > 0 else "ᴛɪᴍᴇʀ: ∞"
            channel_list.append(f"• <code>{channel_name}</code> (<code>{channel_id}</code>) - {request_status}, {timer_status}")
        channels_display = "\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    
    msg = f"""<blockquote>✦ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛᴛɪɴgs</blockquote>
›› <b>ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:</b>
{channels_display}

__<b>ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀᴅᴅ ᴏʀ ʀᴇᴍᴏᴠᴇ ᴀ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ ʙᴀsᴇᴅ ᴏɴ ʏᴏᴜʀ ɴᴇᴇᴅs!</b>__"""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('›› ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ', 'add_fsub'), InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ', 'rm_fsub')], [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]])
    await query.message.edit_text(msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^db_channels$"))
async def db_channels(client, query):
    if not query.from_user.id in client.admins: 
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    db_channels_data = getattr(client, 'db_channels', {})
    if db_channels_data:
        channel_list = []
        for channel_id_str, channel_data in db_channels_data.items():
            channel_name = channel_data.get('name', 'Unknown')
            is_primary = "✓ ᴘʀɪᴍᴀʀʏ" if channel_data.get('is_primary', False) else "• sᴇᴄᴏɴᴅᴀʀʏ"
            is_active = "✓ ᴀᴄᴛɪᴠᴇ" if channel_data.get('is_active', True) else "✗ ɪɴᴀᴄᴛɪᴠᴇ"
            channel_list.append(f"• <code>{channel_name}</code> (<code>{channel_id_str}</code>)\n  {is_primary} | {is_active}")
        channels_display = "\n\n".join(channel_list)
    else: 
        channels_display = "_ɴᴏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    primary_db = getattr(client, 'primary_db_channel', client.db)
    msg = f"""<blockquote>✦ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs sᴇᴛᴛɪɴɢs</blockquote>\n›› <b>ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴍᴀʀʏ ᴅʙ:</b> <code>{primary_db}</code>\n›› <b>ᴛᴏᴛᴀʟ ᴅʙ ᴄʜᴀɴɴᴇʟs:</b> <code>{len(db_channels_data)}</code> \n\n**<b>ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:</b>**\n{channels_display}\n\n__<b>ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs!</b>__"""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('›› ᴀᴅᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'add_db_channel'), InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'rm_db_channel')], [InlineKeyboardButton('›› sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db'), InlineKeyboardButton('›› sᴛᴀᴛᴜs', 'toggle_db_status')], [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    
