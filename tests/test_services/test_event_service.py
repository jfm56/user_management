import pytest
import logging
from app.services.event_service import EventService, event_service

class DummyProducer:
    def publish_event(self, event_type, data):
        return True

class FakeUser:
    def __init__(self):
        self.id = '1234'
        self.email = 'test@example.com'
        self.nickname = 'tester'
        self.verification_token = 'token'
        self.role = 'OLD_ROLE'


def test_publish_event_without_producer(caplog):
    svc = EventService()
    svc._kafka_producer = None
    caplog.set_level(logging.WARNING)
    result = svc.publish_event('ANY_EVENT', {'foo': 'bar'})
    assert result is False
    assert 'not available' in caplog.text.lower() or 'not published' in caplog.text.lower()


def test_publish_event_with_producer():
    svc = EventService()
    dummy = DummyProducer()
    svc._kafka_producer = dummy
    result = svc.publish_event('ANY_EVENT', {'foo': 'bar'})
    assert result is True


@pytest.mark.parametrize('method, args', [
    ('publish_account_verification_event', (DummyProducer(),)),
    ('publish_account_locked_event', (DummyProducer(),)),
    ('publish_account_unlocked_event', (DummyProducer(),)),
    ('publish_professional_status_event', (DummyProducer(),)),
])
def test_specific_publish_methods(monkeypatch, method, args):
    svc = EventService()
    dummy = DummyProducer()
    svc._kafka_producer = dummy
    user = FakeUser()
    func = getattr(svc, method)
    result = func(user)
    assert result is True


def test_publish_role_change_event(monkeypatch):
    svc = EventService()
    dummy = DummyProducer()
    svc._kafka_producer = dummy
    user = FakeUser()
    # call with old_role
    result = svc.publish_role_change_event(user, user.role)
    assert result is True
