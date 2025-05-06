# Kafka Topic Initialization

The system now includes a robust Kafka topic initialization process to ensure all required Kafka topics are created during startup.

## Implementation Details

1. **External Initialization Script**: The `kafka-init.sh` script runs outside the container and:
   - Waits for Kafka to be ready with a timeout mechanism
   - Creates all required topics if they don't exist
   - Verifies that topics were created successfully

2. **Integration with System Startup**: 
   - Add this to your startup process by running `./kafka-init.sh` before starting your containers
   - Use it in CI/CD pipelines to ensure topics exist before running tests

3. **Topics Created**:
   - `user-email-notifications`: For all email-related events
   - `user-account-events`: For user account creation, deletion, and status changes
   - `user-role-changes`: For role assignment and permission changes
   - `user-verification-events`: For email verification and password reset events

## Next Steps

After addressing the Kafka topic initialization, the next issue to focus on is fixing the authentication error handling where 401 Unauthorized errors are being converted to 500 Internal Server Errors.

## Updating Your Start-up Process

Add this to your project's start-up script or run manually when needed:

```bash
# First ensure Kafka and Zookeeper are running
docker compose up -d zookeeper kafka

# Wait a moment for services to initialize
sleep 5

# Run the Kafka topic initialization script
./kafka-init.sh

# Now start the rest of your services
docker compose up -d
```
