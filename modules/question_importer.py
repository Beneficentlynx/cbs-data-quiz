"""
Question Importer & Validator for CBS Data Quiz.
Supports importing from JSON and CSV formats with auto-completion and validation.
"""

import json
import os
import pandas as pd
from typing import Dict, List, Any, Tuple, Union

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions_data.json")

VALID_AGE_CATEGORIES = {"15-24", "25-39", "40-64", "65+"}


def normalize_question_record(raw: Dict[str, Any]) -> Tuple[Union[Dict[str, Any], None], str]:
    """
    Validates and normalizes a single question record.
    Returns (cleaned_record, error_message). If error_message is non-empty, record is None.
    """
    qid = str(raw.get("id", "")).strip()
    if not qid:
        return None, "Ontbrekend 'id' veld"

    title = str(raw.get("title", "")).strip()
    if not title:
        return None, f"Vraag '{qid}': ontbrekende 'title'"

    category = str(raw.get("category", "Algemeen")).strip()

    # Parse target ages with smart mapping (e.g. 18-24 -> 15-24)
    target_ages = raw.get("target_ages", [])
    if isinstance(target_ages, str):
        target_ages = [a.strip() for a in target_ages.replace(";", ",").split(",") if a.strip()]
    elif not isinstance(target_ages, list):
        target_ages = ["25-39"]

    age_mapping = {"18-24": "15-24", "15-24": "15-24", "25-39": "25-39", "40-64": "40-64", "65+": "65+"}
    normalized_ages = [age_mapping.get(str(a).strip().replace("“", "").replace("”", "").replace('"', ''), str(a).strip()) for a in target_ages]
    valid_ages = list(dict.fromkeys([a for a in normalized_ages if a in VALID_AGE_CATEGORIES]))
    if not valid_ages:
        valid_ages = ["25-39"]

    # Check question type (slider vs choice)
    q_type = str(raw.get("type", "")).strip().lower()
    choices = raw.get("choices", [])
    if choices or q_type == "choice" or not str(raw.get("baseline_value", "")).replace(".", "").replace(",", "").isdigit():
        q_type = "choice" if choices or not str(raw.get("baseline_value", "")).replace(".", "").replace(",", "").replace("-", "").isdigit() else "slider"

    if q_type == "choice":
        base_val = str(raw.get("baseline_value", "")).strip()
        act_val = str(raw.get("actual_value", "")).strip()
        actual_change = 0.0
        if not choices:
            choices = [base_val, act_val]
    else:
        # Numeric values
        try:
            base_str = str(raw.get("baseline_value", 0)).replace("€", "").replace("%", "").strip()
            # handle dot thousands separator vs decimal: if contains dot and comma, or dot followed by 3 digits
            if "," in base_str and "." in base_str:
                base_str = base_str.replace(".", "").replace(",", ".")
            elif "," in base_str:
                base_str = base_str.replace(",", ".")
            elif base_str.count(".") == 1 and len(base_str.split(".")[1]) == 3 and float(base_str) > 100:
                # likely thousands separator e.g. 489.072
                base_str = base_str.replace(".", "")

            act_str = str(raw.get("actual_value", 0)).replace("€", "").replace("%", "").strip()
            if "," in act_str and "." in act_str:
                act_str = act_str.replace(".", "").replace(",", ".")
            elif "," in act_str:
                act_str = act_str.replace(",", ".")
            elif act_str.count(".") == 1 and len(act_str.split(".")[1]) == 3 and float(act_str) > 100:
                act_str = act_str.replace(".", "")

            base_val = float(base_str)
            act_val = float(act_str)
        except (ValueError, TypeError):
            return None, f"Vraag '{qid}': 'baseline_value' of 'actual_value' is geen geldig getal"

    # Auto-calculate percentage change if missing or zero
    actual_change = raw.get("actual_change_pct")
    if actual_change is None or actual_change == "":
        if base_val != 0:
            actual_change = round(((act_val - base_val) / base_val) * 100.0, 2)
        else:
            actual_change = 0.0
    else:
        try:
            actual_change = float(str(actual_change).replace(",", ".").replace("%", "").strip())
        except ValueError:
            actual_change = round(((act_val - base_val) / base_val) * 100.0, 2) if base_val != 0 else 0.0

    unit = str(raw.get("unit", "")).strip().lower()
    base_fmt = str(raw.get("baseline_formatted", str(base_val))).strip()
    act_fmt = str(raw.get("actual_formatted", str(act_val))).strip()

    prompt = str(raw.get("question_prompt", "")).strip()
    if not prompt:
        prompt = f"In {raw.get('period_baseline', 'vorig jaar')} was dit **{base_fmt}**. Hoeveel procent veranderde dit in {raw.get('period_current', 'dit jaar')}?"

    explanation = str(raw.get("explanation", "")).strip()
    if not explanation:
        explanation = f"Het cijfer veranderde van {base_fmt} naar {act_fmt} ({actual_change:+.1f}%)."

    statline_id = str(raw.get("statline_table_id", "80590ned")).strip()
    article_url = str(raw.get("cbs_article_url", "")).strip()
    if not article_url or "cbs.nl" not in article_url:
        article_url = f"https://opendata.cbs.nl/statline/#/CBS/nl/dataset/{statline_id}/table"

    article_title = str(raw.get("cbs_article_title", "")).strip()
    if not article_title:
        article_title = f"CBS StatLine: Datatabel ({statline_id})"

    # Slider configuration
    slider_cfg = raw.get("slider_range")
    if not isinstance(slider_cfg, dict):
        bound = max(25.0, abs(actual_change) * 1.6)
        bound = round(bound / 5.0) * 5.0
        slider_cfg = {
            "min": float(-bound),
            "max": float(bound),
            "step": 0.5,
            "default": 0.0,
        }

    tolerance = raw.get("tolerance_pct")
    try:
        tolerance = float(tolerance) if tolerance else 6.0
    except (ValueError, TypeError):
        tolerance = 6.0

    val_preview = str(raw.get("value_format_preview", ""))
    if not val_preview:
        if unit == "euro":
            val_preview = "€ {val:,.0f}" if base_val >= 1000 else "€ {val:.2f}"
        elif unit == "%":
            val_preview = "{val:.1f}%"
        else:
            val_preview = f"{{val:,.0f}} {unit}".strip()

    cleaned = {
        "id": qid,
        "type": q_type,
        "choices": choices,
        "category": category,
        "target_ages": valid_ages,
        "title": title,
        "period_baseline": str(raw.get("period_baseline", "2025")),
        "period_current": str(raw.get("period_current", "2026")),
        "baseline_value": base_val,
        "baseline_formatted": base_fmt,
        "unit": unit,
        "actual_value": act_val,
        "actual_formatted": act_fmt,
        "actual_change_pct": round(actual_change, 2),
        "tolerance_pct": tolerance,
        "slider_range": slider_cfg,
        "question_prompt": prompt,
        "value_format_preview": val_preview,
        "explanation": explanation,
        "cbs_article_title": article_title,
        "cbs_article_url": article_url,
        "statline_table_id": statline_id,
    }
    return cleaned, ""


def import_questions_from_json(json_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Imports and validates questions from a JSON string."""
    try:
        data = json.loads(json_content)
    except Exception as e:
        return [], [f"Ongeldige JSON syntax: {str(e)}"]

    if not isinstance(data, list):
        if isinstance(data, dict):
            data = [data]
        else:
            return [], ["JSON root moet een lijst met vraag-objecten zijn."]

    valid_questions = []
    errors = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"Item #{idx+1} is geen JSON object.")
            continue
        cleaned, err = normalize_question_record(item)
        if err:
            errors.append(f"Item #{idx+1}: {err}")
        else:
            valid_questions.append(cleaned)

    return valid_questions, errors


def import_questions_from_csv(csv_file_or_content: Any) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Imports and validates questions from a CSV file / string."""
    try:
        if isinstance(csv_file_or_content, str):
            from io import StringIO
            df = pd.read_csv(StringIO(csv_file_or_content))
        else:
            df = pd.read_csv(csv_file_or_content)
    except Exception as e:
        return [], [f"Fout bij lezen CSV bestand: {str(e)}"]

    # Fill NaN values with empty string or sensible default
    records = df.fillna("").to_dict(orient="records")

    valid_questions = []
    errors = []
    for idx, rec in enumerate(records):
        cleaned, err = normalize_question_record(rec)
        if err:
            errors.append(f"Rij #{idx+2}: {err}")
        else:
            valid_questions.append(cleaned)

    return valid_questions, errors


def save_imported_questions(new_questions: List[Dict[str, Any]], overwrite: bool = False) -> int:
    """
    Saves validated questions into data/questions_data.json.
    If overwrite=False, updates existing questions by ID and appends new ones.
    Returns the total count of stored questions.
    """
    existing_questions = []
    if os.path.exists(QUESTIONS_FILE) and not overwrite:
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                existing_questions = json.load(f)
        except Exception:
            existing_questions = []

    # Map existing questions by ID
    q_map = {q["id"]: q for q in existing_questions}
    for q in new_questions:
        q_map[q["id"]] = q  # Overwrite or add

    final_list = list(q_map.values())

    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)

    return len(final_list)
