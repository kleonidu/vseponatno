
from aiogram import Router
from aiogram.types import Message

router = Router(name=__name__)

@router.errors()
async def on_error(update, exception):
    if isinstance(update, Message):
        await update.answer("Упс, что-то пошло не так. Попробуй ещё раз или начни заново командой /new.")
    return True
