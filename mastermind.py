
from collections import Counter


VALID_SYMBOLS = {"R", "G", "U", "Y", "B", "W"}


def validate_code(code):
    """Validate and normalize a four-character Mastermind code."""

    if not isinstance(code, str):
        raise ValueError("Code must be a string.")

    code = code.upper()

    if len(code) != 4:
        raise ValueError("Code must contain exactly four characters.")

    if any(symbol not in VALID_SYMBOLS for symbol in code):
        raise ValueError("Code contains an invalid symbol.")

    return code


def evaluate_guess(secret_code, guess_code):
    """Calculate exact and misplaced matches for a guess."""

    secret_code = validate_code(secret_code)
    guess_code = validate_code(guess_code)

    exact_matches = 0

    remaining_secret = []
    remaining_guess = []

    # First, identify exact matches.
    for secret_symbol, guess_symbol in zip(
        secret_code, guess_code
    ):
        if secret_symbol == guess_symbol:
            exact_matches += 1
        else:
            remaining_secret.append(secret_symbol)
            remaining_guess.append(guess_symbol)

    # Count the remaining symbols to identify misplaced matches.
    secret_counts = Counter(remaining_secret)
    guess_counts = Counter(remaining_guess)

    misplaced_matches = sum(
        min(secret_counts[symbol], guess_counts[symbol])
        for symbol in secret_counts
    )

    return exact_matches, misplaced_matches
