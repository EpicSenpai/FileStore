from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import MSG_EFFECT
from pyrogram.errors.pyromod import ListenerTimeout
import config

#===============================================================#

@Client.on_message(filters.command('db') & filters.private)
async def db_channels_command(client: Client, message: Message):
    """Direct command to manage DB channels"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    # Show current DB channels status
    db_channels = getattr(client, 'db_channels', {})
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    if db_channels:
        channel_list = []
        for channel_id_str, channel_data in db_channels.items():
            channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
            is_primary = "✓ ᴘʀɪᴍᴀʀʏ" if channel_data.get('is_primary', False) else "• sᴇᴄᴏɴᴅᴀʀʏ"
            is_active = "✓ ᴀᴄᴛɪᴠᴇ" if channel_data.get('is_active', True) else "✗ ɪɴᴀᴄᴛɪᴠᴇ"
            channel_list.append(f"• `{channel_name}` (`{channel_id_str}`)\n  {is_primary} | {is_active}")
        
        channels_display = "\n\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ᴀᴅᴅɪᴛɪᴏɴᴀʟ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    
    msg = f"""<blockquote>✦ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</blockquote>

›› **<b>ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴍᴀʀʏ ᴅʙ:</b>** `{primary_db}`
›› **<b>ᴛᴏᴛᴀʟ ᴅʙ ᴄʜᴀɴɴᴇʟs:</b>** `{len(db_channels)}`

<b>ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:</b>
{channels_display}

__ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs!__
"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('›› ᴀᴅᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'add_db_channel')],
        [InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'rm_db_channel')],
        [InlineKeyboardButton('›› sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db')],
        [InlineKeyboardButton('›› ᴛᴏɢɢʟᴇ sᴛᴀᴛᴜs', 'toggle_db_status')],
        [InlineKeyboardButton('›› ᴠɪᴇᴡ ᴅᴇᴛᴀɪʟs', 'db_details')]
    ])
    
    await message.reply(msg, reply_markup=reply_markup)

#===============================================================#

@Client.on_callback_query(filters.regex("^db_details$"))
async def db_details(client, query):
    """Show detailed information about DB channels"""
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    
    db_channels = getattr(client, 'db_channels', {})
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    msg = f"""<blockquote>✦ ᴅᴇᴛᴀɪʟᴇᴅ ᴅʙ ᴄʜᴀɴɴᴇʟs ɪɴғᴏʀᴍᴀᴛɪᴏɴ</blockquote>

›› **<b>ᴘʀɪᴍᴀʀʏ ᴅʙ ᴄʜᴀɴɴᴇʟ:</b>** `{primary_db}`
›› **<b>ᴛᴏᴛᴀʟ ᴄᴏɴғɪɢᴜʀᴇᴅ:</b>** `{len(db_channels)}`

"""
    
    if db_channels:
        for i, (channel_id_str, channel_data) in enumerate(db_channels.items(), 1):
            channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
            is_primary = channel_data.get('is_primary', False)
            is_active = channel_data.get('is_active', True)
            added_by = channel_data.get('added_by', 'ᴜɴᴋɴᴏᴡɴ')
            
            status_emoji = "✓" if is_primary else "•"
            active_emoji = "✓" if is_active else "✗"
            
            msg += f"""**{i}. {channel_name}**
• **<b>ɪᴅ:</b>** `{channel_id_str}`
• **<b>sᴛᴀᴛᴜs:</b>** {status_emoji} {'ᴘʀɪᴍᴀʀʏ' if is_primary else 'sᴇᴄᴏɴᴅᴀʀʏ'}
• **<b>ᴀᴄᴛɪᴠᴇ:</b>** {active_emoji} {'ʏᴇs' if is_active else 'ɴᴏ'}
• **<b>ᴀᴅᴅᴇᴅ ʙʏ:</b>** `{added_by}`

"""
    else:
        msg += "_ɴᴏ ᴀᴅᴅɪᴛɪᴏɴᴀʟ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_\n\n"
    
    msg += """**✦ ɴᴏᴛᴇs:**
• ᴘʀɪᴍᴀʀʏ ᴄʜᴀɴɴᴇʟ ɪs ᴜsᴇᴅ ғɪʀsᴛ ғᴏʀ ʀᴇᴛʀɪᴇᴠɪɴɢ ғɪʟᴇs
• sᴇᴄᴏɴᴅᴀʀʏ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴜsᴇᴅ ᴀs ғᴀʟʟʙᴀᴄᴋ
• ɪɴᴀᴄᴛɪᴠᴇ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ sᴋɪᴘᴘᴇᴅ ᴅᴜʀɪɴɢ ғɪʟᴇ ʀᴇᴛʀɪᴇᴠᴀʟ
• ʏᴏᴜ ᴄᴀɴ ʜᴀᴠᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴅʙ ᴄʜᴀɴɴᴇʟs ғᴏʀ ʙᴇᴛᴛᴇʀ ʀᴇʟɪᴀʙɪʟɪᴛʏ"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ', 'back_to_db_management')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#

@Client.on_callback_query(filters.regex("^back_to_db_management$"))
async def back_to_db_management(client, query):
    """Go back to main DB channels management"""
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    
    db_channels = getattr(client, 'db_channels', {})
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    if db_channels:
        channel_list = []
        for channel_id_str, channel_data in db_channels.items():
            channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
            is_primary = "✓ ᴘʀɪᴍᴀʀʏ" if channel_data.get('is_primary', False) else "• sᴇᴄᴏɴᴅᴀʀʏ"
            is_active = "✓ ᴀᴄᴛɪᴠᴇ" if channel_data.get('is_active', True) else "✗ ɪɴᴀᴄᴛɪᴠᴇ"
            channel_list.append(f"• `{channel_name}` (`{channel_id_str}`)\n  {is_primary} | {is_active}")
        
        channels_display = "\n\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ᴀᴅᴅɪᴛɪᴏɴᴀʟ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    
    msg = f"""<blockquote>✦ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</blockquote>

›› **<b>ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴍᴀʀʏ ᴅʙ:</b>** `{primary_db}`
›› **<b>ᴛᴏᴛᴀʟ ᴅʙ ᴄʜᴀɴɴᴇʟs:</b>** `{len(db_channels)}`

<b>ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:</b>
{channels_display}

__ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs!__
"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('›› ᴀᴅᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'add_db_channel')],
        [InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'rm_db_channel')],
        [InlineKeyboardButton('›› sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db')],
        [InlineKeyboardButton('›› ᴛᴏɢɢʟᴇ sᴛᴀᴛᴜs', 'toggle_db_status')],
        [InlineKeyboardButton('›› ᴠɪᴇᴡ ᴅᴇᴛᴀɪʟs', 'db_details')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#

@Client.on_message(filters.command(['adddb', 'add_db']) & filters.private)
async def quick_add_db(client: Client, message: Message):
    """Quick command to add a DB channel"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("""<blockquote>✦ ᴀᴅᴅ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ</blockquote>

›› **<b>ᴜsᴀɢᴇ:</b>** `/adddb <channel_id>`
›› **<b>ᴇxᴀᴍᴘʟᴇ:</b>** `/adddb -1001234567890`

**<b>ɴᴏᴛᴇ:</b>** ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ!""")
    
    try:
        channel_id = int(args[1])
    except ValueError:
        return await message.reply("**✗ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ! ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴇɢᴀᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ.**")
    
    db_channels = getattr(client, 'db_channels', {})
    if str(channel_id) in db_channels:
        return await message.reply(f"**✗ ᴄʜᴀɴɴᴇʟ `{channel_id}` ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ ᴀs ᴀ ᴅʙ ᴄʜᴀɴɴᴇʟ!**")
    
    try:
        chat = await client.get_chat(channel_id)
        test_msg = await client.send_message(chat_id=channel_id, text="ᴛᴇsᴛɪɴɢ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴀᴄᴄᴇss - @Okabe_xRintarou")
        await test_msg.delete()
        
        channel_data = {
            'name': chat.title,
            'is_primary': len(db_channels) == 0,
            'is_active': True,
            'added_by': message.from_user.id
        }
        
        await client.mongodb.add_db_channel(channel_id, channel_data)
        
        if not hasattr(client, 'db_channels'):
            client.db_channels = {}
        client.db_channels[str(channel_id)] = channel_data
        
        if channel_data['is_primary']:
            client.primary_db_channel = channel_id
            await client.mongodb.set_primary_db_channel(channel_id)
        
        await message.reply(f"""**✓ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**

›› **<b><b>ᴄʜᴀɴɴᴇʟ:</b></b>** `{chat.title}`
›› **<b><b>ɪᴅ:</b></b>** `{channel_id}`
›› **<b><b>sᴛᴀᴛᴜs:</b></b>** {'ᴘʀɪᴍᴀʀʏ' if channel_data['is_primary'] else 'sᴇᴄᴏɴᴅᴀʀʏ'}

ᴜsᴇ `/dbchannels` ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀʟʟ ʏᴏᴜʀ ᴅʙ ᴄʜᴀɴɴᴇʟs.""")
    
    except Exception as e:
        await message.reply(f"""**✗ ᴇʀʀᴏʀ ᴀᴄᴄᴇssɪɴɢ ᴄʜᴀɴɴᴇʟ!**

›› **<b>ᴇʀʀᴏʀ:</b>** `{str(e)}`

**<b>ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ sᴜʀᴇ:</b>**
• ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ
• ᴄʜᴀɴɴᴇʟ ɪᴅ ɪs ᴄᴏʀʀᴇᴄᴛ
• ᴄʜᴀɴɴᴇʟ ᴇxɪsᴛs""")

#===============================================================#

@Client.on_message(filters.command(['removedb', 'rm_db']) & filters.private)
async def quick_remove_db(client: Client, message: Message):
    """Quick command to remove a DB channel"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    args = message.text.split()
    if len(args) < 2:
        db_channels = getattr(client, 'db_channels', {})
        if not db_channels:
            return await message.reply("**✗ ɴᴏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴛᴏ ʀᴇᴍᴏᴠᴇ!**")
        
        msg = """<blockquote>✦ ʀᴇᴍᴏᴠᴇ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ</blockquote>

›› **<b>ᴜsᴀɢᴇ:</b>** `/removedb <channel_id>`

**<b>ᴀcodeᴠᴀɪʟᴀʙʟᴇ ᴄʜᴀɴɴᴇʟs:</b>**
"""
        for channel_id_str, channel_data in db_channels.items():
            channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
            is_primary = " (ᴘʀɪᴍᴀʀʏ)" if channel_data.get('is_primary', False) else ""
            msg += f"• `{channel_name}` - `{channel_id_str}`{is_primary}\n"
        
        return await message.reply(msg)
    
    try:
        channel_id = int(args[1])
    except ValueError:
        return await message.reply("**✗ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ! ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴇɢᴀᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ.**")
    
    db_channels = getattr(client, 'db_channels', {})
    if str(channel_id) not in db_channels:
        return await message.reply(f"**✗ ᴄʜᴀɴɴᴇʟ `{channel_id}` ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟs ʟɪsᴛ!**")
    
    if db_channels[str(channel_id)].get('is_primary', False) and len(db_channels) > 1:
        return await message.reply("**✗ ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴘʀɪᴍᴀʀʏ ᴄʜᴀɴɴᴇʟ!**\n\n__ᴘʟᴇᴀsᴇ sᴇᴛ ᴀɴᴏᴛʜᴇ r ᴄʜᴀɴɴᴇʟ ᴀs ᴘʀɪᴍᴀʀʏ ғɪʀsᴛ.__")
    
    channel_name = db_channels[str(channel_id)].get('name', 'ᴜɴᴋɴᴏᴡɴ')
    await client.mongodb.remove_db_channel(channel_id)
    del client.db_channels[str(channel_id)]
    
    await message.reply(f"""**✓ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**

›› **<b>ʀᴇᴍᴏᴠᴇᴅ:</b>** `{channel_name}` (`{channel_id}`)

ᴜsᴇ `/db` ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʀᴇᴍᴀɪɴɪɴɢ ᴅʙ ᴄʜᴀɴɴᴇʟs.""")

#==========================================================================#        
# HIGH-PRIORITY INTEGRACTIVE NAVIGATION COMPLIANCE WITH REAL PHOTO INTERFACE
#==========================================================================#        

@Client.on_callback_query(filters.regex('^home$'))
async def home(client: Client, query: CallbackQuery):
    await query.answer("↩️ Returning back to home dashboard...")
    user_id = query.from_user.id
    
    buttons = [[InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="ABOUT"), InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data="close")]]
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
        # Fixed: Safely edit photo caption layout to maintain exact font style constraints
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
    return

#==========================================================================#        

@Client.on_callback_query(filters.regex('^ABOUT$'))
async def about(client: Client, query: CallbackQuery):
    await query.answer("ℹ️ Loading about documentation details...")
    
    about_text = config.MESSAGES.get('ABOUT', '').format(
        bot_name=client.username,
        mention=query.from_user.mention
    )
    
    back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="home")]])
    
    try:
        await query.message.edit_caption(caption=about_text, reply_markup=back_markup)
    except Exception:
        try:
            await query.message.edit_text(text=about_text, reply_markup=back_markup)
        except Exception:
            pass
    return

#==========================================================================#        

@Client.on_callback_query(filters.regex('^close$'))
async def close(client: Client, query: CallbackQuery):
    await query.answer("🗑️ Interface interface closed.")
    await query.message.delete()
    try:
        await query.message.reply_to_message.delete()
    except:
        pass

#==========================================================================#        

@Client.on_message(filters.command('ban'))
async def ban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c = c + 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id, True)
                continue
            else:
                await client.mongodb.ban_user(user_id)
        return await message.reply(f"__{c} users have been banned!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")

#==========================================================================#        

@Client.on_message(filters.command('unban'))
async def unban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id in user_ids.split():
            user_id = int(user_id)
            c = c + 1
            if user_id in client.admins:
                continue
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id)
                continue
            else:
                await client.mongodb.unban_user(user_id)
        return await message.reply(f"__{c} users have been unbanned!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")
        
