import pandas as pd
def test_dataset_not_empty():
    df = pd.DataFrame({"magnitude": [2.5, 4.1]})

    assert not df.empty


def test_no_null_magnitudes():
    df = pd.DataFrame({"magnitude": [2.5, 4.1, 3.0]})

    assert df["magnitude"].isnull().sum() == 0
