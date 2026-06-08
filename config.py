import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] UserID:%(user_id)s - %(message)s",
    handlers=[logging.FileHandler("app_logs.log"), logging.StreamHandler()],
)


def log_user_activity(user_id, message: str, level: str = "info"):
    # Cast user_id to string to prevent any weird layout formatting anomalies with large numbers
    extra_data = {"user_id": str(user_id)}

    if level == "error":
        logging.error(message, extra=extra_data)
    elif level == "critical":
        logging.critical(message, extra=extra_data)
    else:
        logging.info(message, extra=extra_data)


DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root:Password123!@localhost:3306/cart_db"
)
