from flask import Flask, request
import threading
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from consul_register import register_service

# Ініціалізація Flask
app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    sender = data.get("sender")
    body = data.get("body")
    print(f"[MESSAGE] From {sender}: {body}")
    return {"status": "received"}, 200

def run_flask():
    app.run(host="0.0.0.0", port=5002)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5052), daemon=True).start()
    register_service("messages-service", "messages-5002", port=5002, check_path="/health")
    run_flask()



