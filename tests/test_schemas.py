import pytest
from pydantic import ValidationError
from app.schemas import JobCreate


def test_http_callback():
    item = JobCreate(payload={"x": 1}, callback_url="https://example.com/hook")
    assert str(item.callback_url).startswith("https://")


def test_invalid_callback_scheme():
    with pytest.raises(ValidationError):
        JobCreate(payload={}, callback_url="file:///tmp/x")
