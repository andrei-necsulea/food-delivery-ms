class FakeUser:
    def __init__(self, user_id, role, authenticated=True):
        self.id = user_id
        self.role = role
        self.is_authenticated = authenticated


class FakeOrder:
    def __init__(self, customer_id):
        self.customer_id = customer_id


class FakePayment:
    def __init__(self, customer_id):
        self.order = FakeOrder(customer_id)


def _can_view_payment(user, payment):
    return user.is_authenticated and (user.role == 'admin' or payment.order.customer_id == user.id)


def test_admin_can_view_any_payment():
    user = FakeUser(1, 'admin')
    payment = FakePayment(customer_id=999)
    assert _can_view_payment(user, payment) is True


def test_customer_can_view_own_payment():
    user = FakeUser(7, 'client')
    payment = FakePayment(customer_id=7)
    assert _can_view_payment(user, payment) is True


def test_customer_cannot_view_other_payment():
    user = FakeUser(7, 'client')
    payment = FakePayment(customer_id=8)
    assert _can_view_payment(user, payment) is False


def test_unauthenticated_user_cannot_view_payment():
    user = FakeUser(7, 'client', authenticated=False)
    payment = FakePayment(customer_id=7)
    assert _can_view_payment(user, payment) is False
