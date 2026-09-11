from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserProfileRead, UserRead

router = APIRouter()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


@router.post("/register", response_model=UserRead)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_create.email)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    is_expert = user_create.role == "expert"

    user = User(
        name=user_create.name,
        email=user_create.email,
        password_hash=get_password_hash(user_create.password),

        # Default roles
        is_learner=True,
        is_expert=is_expert,
        is_admin=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(
        {
            "user_id": user.id,
            "is_learner": user.is_learner,
            "is_expert": user.is_expert,
            "is_admin": user.is_admin,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"],
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    return user


@router.get("/profile", response_model=UserProfileRead)
def profile(current_user: User = Depends(get_current_user)):
    expert_profile = current_user.expert_profile

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_learner": current_user.is_learner,
        "is_expert": current_user.is_expert,
        "is_admin": current_user.is_admin,
        "expert_profile": {
            "id": expert_profile.id,
            "user_id": expert_profile.user_id,
            "title": expert_profile.title,
            "company": expert_profile.company,
            "experience_years": expert_profile.experience_years,
            "bio": expert_profile.bio,
            "hourly_rate": expert_profile.hourly_rate,
            "rating": expert_profile.rating,
            "is_verified": bool(expert_profile.is_verified),
            "verification_status": expert_profile.verification_status or ("approved" if expert_profile.is_verified else "pending"),
            "rejection_reason": expert_profile.rejection_reason,
        } if expert_profile else None,
    }
