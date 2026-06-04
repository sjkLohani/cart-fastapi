from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from repositories.cart_repo import CartRepository
from models.db_models import CartItem, Cart
from config import logger
from utils.exceptions import CartNotFound
from config import log_user_activity

class CartService:
    @staticmethod
    def get_active_cart(db: Session, user_id: int):
        cart = CartRepository.get_active_cart_by_user(db, user_id)
        if not cart:
            log_user_activity(user_id, "User requested cart, but no ACTIVE session found.", "error")
            raise CartNotFound()
        
        log_user_activity(user_id, f"Successfully retrieved active cart ID: {cart.id}")
        return cart

    @staticmethod
    def create_new_cart(db: Session, user_id: int):
        # Your creation logic here
        return CartRepository.create_cart(db, user_id)

    @staticmethod
    def add_item(db: Session, user_id: int, product_id: int, quantity: int) -> Cart:
        cart = CartService.get_or_create_cart(db, user_id)
        product = CartRepository.get_product(db, product_id)
        
        if not product:
            logger.error(f"Failed to add item: Product ID {product_id} not found.")
            raise HTTPException(status_code=404, detail="Product not found")

        existing_item = CartRepository.get_cart_item(db, cart.id, product_id)
        if existing_item:
            existing_item.quantity += quantity
            logger.info(f"Updated product_id={product_id} quantity in cart_id={cart.id}")
        else:
            # Capturing the Price Snapshot feature here
            new_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                unit_price_at_addition=product.current_price 
            )
            CartRepository.add_item_to_cart(db, new_item)
            logger.info(f"Added new product_id={product_id} snapshot price={product.current_price} to cart_id={cart.id}")

        db.refresh(cart)
        return cart

    @staticmethod
    def remove_item(db: Session, user_id: int, product_id: int) -> Cart:
        cart = CartRepository.get_active_cart_by_user(db, user_id)
        if not cart:
            raise HTTPException(status_code=404, detail="No active cart found for this user")

        cart_item = CartRepository.get_cart_item(db, cart.id, product_id)
        if not cart_item:
            raise HTTPException(status_code=404, detail="Item not found in cart")

        CartRepository.remove_item(db, cart_item)
        logger.info(f"Removed product_id={product_id} from cart_id={cart.id}")
        db.refresh(cart)
        return cart

    @staticmethod
    def checkout(db: Session, user_id: int) -> Cart:
        cart = CartRepository.get_active_cart_by_user(db, user_id)
        if not cart or not cart.items:
            raise HTTPException(status_code=400, detail="Cannot checkout an empty or non-existent cart")

        cart.status = "CONVERTED"
        db.commit()
        logger.info(f"Cart ID {cart.id} successfully CONVERTED (Checked out) for user_id={user_id}")
        return cart

    @staticmethod
    def delete_cart(db: Session, user_id: int):
        cart = CartRepository.get_active_cart_by_user(db, user_id)
        if not cart:
            raise HTTPException(status_code=404, detail="No active cart found to delete")
        
        cart_id = cart.id
        CartRepository.delete_cart(db, cart)
        logger.info(f"Deleted active cart_id={cart_id} for user_id={user_id}")