# E-Commerce Cart API

A robust, production-grade Cart API built with **FastAPI** and **SQLAlchemy**. Designed with SOLID principles, contextual logging, and a RESTful architecture.

## Features
- **Price Snapshotting:** Prevents total price drift by locking in item prices at the moment of addition.
- **RESTful Design:** Clean separation of `GET` and `POST` for cart lifecycle management.
- **Observability:** Custom logging pipeline with `user_id` injection for easy debugging.
- **Resilience:** Global Exception Handling and an automated Health Check endpoint.
- **PEP 8 Compliant:** Clean, readable snake_case architecture across all files and database schemas.

## Architecture


## Setup
1. **Clone the repo:** `git clone <your-repo-url>`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Configure Database:** Update `DATABASE_URL` in `config.py` with your MySQL credentials.
4. **Run:** `uvicorn main:app --reload`

## Endpoints
- `GET /cart`: Retrieve current active cart.
- `POST /cart`: Initialize a new active cart.
- `POST /cart-items`: Add/Update items in the cart.
- `GET /health`: System health status check.

---
