
from mastermind import validate_code, evaluate_guess


# Test 1: One exact and three misplaced.
result = evaluate_guess("RGBY", "RYGB")
print("Test 1:", result)


# Test 2: All four symbols in the correct positions.
result = evaluate_guess("RGBY", "RGBY")
print("Test 2:", result)


# Test 3: No matching symbols.
result = evaluate_guess("RGBY", "UUUU")
print("Test 3:", result)


# Test 4: Repeated symbols.
result = evaluate_guess("RRGY", "GRRR")
print("Test 4:", result)


# Test 5: Lowercase normalization.
result = evaluate_guess("rgby", "RGBY")
print("Test 5:", result)


# Test 6: Invalid code.
try:
    validate_code("ABCD")
except ValueError as error:
    print("Test 6: Correctly rejected:", error)
