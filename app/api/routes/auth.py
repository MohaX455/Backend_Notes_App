from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_db,
    get_current_user
)

from app.services.auth_service import AuthService
from app.core.config import settings

from app.schemas.auth_schema import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshResponse,
    LogoutResponse,
    AuthUserResponse,
    TokenResponse
)

from app.models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# REGISTER
@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):

    user = await AuthService.register(
        db=db,
        username=data.username,
        email=data.email,
        password=data.password
    )

    return RegisterResponse(
        message="Registration successful",
        user=AuthUserResponse(
            id=user.id,
            username=user.username,
            email=user.email
        )
    )

# LOGIN
@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK
)
async def login(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):

    access_token, refresh_token, user = await AuthService.login(
        db=db,
        email=data.email,
        password=data.password
    )

    # refresh token -> cookie
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_COOKIE_MAX_AGE_SECONDS
    )

    return LoginResponse(
        message="Login successful",
        token=TokenResponse(
            access_token=access_token
        ),
        user=AuthUserResponse(
            id=user.id,
            username=user.username,
            email=user.email
        )
    )

# REFRESH TOKEN
@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK
)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):

    refresh_token = request.cookies.get(
        settings.REFRESH_COOKIE_NAME
    )

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    new_access_token, new_refresh_token = (
        await AuthService.refresh_token(
            db=db,
            token=refresh_token
        )
    )

    # replace old cookie
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=new_refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_COOKIE_MAX_AGE_SECONDS
    )

    return RefreshResponse(
        token=TokenResponse(
            access_token=new_access_token
        )
    )

# CURRENT USER
@router.get(
    "/me",
    response_model=AuthUserResponse,
    status_code=status.HTTP_200_OK
)
async def me(
    current_user: User = Depends(get_current_user)
):

    return AuthUserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email
    )

# LOGOUT
@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK
)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):

    refresh_token = request.cookies.get(
        settings.REFRESH_COOKIE_NAME
    )

    if refresh_token:
        await AuthService.logout(
            db=db,
            refresh_token=refresh_token
        )

    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE
    )

    return LogoutResponse(
        message="Logged out successfully"
    )