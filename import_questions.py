"""
CLI Tool to Import Questions into CBS Data Quiz.
Usage:
    python import_questions.py pad/naar/vragen.csv
    python import_questions.py pad/naar/vragen.json
"""

import sys
import os
from modules.question_importer import (
    import_questions_from_csv,
    import_questions_from_json,
    save_imported_questions,
)


def main():
    if len(sys.argv) < 2:
        print("Gebruik: python import_questions.py <bestand.csv of bestand.json> [--overwrite]")
        print("Voorbeelden:")
        print("  python import_questions.py data/templates/questions_template.csv")
        print("  python import_questions.py data/templates/questions_template.json")
        sys.exit(1)

    file_path = sys.argv[1]
    overwrite = "--overwrite" in sys.argv

    if not os.path.exists(file_path):
        print(f"❌ Bestand niet gevonden: {file_path}")
        sys.exit(1)

    print(f"📖 Bestand inlezen: {file_path}...")
    valid_q = []
    errors = []

    if file_path.lower().endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            valid_q, errors = import_questions_from_json(f.read())
    elif file_path.lower().endswith(".csv"):
        with open(file_path, "r", encoding="utf-8") as f:
            valid_q, errors = import_questions_from_csv(f.read())
    else:
        print("❌ Niet-ondersteund bestandstype. Gebruik een .csv of .json bestand.")
        sys.exit(1)

    if errors:
        print(f"⚠️ Er zijn {len(errors)} waarschuwingen/fouten gevonden:")
        for err in errors:
            print(f"  - {err}")

    if not valid_q:
        print("❌ Geen geldige vragen kunnen inlezen.")
        sys.exit(1)

    total = save_imported_questions(valid_q, overwrite=overwrite)
    print(f"✅ Succesvol {len(valid_q)} vragen geïmporteerd!")
    print(f"📊 Totale vragendatabase bevat nu {total} vragen.")


if __name__ == "__main__":
    main()
