from fastapi import FastAPI

app = FastAPI(title="AgriQ Logistics")

@app.get("/")
def root():
    return {"status": "online", "service": "AgriQ Logistics"}
