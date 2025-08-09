from apps.backend.services.auth.security import verify_password, get_password_hash

def test_password_hashing_and_verification():
    """
    Tests that a password can be hashed and then successfully verified.
    """
    password = "a_strong_password"

    # Hash the password
    hashed_password = get_password_hash(password)

    # Assert that the hash is not the same as the original password
    assert password != hashed_password

    # Assert that the verification works for the correct password
    assert verify_password(password, hashed_password) == True

    # Assert that the verification fails for an incorrect password
    assert verify_password("not_the_right_password", hashed_password) == False
