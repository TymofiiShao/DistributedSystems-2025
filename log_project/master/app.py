from fastapi import FastAPI, Request
import requests
import threading
import time
from queue import Queue

app = FastAPI()
messages = []
message_id = 0

SECONDARIES = {
    "secondary1": {
        "url": "http://secondary:8001",
        "queue": Queue(),
        "acks": set()
    },
    "secondary2": {
        "url": "http://secondary2:8001",
        "queue": Queue(),
        "acks": set()
    }
}


def retry_loop(name):
    secondary = SECONDARIES[name]
    url = secondary["url"]
    queue = secondary["queue"]
    while True:
        msg = queue.get()
        while True:
            try:
                res = requests.post(f"{url}/replicate", json=msg, timeout=2)
                if res.status_code == 200:
                    secondary["acks"].add(msg["id"])
                    break
                else:
                    print(f"[WARN] {name} returned {res.status_code}, retrying...")
            except Exception:
                print(f"[ERROR] Failed to deliver to {name}, retrying...")
            time.sleep(1)  # smart retry delay
        queue.task_done()


@app.on_event("startup")
def start_background_retry_threads():
    for name in SECONDARIES:
        threading.Thread(target=retry_loop, args=(name,), daemon=True).start()


@app.post("/log")
async def add_message(request: Request):
    global message_id
    data = await request.json()
    message = data["message"]
    w = int(data.get("w", 1))

    message_id += 1
    msg_obj = {"id": message_id, "message": message}
    messages.append(msg_obj)

    # enqueue to all secondaries
    for s in SECONDARIES.values():
        s["queue"].put(msg_obj)

    # wait until w-1 acks received
    while True:
        ack_count = sum(1 for s in SECONDARIES.values() if msg_obj["id"] in s["acks"])
        if ack_count >= (w - 1):
            break
        time.sleep(0.1)

    return {"status": f"Replicated with w={w}", "message": msg_obj}


@app.get("/log")
def get_log():
    return {"messages": sorted(messages, key=lambda x: x["id"])}



