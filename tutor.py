
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from ..engine.session import MemoryStore
from ..engine.skills import SKILLS, best_skill, TutorState, Step

router = Router(name=__name__)
store = MemoryStore()

def _current_step_text(state: TutorState) -> str:
    step = state.steps[state.step_index]
    return f"Шаг {state.step_index+1}/{len(state.steps)}:\n{step.prompt}"

@router.message(Command("new"))
async def on_new(m: Message):
    store.clear(m.from_user.id)
    await m.answer("Ок! Пришли новое задание текстом.")

@router.message(Command("hint"))
async def on_hint(m: Message):
    state = store.get(m.from_user.id)
    if not state or state.finished:
        return await m.answer("Сначала начни задачу. Пришли условие или используй /new.")
    step = state.steps[state.step_index]
    used = state.scratch.get("hints_used", 0)
    if used >= len(step.hint_levels):
        return await m.answer("Больше подсказок нет — попробуй сформулировать шаг своими словами.")
    hint = step.hint_levels[used]
    state.scratch["hints_used"] = used + 1
    await m.answer(f"Подсказка: {hint}")

@router.message(Command("giveup"))
async def on_giveup(m: Message):
    state = store.get(m.from_user.id)
    if not state:
        return await m.answer("Нет активной задачи. Пришли условие для начала.")
    if state.skill_id == "linear_eq":
        text = ("План решения линейного уравнения ax + b = c:\n"
                "1) Вычесть b из обеих частей: a·x = c - b\n"
                "2) Разделить обе части на a: x = (c - b)/a\n"
                "Попробуй продолжить сам(а) 😉")
    elif state.skill_id == "quadratic_eq":
        text = ("План решения квадратного уравнения:\n"
                "1) Определи a, b, c\n"
                "2) Посчитай D = b² - 4ac\n"
                "3) Если D≥0, x = (-b ± √D)/(2a)")
    elif state.skill_id == "frac_add":
        text = ("План сложения дробей a/b + c/d:\n"
                "1) Найди НОК знаменателей\n"
                "2) Приведи дроби к нему\n"
                "3) Сложи числители и сократи")
    elif state.skill_id == "proportion":
        text = ("План решения пропорции a:b = c:x:\n"
                "1) Перейди к дробям: a/b = c/x\n"
                "2) Перемножь по диагонали: a·x = b·c\n"
                "3) Вырази x: x = (b·c)/a")
    else:
        text = "Общий план: раздели на шаги и двигайся от определения к преобразованиям."
    await m.answer(text + "\n\nЧтобы продолжить — ответь на текущий шаг или используй /hint.")

@router.message(F.text)
async def on_text(m: Message):
    uid = m.from_user.id
    state = store.get(uid)

    if not state:
        problem = m.text.strip()
        skill = best_skill(problem)
        state = skill.init(problem)
        store.set(uid, state)
        await m.answer("Принял задачу. Я не даю ответ, а веду тебя вопросами к решению. ✍️")
        return await m.answer(_current_step_text(state))

    # route to skill
    skill = {s.id: s for s in SKILLS.values()}[state.skill_id]
    feedback, next_step = skill.next_step(state, m.text.strip())
    if next_step is None:
        if state.finished:
            store.clear(uid)
            return await m.answer(feedback + "\n\nГотов(а) к новой задаче? Используй /new или пришли текст.")
        else:
            return await m.answer(feedback)
    else:
        await m.answer(feedback)
        await m.answer(_current_step_text(state))
