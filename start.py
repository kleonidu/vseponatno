
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

router = Router(name=__name__)

WELCOME = (
    "Привет! Я Математический Коуч 🤖\n\n"
    "Отправь условие задачи (например: 'Реши: 2x + 5 = 17'), "
    "и я разложу её на простые вопросы, чтобы ты сам(а) дошёл(ла) до ответа.\n\n"
    "Команды:\n"
    "/new — начать новую задачу\n"
    "/hint — подсказка к текущему шагу\n"
    "/giveup — показать план решения (без ответа)\n"
    "/topics — список поддерживаемых типов\n"
    "/help — краткая справка"
)

@router.message(CommandStart())
async def on_start(m: Message):
    await m.answer(WELCOME)

@router.message(Command("help"))
async def on_help(m: Message):
    await m.answer(WELCOME)

@router.message(Command("topics"))
async def on_topics(m: Message):
    await m.answer(
        "Поддерживаю пока такие типы задач:\n"
        "• Линейные уравнения (ax + b = c)\n"
        "• Квадратные уравнения (ax² + bx + c = 0)\n"
        "• Сложение дробей (a/b + c/d)\n"
        "• Пропорции (a:b = c:x)\n\n"
        "Просто пришли условие в свободной форме."
    )
