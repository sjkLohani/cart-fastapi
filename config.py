import logging
import os

# Configure logging to write to both a file and the terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] UserID:%(user_id)s - %(message)s",
    handlers=[
        logging.FileHandler("app_logs.log"),
        logging.StreamHandler()
    ]
)

def log_user_activity(user_id: int, message: str, level: str = "info"):
    # Using 'extra' to pass the user_id into the log format
    if level == "info":
        logging.info(message, extra={"user_id": user_id})
    else:
        logging.error(message, extra={"user_id": user_id})
logger = logging.getLogger("cart_api")

DATABASE_URL = "mysql+pymysql://root:Password123!@localhost:3306/cart_db"