# evaluation/dataset.py
EVAL_QUESTIONS = [
    {
        "question": "What is the horsepower of the Porsche 911 Turbo S?",
        "expected_keywords": ["turbo s", "horsepower", "hp", "653", "640"],  # adjust based on your docs
    },
    {
        "question": "What is the top speed of the Porsche 911 GT3 RS?",
        "expected_keywords": ["gt3 rs", "top speed", "mph", "km/h", "205"],
    },
    {
        "question": "How much downforce does the GT3 RS wing generate?",
        "expected_keywords": ["downforce", "wing", "kg", "lb", "gt3 rs"],
    },
    {
        "question": "What engine is used in the Porsche 911 Carrera?",
        "expected_keywords": ["carrera", "engine", "twin-turbo", "flat-six", "3.0"],
    },
    {
        "question": "What is the 0-60 mph time for the 911 Turbo S?",
        "expected_keywords": ["0-60", "turbo s", "seconds", "2.6", "2.7"],
    },
    {
        "question": "When was the 992 generation introduced?",
        "expected_keywords": ["992", "introduced", "2019", "generation"],
    },
    # Add 10–20 more questions covering your documents
]