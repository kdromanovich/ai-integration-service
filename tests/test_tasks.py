from app.tasks import backoff_seconds


def test_backoff_is_bounded():
    assert backoff_seconds(1) == 2
    assert backoff_seconds(10) == 60
