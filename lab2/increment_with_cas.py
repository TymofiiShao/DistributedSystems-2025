import hazelcast
import time

client = hazelcast.HazelcastClient()
my_map = client.get_map("capitals").blocking()

start = time.time()

for i in range(10_000):
    while True:
        old_value = my_map.get("key")
        success = my_map.replace_if_same("key", old_value, old_value + 1)
        if success:
            break

end = time.time()
print(f"⚙️ Оптимістичне завершено за {end - start:.2f} сек")

client.shutdown()

