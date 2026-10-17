import json


def load_data():
    with open(
        "data/raw/earthquakes_090730436692.json",
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def test_dataset_not_empty():
    data = load_data()

    assert len(data) > 0


def test_no_null_coordinates():
    data = load_data()

    for row in data:
        assert row["latitude"] is not None
        assert row["longitude"] is not None


def test_positive_magnitude():
    data = load_data()

    for row in data:
        assert row["magnitude"] >= 0
