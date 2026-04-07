"""
Sri Lanka districts reference data.

All 25 districts with province mappings and major cities.
"""

DISTRICTS = [
    # Western Province
    {
        "code": "CMB",
        "name": "Colombo",
        "province": "Western Province",
        "major_cities": [
            "Colombo", "Dehiwala-Mount Lavinia", "Moratuwa",
            "Sri Jayawardenepura Kotte", "Kolonnawa",
        ],
    },
    {
        "code": "GMP",
        "name": "Gampaha",
        "province": "Western Province",
        "major_cities": [
            "Gampaha", "Negombo", "Wattala", "Ja-Ela", "Kadawatha",
        ],
    },
    {
        "code": "KLT",
        "name": "Kalutara",
        "province": "Western Province",
        "major_cities": [
            "Kalutara", "Panadura", "Horana", "Bandaragama", "Beruwala",
        ],
    },
    # Central Province
    {
        "code": "KDY",
        "name": "Kandy",
        "province": "Central Province",
        "major_cities": [
            "Kandy", "Peradeniya", "Gampola", "Nawalapitiya", "Katugastota",
        ],
    },
    {
        "code": "MTL",
        "name": "Matale",
        "province": "Central Province",
        "major_cities": ["Matale", "Dambulla", "Sigiriya", "Galewela"],
    },
    {
        "code": "NUE",
        "name": "Nuwara Eliya",
        "province": "Central Province",
        "major_cities": [
            "Nuwara Eliya", "Hatton", "Talawakelle", "Bandarawela",
        ],
    },
    # Southern Province
    {
        "code": "GLL",
        "name": "Galle",
        "province": "Southern Province",
        "major_cities": ["Galle", "Ambalangoda", "Hikkaduwa", "Elpitiya"],
    },
    {
        "code": "MTR",
        "name": "Matara",
        "province": "Southern Province",
        "major_cities": ["Matara", "Weligama", "Akuressa", "Deniyaya"],
    },
    {
        "code": "HMB",
        "name": "Hambantota",
        "province": "Southern Province",
        "major_cities": ["Hambantota", "Tangalle", "Tissamaharama", "Beliatta"],
    },
    # Northern Province
    {
        "code": "JFN",
        "name": "Jaffna",
        "province": "Northern Province",
        "major_cities": ["Jaffna", "Chavakachcheri", "Point Pedro", "Nallur"],
    },
    {
        "code": "KLN",
        "name": "Kilinochchi",
        "province": "Northern Province",
        "major_cities": ["Kilinochchi", "Pallai"],
    },
    {
        "code": "MNR",
        "name": "Mannar",
        "province": "Northern Province",
        "major_cities": ["Mannar", "Talaimannar"],
    },
    {
        "code": "MLT",
        "name": "Mullaitivu",
        "province": "Northern Province",
        "major_cities": ["Mullaitivu", "Puthukkudiyiruppu"],
    },
    {
        "code": "VVN",
        "name": "Vavuniya",
        "province": "Northern Province",
        "major_cities": ["Vavuniya", "Cheddikulam"],
    },
    # Eastern Province
    {
        "code": "BTL",
        "name": "Batticaloa",
        "province": "Eastern Province",
        "major_cities": ["Batticaloa", "Kattankudy", "Eravur"],
    },
    {
        "code": "AMP",
        "name": "Ampara",
        "province": "Eastern Province",
        "major_cities": ["Ampara", "Kalmunai", "Akkaraipattu", "Sammanthurai"],
    },
    {
        "code": "TRC",
        "name": "Trincomalee",
        "province": "Eastern Province",
        "major_cities": ["Trincomalee", "Kinniya", "Mutur"],
    },
    # North Western Province
    {
        "code": "KUR",
        "name": "Kurunegala",
        "province": "North Western Province",
        "major_cities": ["Kurunegala", "Kuliyapitiya", "Narammala", "Wariyapola"],
    },
    {
        "code": "PUT",
        "name": "Puttalam",
        "province": "North Western Province",
        "major_cities": ["Puttalam", "Chilaw", "Wennappuwa", "Marawila"],
    },
    # North Central Province
    {
        "code": "ANP",
        "name": "Anuradhapura",
        "province": "North Central Province",
        "major_cities": ["Anuradhapura", "Kekirawa", "Medawachchiya", "Mihintale"],
    },
    {
        "code": "POL",
        "name": "Polonnaruwa",
        "province": "North Central Province",
        "major_cities": ["Polonnaruwa", "Kaduruwela", "Hingurakgoda"],
    },
    # Uva Province
    {
        "code": "BDL",
        "name": "Badulla",
        "province": "Uva Province",
        "major_cities": ["Badulla", "Bandarawela", "Haputale", "Ella"],
    },
    {
        "code": "MNR",
        "name": "Monaragala",
        "province": "Uva Province",
        "major_cities": ["Monaragala", "Wellawaya", "Bibile"],
    },
    # Sabaragamuwa Province
    {
        "code": "RTP",
        "name": "Ratnapura",
        "province": "Sabaragamuwa Province",
        "major_cities": ["Ratnapura", "Balangoda", "Embilipitiya", "Kuruwita"],
    },
    {
        "code": "KGL",
        "name": "Kegalle",
        "province": "Sabaragamuwa Province",
        "major_cities": ["Kegalle", "Mawanella", "Rambukkana", "Warakapola"],
    },
]


def get_districts_by_province(province):
    """Return list of district names for a given province."""
    return [d["name"] for d in DISTRICTS if d["province"] == province]


def get_district_choices():
    """Return Django choices tuple for districts."""
    return [(d["name"], d["name"]) for d in DISTRICTS]


def get_district_province_map():
    """Return dict mapping district names to province names."""
    return {d["name"]: d["province"] for d in DISTRICTS}


def validate_district_province(district, province):
    """
    Validate that a district belongs to the given province.

    Args:
        district: District name.
        province: Province name.

    Returns:
        bool: True if valid, False if mismatch.
    """
    mapping = get_district_province_map()
    if district in mapping:
        return mapping[district] == province
    return True  # Unknown district, allow
