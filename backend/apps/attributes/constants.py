"""
Constants for attribute types and configurations.

These constants are used across models, serializers, and validators
in the attributes app.
"""

# Individual attribute type constants
TEXT = "text"
NUMBER = "number"
SELECT = "select"
MULTISELECT = "multiselect"
BOOLEAN = "boolean"
DATE = "date"

# Attribute types choices tuple for Django model field choices
ATTRIBUTE_TYPES = (
    (TEXT, "Text"),
    (NUMBER, "Number"),
    (SELECT, "Select"),
    (MULTISELECT, "Multi-Select"),
    (BOOLEAN, "Boolean"),
    (DATE, "Date"),
)
