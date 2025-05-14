import hazelcast

client = hazelcast.HazelcastClient(
    cluster_name="dev",  # ❗ обов'язково "dev", бо такий у Hazelcast
    cluster_members=[
        "127.0.0.1:5701",
        "127.0.0.1:5702",
        "127.0.0.1:5703"
    ]
)

log_map = client.get_map("log_storage").blocking()
