"""
CBS Quiz Engine: scoring logic, mathematical computations and Wrapped analytics.
"""

import math
from typing import Dict, List, Any, Tuple


def calculate_projected_value(baseline_value: float, change_pct: float) -> float:
    """Calculates the absolute value given the baseline and percentage change."""
    return baseline_value * (1.0 + (change_pct / 100.0))


def format_number_dutch(val: float, unit: str = "") -> str:
    """Formats numeric values into Dutch locale style."""
    if unit == "%":
        return f"{val:.1f}%".replace(".", ",")
    elif unit == "euro":
        if val >= 1000:
            formatted = f"{val:,.0f}".replace(",", ".")
            return f"€ {formatted}"
        return f"€ {val:.2f}".replace(".", ",")
    elif unit in ("personen", "inwoners", "woningen", "autos"):
        if val >= 1_000_000:
            mil = val / 1_000_000
            return f"{mil:.2f} miljoen {unit}".replace(".", ",")
        formatted = f"{val:,.0f}".replace(",", ".")
        return f"{formatted} {unit}"
    elif unit == "jaar":
        return f"{val:.1f} jaar".replace(".", ",")
    else:
        if val >= 1000:
            formatted = f"{val:,.0f}".replace(",", ".")
            return f"{formatted} {unit}".strip()
        return f"{val:.1f} {unit}".replace(".", ",").strip()


def calculate_question_score(guess_pct: float, actual_pct: float, tolerance_pct: float = 6.0) -> Tuple[float, float, str]:
    """
    Computes proximity score (15 - 100), error margin, and direction bias.
    Uses a smooth decay curve so players never receive a harsh 0 points,
    plus an extra bonus for guessing the correct direction of change.
    """
    error = abs(guess_pct - actual_pct)

    # Base decay curve (range 15 to 100)
    # At error=0 -> 100, at error=5 -> 70, at error=15 -> 35, at error=30+ -> ~18-20
    decay = math.exp(-error / 11.0)
    score_val = 15.0 + 85.0 * decay

    # Direction bonus: +5 points if guessed the correct direction of change (or both near 0)
    guessed_dir = 1 if guess_pct > 0.3 else (-1 if guess_pct < -0.3 else 0)
    actual_dir = 1 if actual_pct > 0.3 else (-1 if actual_pct < -0.3 else 0)

    if guessed_dir == actual_dir and guessed_dir != 0:
        score_val += 5.0
    elif abs(guess_pct) < 1.0 and abs(actual_pct) < 1.0:
        score_val += 5.0

    score = round(min(100.0, max(15.0, score_val)), 1)

    diff = guess_pct - actual_pct
    if abs(diff) < 0.3:
        bias = "Vrijwel exact raak! 🎯"
    elif diff > 0:
        bias = f"{diff:.1f}% te hoog geschat"
    else:
        bias = f"{abs(diff):.1f}% te laag geschat"

    return score, round(error, 2), bias


def generate_wrapped_analytics(answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates full Spotify-Wrapped style analytics based on player's answers.
    """
    if not answers:
        return {}

    total_score = sum(a["score"] for a in answers) / len(answers)
    total_score = round(total_score, 1)

    # Category performance
    categories: Dict[str, List[float]] = {}
    for a in answers:
        cat = a["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(a["score"])

    cat_averages = {
        cat: round(sum(scores) / len(scores), 1)
        for cat, scores in categories.items()
    }
    sorted_cats = sorted(cat_averages.items(), key=lambda x: x[1], reverse=True)
    best_cat = sorted_cats[0]
    worst_cat = sorted_cats[-1]

    # Best and worst questions
    sorted_by_score = sorted(answers, key=lambda x: x["score"], reverse=True)
    best_3 = sorted_by_score[:3]
    worst_3 = sorted_by_score[-3:]
    worst_3.reverse()  # lowest score first

    # Overall bias calculation
    signed_diffs = [a["guess_pct"] - a["actual_pct"] for a in answers]
    avg_bias = sum(signed_diffs) / len(signed_diffs)

    # Archetype & Personality Badge (CBS official authoritative tone)
    if total_score >= 80:
        archetype = "Statistisch Scherpzinnig 🧠"
        archetype_desc = "Uw kennis van actuele maatschappelijke ontwikkelingen sluit nauwgezet aan op de officiële CBS-statistieken."
    elif total_score >= 65:
        archetype = "Goed Geïnformeerd Waarnemer 📊"
        archetype_desc = "U beschikt over een gedegen en realistisch overzicht van trends in de economie, arbeidsmarkt en woningbouw."
    elif total_score >= 50:
        archetype = "Maatschappelijk Betrokken 📰"
        archetype_desc = "Uw inschattingen volgen veelal de juiste richting, hoewel enkele conjuncturele indicatoren u wisten te verrassen."
    else:
        archetype = "Intuïtief Waarnemer 💭"
        archetype_desc = "Uw maatschappelijke beeld wijkt op meerdere indicatoren af van de geregistreerde CBS-statistieken."

    if avg_bias > 2.5:
        bias_label = "Tendens tot overschatting van stijgingen"
        bias_desc = f"U schatte de veranderingen gemiddeld {avg_bias:+.1f}% hoger in dan de geregistreerde CBS-realiteit."
    elif avg_bias < -2.5:
        bias_label = "Tendens tot onderschatting van mutaties"
        bias_desc = f"U schatte de ontwikkelingen gemiddeld {abs(avg_bias):.1f}% gematigder in dan de CBS-cijfers uitwijzen."
    else:
        bias_label = "Gebalanceerd waarnemingspatroon"
        bias_desc = "Uw inschattingen waren evenwichtig verdeeld rondom de feitelijke CBS-waarden."

    # Share text
    share_text = (
        f"📊 CBS Statistische Feitencheck 2026\n"
        f"🏆 Totale Score: {total_score:.0f}%\n"
        f"🎖️ Profiel: {archetype}\n"
        f"🌟 Meest accurate domein: {best_cat[0]} ({best_cat[1]:.0f}%)\n"
        f"⚠️ Grootste afwijking: {worst_cat[0]} ({worst_cat[1]:.0f}%)\n"
        f"Centraal Bureau voor de Statistiek — Voor wat er feitelijk gebeurt."
    )

    return {
        "total_score": total_score,
        "archetype": archetype,
        "archetype_desc": archetype_desc,
        "bias_label": bias_label,
        "bias_desc": bias_desc,
        "best_category": best_cat,
        "worst_category": worst_cat,
        "category_scores": cat_averages,
        "best_3_questions": best_3,
        "worst_3_questions": worst_3,
        "share_text": share_text,
    }
