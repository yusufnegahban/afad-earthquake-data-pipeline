
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

# 🧪 Testing 101 — Catch Bugs Before They Escape!

## Why do we test?

Imagine a tiny earthquake with magnitude `-2`. 🌍 Our pipeline shouldn't accept it as a valid earthquake!

Tests check whether our code behaves as expected, before bad data reaches our dashboard.

## 🔍 How a test works

```text
📥 Input → ⚙️ Code → 🔎 Actual result
                         ↓
                 Compare with Expected
                         ↓
                  ✅ PASS / ❌ FAIL
```

Example: filtering earthquake magnitudes

| Input | Expected result |
|---|---|
| `5.1` | ✅ Keep |
| `0` | ❌ Reject |
| `-1` | ❌ Reject |
| `None` | ❌ Reject |

**Expected** = what we want.  
**Actual** = what the code really returns.

If they match, the test passes. If not, investigate the bug! 🐛

## 🧰 Tests in this project

- `test_magnitude_filter.py` — checks magnitude filtering.
- `test_data_quality.py` — checks data quality rules.
- `realtime_mock.py` — a mock/simulation script; not necessarily a pytest test.

## ▶️ Run the tests

From the project root:

```bash
python -m pytest tests/ -v
```

## 💡 Remember

A passing test doesn't prove the whole pipeline is perfect. It proves only that the behavior covered by that test passed.

**Good tests make bugs easier to find, explain, and fix.** 🚀

# 🧪 Data Engineering Testing — Beginner's Guide

A practical guide to understanding data tests through the Earthquake Data Pipeline project.

## 🌍 Why Do Data Engineers Test?

Imagine collecting thousands of earthquake records. Some records may have missing magnitudes, invalid values, or unexpected formats.

If incorrect data reaches a dashboard, people may misunderstand the results.

**Testing helps us detect problems early and improve data reliability.**

## 1. 🧩 Unit Test

**What it means:** Tests one small piece of code independently.

**Project example:** Check whether the magnitude validation logic accepts positive values and rejects zero or negative values.

**Interview answer:**
> A unit test checks whether a small piece of code works as expected.

## 2. 📋 Test Case

**What it means:** A specific situation we want to test.

**Project example:**
- Input: `2.5` → Expected: accepted
- Input: `0` → Expected: rejected
- Input: `None` → Expected: rejected

**Interview answer:**
> A test case defines an input, an expected result, and the condition we want to verify.

## 3. 🎯 Expected vs. Actual Output

**What it means:** Compare what we expect with what the code actually produces.

**Project example:**

- Input: `[0, 2.5, None, 5.1, -1]`
- Expected valid values: `[2.5, 5.1]`
- Actual output: the values returned by the filter.

If the outputs match, the test passes.

**Interview answer:**
> We compare the actual output with the expected output to verify the logic.

## 4. ✅ Assertion

**What it means:** A check that fails when a condition is false.

**Project example:**
`assert actual_output == expected_output`

This checks whether the filter returned the correct values.

**Interview answer:**
> An assertion verifies that a condition is true. If it is false, the test fails.

## 5. 🧹 Data Quality Testing

**What it means:** Checks whether data meets defined quality rules.

**Project examples:**
- 📦 The dataset is not empty.
- 🔍 Required magnitude values are not missing.
- 📏 Magnitudes meet the project's validation rules.
- 🧾 Records contain the expected fields.

**Interview answer:**
> Data quality tests check whether data is complete, valid, and suitable for its intended use.

## 6. 🕳️ Null and Missing Values

**What it means:** A value is missing or unknown.

**Project example:** An earthquake record has no magnitude.

A missing magnitude should not automatically be treated as zero. The correct handling depends on the business rule.

**Interview answer:**
> I check for missing values because they can cause incorrect calculations and unreliable analysis.

## 7. 🔗 Testing the Real Function

**What it means:** Test the actual application code instead of rewriting its logic inside the test.

**Project example:** The project has a `filter_valid_magnitudes` function in `pipelines/silver/transformations.py`.

A stronger test calls that function directly rather than testing a separate helper that duplicates the same rule.

**Why it matters:** If the production function changes or breaks, the test can detect the problem.

**Interview answer:**
> Tests should verify the actual code used by the pipeline, not only a separate copy of its logic.

## 8. 🔄 Integration Test

**What it means:** Check whether multiple components work together correctly.

**Project example:** Verify that Spark can read the stored Bronze data, apply transformations, and write the cleaned output to the Silver layer.

**Interview answer:**
> An integration test checks whether different components work together as expected.

## 9. 🏗️ End-to-End Test

**What it means:** Check the workflow from beginning to end.

**Project example:** Validate the main path from earthquake data ingestion through processing and preparation of the analytical dataset.

**Interview answer:**
> An end-to-end test verifies that the complete workflow produces the expected result.

## 10. 🧪 Mock Data and Simulation

**What it means:** Generate artificial data to test a system without depending entirely on a live external source.

**Project example:** `realtime_mock.py` generates sample earthquake records and saves them as JSON files every five minutes.

**Important:** These are simulated records, not real earthquake observations. The script simulates periodic data generation; it does not prove that the pipeline is a real-time streaming system.

**Interview answer:**
> Mock data helps us test ingestion workflows in a controlled and repeatable way.

## 11. 🔁 Regression Testing

**What it means:** Run tests again after a code change to check that previously working behavior still works.

**Project example:** After changing the magnitude filter, rerun the tests to make sure valid magnitudes are still accepted and invalid ones are rejected.

**Interview answer:**
> Regression testing helps detect whether a new change has broken existing functionality.

## 12. 🛠️ Test Automation

**What it means:** Run tests automatically instead of checking every result manually.

**Project example:** Use `pytest` to discover and execute Python test functions.

Run the tests locally with:

```bash
python -m pytest tests/ -v
```

**Interview answer:**
> Automated tests make it easier to repeat checks consistently and detect problems early.

## 13. 🚦 Test Pass vs. Test Coverage

**Test pass:** The code behaved as expected for the cases tested.

**Test coverage:** How much of the code is exercised by tests.

A passing test does not prove that the entire pipeline is correct. A few passing tests also do not necessarily mean the project has good test coverage.

**Interview answer:**
> Passing tests confirm specific behaviors, while coverage helps us understand which parts of the code are tested.

## 14. 🧠 What Makes a Good Data Engineering Test?

A useful test should:

- 🎯 Check one clearly defined behavior.
- 📥 Use meaningful input data.
- ✅ Define the expected result.
- 🔍 Detect realistic data problems.
- 🔗 Test the actual function or component when possible.
- 🔁 Be repeatable and easy to run.
- 📝 Explain what is being checked and why.

## 🎤 Interview Summary

**Question: Why is testing important in data engineering?**

> Testing helps ensure that data is collected, transformed, and delivered correctly. I use unit tests for individual rules, data quality tests to validate records, and integration or end-to-end tests to check how pipeline components work together. This helps identify problems before incorrect data reaches analytical datasets or dashboards.

## 📌 Current Project Note

The current beginner tests use sample data to check basic conditions and magnitude-filtering logic. The mock scraper generates simulated records. These are useful learning steps, but they do not yet demonstrate complete end-to-end validation of the actual pipeline.

The next improvement is to test the real PySpark transformation and then add integration tests for the Bronze-to-Silver workflow.

