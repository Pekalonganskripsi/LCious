"""
Dependency injection utilities for API endpoints
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import create_access_token, decode_access_token
from app.models.user import User, Customer

# HTTP Bearer token scheme
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency untuk get database session

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception

    return user


def get_current_customer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify current user is a customer

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        User if role is customer

    Raises:
        HTTPException: If user is not a customer
    """
    from app.models.user import UserRole

    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Customer role required."
        )
    return current_user


def get_current_merchant(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify current user is a merchant

    Args:
        current_user: Current authenticated user

    Returns:
        User if role is merchant

    Raises:
        HTTPException: If user is not a merchant
    """
    from app.models.user import UserRole

    if current_user.role != UserRole.MERCHANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Merchant role required."
        )
    return current_user


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify current user is a superadmin

    Args:
        current_user: Current authenticated user

    Returns:
        User if role is superadmin

    Raises:
        HTTPException: If user is not a superadmin
    """
    from app.models.user import UserRole

    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Superadmin role required."
        )
    return current_user


def get_current_user_optional(
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional current user (tidak wajib login)

    Returns:
        User if logged in, None otherwise
    """
    try:
        from fastapi import Request
        import contextlib

        # Try to get user from token
        with contextlib.suppress(Exception):
            return get_current_user(db=db)
    except:
        pass

    return None


def get_customer_by_id(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """
    Get customer by ID

    Args:
        customer_id: Customer UUID
        db: Database session

    Returns:
        Customer object

    Raises:
        HTTPException: If customer not found
    """
    from app.models.user import Customer

    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return customer


def get_merchant_by_id(
    merchant_id: str,
    db: Session = Depends(get_db)
):
    """
    Get merchant by ID

    Args:
        merchant_id: Merchant UUID
        db: Database session

    Returns:
        Merchant object

    Raises:
        HTTPException: If merchant not found
    """
    from app.models.user import Merchant

    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )

    return merchant


def get_menu_by_id(
    menu_id: str,
    db: Session = Depends(get_db)
):
    """
    Get menu by ID

    Args:
        menu_id: Menu UUID
        db: Database session

    Returns:
        Menu object

    Raises:
        HTTPException: If menu not found
    """
    from app.models.menu import Menu

    menu = db.query(Menu).filter(Menu.id == menu_id).first()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found"
        )

    return menu
