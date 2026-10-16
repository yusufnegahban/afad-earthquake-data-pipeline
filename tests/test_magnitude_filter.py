"""
Test: Earthquake magnitude validation

Acceptance criteria:
- Reject zero, negative, and missing magnitudes.
- Accept positive magnitudes.
- Actual output must match expected output.
"""

def is_valid_magnitude(magnitude):
    return magnitude is not None and magnitude > 0


def test_magnitude_filter():
    input_data = [0, 2.5, None, 5.1, -1]
    expected_output = [2.5, 5.1]

    actual_output = [
        value for value in input_data
        if is_valid_magnitude(value)
    ]

    print("\n--- Magnitude Filter Test ---")
    print(f"Input data:      {input_data}")
    print(f"Expected output: {expected_output}")
    print(f"Actual output:   {actual_output}")
    print(f"Accepted:        {len(actual_output)}")
    print(f"Rejected:        {len(input_data) - len(actual_output)}")

    assert actual_output == expected_output, (
        f"Expected {expected_output}, got {actual_output}"
    )

    print("Result: PASS")


if __name__ == "__main__":
    test_magnitude_filter()