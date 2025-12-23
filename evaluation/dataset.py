# evaluation/dataset.py

EVAL_QUESTIONS = [
    {
        "id": "Q1",
        "question": "What is the horsepower of the Porsche 911 Turbo S?",
        "answer_type": "numeric",
        "expected_facts": {
            "horsepower": [701]  # Updated to 2025 Turbo S spec from official sources
        },
        "numeric_tolerance": 5,
        "must_mention": ["turbo s"],
        "optional_mentions": ["hp", "ps", "kw"],
        "source_hint": "technical specifications"
    },
    {
        "id": "Q2",
        "question": "When was the Porsche 911 (992 generation) introduced?",
        "answer_type": "date",
        "expected_facts": {
            "year": [2018]  # Confirmed November 2018 introduction
        },
        "must_mention": ["992"],
        "source_hint": "press kit"
    },
    {
        "id": "Q3",
        "question": "What engine is used in the Porsche 911 Carrera?",
        "answer_type": "descriptive",
        "expected_facts": {
            "engine": ["twin-turbo flat-six", "boxer", "3.0-liter", "6-cylinder"]
        },
        "must_mention": ["carrera"],
        "optional_mentions": ["3.0", "flat-6", "twin-turbo"],
        "source_hint": "technical specifications"
    },
    {
        "id": "Q4",
        "question": "What is the top speed of the Porsche 911 GT3?",
        "answer_type": "numeric",
        "expected_facts": {
            "top_speed_mph": [193],
            "top_speed_kmh": [311]
        },
        "numeric_tolerance": 3,
        "must_mention": ["gt3"],
        "source_hint": "technical specifications"
    },
    # New questions for better coverage
    {
        "id": "Q5",
        "question": "What is the 0-60 mph time for the Porsche 911 Carrera GTS?",
        "answer_type": "numeric",
        "expected_facts": {
            "zero_to_sixty": [2.9]  # From 2025 GTS specs
        },
        "numeric_tolerance": 0.2,
        "must_mention": ["gts"],
        "optional_mentions": ["seconds", "sport chrono"],
        "source_hint": "technical specifications"
    },
    {
        "id": "Q6",
        "question": "What is the maximum power combined for the Porsche 911 Turbo S?",
        "answer_type": "numeric",
        "expected_facts": {
            "power": [701]  # hp
        },
        "numeric_tolerance": 5,
        "must_mention": ["turbo s"],
        "optional_mentions": ["hp", "combined"],
        "source_hint": "technical specifications"
    },
    {
        "id": "Q7",
        "question": "What is the engine displacement of the Porsche 911 Carrera S?",
        "answer_type": "numeric",
        "expected_facts": {
            "displacement": [2981]  # cc
        },
        "numeric_tolerance": 10,
        "must_mention": ["carrera s"],
        "optional_mentions": ["cc", "liter"],
        "source_hint": "technical specifications"
    },
    {
        "id": "Q8",
        "question": "What drivetrain options are available for the Porsche 911 GT3?",
        "answer_type": "descriptive",
        "expected_facts": {
            "drivetrain": ["rear-wheel drive", "RWD"]
        },
        "must_mention": ["gt3"],
        "optional_mentions": ["PDK", "manual"],
        "source_hint": "technical specifications"
    }
]