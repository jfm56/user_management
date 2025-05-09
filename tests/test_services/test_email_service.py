import pytest
from app.services.email_service import EmailService
from app.models.user_model import User

class DummySMTPClient:
    def __init__(self):
        self.sent = []
    def send_email(self, subject, content, recipient):
        self.sent.append((subject, content, recipient))
    def send_text_email(self, subject, content, recipient):
        self.sent.append((subject, content, recipient))

class DummyTemplateManager:
    def render_template(self, template_name, **data):
        return "<html>dummy</html>"

@pytest.fixture
def email_service(monkeypatch):
    # Patch SMTPClient to use dummy
    monkeypatch.setattr(
        'app.services.email_service.SMTPClient',
        lambda server, port, username, password: DummySMTPClient()
    )
    svc = EmailService(template_manager=DummyTemplateManager())
    return svc


def test_send_user_email_html_success(email_service):
    result = email_service.send_user_email(
        {'email': 'a@b.com', 'name': 'Alice'},
        'subj', '<html/>', 'html'
    )
    assert result is True
    assert email_service.smtp_client.sent


def test_send_user_email_text_success(email_service):
    result = email_service.send_user_email(
        {'email': 'b@c.com', 'name': 'Bob'},
        'subj2', 'text', 'text'
    )
    assert result is True
    assert email_service.smtp_client.sent


def test_send_user_email_no_email(email_service):
    with pytest.raises(ValueError):
        email_service.send_user_email(
            {'name': 'NoEmail'}, 's', 'c', 'html'
        )


def test_publish_email_event_no_producer(email_service):
    email_service._kafka_producer = None
    assert email_service._publish_email_event('x', {'y': 'z'}) is False


def test_publish_email_event_with_producer(email_service):
    class Prod:
        def publish_event(self, t, d):
            return True
    svc = email_service
    svc._kafka_producer = Prod()
    assert svc._publish_email_event('x', {'y': 'z'}) is True

@pytest.mark.asyncio
async def test_send_user_email_async_invalid_type(email_service):
    with pytest.raises(ValueError):
        await email_service.send_user_email_async({'email': 'a@b.com'}, 'invalid')

@pytest.mark.asyncio
async def test_send_verification_email_missing_token(email_service):
    # Create user without token
    user = User(
        id='1', email='a@b.com', nickname='Alice', verification_token=None
    )
    with pytest.raises(ValueError):
        await email_service.send_verification_email(user)

@pytest.mark.asyncio
async def test_send_user_email_async_role_upgrade_success(email_service):
    # Test sending role upgrade emails asynchronously
    user_data = {'email': 'a@b.com', 'name': 'Alice'}
    result = await email_service.send_user_email_async(user_data, 'role_upgrade')
    assert result is True
    # Email should be sent via SMTP client
    assert email_service.smtp_client.sent
    subject, content, recipient = email_service.smtp_client.sent[0]
    assert subject == "Role Upgrade Notification"
    assert content == "<html>dummy</html>"
    assert recipient == 'a@b.com'
