def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


def div(value, arg):
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0


def test_mul_with_integers():
    assert mul(3, 4) == 12.0


def test_mul_with_strings():
    assert mul('2.5', '4') == 10.0


def test_mul_invalid_value_returns_zero():
    assert mul('abc', 4) == 0


def test_div_with_integers():
    assert div(10, 4) == 2.5


def test_div_by_zero_returns_zero():
    assert div(10, 0) == 0
