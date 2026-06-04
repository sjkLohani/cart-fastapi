from fastapi import FastAPI, Depends, Header, status
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from schemas.cart_schemas import CartResponse, CartItemCreate, MessageResponse
from services.cart_service import CartService
from fastapi.responses import JSONResponse
from sqlalchemy import text

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce Cart Management API",
    description="Cart API implementing SOLID principles.",
    version="1.0.0"
)

# Mocking user context via a Header for simulation simplicity
def get_current_user_id(x_user_id: int = Header(..., description="logged-in User ID", gt=0)):
    return x_user_id

@app.get("/cart", response_model=CartResponse, tags=["Cart"])
def get_cart(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    # Simply retrieves an existing cart
    return CartService.get_active_cart(db, user_id)

@app.post("/cart", response_model=CartResponse, status_code=201, tags=["Cart"])
def create_cart(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    # Creates a brand new cart
    return CartService.create_new_cart(db, user_id)

# 2. Add Item to Cart
@app.post("/cart/items", response_model=CartResponse, tags=["Cart Items"])
def add_item_to_cart(item: CartItemCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return CartService.add_item(db, user_id, item.product_id, item.quantity)

# 3. Remove Item from Cart
@app.delete("/cart/items/{product_id}", response_model=CartResponse, tags=["Cart Items"])
def remove_item_from_cart(product_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return CartService.remove_item(db, user_id, product_id)

# 4. Checkout Cart
@app.post("/cart/checkout", response_model=CartResponse, tags=["Cart Checkout"])
def checkout_cart(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return CartService.checkout(db, user_id)

# 5. Delete Cart
@app.delete("/cart", response_model=MessageResponse, tags=["Cart"])
def delete_active_cart(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    CartService.delete_cart(db, user_id)
    return {"message": "Active cart successfully deleted"}

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to check DB connectivity
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "database": "disconnected"})

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please contact support.", "details": str(exc)},
    )