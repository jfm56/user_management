from confluent_kafka.admin import AdminClient

if __name__ == "__main__":
    admin = AdminClient({'bootstrap.servers': 'localhost:9092'})
    topics = admin.list_topics(timeout=10).topics
    print("Kafka topics:")
    for topic in topics:
        print(topic)
