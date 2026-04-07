"""
Sri Lankan administrative divisions.

9 Provinces, 25 Districts
Each includes English name, Sinhala name, and code.
"""

PROVINCES = [
    {"code": "WP", "name": "Western Province", "sinhala": "බස්නාහිර පළාත"},
    {"code": "CP", "name": "Central Province", "sinhala": "මධ්‍යම පළාත"},
    {"code": "SP", "name": "Southern Province", "sinhala": "දකුණු පළාත"},
    {"code": "NP", "name": "Northern Province", "sinhala": "උතුරු පළාත"},
    {"code": "EP", "name": "Eastern Province", "sinhala": "නැගෙනහිර පළාත"},
    {"code": "NWP", "name": "North Western Province", "sinhala": "වයඹ පළාත"},
    {"code": "NCP", "name": "North Central Province", "sinhala": "උතුරු මැද පළාත"},
    {"code": "UP", "name": "Uva Province", "sinhala": "ඌව පළාත"},
    {"code": "SG", "name": "Sabaragamuwa Province", "sinhala": "සබරගමුව පළාත"},
]

DISTRICTS = [
    # Western Province
    {"code": "CO", "name": "Colombo", "sinhala": "කොළඹ", "province": "WP"},
    {"code": "GM", "name": "Gampaha", "sinhala": "ගම්පහ", "province": "WP"},
    {"code": "KT", "name": "Kalutara", "sinhala": "කළුතර", "province": "WP"},
    # Central Province
    {"code": "KY", "name": "Kandy", "sinhala": "මහනුවර", "province": "CP"},
    {"code": "MT", "name": "Matale", "sinhala": "මාතලේ", "province": "CP"},
    {"code": "NE", "name": "Nuwara Eliya", "sinhala": "නුවරඑළිය", "province": "CP"},
    # Southern Province
    {"code": "GL", "name": "Galle", "sinhala": "ගාල්ල", "province": "SP"},
    {"code": "MH", "name": "Matara", "sinhala": "මාතර", "province": "SP"},
    {"code": "HB", "name": "Hambantota", "sinhala": "හම්බන්තොට", "province": "SP"},
    # Northern Province
    {"code": "JA", "name": "Jaffna", "sinhala": "යාපනය", "province": "NP"},
    {"code": "KL", "name": "Kilinochchi", "sinhala": "කිලිනොච්චිය", "province": "NP"},
    {"code": "MN", "name": "Mannar", "sinhala": "මන්නාරම", "province": "NP"},
    {"code": "MU", "name": "Mullaitivu", "sinhala": "මුලතිව්", "province": "NP"},
    {"code": "VA", "name": "Vavuniya", "sinhala": "වව්නියාව", "province": "NP"},
    # Eastern Province
    {"code": "AP", "name": "Ampara", "sinhala": "අම්පාර", "province": "EP"},
    {"code": "BD", "name": "Batticaloa", "sinhala": "මඩකලපුව", "province": "EP"},
    {"code": "TC", "name": "Trincomalee", "sinhala": "ත්‍රිකුණාමලය", "province": "EP"},
    # North Western Province
    {"code": "KR", "name": "Kurunegala", "sinhala": "කුරුණෑගල", "province": "NWP"},
    {"code": "PT", "name": "Puttalam", "sinhala": "පුත්තලම", "province": "NWP"},
    # North Central Province
    {"code": "AD", "name": "Anuradhapura", "sinhala": "අනුරාධපුරය", "province": "NCP"},
    {"code": "PO", "name": "Polonnaruwa", "sinhala": "පොළොන්නරුව", "province": "NCP"},
    # Uva Province
    {"code": "BA", "name": "Badulla", "sinhala": "බදුල්ල", "province": "UP"},
    {"code": "MO", "name": "Monaragala", "sinhala": "මොණරාගල", "province": "UP"},
    # Sabaragamuwa Province
    {"code": "KG", "name": "Kegalle", "sinhala": "කෑගල්ල", "province": "SG"},
    {"code": "RP", "name": "Ratnapura", "sinhala": "රත්නපුර", "province": "SG"},
]


def get_province_by_code(code):
    """
    Get province by code.

    Args:
        code: Province code (e.g., 'WP')

    Returns:
        dict or None: Province dict if found
    """
    code = code.upper() if isinstance(code, str) else code
    return next((p for p in PROVINCES if p['code'] == code), None)


def get_province_choices():
    """
    Get province choices for Django forms/models.

    Returns:
        list: List of (code, name) tuples

    Example:
        >>> get_province_choices()
        [('WP', 'Western Province'), ('CP', 'Central Province'), ...]
    """
    return [(p['code'], p['name']) for p in PROVINCES]


def get_districts_by_province(province_code):
    """
    Get all districts for a province.

    Args:
        province_code: Province code (e.g., 'WP')

    Returns:
        list: List of district dicts
    """
    code = province_code.upper() if isinstance(province_code, str) else province_code
    return [d for d in DISTRICTS if d['province'] == code]


def get_district_by_code(code):
    """
    Get district by code.

    Args:
        code: District code (e.g., 'CO')

    Returns:
        dict or None: District dict if found
    """
    code = code.upper() if isinstance(code, str) else code
    return next((d for d in DISTRICTS if d['code'] == code), None)


def get_district_choices(province_code=None):
    """
    Get district choices for Django forms/models.

    Args:
        province_code: Optional province code to filter by

    Returns:
        list: List of (code, name) tuples
    """
    if province_code:
        districts = get_districts_by_province(province_code)
    else:
        districts = DISTRICTS
    return [(d['code'], d['name']) for d in districts]
