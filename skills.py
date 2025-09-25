
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
import re
from fractions import Fraction
from math import isclose

from .session import Step, TutorState
from .utils import is_number, to_float

@dataclass
class Skill:
    id: str

    def match(self, problem_text: str) -> float:
        raise NotImplementedError

    def init(self, problem_text: str) -> TutorState:
        raise NotImplementedError

    def next_step(self, state: TutorState, user_text: str) -> Tuple[str, Optional[Step]]:
        raise NotImplementedError

class LinearEq(Skill):
    id = "linear_eq"

    def match(self, problem_text: str) -> float:
        return 0.7 if "x" in problem_text and "^2" not in problem_text else 0.0

    def init(self, problem_text: str) -> TutorState:
        steps = [
            Step(
                prompt="Какой коэффициент при x (a) в уравнении? Напиши число.",
                hint_levels=["Посмотри на множитель, который стоит рядом с x.",
                             "Если x без числа — коэффициент равен 1 или -1.",
                             "В записи ax+b=c — a это число перед x."],
                answer_checker="coef_a"
            ),
            Step(
                prompt="Какое свободное слагаемое перенесено влево (b) в форме ax + b = c?",
                hint_levels=["Ищи число, которое стоит отдельно от x в левой части.",
                             "Знак важен: если '- 5', то b = -5.",
                             "В форме ax + b = c — b это 'плюс/минус число' слева."],
                answer_checker="coef_b"
            ),
            Step(
                prompt="Чему равна правая часть (c)? Напиши число.",
                hint_levels=["Смотри на число после знака '='.",
                             "Если справа выражение — оцени его значение.",
                             "В форме ax + b = c — c это правая часть."],
                answer_checker="coef_c"
            ),
            Step(
                prompt="Выполни шаг: вычти b из обеих частей. Чему равно a·x после этого шага?",
                hint_levels=["a·x = c - b.",
                             "Подставь найденные a, b, c в c - b.",
                             "Запиши результат как число."],
                answer_checker="ax_after"
            ),
            Step(
                prompt="Теперь раздели обе части на a. Чему равен x? (число)",
                hint_levels=["x = (c - b)/a.",
                             "Подставь свои значения.",
                             "Вычисли численно, округление не требуется."],
                answer_checker="x_value"
            ),
        ]
        return TutorState(skill_id=self.id, problem_text=problem_text, steps=steps, scratch={})

    def next_step(self, state: TutorState, user_text: str):
        i = state.step_index
        step = state.steps[i]
        if step.answer_checker == "coef_a":
            if is_number(user_text):
                state.scratch["a"] = to_float(user_text)
                fb = f"Принято: a = {state.scratch['a']}"
            else:
                return ("Нужно число. Например: 2 или -3.", step)
        elif step.answer_checker == "coef_b":
            if is_number(user_text):
                state.scratch["b"] = to_float(user_text)
                fb = f"Ок: b = {state.scratch['b']}"
            else:
                return ("Ответ должен быть числом со знаком при необходимости.", step)
        elif step.answer_checker == "coef_c":
            if is_number(user_text):
                state.scratch["c"] = to_float(user_text)
                fb = f"Записал: c = {state.scratch['c']}"
            else:
                return ("Введи число.", step)
        elif step.answer_checker == "ax_after":
            if is_number(user_text):
                val = to_float(user_text)
                a = state.scratch.get("a"); b = state.scratch.get("b"); c = state.scratch.get("c")
                if a is None or b is None or c is None:
                    return ("Сначала определим a, b, c выше.", step)
                expected = c - b
                if abs(val - expected) <= max(1e-9, abs(expected)*1e-6):
                    fb = f"Верно: a·x = c - b = {val:.6g}"
                    state.scratch["ax_val"] = val
                else:
                    return (f"Проверь вычисления: должно получиться {expected:.6g} (из c - b). Попробуй ещё раз.", step)
            else:
                return ("Напиши число, которое равно c - b.", step)
        elif step.answer_checker == "x_value":
            if is_number(user_text):
                val = to_float(user_text)
                a = state.scratch.get("a"); ax = state.scratch.get("ax_val")
                if a is None or ax is None:
                    return ("Сначала вычислим c - b на предыдущем шаге.", step)
                expected = ax / a
                if abs(val - expected) <= max(1e-9, abs(expected)*1e-6):
                    fb = f"Отлично! x = {val:.6g}. Ты сам пришёл к ответу."
                    state.finished = True
                    return (fb, None)
                else:
                    return (f"Не сходится. Подумай: x = (c - b)/a = {expected:.6g}. Введи точное значение.", step)
            else:
                return ("Нужно число.", step)
        else:
            fb = "Ок."

        state.step_index += 1
        if state.step_index < len(state.steps):
            return (fb, state.steps[state.step_index])
        else:
            state.finished = True
            return (fb, None)

class FracAdd(Skill):
    id = "frac_add"

    def match(self, problem_text: str) -> float:
        return 0.8 if re.search(r"\d+/\d+\s*\+\s*\d+/\d+", problem_text) else 0.0

    def init(self, problem_text: str) -> TutorState:
        steps = [
            Step("Какие знаменатели у дробей? Напиши через запятую.",
                 ["Посмотри на числа снизу каждой дроби.",
                  "Формат: b, d.",
                  "Пример: 3, 4"],
                 "denoms"),
            Step("Найди общий знаменатель (НОК знаменателей).",
                 ["Подумай о кратном обоим знаменателям.",
                  "Найди наименьшее общее кратное.",
                  "Пример: для 3 и 4 — 12."],
                 "lcd"),
            Step("Приведи обе дроби к общему знаменателю. Каковы новые числители? (через запятую)",
                 ["Умножь числитель и знаменатель каждой дроби на недостающий множитель.",
                  "Формат: n1, n2",
                  "Не сокращай пока."],
                 "new_nums"),
            Step("Сложи числители. Какой числитель итоговой дроби?",
                 ["Сложи два получившихся числителя.", "Только число.", "Проверь внимательно."],
                 "sum_num"),
            Step("Сократи дробь, если возможно. Запиши окончательный ответ в виде несократимой дроби n/m.",
                 ["Раздели числитель и знаменатель на их НОД.",
                  "Можно привести к неправильной дроби.",
                  "Убедись, что сократить больше нельзя."],
                 "final_frac"),
        ]
        return TutorState(skill_id=self.id, problem_text=problem_text, steps=steps, scratch={})

    def next_step(self, state: TutorState, user_text: str):
        i = state.step_index
        step = state.steps[i]
        if step.answer_checker == "denoms":
            parts = [p.strip() for p in user_text.replace(";", ",").split(",")]
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                return ("Формат: b, d. Пример: 3, 4", step)
            b, d = map(int, parts)
            state.scratch.update({"b": b, "d": d})
            fb = f"Ок, знаменатели: {b} и {d}."
        elif step.answer_checker == "lcd":
            if not is_number(user_text):
                return ("Введи число — общий знаменатель.", step)
            lcd = int(float(user_text))
            state.scratch["lcd"] = lcd
            fb = f"Принято: общий знаменатель {lcd}."
        elif step.answer_checker == "new_nums":
            parts = [p.strip() for p in user_text.replace(";", ",").split(",")]
            if len(parts) != 2 or not all(re.match(r"^-?\d+$", p) for p in parts):
                return ("Формат: n1, n2 (только целые).", step)
            n1, n2 = map(int, parts)
            state.scratch.update({"n1": n1, "n2": n2})
            fb = f"Есть: новые числители {n1} и {n2}."
        elif step.answer_checker == "sum_num":
            if not re.match(r"^-?\d+$", user_text.strip()):
                return ("Нужно целое число.", step)
            total = int(user_text.strip())
            state.scratch["sum_num"] = total
            fb = f"Сумма числителей = {total}."
        elif step.answer_checker == "final_frac":
            m = re.match(r"^\s*(-?\d+)\s*/\s*(\d+)\s*$", user_text)
            if not m:
                return ("Формат ответа: n/m (например, 7/12).", step)
            n, m_ = int(m.group(1)), int(m.group(2))
            fr = Fraction(n, m_)
            if fr.numerator != n or fr.denominator != m_:
                fb = f"Хорошо! Несократимый вид: {fr.numerator}/{fr.denominator}."
            else:
                fb = "Отлично! Дробь уже несократима."
            state.finished = True
            return (fb, None)
        else:
            fb = "Ок."

        state.step_index += 1
        if state.step_index < len(state.steps):
            return (fb, state.steps[state.step_index])
        else:
            state.finished = True
            return (fb, None)

class QuadraticEq(Skill):
    id = "quadratic_eq"

    def match(self, problem_text: str) -> float:
        return 0.9 if ("x^2" in problem_text or "x²" in problem_text) else 0.0

    def init(self, problem_text: str) -> TutorState:
        steps = [
            Step("Определи коэффициенты a, b, c в уравнении ax^2 + bx + c = 0. Напиши: a, b, c",
                 ["Смотри на множители при x^2 и x, и свободный член.",
                  "Не забудь про знаки.",
                  "Формат: a, b, c (например, 1, -5, 6)"],
                 "abc"),
            Step("Найди дискриминант: D = b^2 - 4ac. Введи его значение.",
                 ["Подставь свои a, b, c.",
                  "Сначала посчитай b^2, затем 4ac.",
                  "Только число."],
                 "disc"),
            Step("Сколько корней уравнения? (введи 0, 1 или 2)",
                 ["Если D > 0 — два корня; D = 0 — один; D < 0 — нет действительных корней.",
                  "Сравни D с нулем.",
                  "Только 0/1/2."],
                 "roots_count"),
            Step("Вычисли корень(я) по формуле: x = (-b ± √D) / (2a). Введи через запятую (если два).",
                 ["Используй точные значения. Округлять не нужно.",
                  "Порядок любой, раздели запятой.",
                  "Для одного корня введи только его."],
                 "roots_values"),
        ]
        return TutorState(skill_id=self.id, problem_text=problem_text, steps=steps, scratch={})

    def next_step(self, state: TutorState, user_text: str):
        i = state.step_index
        step = state.steps[i]
        if step.answer_checker == "abc":
            parts = [p.strip() for p in user_text.replace(";", ",").split(",")]
            if len(parts) != 3:
                return ("Формат: a, b, c (например, 1, -5, 6).", step)
            try:
                a, b, c = map(float, parts)
            except:
                return ("Коэффициенты должны быть числами.", step)
            state.scratch.update({"a": a, "b": b, "c": c})
            fb = f"Записал: a={a}, b={b}, c={c}."
        elif step.answer_checker == "disc":
            try:
                D = float(user_text.replace(",", "."))
            except:
                return ("Введи числовое значение дискриминанта.", step)
            state.scratch["D"] = D
            fb = f"D = {D}."
        elif step.answer_checker == "roots_count":
            if user_text.strip() not in {"0","1","2"}:
                return ("Введи 0, 1 или 2.", step)
            cnt = int(user_text.strip())
            state.scratch["roots_count"] = cnt
            fb = f"Принято: {cnt} корень(я)."
        elif step.answer_checker == "roots_values":
            parts = [p.strip() for p in user_text.replace(";", ",").split(",") if p.strip()]
            xs = []
            for p in parts:
                try:
                    xs.append(float(p.replace(",", ".")))
                except:
                    return ("Корни должны быть числами, раздели запятой.", step)
            fb = "Отличная работа! Ты вывел(а) корни сам(а)."
            state.finished = True
            return (fb, None)
        else:
            fb = "Ок."

        state.step_index += 1
        if state.step_index < len(state.steps):
            return (fb, state.steps[state.step_index])
        else:
            state.finished = True
            return (fb, None)

class Proportion(Skill):
    id = "proportion"

    def match(self, problem_text: str) -> float:
        return 0.7 if (":" in problem_text and "=" in problem_text) else 0.0

    def init(self, problem_text: str) -> TutorState:
        steps = [
            Step("Запиши пропорцию в виде дробей: a/b = c/x. Что будет в числителе и знаменателе слева? (a/b)",
                 ["Читай пропорцию 'a относится к b'.",
                  "Левая дробь — первая пара.",
                  "Запиши как a/b."],
                 "left_frac"),
            Step("Сформулируй правило: произведение крайних равно произведению средних. Как выглядит уравнение?",
                 ["a·x = b·c.", "Перемножь по диагонали.", "Запиши без вычислений."],
                 "diag_rule"),
            Step("Вырази x из уравнения. Что получится?",
                 ["x = (b·c)/a.", "Сначала вырази x символически.", "Числа подставим позже."],
                 "solve_x"),
            Step("Подставь числа из задачи и вычисли x. Напиши число.",
                 ["Аккуратно подставь и сократи при необходимости.", "Только число.", "Без округления."],
                 "x_value"),
        ]
        return TutorState(skill_id=self.id, problem_text=problem_text, steps=steps, scratch={})

    def next_step(self, state: TutorState, user_text: str):
        i = state.step_index
        step = state.steps[i]
        if step.answer_checker == "left_frac":
            if "/" not in user_text:
                return ("Запиши как a/b (пример: 2/3).", step)
            fb = "Ок."
        elif step.answer_checker == "diag_rule":
            fb = "Правильно: a·x = b·c."
        elif step.answer_checker == "solve_x":
            if "x" not in user_text:
                return ("Вырази именно x (например: x = (b·c)/a).", step)
            fb = "Верно: x = (b·c)/a."
        elif step.answer_checker == "x_value":
            if not is_number(user_text):
                return ("Нужно число.", step)
            fb = "Готово! Ты нашёл(ла) значение x сам(а)."
            state.finished = True
            return (fb, None)
        else:
            fb = "Ок."

        state.step_index += 1
        if state.step_index < len(state.steps):
            return (fb, state.steps[state.step_index])
        else:
            state.finished = True
            return (fb, None)

SKILLS: Dict[str, Skill] = {
    LinearEq.id: LinearEq(),
    FracAdd.id: FracAdd(),
    QuadraticEq.id: QuadraticEq(),
    Proportion.id: Proportion(),
}

def best_skill(problem_text: str) -> Skill:
    best = None
    best_score = -1
    for s in SKILLS.values():
        score = s.match(problem_text)
        if score > best_score:
            best_score = score
            best = s
    return best if best else SKILLS["linear_eq"]
