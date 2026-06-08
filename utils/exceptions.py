from fastapi import HTTPException, status


class CartException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class CartNotFound(CartException):
    def __init__(self):
        super().__init__(detail="Active cart not found for this user.")


class DataBoundaryViolation(HTTPException):
    def __init__(
        self, detail: str = "The provided identifier or value exceeds system limits."
    ):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
