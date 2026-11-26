"""
Authentication API Router
Implements user registration, OAuth2 password login with JWT issuance, and profile retrieval:
- POST /api/auth/register (Create new user)
- POST /api/auth/login    (Authenticate and receive JWT)
- GET  /api/auth/me       (Get current authenticated user profile)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Registers a new student or evaluator:
    1. Validates username, email, and password requirements using Pydantic.
    2. Checks for duplicate username or email.
    3. Cryptographically hashes the password with Argon2id.
    4. Persists the new user in SQLite.
    5. Returns the user profile without the password or password hash.
    """
    # Check for existing username
    existing_username = db.query(User).filter(User.username == payload.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists."
        )

    # Check for existing email
    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Hash the password securely
    hashed_pw = hash_password(payload.password)

    # Create and save user record
    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User login with JWT token issuance"
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """
    OAuth2-compliant password login flow:
    1. Accepts credentials via standard OAuth2 form (username field accepts either username or email).
    2. Queries user in SQLite.
    3. Verifies provided password against stored Argon2id hash.
    4. Generates and returns a signed JWT access token.
    """
    # Lookup by either username or email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()

    # Reject if user doesn't exist or password mismatch
    # Note: Generic error message prevents username/email enumeration attacks
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Issue signed JWT with username as subject ('sub')
    access_token = create_access_token(data={"sub": user.username})

    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile (Protected)"
)
def read_current_user(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Protected endpoint:
    Requires a valid 'Authorization: Bearer <token>' header.
    Returns the authenticated user's profile information.
    """
    return current_user
