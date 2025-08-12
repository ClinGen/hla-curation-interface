"""Houses constants used in the views module of the firebase app."""

VERIFICATION_SUCCESS = {
    "valid": True,
    "message": "Verified ID the token from the OAuth provider.",
}
VERIFICATION_FAILURE = {
    "valid": False,
    "message": "Unable to verify the ID token from the OAuth provider.",
}
INVALID_JSON = {
    "valid": False,
    "message": "The JSON sent to the backend to verify the ID token was not valid.",
}
