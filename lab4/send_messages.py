import requests

for i in range(1, 11):
    msg = f"msg{i}"
    res = requests.post("http://127.0.0.1:7000/log", json={"msg": msg})
    print(f"Sent {msg}: {res.status_code} {res.json()}")
