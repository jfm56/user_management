import os

# Broker settings
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')

# Task execution settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Task execution pool - using prefork for better compatibility
task_default_queue = 'default'

# Task result settings
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
result_expires = 60 * 60 * 24  # 1 day

# Logging
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# Task retry settings
task_acks_late = True
task_reject_on_worker_lost = True
task_default_retry_delay = 60  # 1 minute
task_max_retries = 3

# Configuring Kafka integration
# We'll use Redis as the broker for Celery, and Kafka for event streaming
# There's no direct Kafka broker for Celery, but we'll consume Kafka topics in our tasks

# Additional module level variables for configuration
kafka_bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
kafka_topics = {
    'email_notifications': 'user-email-notifications',
    'account_events': 'user-account-events',
    'role_changes': 'user-role-changes',
    'verification_events': 'user-verification-events',
}
