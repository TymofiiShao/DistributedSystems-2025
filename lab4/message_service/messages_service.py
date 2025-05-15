import hazelcast
from flask import Flask, jsonify
import threading

app = Flask(__name__)
message_storage = []

client = hazelcast.HazelcastClient(
    cluster_name="dev",
    cluster_members=[
        "127.0.0.1:5701",
        "127.0.0.1:5702",
        "127.0.0.1:5703"
    ]
)
log_queue = client.get_queue("log_queue").blocking()

@app.route("/messages", methods=["GET"])
def get_messages():
    return jsonify({"messages": message_storage})

def consume_messages():
    print("🟢 Starting message consumer loop...")
    while True:
        msg = log_queue.take()
        print(f"[CONSUMED] {msg}")
        message_storage.append(msg)

threading.Thread(target=consume_messages, daemon=True).start()

if __name__ == "__main__":
    app.run(port=8084)



