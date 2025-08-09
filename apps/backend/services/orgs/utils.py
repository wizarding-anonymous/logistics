def format_org_name(name: str) -> str:
    """
    A simple utility function to demonstrate testing.
    It capitalizes the first letter of each word in the organization name.
    """
    if not name:
        return ""
    return name.title()

def is_valid_invitation_role(role: str) -> bool:
    """
    Checks if a role is a valid, assignable role for an invitation.
    Prevents arbitrary roles from being assigned.
    """
    VALID_ROLES = {'member', 'admin', 'billing'}
    return role in VALID_ROLES
