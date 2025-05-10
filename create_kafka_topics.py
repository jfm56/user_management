from confluent_kafka.admin import AdminClient, NewTopic

admin = AdminClient({'bootstrap.servers': 'localhost:9092'})
topics = [
    "user-verification-events",
    "user-email-notifications",
    "user-account-events",
    "user-role-changes"
]
new_topics = [NewTopic(topic, num_partitions=3, replication_factor=1) for topic in topics]
fs = admin.create_topics(new_topics)
for topic, f in fs.items():
    try:
        f.result()
        print(f"Topic {topic} created")
    except Exception as e:
        print(f"Failed to create topic {topic}: {e}")
