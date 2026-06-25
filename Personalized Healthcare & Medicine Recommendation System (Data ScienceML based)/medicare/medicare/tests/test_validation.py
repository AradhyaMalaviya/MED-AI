# ============================================================================
# test_validation.py — Unit Tests for Input Validation
# ============================================================================
# Tests the `validate_input()` function from app.py.
# Covers valid inputs, missing fields, out-of-range values, and type errors.
# ============================================================================

import sys
from pathlib import Path

import pytest

# Ensure app directory is importable
APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app import validate_input


# ---------- Helper: build a valid payload (all fields present & in range) ----

def _valid_data():
    """Return a complete, valid input dictionary."""
    return {
        'age': 45,
        'gender': 1,
        'fever': 1,
        'cough': 0,
        'fatigue': 1,
        'breathing': 0,
        'bloodPressure': 1,
        'cholesterol': 1,
    }


# ============================================================================
# Valid input tests
# ============================================================================

class TestValidInput:
    """Tests that correct data passes validation cleanly."""

    @pytest.mark.unit
    def test_valid_input_returns_true(self):
        """Complete valid data → (True, [])."""
        is_valid, errors = validate_input(_valid_data())
        assert is_valid is True
        assert errors == []

    @pytest.mark.unit
    def test_valid_input_minimum_values(self):
        """All fields at their minimum allowed value → valid."""
        data = {
            'age': 0,
            'gender': 0,
            'fever': 0,
            'cough': 0,
            'fatigue': 0,
            'breathing': 0,
            'bloodPressure': 0,
            'cholesterol': 0,
        }
        is_valid, errors = validate_input(data)
        assert is_valid is True
        assert errors == []

    @pytest.mark.unit
    def test_valid_input_maximum_values(self):
        """All fields at their maximum allowed value → valid."""
        data = {
            'age': 120,
            'gender': 1,
            'fever': 1,
            'cough': 1,
            'fatigue': 1,
            'breathing': 1,
            'bloodPressure': 2,
            'cholesterol': 2,
        }
        is_valid, errors = validate_input(data)
        assert is_valid is True
        assert errors == []

    @pytest.mark.unit
    def test_valid_input_string_numbers(self):
        """Numeric string values (e.g., '45') should still validate (int() converts them)."""
        data = {
            'age': '45',
            'gender': '1',
            'fever': '0',
            'cough': '1',
            'fatigue': '0',
            'breathing': '1',
            'bloodPressure': '2',
            'cholesterol': '0',
        }
        is_valid, errors = validate_input(data)
        assert is_valid is True
        assert errors == []


# ============================================================================
# Missing field tests
# ============================================================================

class TestMissingFields:
    """Tests that missing required fields are caught."""

    @pytest.mark.unit
    def test_missing_age(self):
        """Omitting 'age' → error mentioning 'age'."""
        data = _valid_data()
        del data['age']
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("age" in e for e in errors)

    @pytest.mark.unit
    def test_missing_gender(self):
        """Omitting 'gender' → error."""
        data = _valid_data()
        del data['gender']
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("gender" in e for e in errors)

    @pytest.mark.unit
    def test_missing_all_symptom_fields(self):
        """Omitting all symptom fields → 4 errors."""
        data = _valid_data()
        for field in ['fever', 'cough', 'fatigue', 'breathing']:
            del data[field]
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert len(errors) == 4

    @pytest.mark.unit
    def test_empty_dict(self):
        """Empty dictionary → errors for all 8 required fields."""
        is_valid, errors = validate_input({})
        assert is_valid is False
        assert len(errors) == 8

    @pytest.mark.unit
    def test_missing_bloodpressure_and_cholesterol(self):
        """Omitting 'bloodPressure' and 'cholesterol' → 2 errors."""
        data = _valid_data()
        del data['bloodPressure']
        del data['cholesterol']
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert len(errors) == 2


# ============================================================================
# Out-of-range value tests
# ============================================================================

class TestOutOfRange:
    """Tests that values outside allowed ranges are rejected."""

    @pytest.mark.unit
    def test_age_negative(self):
        """age = -5 → rejected."""
        data = _valid_data()
        data['age'] = -5
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("age" in e for e in errors)

    @pytest.mark.unit
    def test_age_too_high(self):
        """age = 121 → rejected (max 120)."""
        data = _valid_data()
        data['age'] = 121
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("age" in e for e in errors)

    @pytest.mark.unit
    def test_gender_out_of_range(self):
        """gender = 3 → rejected (only 0 or 1)."""
        data = _valid_data()
        data['gender'] = 3
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("gender" in e for e in errors)

    @pytest.mark.unit
    def test_fever_out_of_range(self):
        """fever = 2 → rejected (only 0 or 1)."""
        data = _valid_data()
        data['fever'] = 2
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("fever" in e for e in errors)

    @pytest.mark.unit
    def test_bloodpressure_out_of_range(self):
        """bloodPressure = 5 → rejected (max 2)."""
        data = _valid_data()
        data['bloodPressure'] = 5
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("bloodPressure" in e for e in errors)

    @pytest.mark.unit
    def test_cholesterol_negative(self):
        """cholesterol = -1 → rejected."""
        data = _valid_data()
        data['cholesterol'] = -1
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("cholesterol" in e for e in errors)

    @pytest.mark.unit
    def test_multiple_out_of_range(self):
        """Multiple fields out of range → multiple errors."""
        data = _valid_data()
        data['age'] = -1
        data['gender'] = 5
        data['cholesterol'] = 10
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert len(errors) >= 3


# ============================================================================
# Type error tests
# ============================================================================

class TestTypeErrors:
    """Tests that non-numeric values are rejected."""

    @pytest.mark.unit
    def test_age_string_non_numeric(self):
        """age = 'abc' → rejected."""
        data = _valid_data()
        data['age'] = 'abc'
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("age" in e and "integer" in e for e in errors)

    @pytest.mark.unit
    def test_gender_none(self):
        """gender = None → rejected."""
        data = _valid_data()
        data['gender'] = None
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("gender" in e for e in errors)

    @pytest.mark.unit
    def test_fever_float_string(self):
        """fever = '1.5' → rejected (int() can't parse '1.5')."""
        data = _valid_data()
        data['fever'] = '1.5'
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("fever" in e for e in errors)

    @pytest.mark.unit
    def test_bloodpressure_list(self):
        """bloodPressure = [1] → rejected (not an int-castable value)."""
        data = _valid_data()
        data['bloodPressure'] = [1]
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert any("bloodPressure" in e for e in errors)


# ============================================================================
# Combination / mixed tests
# ============================================================================

class TestMixedErrors:
    """Tests combining multiple error types."""

    @pytest.mark.unit
    def test_missing_and_out_of_range_combined(self):
        """Missing 'age' AND 'gender' = 5 → 2 separate errors."""
        data = _valid_data()
        del data['age']
        data['gender'] = 5
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert len(errors) == 2

    @pytest.mark.unit
    def test_all_fields_invalid(self):
        """Every field is non-numeric → 8 errors."""
        data = {
            'age': 'old',
            'gender': 'male',
            'fever': 'yes',
            'cough': 'yes',
            'fatigue': 'yes',
            'breathing': 'yes',
            'bloodPressure': 'high',
            'cholesterol': 'high',
        }
        is_valid, errors = validate_input(data)
        assert is_valid is False
        assert len(errors) == 8

    @pytest.mark.unit
    def test_error_messages_are_descriptive(self):
        """Error messages should mention the offending field name."""
        data = _valid_data()
        data['age'] = -100
        _, errors = validate_input(data)
        assert len(errors) == 1
        assert "age" in errors[0]
        assert "0" in errors[0] and "120" in errors[0]
