from app.tasks.kafka_consumers import start_kafka_consumers

if __name__ == "__main__":
    print("Starting dedicated Kafka consumer...")
    start_kafka_consumers()
    # Keep the process alive
    import time
    while True:
        time.sleep(60)
