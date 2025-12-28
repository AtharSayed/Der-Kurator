# evaluation/golden_dataset.py (expanded from dataset.py)
EVAL_QUESTIONS = [
    # Existing (slightly refined)
    {
        "id": "Q1",
        "question": "What is the horsepower of the Porsche 911 Turbo S?",
        "expected_answer": "The 2025 Porsche 911 Turbo S has 701 hp.",
        "answer_type": "numeric",
        "expected_facts": {"horsepower": [701]},
        "numeric_tolerance": 5,
        "must_mention": ["turbo s", "701", "hp"],
        "source_hint": "technical specifications (992.2 T-Hybrid)"
    },
    {
        "id": "Q2",
        "question": "When was the Porsche 911 (992 generation) introduced?",
        "expected_answer": "The 992 generation was introduced in November 2018.",
        "answer_type": "date",
        "expected_facts": {"year": [2018]},
        "must_mention": ["992", "2018"],
        "source_hint": "press kit"
    },
    # ... (include all your original 8 here, refined similarly)

    # New: History & Generations
    {
        "id": "Q9",
        "question": "What was the first air-cooled Porsche 911 model?",
        "expected_answer": "The original 911 (1963-1998) used air-cooled engines.",
        "answer_type": "descriptive",
        "expected_facts": {"engine_type": ["air-cooled"], "years": [1963, 1998]},
        "must_mention": ["air-cooled", "1963"],
        "source_hint": "historical overview"
    },
    {
        "id": "Q10",
        "question": "How did the 991 generation differ from the 997?",
        "expected_answer": "The 991 (2011-2019) introduced a longer wheelbase, wider track, and turbocharging across more models compared to the 997 (2004-2012).",
        "answer_type": "descriptive",
        "expected_facts": {"changes": ["longer wheelbase", "wider track", "turbocharging"]},
        "must_mention": ["991", "997"],
        "source_hint": "generation comparison"
    },

    # New: Comparisons & Edge Cases
    {
        "id": "Q11",
        "question": "Compare the torque of the 911 GT3 vs GT3 RS.",
        "expected_answer": "GT3: 346 lb-ft; GT3 RS: 342 lb-ft (both 992 generation).",
        "answer_type": "numeric",
        "expected_facts": {"gt3_torque": [346], "gt3_rs_torque": [342]},
        "numeric_tolerance": 5,
        "must_mention": ["gt3", "gt3 rs", "lb-ft"],
        "source_hint": "technical specifications"
    },
    {
        "id": "Q12",
        "question": "What is the fuel economy of the 911 Carrera?",
        "expected_answer": "I don't know — insufficient data in documents.",
        "answer_type": "abstention",  # Test refusal
        "expected_facts": {},
        "must_mention": [],
        "source_hint": "none (unanswerable)"
    },

    # New: Variants & Performance
    {
        "id": "Q13",
        "question": "What transmission options are available for the 911 GTS?",
        "expected_answer": "8-speed PDK automatic or 7-speed manual.",
        "answer_type": "descriptive",
        "expected_facts": {"transmissions": ["PDK", "manual"]},
        "must_mention": ["gts", "pdk"],
        "source_hint": "technical specifications"
    },
    {
        "id": "Q14",
        "question": "What is the Nürburgring lap time for the 911 GT2 RS?",
        "expected_answer": "6:43.30 minutes (2018 model).",
        "answer_type": "numeric",
        "expected_facts": {"lap_time": [6.43]},
        "numeric_tolerance": 0.1,
        "must_mention": ["gt2 rs", "nürburgring"],
        "source_hint": "performance records"
    },

    # New: Design & Features
    {
        "id": "Q15",
        "question": "What are the key design features of the Porsche 911?",
        "expected_answer": "Iconic sloping roofline, round headlights, rear-engine layout.",
        "answer_type": "descriptive",
        "expected_facts": {"design_features": ["sloping roofline", "round headlights", "rear-engine"]},
        "must_mention": ["design", "roofline", "headlights"],
        "source_hint": "design overview"
    },
    {
        "id": "Q16",
        "question": "Does the Porsche 911 come with adaptive cruise control?",
        "expected_answer": "Yes, adaptive cruise control is available as an option.",
        "answer_type": "yes/no",
        "expected_facts": {"adaptive_cruise_control": ["yes"]},
        "must_mention": ["adaptive cruise control"],
        "source_hint": "features list"
    },

    {"id": "Q17",
        "question": "What is the top speed of the Porsche 911 Carrera S?",
        "expected_answer": "The top speed of the Porsche 911 Carrera S is approximately 191 mph.",
        "answer_type": "numeric",
        "expected_facts": {"top_speed": [191]},
        "numeric_tolerance": 5,
        "must_mention": ["carrera s", "191", "mph"],
        "source_hint": "technical specifications"
    }
]