from fastapi import HTTPException
from sqlalchemy.orm import Session

from config import log_user_activity
from models.db_models import Cart, CartItem
from repositories.cart_repo import CartRepository
from utils.exceptions import CartException, CartNotFound, DataBoundaryViolation


class CartService:
    @staticmethod
    def get_active_cart(db: Session, user_id: int):
        try:
            cart = CartRepository.get_active_cart_by_user(db, user_id)
            if not cart:
                log_user_activity(
                    user_id,
                    "Failed to retrieve cart: Active session not found.",
                    "error",
                )
                raise CartNotFound()

            log_user_activity(user_id, f"Active cart found with ID: {cart.id}", "info")
            return cart
        except DataBoundaryViolation as env_exc:
            log_user_activity(
                user_id=user_id,
                message="CRITICAL BOUNDARY VIOLATION: User ID requested during retrieval exceeds database integer limits. Swallowed SQL metadata to prevent leak.",
                level="error",
            )
            raise env_exc

    @staticmethod
    def create_new_cart(db: Session, user_id: int):
        try:
            # 1. Check if an active cart already exists to prevent duplicates
            existing_cart = CartRepository.get_active_cart_by_user(db, user_id)
            if existing_cart:
                log_user_activity(
                    user_id,
                    "Aborted cart creation: Active cart already exists.",
                    "error",
                )
                raise CartException(detail="You already have an active cart session.")

            # 2. Attempt creation
            new_cart = CartRepository.create_cart(db, user_id)
            log_user_activity(
                user_id,
                f"Successfully created new active cart ID: {new_cart.id}",
                "info",
            )
            return new_cart

        except DataBoundaryViolation as env_exc:
            # Capturing the infinite integer block here safely
            log_user_activity(
                user_id=user_id,
                message="CRITICAL BOUNDARY VIOLATION: User ID requested during creation exceeds database integer limits. Swallowed SQL metadata to prevent leak.",
                level="error",
            )
            raise env_exc

    @staticmethod
    def add_item(db: Session, user_id: int, product_id: int, quantity: int) -> Cart:
        # Fetch or create the active cart context safely from the Repository layer
        cart = CartRepository.get_active_cart_by_user(db, user_id)
        if not cart:
            cart = CartRepository.create_cart(db, user_id)
            log_user_activity(
                user_id,
                f"Auto-initialized fresh active cart session ID: {cart.id}",
                "info",
            )

        product = CartRepository.get_product(db, product_id)
        if not product:
            log_user_activity(
                user_id,
                f"Failed to add item: Product ID {product_id} not found in database catalog.",
                "error",
            )
            raise HTTPException(status_code=404, detail="Product not found")

        existing_item = CartRepository.get_cart_item(db, cart.id, product_id)
        if existing_item:
            existing_item.quantity += quantity
            db.commit()
            log_user_activity(
                user_id,
                f"Aggregated quantity: product_id={product_id} increased by count={quantity} in cart_id={cart.id}",
                "info",
            )
        else:
            # Capturing the Price Snapshot feature here
            new_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                unit_price_at_addition=product.current_price,
            )
            CartRepository.add_item_to_cart(db, new_item)
            log_user_activity(
                user_id,
                f"Added new product_id={product_id} snapshot price={product.current_price} to cart_id={cart.id}",
                "info",
            )

        db.refresh(cart)
        return cart

    @staticmethod
    def remove_item(db: Session, user_id: int, product_id: int) -> Cart:
        cart = CartRepository.get_active_cart_by_user(db, user_id)
        if not cart:
            raise HTTPException(
                status_code=404, detail="No active cart found for this user"
            )

        cart_item = CartRepository.get_cart_item(db, cart.id, product_id)
        if not cart_item:
            raise HTTPException(status_code=404, detail="Item not found in cart")

        CartRepository.remove_item(db, cart_item)
        log_user_activity(
            user_id, f"Removed product_id={product_id} from cart_id={cart.id}", "info"
        )
        db.refresh(cart)
        return cart

    @staticmethod
    def checkout(db: Session, user_id: int) -> Cart:
        cart = CartRepository.get_active_cart_by_user(db, user_id)
        if not cart or not cart.items:
            raise HTTPException(
                status_code=400, detail="Cannot checkout an empty or non-existent cart"
            )

        cart.status = "CONVERTED"
        db.commit()
        log_user_activity(
            user_id, f"Cart ID {cart.id} successfully CONVERTED (Checked out)", "info"
        )
        return cart

    @staticmethod
    def delete_cart(db: Session, user_id: int):
        cart = CartRepository.get_active_cart_by_user(db, user_id)
        if not cart:
            raise HTTPException(
                status_code=404, detail="No active cart found to delete"
            )

        cart_id = cart.id
        CartRepository.delete_cart(db, cart)
        log_user_activity(
            user_id, f"Successfully deleted active cart session ID: {cart_id}", "info"
        )
