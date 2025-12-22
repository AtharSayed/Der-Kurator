# evaluation/dataset.py

EVAL_QUESTIONS = [
    {
        "id": "Q1",
        "question": "What is the horsepower of the Porsche 911 Turbo S?",
        "answer_type": "numeric",
        "expected_facts": {
            "horsepower": [640, 653, 701]  # market & generation dependent
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
            "year": [2018, 2019]
        },
        "must_mention": ["992"],
        "source_hint": "press kit"
    },
    {
        "id": "Q3",
        "question": "What engine is used in the Porsche 911 Carrera?",
        "answer_type": "descriptive",
        "expected_facts": {
            "engine": ["twin-turbo flat-six", "boxer"]
        },
        "must_mention": ["carrera"],
        "optional_mentions": ["3.0", "flat-6"],
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
    }
]
