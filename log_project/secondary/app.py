from fastapi import FastAPI, Request
import time
import random

app = FastAPI()
messages = {}
expected_id = 1


@app.get("/log")
def get_log():
    sorted_msgs = [messages[i] for i in sorted(messages) if i < expected_id]
    return {"messages": sorted_msgs}


@app.post("/replicate")
async def replicate(request: Request):
    global expected_id
    data = await request.json()
    msg_id = data["id"]

    time.sleep(2)

    if random.random() < 0.1:
        print(f"[DEBUG] Simulated 500 error for message {msg_id}")
        return {"status": "fail"}, 500

    if msg_id not in messages:
        messages[msg_id] = data
        print(f"[INFO] Accepted msg {msg_id}")

        while expected_id in messages:
            expected_id += 1

    return {"status": "ACK"}


