
import re
from typing import List, Tuple

def classify(problem: str) -> List[Tuple[str, float]]:
    text = problem.replace(" ", "").lower()
    scores = []

    if re.search(r"=.+x", text) or re.search(r"x.+=", text):
        if re.search(r"x\^2", text):
            pass
        else:
            scores.append(("linear_eq", 0.8))

    if re.search(r"x\^2", text) or "x²" in text or "discriminant" in text:
        scores.append(("quadratic_eq", 0.9))

    if re.search(r"\d+/\d+\+\d+/\d+", text):
        scores.append(("frac_add", 0.85))

    if (":" in problem and "=" in problem):
        scores.append(("proportion", 0.7))

    if not scores:
        scores.append(("linear_eq", 0.3))
    return sorted(scores, key=lambda t: t[1], reverse=True)
