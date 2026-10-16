
# Testing Basics — Earthquake Data Pipeline

## What is a test?

A test checks whether code produces the expected result
for a known input.

## Example: Earthquake Magnitude Filter

Input magnitudes:

`[0, 2.5, null, 5.1, -1]`

Rule:

- Reject null values.
- Reject zero and negative values.
- Accept positive values.

Expected output:

`[2.5, 5.1]`

Expected result:
- 2 records accepted.
- 3 records rejected.

## How do we know the test passed?

The test compares the actual output with the expected output.

- PASS: Both outputs match.
- FAIL: The outputs differ, so we investigate the problem.

## Important

A test must check the actual project code, not a separate
copy of the same rule.

This test checks the filtering rule only. It does not prove
that the entire data pipeline works correctly.
