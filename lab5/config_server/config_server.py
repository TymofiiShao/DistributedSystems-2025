# config_server/config_server.py

from flask import Flask, jsonify

app = Flask(__name__)

# "Сервісний реєстр"
SERVICES = {
    "logging-service": [
        "127.0.0.1:50051",
        "127.0.0.1:50052",
        "127.0.0.1:50053"
    ],
    "messages-service": [  #
        "127.0.0.1:8084"
    ]
}

@app.route("/services/<service_name>", methods=["GET"])
def get_service_instances(service_name):
    if service_name in SERVICES:
        return jsonify(SERVICES[service_name])
    return jsonify([]), 404

if __name__ == "__main__":
    app.run(port=8000)

