from sqlalchemy.orm import Session
from models.db_models import Cart, CartItem, Product

class CartRepository:
    @staticmethod
    def get_active_cart_by_user(db: Session, user_id: int) -> Cart:
        return db.query(Cart).filter(Cart.user_id == user_id, Cart.status == "ACTIVE").first()

    @staticmethod
    def create_cart(db: Session, user_id: int) -> Cart:
        db_cart = Cart(user_id=user_id, status="ACTIVE")
        db.add(db_cart)
        db.commit()
        db.refresh(db_cart)
        return db_cart

    @staticmethod
    def get_product(db: Session, product_id: int) -> Product:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_cart_item(db: Session, cart_id: int, product_id: int) -> CartItem:
        return db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id).first()

    @staticmethod
    def add_item_to_cart(db: Session, cart_item: CartItem):
        db.add(cart_item)
        db.commit()

    @staticmethod
    def remove_item(db: Session, cart_item: CartItem):
        db.delete(cart_item)
        db.commit()

    @staticmethod
    def delete_cart(db: Session, cart: Cart):
        db.delete(cart)
        db.commit()