import hazelcast

client = hazelcast.HazelcastClient()
my_map = client.get_map("capitals").blocking()

value = my_map.get("key")
print(f"🔍 Кінцеве значення key = {value}")

client.shutdown()