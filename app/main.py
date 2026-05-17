import os
import socket
import subprocess
import sys
import threading
import time
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

load_dotenv()

def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.connect_ex((host, port)) == 0


def run_backend():
    try:
        host = "127.0.0.1"
        port = int(os.environ.get("BACKEND_PORT", "9999"))
        if is_port_in_use(host, port):
            logger.warning(f"Port {port} is already in use; assuming backend is already running")
            return

        logger.info("starting backend service..")
        subprocess.run([
            sys.executable, "-m", "uvicorn", "app.backend.api:app",
            "--host", host, "--port", str(port)
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Problem with backend service")
        raise CustomException("Failed to start backend", e)
    except CustomException as e:
        logger.error("Problem with backend service")
        raise CustomException("Failed to start backend", e)
    
def run_frontend():
    try:
        host = "0.0.0.0"
        port = int(os.environ.get("PORT", "8501"))
        local_host = "127.0.0.1"
        while is_port_in_use(local_host, port):
            logger.warning(f"Port {port} is already in use; trying next port")
            port += 1

        logger.info(f"Starting Frontend service on port {port}")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app/frontend/ui.py",
            "--server.port", str(port),
            "--server.address", host
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Problem with frontend service")
        raise CustomException("Failed to start frontend", e)
    except CustomException as e:
        logger.error("Problem with frontend service")
        raise CustomException("Failed to start frontend" , e)
    
if __name__=="__main__":
    try:
        threading.Thread(target=run_backend).start()
        time.sleep(2)
        run_frontend()
    
    except CustomException as e:
        logger.exception(f"CustomException occured : {str(e)}")


    
