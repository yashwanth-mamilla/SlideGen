import pytest
from slidegen.utils import format_timestamp, require_command


def test_format_timestamp():
    assert format_timestamp(0.0) == "00:00.00"
    assert format_timestamp(65.5) == "01:05.50"
    assert format_timestamp(3600.0) == "60:00.00"


def test_require_command():
    # Command that exists on standard Unix systems
    require_command("ls")
    require_command("python3")

    with pytest.raises(RuntimeError):
        require_command("non_existent_command_12345")

