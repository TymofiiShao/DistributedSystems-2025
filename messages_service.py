from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def get_message():
    return {"message": "not implemented yet"}