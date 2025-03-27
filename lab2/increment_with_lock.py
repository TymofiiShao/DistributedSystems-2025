import hazelcast
import time

client = hazelcast.HazelcastClient()
my_map = client.get_map("capitals").blocking()

start = time.time()

for i in range(10_000):
    my_map.lock("key")
    try:
        value = my_map.get("key")
        my_map.put("key", value + 1)
    finally:
        my_map.unlock("key")

end = time.time()
print(f"🛡️ Песимістичне завершено за {end - start:.2f} сек")

client.shutdown()
