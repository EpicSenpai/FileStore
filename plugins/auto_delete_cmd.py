from pyrogram import Client, filters
from pyrogram.types import Message


async def _is_command(_, __, message: Message) -> bool:
    return bool(message.text and message.text.startswith("/"))


is_any_command = filters.create(_is_command)


@Client.on_message(is_any_command, group=-1)
async def delete_command_message(client: Client, message: Message):
    try:
        await message.delete()
    except Exception:
        pass
    message.continue_propagation()
