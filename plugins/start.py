from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import humanize
import asyncio
from config import (
    MESSAGES, MSG_EFFECT, OWNER_ID, 
    SHORT_URL_1, SHORT_API_1, SHORT_TUT_1,
    SHORT_URL_2, SHORT_API_2, SHORT_TUT_2,
    SHORT_URL_3, SHORT_API_3, SHORT_TUT_3
)
from plugins.shortner import get_short
from helper.helper_func import get_messages, force_sub, decode, batch_auto_del_notification

#===============================================================#

@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    # 1. Add user if not present
    present = await client.mongodb.present_user(user_id)
    if not present:
        try:
            await client.mongodb.add_user(user_id)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error adding a user:\n{e}")

    # 2. Check if banned
    is_banned = await client.mongodb.is_banned(user_id)
    if is_banned:
        return await message.reply("<b>✗ ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇ Dil ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ!</b>")

    text = message.text
    if len(text) > 7:
        try:
            original_payload = text.split(" ", 1)[1]
            base64_string = original_payload

            is_short_link = False
            if base64_string.startswith("yu3elk"):
                base64_string = base64_string[6:-1]
                is_short_link = True

        except IndexError:
            return await message.reply("<b>✗ ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ ꜰᴏʀᴍᴀᴛ.</b>")

        is_user_pro = await client.mongodb.is_pro(user_id)
        shortner_enabled = getattr(client, 'shortner_enabled', True)

        #===============================================================#
        # SMART DATABASE ROTATION & TOKEN LOGIC FOR FREE USERS
        #===============================================================#
        if not is_user_pro and user_id != OWNER_ID and shortner_enabled:
            
            # Fetch real-time mapping from database collection
            user_data = await client.mongodb.db.users.find_one({"id": user_id}) or {}
            user_credits = user_data.get("credits", 0)
            rotation_index = user_data.get("rotation_index", 0)

            # Case A: User successfully bypassed the token verification link
            if is_short_link:
                user_credits = 3  # Reward exactly 3 tokens
                next_rotation = (rotation_index + 1) % 3
                await client.mongodb.db.users.update_one(
                    {"id": user_id}, 
                    {"$set": {"credits": user_credits, "rotation_index": next_rotation}}, 
                    upsert=True
                )
                
                # Successful Verification Layout Screen (Image 1 Style)
                success_photo = client.messages.get("SHORT_PIC", "https://litter.catbox.moe/w9bw9z.jpg")
                success_msg = (
                    "<b>● ʏᴏᴜʀ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ɪs sᴜᴄᴄᴇssꜰᴜʟ!\n\n"
                    "⧗ 3 ᴄʀᴇᴅɪᴛs ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ\nᴀᴄᴄᴏᴜɴᴛ.</b>"
                )
                
                await client.send_photo(
                    chat_id=message.chat.id,
                    photo=success_photo,
                    caption=success_msg,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✨ ᴄʟɪᴄᴋ ʜᴇʀᴇ ✨", callback_data=f"getfiles_{base64_string}")]
                    ])
                )
                return
            
            # Case B: Token is expired (0 Credits State) -> Prompt Token Expired View
            elif user_credits <= 0:
                current_url, current_api, current_tut = SHORT_URL_1, SHORT_API_1, SHORT_TUT_1
                
                # Dynamic line-by-line verification parsing
                if rotation_index == 1 and SHORT_URL_2 and SHORT_API_2:
                    current_url, current_api, current_tut = SHORT_URL_2, SHORT_API_2, SHORT_TUT_2
                elif rotation_index == 2 and SHORT_URL_3 and SHORT_API_3:
                    current_url, current_api, current_tut = SHORT_URL_3, SHORT_API_3, SHORT_TUT_3

                if current_url and current_api:
                    try:
                        client.shortner_url = current_url
                        client.shortner_api = current_api
                        
                        short_link = get_short(f"https://t.me/{client.username}?start=yu3elk{base64_string}7", client)
                        short_photo = client.messages.get("SHORT_PIC", "https://litter.catbox.moe/q9aqxh.jpg")
                        tutorial_link = current_tut if current_tut else "https://t.me/How_To_Open_Shortners"

                        # Aesthetic layout parsing using clean HTML quote tags
                        custom_credit_msg = (
                            "<b><i>◍ Yeah the link's ready :), Here is your link ⬇️</i>\n\n"
                            "⧗ ᴄʀᴇᴅɪᴛs ᴍᴏᴅᴇ:\n"
                            "<blockquote>◍ Eᴀᴄʜ ᴀᴅ ʙʏᴘᴀss ʀᴇᴡᴀʀᴅs ʏᴏᴜ ᴡɪᴛʜ 3 ᴄʀᴇᴅɪᴛs.</blockquote>\n"
                            "<blockquote>◍ Oɴᴇ ᴄʀᴇᴅɪᴛ ɪs ᴄᴏɴsᴜᴍᴇᴅ ᴘᴇʀ ғɪʟᴇ/ʟɪɴᴋ ᴀᴄᴄᴇss.</blockquote></b>"
                        )

                        await client.send_photo(
                            chat_id=message.chat.id,
                            photo=short_photo,
                            caption=custom_credit_msg,
                            reply_markup=InlineKeyboardMarkup([
                                [
                                    InlineKeyboardButton("• ᴏᴘᴇɴ ʟɪɴᴋ", url=short_link),
                                    InlineKeyboardButton("ᴛᴜᴛᴏʀɪᴀʟ •", url=tutorial_link)
                                ],
                                [
                                    InlineKeyboardButton(" • ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", url="https://t.me/Premiium_Tube/6")
                                ]
                            ])
                        )
                        return
                    except Exception as e:
                        client.LOGGER(__name__, client.name).warning(f"Shortener node tracking failed: {e}")
                        pass

            # Case C: Free user has structural active tokens -> Deduct single unit smoothly
            if user_credits > 0 and not is_short_link:
                user_credits -= 1
                await client.mongodb.db.users.update_one({"id": user_id}, {"$set": {"credits": user_credits}})

        # Deliver files dynamically if conditions are already satisfied
        await deliver_files_routing(client, message, base64_string, original_payload)
        return

    # Normal start layout execution
    else:
        buttons = [[InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="ABOUT"), InlineKeyboardButton("ᴄʟᴏꜱᴇ •", callback_data='close')]]
        if user_id in client.admins:
            buttons.insert(0, [InlineKeyboardButton("• ꜱᴇᴛᴛɪɴɢꜱ •", callback_data="settings")])

        photo = client.messages.get("START_PHOTO", "")
        start_caption = client.messages.get('START', 'Welcome, {mention}').format(
            first=message.from_user.first_name,
            last=message.from_user.last_name or "",
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        )

        if photo:
            await client.send_photo(chat_id=message.chat.id, photo=photo, caption=start_caption, message_effect_id=MSG_EFFECT, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await client.send_message(chat_id=message.chat.id, text=start_caption, message_effect_id=MSG_EFFECT, reply_markup=InlineKeyboardMarkup(buttons))
        return

#===============================================================#
# INTERACTIVE CALLBACK PROCESSING TO EXECUTE SECURE LINKS
#===============================================================#

@Client.on_callback_query(filters.regex("^getfiles_"))
async def process_file_button_callback(client: Client, query: CallbackQuery):
    await query.answer("🚀 Redirecting to download endpoint...")
    base64_string = query.data.split("_")[1]
    original_payload = base64_string
    
    # Clear the confirmation interface layout
    await query.message.delete()
    
    # Process secure link routing destination
    await deliver_files_routing(client, query.message, base64_string, original_payload, is_callback=True)

#===============================================================#
# CORE CORE STRUCTURAL ROUTING REDIRECTION METHOD
#===============================================================#

async def deliver_files_routing(client, message, base64_string, original_payload, is_callback=False):
    chat_target = message.chat.id if is_callback else message.from_user.id
    
    try:
        string = await decode(base64_string)
        argument = string.split("-")
        ids = []
        source_channel_id = None

        if len(argument) == 3:
            encoded_start = int(argument[1])
            encoded_end = int(argument[2])
            
            primary_multiplier = abs(client.db)
            start_primary = int(encoded_start / primary_multiplier)
            end_primary = int(encoded_end / primary_multiplier)
            
            if encoded_start % primary_multiplier == 0 and encoded_end % primary_multiplier == 0:
                source_channel_id = client.db
                start, end = start_primary, end_primary
            else:
                db_channels = getattr(client, 'db_channels', {})
                for channel_id_str in db_channels.keys():
                    channel_id = int(channel_id_str)
                    channel_multiplier = abs(channel_id)
                    if encoded_start % channel_multiplier == 0 and encoded_end % channel_multiplier == 0:
                        source_channel_id = channel_id
                        start = int(encoded_start / channel_multiplier)
                        end = int(encoded_end / channel_multiplier)
                        break
                if source_channel_id is None:
                    source_channel_id = client.db
                    start, end = start_primary, end_primary
            
            ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))

        elif len(argument) == 2:
            encoded_msg = int(argument[1])
            if hasattr(client, 'db_channel') and client.db_channel:
                primary_multiplier = abs(client.db_channel.id)
                if encoded_msg % primary_multiplier == 0:
                    source_channel_id = client.db_channel.id
                    ids = [int(encoded_msg / primary_multiplier)]
                else:
                    db_channels = getattr(client, 'db_channels', {})
                    for channel_id_str in db_channels.keys():
                        channel_id = int(channel_id_str)
                        if encoded_msg % abs(channel_id) == 0:
                            source_channel_id = channel_id
                            ids = [int(encoded_msg / abs(channel_id))]
                            break
                    if source_channel_id is None:
                        source_channel_id = client.db_channel.id if hasattr(client, 'db_channel') else client.db
                        ids = [int(encoded_msg / primary_multiplier)]
            else:
                source_channel_id = client.db
                ids = [int(encoded_msg / abs(client.db))]

    except Exception as e:
        return await client.send_message(chat_target, "<b>✗ ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ꜰɪʟᴇ ʟɪɴᴋ.</b>")

    # Redirect deep-link text formatting layer matching Image 2 style perfectly
    nova_redirect_url = f"https://t.me/NovaFileBot?start={original_payload}"
    delivery_msg_text = (
        f"<b>Download Link: <a href='{nova_redirect_url}'>{nova_redirect_url}</a>\n\n"
        f"This File is deleting automatically in 10 Minutes.. "
        f"Forward in your Saved Messages..!</b>"
    )
    
    await client.send_message(
        chat_id=chat_target,
        text=delivery_msg_text,
        disable_web_page_preview=False
    )
    return

#===============================================================#

@Client.on_message(filters.command('request') & filters.private)
async def request_command(client: Client, message: Message):
    user_id = message.from_user.id
    is_admin = user_id in client.admins
    is_user_premium = await client.mongodb.is_pro(user_id)

    if is_admin or user_id == OWNER_ID:
        await message.reply_text("<b>🔹 ʏᴏᴜ ᴀʀᴇ ᴍʏ sᴇɴsᴇɪ!\nᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ꜰᴏʀ ᴜsᴇʀs.</b>")
        return

    if not is_user_premium: 
        BUTTON_URL = "https://t.me/Premiium_Tube/6"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("💎 Upgrade to Premium", url=BUTTON_URL)]])
        await message.reply("<b>✗ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ.\nᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ᴀᴄᴄᴇs sᴛʀᴜᴄᴛᴜʀᴀʟ ꜰᴇᴀᴛᴜʀᴇs.</b>", reply_markup=reply_markup)
        return

    if len(message.command) < 2:
        await message.reply("<b>⚠️ sᴇɴᴅ ᴍᴇ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɪɴ ᴛʜɪs ꜰᴏʀᴍᴀᴛ:\n<code>/request Your_Request_Here</code></b>")
        return

    requested = " ".join(message.command[1:])
    owner_message = f"<b>📩 ɴᴇᴡ ʀᴇǫᴜᴇsᴛ ꜰʀᴏᴍ {message.from_user.mention}\n\n🆔 ᴜsᴇʀ ɪᴅ: <code>{user_id}</code>\n📝 ʀᴇǫᴜᴇsᴛ: <code>{requested}</code></b>"
    await client.send_message(OWNER_ID, owner_message)
    await message.reply("<b>✅ ᴛʜᴀɴᴋs ꜰᴏʀ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ!\nʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴡɪʟʟ ʙᴇ ʀᴇᴠɪᴇᴡᴇᴅ sᴏᴏɴ.</b>")

#===============================================================#

@Client.on_message(filters.command('profile') & filters.private)
async def my_plan(client: Client, message: Message):
    user_id = message.from_user.id
    is_admin = user_id in client.admins

    if is_admin or user_id == OWNER_ID:
        await message.reply_text("<b>🔹 ʏᴏᴜ'ʀᴇ ᴍʏ sᴇɴsᴇɪ! ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ꜰᴏʀ ᴜsᴇʀs.</b>")
        return
    
    is_user_premium = await client.mongodb.is_pro(user_id)
    user_data = await client.mongodb.db.users.find_one({"id": user_id}) or {}
    user_credits = user_data.get("credits", 0)

    if is_user_premium:
        await message.reply_text("<b>👤 ᴘʀᴏꜰɪʟᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ:\n\n🔸 ᴀᴅs: ᴅɪsᴀʙʟᴇᴅ\n🔸 ᴘʟᴀɴ: ᴘʀᴇᴍɪᴜᴍ\n🔸 ʀᴇǫᴜᴇsᴛ: ᴇɴᴀʙʟᴇᴅ\n\n🌟 ʏᴏᴜ'ʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ!</b>")
    else:
        await message.reply_text(f"<b>👤 ᴘʀᴏꜰɪʟᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ:\n\n🔸 ᴀᴅs: ᴇɴᴀʙʟᴇᴅ\n🔸 ᴘʟᴀɴ: ꜰʀᴇᴇ\n🔸 ᴠᴀʟɪᴅ ᴄʀᴇᴅɪᴛs: <code>{user_credits}</code> ᴄʀᴇᴅɪᴛs\n🔸 ʀᴇǫᴜᴇsᴛ: ᴅɪsᴀʙʟᴇᴅ\n\n🔓 ᴜɴʟᴏᴄᴋ ᴘʀᴇᴍɪᴜᴍ ᴛᴏ ɢᴇᴛ ᴍᴏʀᴇ ʙᴇɴᴇꜰɪᴛs\nᴄᴏɴᴛᴀᴄᴛ: @EpicSenpai</b>")
                                
