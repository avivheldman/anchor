from fastapi import FastAPI
from Routers.sheet_router import router as sheet_router
from Routers.cell_router import router as cell_router

app = FastAPI(title="Sheet API", version="1.0.0")

app.include_router(sheet_router)
app.include_router(cell_router)

@app.get("/")
def root():
    return {"message": "Sheet API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)