from fastapi import FastAPI

app = FastAPI(
    title="Byro API",
    description="Digital Chief of Staff for the Modern Family Office",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Byro API is running"}