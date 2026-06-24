from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.pyromod import ListenerTimeout
import config
import humanize

#===============================================================#

@Client.on_callback_query(filters.regex("^settings$"))
async def settings(client, query):
    total_fsub = len(client.fsub_dict)
    request_enabled = sum(1 for data in client.fsub_dict.values() if data[2])
    timer_enabled = sum(1 for data in client.fsub_dict.values() if data[3] > 0)
    
    total_db_channels = len(getattr(client, 'db_channels', {}))
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    msg = f"""<blockquote>✦ sᴇᴛᴛɪɴɢs ᴏғ @{client.username} (ᴘᴀɢᴇ 1)</blockquote>
›› **暗sᴜʙ ᴄʜᴀɴɴᴇʟs:** `{total_fsub}` (ʀᴇǫᴜᴇsᴛ: {request_enabled}, ᴛɪᴍᴇʀ: {timer_enabled})
›› **ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{total_db_channels}` (ᴘʀɪᴍᴀʀʏ: `{primary_db}`)
›› **ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:** `{client.auto_del}`
›› **ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:** `{"✓ ᴛʀᴜᴇ" if client.protect else "✗ ꜰᴀʟsᴇ"}`
›› **ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:** `{"✓ ᴛʀᴜᴇ" if client.disable_btn else "✗ ꜰᴀʟsᴇ"}`
›› **ʀᴇᴘʟʏ ᴛᴇxᴛ:** `{client.reply_text if client.reply_text else 'ɴᴏɴᴇ'}`
›› **ᴀᴅᴍɪɴs:** `{len(client.admins)}`

<blockquote><u>**≡ ᴍᴜʟᴛɪ-sʜᴏʀᴛᴇɴᴇʀ sᴛᴀᴛᴜs:**</u></blockquote>
›› **sʜᴏʀᴛɴᴇʀ 1:** `{config.SHORT_URL_1}`
›› **sʜᴏʀᴛɴᴇʀ 2:** `{config.SHORT_URL_2}`
›› **sʜᴏʀᴛɴᴇʀ 3:** `{config.SHORT_URL_3}`
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ', 'fsub'), InlineKeyboardButton('ᴅʙ ᴄʜᴀɴɴᴇʟꜱ', 'db_channels')],
        [InlineKeyboardButton('ᴀᴅᴍɪɴꜱ', 'admins'), InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', 'auto_del')],
        [InlineKeyboardButton('ʜᴏᴍᴇ', 'home'), InlineKeyboardButton('›› ɴᴇxᴛ', 'settings_page_2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^settings_page_2$"))
async def settings_page_2(client, query):
    total_fsub = len(client.fsub_dict)
    total_db_channels = len(getattr(client, 'db_channels', {}))
    
    msg = f"""<blockquote>✦ sᴇᴛᴛɪɴɢs ᴏғ @{client.username} (ᴘᴀɢᴇ 2)</blockquote>
›› **ꜰsᴜʙ ᴄʜᴀɴɴᴇʟs:** `{total_fsub}`
›› **ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{total_db_channels}`
›› **ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:** `{"✓ ᴛʀᴜᴇ" if client.protect else "✗ ꜰᴀʟsᴇ"}`
›› **ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:** `{"✓ ᴛʀᴜᴇ" if client.disable_btn else "✗ ꜰᴀʟsᴇ"}`

<blockquote><u>**≡ 1sᴛ sʜᴏʀᴛᴇɴᴇʀ sᴇᴛᴛɪɴɢs:**</u></blockquote>
›› **ᴜʀʟ:** `{config.SHORT_URL_1}`
›› **ᴀᴘɪ:** `{config.SHORT_API_1[:6] if config.SHORT_API_1 else 'ɴᴏᴛ sᴇᴛ'}*****`
›› **ᴛᴜᴛᴏʀɪᴀʟ:** `{config.SHORT_TUT_1}`

<blockquote><u>**≡ 2ɴᴅ sʜᴏʀᴛᴇɴᴇʀ sᴇᴛᴛɪɴɢs:**</u></blockquote>
›› **ᴜʀʟ:** `{config.SHORT_URL_2}`
›› **ᴀᴘɪ:** `{config.SHORT_API_2[:6] if config.SHORT_API_2 else 'ɴᴏᴛ sᴇᴛ'}*****`
›› **ᴛᴜᴛᴏʀɪᴀʟ:** `{config.SHORT_TUT_2}`

<blockquote><u>**≡ 3ʀᴅ sʜᴏʀᴛᴇɴᴇʀ sᴇᴛᴛɪɴɢs:**</u></blockquote>
›› **ᴜʀʟ:** `{config.SHORT_URL_3}`
›› **ᴀᴘɪ:** `{config.SHORT_API_3[:6] if config.SHORT_API_3 else 'ɴᴏᴛ sᴇᴛ'}*****`
›› **ᴛᴜᴛᴏʀɪᴀʟ:** `{config.SHORT_TUT_3}`
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ', 'protect'), InlineKeyboardButton('ᴘʜᴏᴛᴏs', 'photos')],
        [InlineKeyboardButton('ᴛᴇxᴛs', 'texts'), InlineKeyboardButton('🛠️ sʜᴏʀᴛɴᴇʀ sᴇᴛᴛɪɴɢs', 'manage_shortners')],
        [InlineKeyboardButton('‹ ᴘʀᴇᴠ', 'settings'), InlineKeyboardButton('ʜᴏᴍᴇ', 'home')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^manage_shortners$"))
async def manage_shortners(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    msg = f"""<blockquote>✦ ᴍᴜʟᴛɪ-sʜᴏʀᴛᴇɴᴇʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴘᴀɴᴇʟ</blockquote>

›› **1sᴛ:** `{config.SHORT_URL_1}`
›› **2ɴᴅ:** `{config.SHORT_URL_2}`
›› **3ʀᴅ:** `{config.SHORT_URL_3}`

__ᴄʟɪᴄᴋ ᴏɴ ᴀɴʏ sʜᴏʀᴛᴇɴᴇʀ ʙᴇʟᴏᴡ ᴛᴏ ᴄʜᴀɴɢᴇ ɪᴛs ᴜʀʟ, ᴀᴘɪ, ᴀɴᴅ sᴇᴘᴀʀᴀᴛᴇ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ line-by-line!__"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('🔧 sʜᴏʀᴛɴᴇʀ 1', 'edit_short_1'), InlineKeyboardButton('🔧 sʜᴏʀᴛɴᴇʀ 2', 'edit_short_2')],
        [InlineKeyboardButton('🔧 sʜᴏʀᴛɴᴇʀ 3', 'edit_short_3')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings_page_2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#

@Client.on_callback_query(filters.regex("^edit_short_(1|2|3)$"))
async def edit_specific_shortner(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    num = query.data.split("_")[2]
    url_val = getattr(config, f"SHORT_URL_{num}")
    tut_val = getattr(config, f"SHORT_TUT_{num}")
    
    msg = f"""<blockquote>🛠️ ᴄᴏɴꜰɪɢᴜʀᴇ sʜᴏʀᴛᴇɴᴇʀ {num}</blockquote>
›› **ᴄᴜʀʀᴇɴᴛ ᴜʀʟ:** `{url_val}`
›› **ᴄᴜʀʀᴇɴᴛ ᴛᴜᴛᴏʀɪᴀʟ:** `{tut_val}`

__sᴇʟᴇᴄᴛ ᴡʜɪᴄʜ ᴘᴀʀᴀᴍᴇᴛᴇʀ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ꜰᴏʀ ᴛʜɪs sᴘᴇᴄɪꜰɪᴄ sʜᴏʀᴛᴇɴᴇʀ ɴᴏᴅᴇ:__"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('🌐 sᴇᴛ ᴜʀʟ', f'set_url_{num}'), InlineKeyboardButton('🔑 sᴇᴛ ᴀᴘɪ', f'set_api_{num}')],
        [InlineKeyboardButton('🎬 sᴇᴛ ᴛᴜᴛᴏʀɪᴀʟ', f'set_tut_{num}')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'manage_shortners')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)

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

__sᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ᴠᴀʟᴜᴇ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!__

**ᴇxᴀᴍᴘʟᴇ:** `{examples[field]}`"""
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        new_value = res.text.strip()
        
        target_var = f"SHORT_{field.upper()}_{num}"
        setattr(config, target_var, new_value)
        
        if num == "1":
            setattr(config, f"SHORT_{field.upper()}", new_value)
            if field == "url":
                client.shortner_url = new_value
            elif field == "api":
                client.shortner_api = new_value
                
        await query.message.edit_text(f"<b>✓ sʜᴏʀᴛᴇɴᴇʀ {num} {field.upper()} ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!</b>\n\n›› **ɴᴇᴡ ᴠᴀʟᴜᴇ:** `{new_value}`", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', f'edit_short_{num}')]]))
        await res.delete()
    except ListenerTimeout:
        await query.message.edit_text("<b>✗ ᴛɪᴍᴇᴏᴜᴛ! ʏᴏᴜ ᴅɪᴅ ɴᴏᴛ sᴇɴᴅ ᴀɴʏ ᴛᴇxᴛ ᴡɪᴛʜɪɴ 60 sᴇᴄᴏɴᴅs.</b>", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', f'edit_short_{num}')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^fsub$"))
async def fsub(client, query):
    if client.fsub_dict:
        channel_list = []
        for channel_id, channel_data in client.fsub_dict.items():
            channel_name = channel_data[0] if channel_data and len(channel_data) > 0 else "Unknown"
            request_status = "✓ ʀᴇǫᴜᴇsᴛ" if channel_data[2] else "✗ ʀᴇǫᴜᴇsᴛ"
            timer_status = f"ᴛɪᴍᴇʀ: {channel_data[3]}ᴍ" if channel_data[3] > 0 else "ᴛɪᴍᴇʀ: ∞"
            channel_list.append(f"• `{channel_name}` (`{channel_id}`) - {request_status}, {timer_status}")
        channels_display = "\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    
    msg = f"""<blockquote>✦ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛᴛɪɴɢs</blockquote>
›› **ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:**
{channels_display}

__ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀᴅᴅ ᴏʀ ʀᴇᴍᴏᴠᴇ ᴀ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ ʙᴀsᴇᴅ ᴏɴ ʏᴏᴜʀ ɴᴇᴇᴅs!__"""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('›› ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ', 'add_fsub'), InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ', 'rm_fsub')], [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]])
    await query.message.edit_text(msg, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^db_channels$"))
async def db_channels(client, query):
    if not query.from_user.id in client.admins: 
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    db_channels = getattr(client, 'db_channels', {})
    if db_channels:
        channel_list = []
        for channel_id_str, channel_data in db_channels.items():
            channel_name = channel_data.get('name', 'Unknown')
            is_primary = "✓ ᴘʀɪᴍᴀʀʏ" if channel_data.get('is_primary', False) else "• sᴇᴄᴏɴᴅᴀʀʏ"
            is_active = "✓ ᴀᴄᴛɪᴠᴇ" if channel_data.get('is_active', True) else "✗ ɪɴᴀᴄᴛɪᴠᴇ"
            channel_list.append(f"• `{channel_name}` (`{channel_id_str}`)\n  {is_primary} | {is_active}")
        channels_display = "\n\n".join(channel_list)
    else: 
        channels_display = "_ɴᴏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    primary_db = getattr(client, 'primary_db_channel', client.db)
    msg = f"""<blockquote>✦ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs sᴇᴛᴛɪɴɢs</blockquote>\n›› **ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴍᴀʀʏ ᴅʙ:** `{primary_db}`\n›› **ᴛᴏᴛᴀʟ ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{len(db_channels)}` \n\n**ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:**\n{channels_display}\n\n__ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs!__"""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('›› ᴀᴅᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'add_db_channel'), InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'rm_db_channel')], [InlineKeyboardButton('›› sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db'), InlineKeyboardButton('›› sᴛᴀᴛᴜs', 'toggle_db_status')], [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]])
    await query.message.edit_text(msg, reply_markup=reply_markup)
                          
