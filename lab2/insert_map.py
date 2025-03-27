import hazelcast

client = hazelcast.HazelcastClient(
    cluster_name="dev",  # дуже важливо!
    cluster_members=[
        "192.168.0.180:5701",
        "192.168.0.180:5702",
        "192.168.0.180:5703"
    ]
)

distributed_map = client.get_map("capitals").blocking()

for i in range(1000):
    distributed_map.put(str(i), f"value-{i}")

print("✅ 1000 entries inserted into 'capitals' map.")
client.shutdown()