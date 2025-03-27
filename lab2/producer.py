
import hazelcast
import time

client = hazelcast.HazelcastClient()
queue = client.get_queue("my-bounded-queue").blocking()

for i in range(1, 101):
    queue.put(i)
    print(f"🚀 Вставлено {i}")
    time.sleep(0.1)
