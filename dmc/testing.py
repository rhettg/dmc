import contextlib

_MOCK_NOW = []


def set_mock_now(now):
    _MOCK_NOW.insert(0, now)


def clear_mock_now():
    del _MOCK_NOW[:]


def get_mock_now():
    try:
        return _MOCK_NOW[0]
    except IndexError:
        return None


@contextlib.contextmanager
def MockNow(now):
    set_mock_now(now)
    yield
    clear_mock_now()
