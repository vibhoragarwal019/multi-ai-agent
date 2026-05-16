import socket
import subprocess
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
        port = 9999
        if is_port_in_use(host, port):
            logger.warning(f"Port {port} is already in use; assuming backend is already running")
            return

        logger.info("starting backend service..")
        subprocess.run(["uvicorn", "app.backend.api:app", "--host", host, "--port", str(port)], check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Problem with backend service")
        raise CustomException("Failed to start backend", e)
    except CustomException as e:
        logger.error("Problem with backend service")
        raise CustomException("Failed to start backend", e)
    
def run_frontend():
    try:
        logger.info("Starting Frontend service")
        subprocess.run(["streamlit" , "run" , "app/frontend/ui.py"],check=True)
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


    
