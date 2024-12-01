from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import threading
from utils import find_free_port, Com
import uvicorn
import json
from predict import predict_number
from depedencies import get_com

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://localhost:\d+$",
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


def start_server(port):
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    server.run()


@app.post("/api/create_com")
def create_com(port: str | None = None):
    try:
        com = Com(port)
        app.state.com = com
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/predict")
async def predict(file: UploadFile = File(...), com: Com = Depends(get_com)):
    try:
        content = await file.read()
        result, figure = predict_number(content)
        com.write(figure)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


def main():
    port = find_free_port()
    port_info_path = os.path.join(os.path.dirname(__file__), "port.json")
    threading.Thread(target=start_server, args=(port,)).start()
    with open(port_info_path, "w") as f:
        json.dump({"port": port}, f)


if __name__ == "__main__":
    main()
