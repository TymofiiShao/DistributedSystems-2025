import hazelcast

client = hazelcast.HazelcastClient()
my_map = client.get_map("capitals").blocking()

# Ініціалізація ключа
my_map.put_if_absent("key", 0)

print("Ініціалізовано ключ 'key' значенням 0")

client.shutdown()