"""
Authentication API endpoints
Register, Login, and User Management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db, get_current_user, get_current_customer, get_current_merchant
from app.core.security import (
    get_password_hash,
    authenticate_user,
    create_token_response,
)
from app.schemas.user import (
    UserCreate,
    UserResponse,
    CustomerCreate,
    CustomerResponse,
    CustomerWithUser,
    CustomerPreferenceCreate,
    CustomerPreferenceResponse,
    MerchantCreate,
    MerchantResponse,
    MerchantWithUser,
    LoginRequest,
    TokenResponse
)
from app.models.user import User, Customer, Merchant, UserRole
from app.models.fuzzy import CustomerPreference

router = APIRouter()


# =====================
# Register Endpoints
# =====================

@router.post("/register/customer", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Register new customer

    - **full_name**: Full name (required)
    - **email**: Email address (required, unique)
    - **username**: Username (required, unique, 3-50 chars)
    - **password**: Password (required, min 6 chars)
    - **phone**: Phone number (optional)
    - **address**: Address (optional)
    - **latitude, longitude**: Location coordinates (optional)
    - **date_of_birth**: Date of birth (optional)
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == customer_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    existing_email = db.query(User).filter(User.email == customer_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # Create user
        user = User(
            username=customer_data.username,
            email=customer_data.email,
            password_hash=get_password_hash(customer_data.password),
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=False
        )
        db.add(user)
        db.flush()  # Get user.id

        # Create customer profile
        customer = Customer(
            user_id=user.id,
            full_name=customer_data.full_name,
            phone=customer_data.phone,
            address=customer_data.address,
            latitude=str(customer_data.latitude) if customer_data.latitude else None,
            longitude=str(customer_data.longitude) if customer_data.longitude else None,
            date_of_birth=customer_data.date_of_birth
        )
        db.add(customer)
        db.flush()  # Flush to get customer.id before creating preferences

        # Create preferences (use provided or default)
        if customer_data.preferences:
            # Use customer's preferences from registration
            prefs = customer_data.preferences
            customer_prefs = CustomerPreference(
                customer_id=customer.id,
                pref_price_importance=prefs.pref_price_importance,
                pref_price_sensitivity=prefs.pref_price_sensitivity,
                pref_distance_importance=prefs.pref_distance_importance,
                pref_max_distance_km=prefs.pref_max_distance_km,
                pref_popularity_importance=prefs.pref_popularity_importance,
                pref_spice_level=prefs.pref_spice_level,
                pref_sweetness_level=prefs.pref_sweetness_level,
                pref_savory_level=prefs.pref_savory_level,
                pref_cuisines=prefs.pref_cuisines,
                pref_dietary_restrictions=prefs.pref_dietary_restrictions
            )
        else:
            # Use default preferences
            customer_prefs = CustomerPreference(
                customer_id=customer.id,
                pref_price_importance=0.5,
                pref_price_sensitivity='medium',
                pref_distance_importance=0.3,
                pref_max_distance_km=10,
                pref_popularity_importance=0.2,
                pref_spice_level=0,
                pref_sweetness_level=0,
                pref_savory_level=0
            )
        db.add(customer_prefs)

        db.commit()

        # Refresh to get relationships
        db.refresh(user)

        # Create token response
        return create_token_response(user)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating customer: {str(e)}"
        )


@router.post("/register/merchant", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_merchant(
    merchant_data: MerchantCreate,
    db: Session = Depends(get_db)
):
    """
    Register new merchant (UMKM)

    - **shop_name**: Shop/restaurant name (required)
    - **email**: Email address (required, unique)
    - **username**: Username (required, unique, 3-50 chars)
    - **password**: Password (required, min 6 chars)
    - **address**: Address (required)
    - **latitude, longitude**: Location coordinates (required)
    - **phone**: Phone number (optional)
    - **description**: Business description (optional)
    - **price_range**: Price range $, $$, or $$$ (optional)
    - **cuisine_type**: Type of cuisine (optional)
    - **opening_hours**: Operating hours (optional, JSON format)
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == merchant_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    existing_email = db.query(User).filter(User.email == merchant_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # Create user
        user = User(
            username=merchant_data.username,
            email=merchant_data.email,
            password_hash=get_password_hash(merchant_data.password),
            role=UserRole.MERCHANT,
            is_active=True,
            is_verified=False
        )
        db.add(user)
        db.flush()

        # Create merchant profile
        merchant = Merchant(
            user_id=user.id,
            shop_name=merchant_data.shop_name,
            description=merchant_data.description,
            address=merchant_data.address,
            latitude=str(merchant_data.latitude),
            longitude=str(merchant_data.longitude),
            phone=merchant_data.phone,
            opening_hours=str(merchant_data.opening_hours) if merchant_data.opening_hours else None,
            price_range=merchant_data.price_range,
            cuisine_type=merchant_data.cuisine_type,
            is_active=True
        )
        db.add(merchant)

        db.commit()
        db.refresh(user)

        return create_token_response(user)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating merchant: {str(e)}"
        )


# =====================
# Login Endpoint
# =====================

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with username and password

    Returns JWT access token and user info
    """
    user = authenticate_user(db, credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_token_response(user)


# =====================
# Current User Endpoint
# =====================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user info

    Requires valid JWT token
    """
    return current_user


@router.get("/me/customer", response_model=CustomerWithUser)
async def get_current_customer_profile(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get current customer profile with preferences

    Requires customer role
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    # Add user info
    customer.email = current_user.email
    customer.username = current_user.username
    customer.is_verified = current_user.is_verified

    return customer


@router.get("/me/merchant", response_model=MerchantWithUser)
async def get_current_merchant_profile(
    current_user: User = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """
    Get current merchant profile

    Requires merchant role
    """
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant profile not found"
        )

    # Add user info
    merchant.email = current_user.email
    merchant.username = current_user.username
    merchant.is_verified = current_user.is_verified

    return merchant
