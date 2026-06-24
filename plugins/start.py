from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait
import humanize
import asyncio
from config import (
    MESSAGES, MSG_EFFECT, OWNER_ID, 
    SHORT_URL_1, SHORT_API_1, SHORT_TUT_1,
    SHORT_URL_2, SHORT_API_2, SHORT_TUT_2,
    SHORT_URL_3, SHORT_API_3, SHORT_TUT_3
)
from plugins.shortner import get_short
from helper.helper_func import get_messages, force_sub, decode

# Background clean scheduler loop task handler
async def schedule_dynamic_deletion(client: Client, chat_id: int, media_messages: list, banner_msg: Message, transfer_link: str):
    # 30 Minutes structural deletion latency = 1800 seconds
    await asyncio.sleep(1800)
    
    # 1. Purge all media nodes safely from chat history
    for msg in media_messages:
        try:
            await msg.delete()
        except Exception:
            pass

    # 2. Render the short and crisp structural recovery text block with aesthetic small caps
    retrieval_text = (
        "<b>›› ᴘʀᴇᴠɪᴏᴜs ᴍᴇssᴀɢᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ\n\n"
        "ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ꜰɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: • ɢᴇᴛ ꜰɪʟᴇs • "
        "ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.</b>"
    )
    
    retrieval_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("• ɢᴇᴛ ꜰɪʟᴇs •", callback_data=f"getfiles_{transfer_link}"),
            InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data="close")
        ]
    ])
    
    try:
        await banner_msg.edit_text(
            text=retrieval_text,
            reply_markup=retrieval_markup
        )
    except Exception:
        try:
            await client.send_message(chat_id=chat_id, text=retrieval_text, reply_markup=retrieval_markup)
        except Exception:
            pass

#===============================================================#

@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    present = await client.mongodb.present_user(user_id)
    if not present:
        try:
            await client.mongodb.add_user(user_id)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error adding a user:\n{e}")

    is_banned = await client.mongodb.is_banned(user_id)
    if is_banned:
        return await message.reply("<b>✗ ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ!</b>")

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
        # MONGO TOKEN TRACKING LOGIC
        #===============================================================#
        if not is_user_pro and user_id != OWNER_ID and shortner_enabled:
            
            user_data = await client.mongodb.db.users.find_one({"id": user_id}) or {}
            user_credits = user_data.get("credits", 0)
            rotation_index = user_data.get("rotation_index", 0)

            # Case A: Shortener successfully bypassed -> Reward interface pipeline
            if is_short_link:
                user_credits = 3  
                next_rotation = (rotation_index + 1) % 3
                await client.mongodb.db.users.update_one(
                    {"id": user_id}, 
                    {"$set": {"credits": user_credits, "rotation_index": next_rotation}}, 
                    upsert=True
                )
                
                # Image 2 Style Exact Verification parsing structure with exact custom photo
                success_msg = (
                    "<b>◍ ʏᴏᴜʀ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɪs sᴜᴄᴄᴇssғᴜʟ!\n\n"
                    "<blockquote>⧗ 3 ᴄʀᴇᴅɪᴛs ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ.</blockquote></b>"
                )
                
                # Dynamic Photo response injected via explicit reply formatting
                await message.reply_photo(
                    photo="https://litter.catbox.moe/2zd2uk.jpg",
                    caption=success_msg,
                    quote=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✨ ᴄʟɪᴄᴋ ʜᴇʀᴇ ✨", callback_data=f"getfiles_{base64_string}")],
                        [InlineKeyboardButton("• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", url="https://t.me/Premiium_Tube/6")]
                    ])
                )
                return
            
            # Case B: Free user token loop expired screen layout
            elif user_credits <= 0:
                current_url, current_api, current_tut = SHORT_URL_1, SHORT_API_1, SHORT_TUT_1
                
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

                        # Spelling Error Fixed: 'consumed' standard small-caps implemented cleanly
                        custom_credit_msg = (
                            "<b><i>◍ Yeah the link's ready :), Here is your link ⬇️</i>\n\n"
                            "⧗ ᴄʀᴇᴅɪᴛs ᴍᴏᴅᴇ:\n"
                            "<blockquote>◍ ᴇᴀᴄʜ ᴀᴅ ʙʏᴘᴀss ʀᴇᴡᴀʀᴅs ʏᴏᴜ ᴡɪᴛʜ 3 ᴄʀᴇᴅɪᴛs.</blockquote>\n"
                            "<blockquote>◍ ᴏɴᴇ ᴄʀᴇᴅɪᴛ ɪs ᴄᴏɴsᴜᴍᴇᴅ ᴘᴇʀ ꜰɪʟᴇ/ʟɪɴᴋ ᴀᴄᴄᴇss.</blockquote></b>"
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
                        client.LOGGER(__name__, client.name).warning(f"Shortener tracking node breakdown: {e}")
                        pass

            if user_credits > 0 and not is_short_link:
                user_credits -= 1
                await client.mongodb.db.users.update_one({"id": user_id}, {"$set": {"credits": user_credits}})

        await deliver_files_routing(client, message, base64_string, original_payload)
        return

    else:
        buttons = [[InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="ABOUT"), InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data='close')]]
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

@Client.on_callback_query(filters.regex("^getfiles_"))
async def process_file_button_callback(client: Client, query: CallbackQuery):
    await query.answer("🚀 Dispatching download nodes safely...")
    base64_string = query.data.split("_")[1]
    original_payload = base64_string
    await query.message.delete()
    await deliver_files_routing(client, query.message, base64_string, original_payload, is_callback=True)

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

    temp_msg = await client.send_message(chat_target, "<b><blockquote>›› ꜰᴇᴛᴄʜɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇs, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</blockquote></b>")
    messages = []

    try:
        if source_channel_id:
            try:
                msgs = await client.get_messages(chat_id=source_channel_id, message_ids=list(ids))
                valid_msgs = [msg for msg in msgs if msg is not None]
                messages.extend(valid_msgs)
            except Exception as e:
                messages = await get_messages(client, ids)
        else:
            messages = await get_messages(client, ids)
    except Exception as e:
        await temp_msg.edit_text("<b>✗ sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ ᴡʜɪʟᴇ ʀᴇᴛʀɪᴇᴠɪɴɢ ᴅᴀᴛᴀ!</b>")
        return

    if not messages:
        return await temp_msg.edit("<b>✗ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ꜰɪʟᴇs ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ!</b>")
    await temp_msg.delete()

    media_messages = []
    for msg in messages:
        caption = (
            client.messages.get('CAPTION', '').format(
                previouscaption=msg.caption.html if msg.caption else msg.document.file_name
            ) if bool(client.messages.get('CAPTION', '')) and bool(msg.document)
            else ("" if not msg.caption else msg.caption.html)
        )
        reply_markup = msg.reply_markup if not client.disable_btn else None

        try:
            copied_msg = await msg.copy(chat_id=chat_target, caption=caption, reply_markup=reply_markup, protect_content=client.protect)
            media_messages.append(copied_msg)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            copied_msg = await msg.copy(chat_id=chat_target, caption=caption, reply_markup=reply_markup, protect_content=client.protect)
            media_messages.append(copied_msg)
        except Exception:
            pass

    # Notice text banner container setup
    if media_messages:
        warning_banner_text = (
            "<b><u>⚠️ This File is deleting automatically in<a href="https://t.me/RezeFilesBot">30 Minutes...</a>Forward in your Saved Messages..!</u></b>"
        )
        try:
            banner_msg = await client.send_message(chat_id=chat_target, text=warning_banner_text)
            
            # Explicit background process scheduler thread invocation
            transfer_link = original_payload
            asyncio.create_task(schedule_dynamic_deletion(
                client=client, 
                chat_id=chat_target, 
                media_messages=media_messages, 
                banner_msg=banner_msg,
                transfer_link=transfer_link
            ))
        except Exception:
            pass
    return
    
