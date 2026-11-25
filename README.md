# CBS Data Quiz & Wrapped 📊

Een interactieve data-applicatie gebouwd met **Python & Streamlit** waarin gebruikers hun maatschappelijke intuïtie testen tegen de officiële cijfers van het **Centraal Bureau voor de Statistiek (CBS)**.

Ontworpen volgens het officiële **[CBS Design System](https://designsystem.cbs.nl/)** met authentieke huisstijlkleuren (`#271D6C` Corporate Blauw, `#00A1CD` CBS Cyaan), een professionele overheidstypografie, en een direct deelbaar **Spotify-Wrapped** eindscherm.

---

## ✨ Functionaliteiten

### 1. Doelgroepgerichte Vragenkaders
Vragen zijn specifiek afgestemd op de levensfase van de gebruiker:
- **15–24 jaar**: Focus op jeugdwerkloosheid, studieschuld, kamermarkt en thuiswonende jongvolwassenen.
- **25–39 jaar**: Focus op koopwoningprijzen, kinderopvangkosten, werk-privébalans en gezinsvorming.
- **40–64 jaar**: Focus op inflatie (CPI), vermogensontwikkeling, verduurzaming (zonnepanelen) en zorgkosten.
- **65+ jaar**: Focus op AOW-ontwikkeling, levensverwachting, pensioen en ouderenzorg.
- **Alle leeftijden**: Een gebalanceerde selectie van maatschappelijke kernindicatoren.

### 2. Interactieve Percentage-Slider & Live Indicatie
- Formaat: *"In 2025 bedroeg indicator X ... Met welk percentage veranderde dit in 2026?"*
- Dynamische mutatie-slider (`-30%` tot `+30%`) met automatische omrekening naar de verwachte absolute waarde.

### 3. Directe Feedback & StatLine Validatie
- Directe evaluatie met een eerlijke, progressieve nauwkeurigheidsscore.
- Journalistic toelichting over de maatschappelijke context en economische oorzaken.
- Directe link naar de officiële **CBS StatLine** tabel (o.a. `80590ned`, `85773NED`, `86141NED`, etc.).

### 4. Spotify-Wrapped Stijl Eindscherm & 9:16 Story Export
- **Statistisch Archetype** (bijv. *De CBS Connaisseur*, *De Scherpe Schatter*, *De Zorgelijke Pessimist*).
- **Denkpatroonanalyse**: Neiging tot overschatting vs. onderschatting van maatschappelijke trends.
- **Top Thema & Aandachtsgebied**: Inzicht in sterkste en zwakste beleidscategorieën.
- **Top 3 & Bottom 3**: Overzicht van de beste inschattingen en grootste blinde vlekken.
- **Instagram / WhatsApp Story Card**: Automatische generatie van een hoge resolutie (1080x1920) 9:16 story-afbeelding met één klik downloaden.

### 5. Vragen Import Module (CSV & JSON)
- Flexibele importfunctie via de web-UI of CLI (`python import_questions.py`).
- Inclusief validatie op verplichte velden, numerieke types en leeftijdscategorieën.
- Sjablonen beschikbaar in `data/templates/` (`questions_template.csv` en `questions_template.json`).

---

## 🚀 Lokale Installatie & Gebruik

### 1. Repository klonen
```bash
git clone https://github.com/Beneficentlynx/cbs-data-quiz.git
cd cbs-data-quiz
```

### 2. Virtuele omgeving aanmaken & activeren
```bash
python -m venv .venv
# Op Windows:
.venv\Scripts\activate
# Op macOS / Linux:
source .venv/bin/activate
```

### 3. Afhankelijkheden installeren
```bash
pip install -r requirements.txt
```

### 4. Applicatie starten
```bash
streamlit run app.py
```
De applicatie opent automatisch in je browser op **`http://localhost:8501`**.

---

## 🧪 Tests Uitvoeren

De codebase bevat geautomatiseerde tests voor de CBS API, rekenmodellen, scoring-algoritmes en Wrapped-generatie:

```bash
python test_app.py
```

---

## 📁 Projectstructuur

```text
CBS/
├── .streamlit/
│   └── config.toml             # CBS Huisstijl & Streamlit configuratie
├── data/
│   ├── cbs_logo.svg            # Officieel vector CBS logo
│   ├── questions_data.json     # 2025/2026 gekalibreerde vragenbank
│   └── templates/              # CSV & JSON importsjablonen
├── modules/
│   ├── cbs_api.py              # CBS StatLine Open Data API connector
│   ├── quiz_engine.py          # Rekenmachine, scoring & Wrapped logica
│   ├── question_importer.py    # CSV/JSON import & validatie
│   ├── story_card_generator.py # 1080x1920 9:16 PNG generator (Pillow)
│   └── ui_components.py        # CBS Design System componenten & CSS
├── app.py                      # Hoofdapplicatie (Streamlit controller)
├── import_questions.py         # CLI vragenimporteur
├── test_app.py                 # Testsuite
├── requirements.txt            # Python dependencies
└── README.md                   # Documentatie
```

---

## 📄 Licentie & Bronvermelding
Data is afkomstig van het **Centraal Bureau voor de Statistiek (CBS)** via [CBS Open Data StatLine](https://opendata.cbs.nl/).
