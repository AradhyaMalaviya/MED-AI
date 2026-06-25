# ============================================================================
# test_risk_level.py — Unit Tests for Risk Level Calculation
# ============================================================================
# Tests the extracted `calculate_risk_level()` function from app.py.
# Covers all business rule branches plus boundary / edge cases.
# ============================================================================

import sys
from pathlib import Path

import pytest

# Ensure app directory is importable
APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app import calculate_risk_level  # noqa: E402

# ============================================================================
# HIGH risk: symptom_count >= 3 AND (age > 60 OR blood_pressure == 2)
# ============================================================================

class TestHighRisk:
    """Tests for the HIGH risk level branch."""

    @pytest.mark.unit
    def test_high_risk_many_symptoms_elderly(self):
        """3+ symptoms AND age > 60 → HIGH."""
        assert calculate_risk_level(symptom_count=3, age=65, blood_pressure=1) == "High"

    @pytest.mark.unit
    def test_high_risk_many_symptoms_high_bp(self):
        """3+ symptoms AND high blood pressure (2) → HIGH."""
        assert calculate_risk_level(symptom_count=3, age=30, blood_pressure=2) == "High"

    @pytest.mark.unit
    def test_high_risk_all_symptoms_elderly_high_bp(self):
        """4 symptoms AND both elderly AND high BP → HIGH."""
        assert calculate_risk_level(symptom_count=4, age=70, blood_pressure=2) == "High"

    @pytest.mark.unit
    def test_high_risk_exact_threshold_symptoms_and_age(self):
        """Exactly 3 symptoms AND age=61 → HIGH (age > 60 is strict greater-than)."""
        assert calculate_risk_level(symptom_count=3, age=61, blood_pressure=0) == "High"

    @pytest.mark.unit
    def test_high_risk_max_symptoms_elderly(self):
        """Maximum symptom count (4) AND elderly → HIGH."""
        assert calculate_risk_level(symptom_count=4, age=90, blood_pressure=1) == "High"


# ============================================================================
# MEDIUM risk: symptom_count >= 2 (and not HIGH)
# ============================================================================

class TestMediumRisk:
    """Tests for the MEDIUM risk level branch."""

    @pytest.mark.unit
    def test_medium_risk_two_symptoms_young(self):
        """2 symptoms, young patient, normal BP → MEDIUM."""
        assert calculate_risk_level(symptom_count=2, age=25, blood_pressure=1) == "Medium"

    @pytest.mark.unit
    def test_medium_risk_three_symptoms_young_normal_bp(self):
        """3 symptoms BUT young AND normal BP → MEDIUM (not HIGH)."""
        assert calculate_risk_level(symptom_count=3, age=30, blood_pressure=1) == "Medium"

    @pytest.mark.unit
    def test_medium_risk_three_symptoms_age_exactly_60(self):
        """3 symptoms AND age exactly 60 → MEDIUM (age > 60 is strict, 60 is NOT > 60)."""
        assert calculate_risk_level(symptom_count=3, age=60, blood_pressure=0) == "Medium"

    @pytest.mark.unit
    def test_medium_risk_two_symptoms_exactly(self):
        """Exactly 2 symptoms, middle age, low BP → MEDIUM."""
        assert calculate_risk_level(symptom_count=2, age=45, blood_pressure=0) == "Medium"

    @pytest.mark.unit
    def test_medium_risk_four_symptoms_young_low_bp(self):
        """4 symptoms BUT young AND low BP → MEDIUM (fails both age > 60 and bp == 2)."""
        assert calculate_risk_level(symptom_count=4, age=25, blood_pressure=0) == "Medium"

    @pytest.mark.unit
    def test_medium_risk_two_symptoms_elderly(self):
        """2 symptoms AND elderly → MEDIUM (symptom_count < 3 so HIGH rule not triggered)."""
        assert calculate_risk_level(symptom_count=2, age=75, blood_pressure=2) == "Medium"


# ============================================================================
# LOW risk: symptom_count < 2
# ============================================================================

class TestLowRisk:
    """Tests for the LOW risk level branch."""

    @pytest.mark.unit
    def test_low_risk_zero_symptoms(self):
        """No symptoms → LOW."""
        assert calculate_risk_level(symptom_count=0, age=30, blood_pressure=1) == "Low"

    @pytest.mark.unit
    def test_low_risk_one_symptom(self):
        """1 symptom → LOW."""
        assert calculate_risk_level(symptom_count=1, age=50, blood_pressure=1) == "Low"

    @pytest.mark.unit
    def test_low_risk_one_symptom_elderly_high_bp(self):
        """1 symptom even with age > 60 and high BP → LOW (symptom_count < 2)."""
        assert calculate_risk_level(symptom_count=1, age=80, blood_pressure=2) == "Low"

    @pytest.mark.unit
    def test_low_risk_zero_symptoms_max_age(self):
        """No symptoms, maximum age → LOW."""
        assert calculate_risk_level(symptom_count=0, age=120, blood_pressure=2) == "Low"


# ============================================================================
# Boundary / Edge cases
# ============================================================================

class TestEdgeCases:
    """Edge case tests for risk level boundaries."""

    @pytest.mark.unit
    def test_boundary_symptom_count_1_to_2(self):
        """Crossing from 1 to 2 symptoms changes LOW → MEDIUM."""
        assert calculate_risk_level(symptom_count=1, age=45, blood_pressure=1) == "Low"
        assert calculate_risk_level(symptom_count=2, age=45, blood_pressure=1) == "Medium"

    @pytest.mark.unit
    def test_boundary_symptom_count_2_to_3_with_age_trigger(self):
        """Crossing from 2 to 3 symptoms with age > 60 changes MEDIUM → HIGH."""
        assert calculate_risk_level(symptom_count=2, age=65, blood_pressure=0) == "Medium"
        assert calculate_risk_level(symptom_count=3, age=65, blood_pressure=0) == "High"

    @pytest.mark.unit
    def test_boundary_age_60_vs_61(self):
        """Age 60 is NOT > 60 (strict greater-than), age 61 IS."""
        assert calculate_risk_level(symptom_count=3, age=60, blood_pressure=0) == "Medium"
        assert calculate_risk_level(symptom_count=3, age=61, blood_pressure=0) == "High"

    @pytest.mark.unit
    def test_boundary_bp_1_vs_2(self):
        """BP=1 does NOT trigger HIGH, BP=2 DOES (with enough symptoms)."""
        assert calculate_risk_level(symptom_count=3, age=30, blood_pressure=1) == "Medium"
        assert calculate_risk_level(symptom_count=3, age=30, blood_pressure=2) == "High"

    @pytest.mark.unit
    def test_return_type_is_string(self):
        """calculate_risk_level always returns a string."""
        result = calculate_risk_level(symptom_count=0, age=30, blood_pressure=0)
        assert isinstance(result, str)

    @pytest.mark.unit
    def test_return_values_are_capitalized(self):
        """Risk values use title case: 'High', 'Medium', 'Low'."""
        assert calculate_risk_level(4, 65, 2) == "High"
        assert calculate_risk_level(2, 30, 0) == "Medium"
        assert calculate_risk_level(0, 20, 0) == "Low"

    @pytest.mark.unit
    def test_zero_age_zero_bp_zero_symptoms(self):
        """All-zero edge case → LOW."""
        assert calculate_risk_level(symptom_count=0, age=0, blood_pressure=0) == "Low"
