# nuitka-project: --standalone
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/data=data

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import threading
from utils import find_free_port
import uvicorn
import json
from predict import predict_number
from depedencies import get_connection
from connection import Connection, Com, get_available_ports

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://localhost:\d+$",
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


def start_server(port):
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    server.run()


@app.get("/api/serial_ports")
def get_serial_ports():
    try:
        serial_ports = get_available_ports()
        return serial_ports
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/create_com/{port}")
def create_com(port: str | None = None):
    try:
        com = Com(port)
        app.state.con = com
    except Exception as e:
        raise HTTPException(400, detail=str(e))


@app.post("/api/predict")
async def predict(
    file: UploadFile = File(...), con: Connection = Depends(get_connection)
):
    try:
        content = await file.read()
        result, figure = predict_number(content)
        con.write(figure)
        return {"result": result}
    except Exception as e:
        raise HTTPException(400, detail=str(e))


def main():
    port = find_free_port()
    port_info_path = os.path.join(os.path.dirname(__file__), "port.json")
    threading.Thread(target=start_server, args=(port,)).start()
    with open(port_info_path, "w") as f:
        json.dump({"port": port}, f)


if __name__ == "__main__":
    main()
