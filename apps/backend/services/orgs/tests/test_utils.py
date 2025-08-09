import pytest
from apps.backend.services.orgs.utils import format_org_name, is_valid_invitation_role

@pytest.mark.parametrize("input_name, expected_output", [
    ("my awesome company", "My Awesome Company"),
    ("singleword", "Singleword"),
    ("ALREADY CAPITALIZED", "Already Capitalized"),
    ("", ""),
])
def test_format_org_name(input_name, expected_output):
    """
    Tests the format_org_name utility function with various inputs.
    """
    assert format_org_name(input_name) == expected_output

@pytest.mark.parametrize("role, is_valid", [
    ("member", True),
    ("admin", True),
    ("billing", True),
    ("owner", False), # Owner role should be assigned on creation, not via invite
    ("superadmin", False),
    ("", False),
])
def test_is_valid_invitation_role(role, is_valid):
    """
    Tests the role validation logic for invitations.
    """
    assert is_valid_invitation_role(role) == is_valid
