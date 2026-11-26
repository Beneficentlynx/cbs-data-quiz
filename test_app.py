"""
Unit tests for CBS Quiz modules.
"""

from modules.cbs_api import CBSApiManager
from modules.quiz_engine import (
    calculate_projected_value,
    format_number_dutch,
    calculate_question_score,
    calculate_choice_score,
    generate_wrapped_analytics,
)


def test_cbs_api():
    manager = CBSApiManager()
    questions = manager.get_all_questions()
    assert len(questions) >= 10, f"Expected at least 10 questions, got {len(questions)}"
    
    # Check age filtering
    for age in ["15-24", "25-39", "40-64", "65+", "alle"]:
        q_age = manager.get_questions_for_age(age)
        assert len(q_age) > 0, f"Expected questions for age {age}"
    print("✅ CBS API and questions database verified.")


def test_calculations():
    # Base 360,000 with +5.0% change = 378,000
    val = calculate_projected_value(360000, 5.0)
    assert abs(val - 378000) < 1e-3, f"Expected 378000, got {val}"

    # Formatting test
    formatted_eur = format_number_dutch(448000, "euro")
    assert "448.000" in formatted_eur and "€" in formatted_eur

    formatted_pct = format_number_dutch(8.7, "%")
    assert formatted_pct == "8,7%"
    print("✅ Numerical formatting and projections verified.")


def test_scoring():
    # Exact guess gets 100
    score, error, bias = calculate_question_score(5.0, 5.0, 6.0)
    assert score == 100.0
    assert error == 0.0

    # Off by 3% gives rewarding score (> 70) and never 0
    score, error, bias = calculate_question_score(8.0, 5.0, 6.0)
    assert score >= 70.0, f"Expected >= 70, got {score}"
    assert error == 3.0

    # Even far off (e.g. off by 25%), score is >= 15 points (never 0 points)
    score, error, bias = calculate_question_score(30.0, 5.0, 6.0)
    assert score >= 15.0, f"Expected >= 15, got {score}"

    # Choice question scoring
    c_score, c_err, c_bias = calculate_choice_score("Juli", "Juli")
    assert c_score == 100.0 and c_err == 0.0

    w_score, w_err, w_bias = calculate_choice_score("Januari", "Juli")
    assert w_score == 25.0 and w_err == 1.0

    print(f"✅ Friendly scoring formula verified (far off score: {score}, choice exact: {c_score}, choice wrong: {w_score}).")


def test_wrapped_generation():
    dummy_answers = [
        {"id": "q1", "title": "Huizenprijzen", "category": "Woningmarkt", "guess_pct": 8.0, "actual_pct": 7.7, "score": 95.0, "error": 0.3},
        {"id": "q2", "title": "Werkloosheid", "category": "Arbeidsmarkt", "guess_pct": 12.0, "actual_pct": 5.0, "score": 20.0, "error": 7.0},
        {"id": "q3", "title": "Inflatie", "category": "Economie", "guess_pct": -5.0, "actual_pct": -10.5, "score": 60.0, "error": 5.5},
        {"id": "q4", "title": "Zonnepanelen", "category": "Klimaat", "guess_pct": 14.0, "actual_pct": 13.5, "score": 98.0, "error": 0.5},
    ]
    wrapped = generate_wrapped_analytics(dummy_answers)
    assert "total_score" in wrapped
    assert "archetype" in wrapped
    assert "best_category" in wrapped
    assert "worst_category" in wrapped
    assert len(wrapped["best_3_questions"]) == 3
    assert len(wrapped["worst_3_questions"]) == 3
    print("✅ CBS Wrapped generation verified.")


if __name__ == "__main__":
    test_cbs_api()
    test_calculations()
    test_scoring()
    test_wrapped_generation()
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
