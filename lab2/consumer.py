import hazelcast

client = hazelcast.HazelcastClient()
queue = client.get_queue("my-bounded-queue").blocking()

while True:
    item = queue.take()
    print(f"🟢 Прочитано: {item}")