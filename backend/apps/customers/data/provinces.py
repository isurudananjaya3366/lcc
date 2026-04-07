"""
Sri Lanka provinces reference data.

All 9 provinces with Sinhala and Tamil names.
"""

PROVINCES = [
    {
        "code": "WP",
        "name": "Western Province",
        "sinhala_name": "බස්නාහිර පළාත",
        "tamil_name": "மேல் மாகாணம்",
        "districts": ["Colombo", "Gampaha", "Kalutara"],
    },
    {
        "code": "CP",
        "name": "Central Province",
        "sinhala_name": "මධ්‍යම පළාත",
        "tamil_name": "மத்திய மாகாணம்",
        "districts": ["Kandy", "Matale", "Nuwara Eliya"],
    },
    {
        "code": "SP",
        "name": "Southern Province",
        "sinhala_name": "දකුණු පළාත",
        "tamil_name": "தென் மாகாணம்",
        "districts": ["Galle", "Matara", "Hambantota"],
    },
    {
        "code": "NP",
        "name": "Northern Province",
        "sinhala_name": "උතුරු පළාත",
        "tamil_name": "வடக்கு மாகாணம்",
        "districts": ["Jaffna", "Kilinochchi", "Mannar", "Mullaitivu", "Vavuniya"],
    },
    {
        "code": "EP",
        "name": "Eastern Province",
        "sinhala_name": "නැගෙනහිර පළාත",
        "tamil_name": "கிழக்கு மாகாணம்",
        "districts": ["Batticaloa", "Ampara", "Trincomalee"],
    },
    {
        "code": "NWP",
        "name": "North Western Province",
        "sinhala_name": "වයඹ පළාත",
        "tamil_name": "வடமேல் மாகாணம்",
        "districts": ["Kurunegala", "Puttalam"],
    },
    {
        "code": "NCP",
        "name": "North Central Province",
        "sinhala_name": "උතුරු මැද පළාත",
        "tamil_name": "வட மத்திய மாகாணம்",
        "districts": ["Anuradhapura", "Polonnaruwa"],
    },
    {
        "code": "UP",
        "name": "Uva Province",
        "sinhala_name": "ඌව පළාත",
        "tamil_name": "ஊவா மாகாணம்",
        "districts": ["Badulla", "Monaragala"],
    },
    {
        "code": "SGP",
        "name": "Sabaragamuwa Province",
        "sinhala_name": "සබරගමුව පළාත",
        "tamil_name": "சபரகமுவ மாகாணம்",
        "districts": ["Ratnapura", "Kegalle"],
    },
]


def get_province_names():
    """Return list of province names."""
    return [p["name"] for p in PROVINCES]


def get_province_choices():
    """Return Django choices tuple for provinces."""
    return [(p["name"], p["name"]) for p in PROVINCES]
