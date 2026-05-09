from decimal import Decimal
from datetime import timedelta


def serialize_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f'Type {type(obj)} not serializable')


def format_duration_hhmm(duration):
    if not duration:
        return '-'

    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f'{hours}h {minutes}m'


def test_serialize_decimal_returns_float():
    val = Decimal('12.34')
    out = serialize_decimal(val)
    assert isinstance(out, float)
    assert out == 12.34


def test_serialize_decimal_raises_for_other_types():
    try:
        serialize_decimal(object())
    except TypeError:
        pass
    else:
        raise AssertionError('Expected TypeError')


def test_format_duration_hhmm_none():
    assert format_duration_hhmm(None) == '-'


def test_format_duration_hhmm_hours_minutes():
    d = timedelta(hours=2, minutes=20, seconds=15)
    assert format_duration_hhmm(d) == '2h 20m'
