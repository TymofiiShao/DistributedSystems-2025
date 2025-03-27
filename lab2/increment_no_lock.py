import hazelcast

client = hazelcast.HazelcastClient()
my_map = client.get_map("capitals").blocking()

for i in range(10_000):
    value = my_map.get("key")
    my_map.put("key", value + 1)

print("Клієнт завершив інкремент")

client.shutdown()
