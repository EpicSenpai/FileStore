from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait
import humanize
import asyncio
from config import MESSAGES, MSG_EFFECT, OWNER_ID
import config
from plugins.shortner import get_short
from helper.helper_func import get_messages, force_sub, decode

async def schedule_dynamic_deletion(client: Client, chat_id: int, media_messages: list, banner_msg: Message, transfer_link: str):
    deletion_seconds = getattr(client, 'auto_del', 1800)
    await asyncio.sleep(deletion_seconds)
    for msg in media_messages:
        try:
            await msg.delete()
        except Exception:
            pass
    retrieval_text = (
        "<b>›› ᴘʀᴇᴠɪᴏᴜs ᴍᴇssᴀɢᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ\n\n"
        "ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ꜰɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: • ɢᴇᴛ ꜰɪʟᴇs • "
        "ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.</b>"
    )
    retrieval_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("• ɢᴇᴛ ꜰɪʟᴇs •", callback_data=f"getfiles_{transfer_link}"), InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data="close")]
    ])
    try:
        await banner_msg.edit_text(text=retrieval_text, reply_markup=retrieval_markup)
    except Exception:
        try:
            await client.send_message(chat_id=chat_id, text=retrieval_text, reply_markup=retrieval_markup)
        except Exception:
            pass

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
        reward_amount = await client.mongodb.get_set_credits_amount()
        if not is_user_pro and user_id != OWNER_ID and shortner_enabled:
            user_data = await client.mongodb.user_data.find_one({"_id": user_id})
            if not user_data:
                user_data = {}
            user_credits = user_data.get("credits", 0)
            rotation_index = user_data.get("rotation_index", 0)
            if is_short_link:
                user_credits = reward_amount
                next_rotation = (rotation_index + 1) % 3
                # Deduct 1 credit for current file access (net = reward_amount - 1)
                await client.mongodb.user_data.update_one({"_id": user_id}, {"$set": {"credits": user_credits - 1, "rotation_index": next_rotation}}, upsert=True)
                user_credits = user_credits - 1
                try:
                    await client.mongodb.db.shortner_analytics.update_one({"shortner_id": int(rotation_index)}, {"$inc": {"clicks": 1}}, upsert=True)
                except Exception:
                    pass
                success_msg = (
                    "<b>◍ ʏᴏᴜʀ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ɪs sᴜᴄᴄᴇssꜰᴜʟ!\n\n"
                    f"<blockquote>⧗ {reward_amount} ᴄʀᴇᴅɪᴛs ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ.</blockquote></b>"
                )
                await message.reply_photo(
                    photo="https://litter.catbox.moe/2zd2uk.jpg",
                    caption=success_msg,
                    quote=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✨ ᴄʟɪᴄᴋ ʜᴇʀᴇ ✨", callback_data=f"getfiles_{base64_string}")],
                        [InlineKeyboardButton("• ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", url="https://t.me/SenFlux/14")]
                    ])
                )
                return
            elif user_credits <= 0:
                current_url = config.SHORT_URL_1
                current_api = config.SHORT_API_1
                current_tut = config.SHORT_TUT_1
                if rotation_index == 1 and config.SHORT_URL_2 and config.SHORT_API_2:
                    current_url = config.SHORT_URL_2
                    current_api = config.SHORT_API_2
                    current_tut = config.SHORT_TUT_2
                elif rotation_index == 2 and config.SHORT_URL_3 and config.SHORT_API_3:
                    current_url = config.SHORT_URL_3
                    current_api = config.SHORT_API_3
                    current_tut = config.SHORT_TUT_3
                if current_url and current_api:
                    try:
                        client.short_url = current_url
                        client.short_api = current_api
                        short_link = get_short(f"https://t.me/{client.username}?start=yu3elk{base64_string}7", client)
                        short_photo = client.messages.get("SHORT_PIC", "https://litter.catbox.moe/q9aqxh.jpg")
                        tutorial_link = current_tut if current_tut else "https://t.me/How_To_Open_Shortners"
                        custom_credit_msg = (
                            "<b><i>◍ Yeah the link's ready :), Here is your link ⬇️</i>\n\n"
                            "⧗ ᴄʀᴇᴅɪᴛs ᴍᴏᴅᴇ:\n"
                            f"<blockquote>◍ ᴇᴀᴄʜ ᴀᴅ ʙʏᴘᴀss ʀᴇᴡᴀʀᴅs ʏᴏᴜ ᴡɪᴛʜ {reward_amount} ᴄʀᴇᴅɪᴛs.</blockquote>\n"
                            "<blockquote>◍ ᴏɴᴇ ᴄʀᴇᴅɪᴛ ɪs ᴄᴏɴsᴜᴍᴇᴅ ᴘᴇʀ ꜰɪʟᴇ/ʟɪɴᴋ ᴀᴄᴄᴇss.</blockquote></b>"
                        )
                        await client.send_photo(
                            chat_id=message.chat.id,
                            photo=short_photo,
                            caption=custom_credit_msg,
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("• ᴏᴘᴇɴ ʟɪɴᴋ", url=short_link), InlineKeyboardButton("ᴛᴜᴛᴏʀɪᴀʟ •", url=tutorial_link)],
                                [InlineKeyboardButton(" • ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", url="https://t.me/SenFlux/14")]
                            ])
                        )
                        return
                    except Exception as e:
                        client.LOGGER(__name__, client.name).warning(f"Shortener tracking node breakdown: {e}")
                        pass
            if user_credits > 0 and not is_short_link:
                user_credits -= 1
                await client.mongodb.user_data.update_one({"_id": user_id}, {"$set": {"credits": user_credits}})
        await deliver_files_routing(client, message, base64_string, original_payload)
        return
    else:
        buttons = [[InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="ABOUT"), InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data='close')]]
        if user_id in client.admins:
            buttons.insert(0, [InlineKeyboardButton("• ꜱᴇᴛᴛɪɴɢs •", callback_data="settings")])
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

@Client.on_callback_query(filters.regex("^getfiles_"))
async def process_file_button_callback(client: Client, query: CallbackQuery):
    await query.answer("🚀 Dispatching download nodes safely...")
    base64_string = query.data.split("_")[1]
    original_payload = base64_string
    await query.message.delete()
    await deliver_files_routing(client, query.message, base64_string, original_payload, is_callback=True)

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
    temp_msg = await client.send_message(chat_target, "<i>Wait A Sec...</i>")
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
            client.messages.get('CAPTION', '').format(previouscaption=msg.caption.html if msg.caption else msg.document.file_name)
            if bool(client.messages.get('CAPTION', '')) and bool(msg.document)
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
    if media_messages:
        auto_del_seconds = getattr(client, 'auto_del', 1800)
        readable_time = humanize.naturaldelta(auto_del_seconds)
        warning_banner_text = (
            "<b><blockquote>⧗ Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....</blockquote>\n"
            f'<blockquote>›› Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ <code>{readable_time}</code>... '
            'Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ..</blockquote>\n'
            '<blockquote>≡ Nᴏᴛᴇ : ᴜsᴇ <a href="https://play.google.com/store/apps/details?id=org.videolan.vlc">ᴠʟᴄ ᴘʟᴀʏᴇʀ</a> ᴏʀ '
            '<a href="https://play.google.com/store/apps/details?id=com.mxtech.videoplayer.ad">ᴍx ᴘʟᴀʏᴇʀ</a> '
            "ᴛᴏ ᴡᴀᴛᴄʜ ᴛʜᴇ ᴍᴏᴠɪᴇꜱ/ꜱᴇʀɪᴇꜱ ᴡɪᴛʜ ɢᴏᴏᴅ ᴇxᴘᴇʀɪᴇɴᴄᴇ !.</blockquote></b>"
        )
        try:
            banner_msg = await client.send_message(
                chat_id=chat_target,
                text=warning_banner_text,
                disable_web_page_preview=True
            )
            transfer_link = original_payload
            asyncio.create_task(schedule_dynamic_deletion(client=client, chat_id=chat_target, media_messages=media_messages, banner_msg=banner_msg, transfer_link=transfer_link))
        except Exception:
            pass
    return
        
