# Import Celery tasks to register them
from app.tasks.email_tasks import (
    send_verification_email,
    send_account_locked_email,
    send_account_unlocked_email,
    send_role_upgrade_email,
    send_professional_status_email
)

# This module is imported by Celery when it starts up, which ensures
# that all tasks are registered correctly
