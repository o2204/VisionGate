from fastapi.templating import Jinja2Templates
from typing_extensions import Annotated

from fastapi import (
    BackgroundTasks,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.db.redis import is_jti_blacklisted
from src.core.constant_manger import TEMPLATE_DIR
from src.clients.db.database import get_db

from src.service.notification_service import (
    NotificationService
)

from src.service.alert_service import (
    AlertService
)

from src.service.face_recognition_service import (
    FaceRecognitionService
)

from src.service.history_service import (
    HistoryService
)

from src.service.auth_service import (
    AuthService
)

from src.models.admin_model import (
    AdminModel
)

from src.models.user_model import (
    UserModel
)

from src.service.admin_service import (
    AdminService
)

from src.service.user_service import (
    UserService
)

from src.core.security import (
    oauth2_user_scheme,
    oauth2_admin_scheme
)

from src.core.utils.utils import (
    decode_access_token
)

# =========================
# Database Session
# =========================

SessionDep = Annotated[
    AsyncSession,
    Depends(get_db)
]

# =========================
# Templates
# =========================

templates = Jinja2Templates(
    TEMPLATE_DIR
)

# =========================
# Tokens
# =========================

UserTokenDep = Annotated[
    str,
    Depends(oauth2_user_scheme)
]

AdminTokenDep = Annotated[
    str,
    Depends(oauth2_admin_scheme)
]

# =========================
# Validate Token
# =========================

async def validate_token(
    token: str
) -> dict:

    data = decode_access_token(
        token
    )

    if (
        data is None
        or await is_jti_blacklisted(
            data["jti"]
        )
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return data

# =========================
# User Token
# =========================

async def get_user_token(
    token: UserTokenDep
):

    return await validate_token(
        token
    )

# =========================
# Admin Token
# =========================

async def get_admin_token(
    token: AdminTokenDep
):

    return await validate_token(
        token
    )

# =========================
# Current User
# =========================

async def get_current_user(
    token_data: Annotated[
        dict,
        Depends(get_user_token)
    ],

    session: SessionDep,
):

    user_id = token_data.get(
        "id"
    )

    role = token_data.get(
        "role"
    )

    if (
        not user_id
        or role != "user"
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid user token"
        )

    user = await session.get(
        UserModel,
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

# =========================
# Current Admin
# =========================

async def get_current_admin(
    token_data: Annotated[
        dict,
        Depends(get_admin_token)
    ],

    session: SessionDep
):

    admin_id = token_data.get(
        "id"
    )

    role = token_data.get(
        "role"
    )

    if (
        not admin_id
        or role != "admin"
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid admin token"
        )

    admin = await session.get(
        AdminModel,
        admin_id
    )

    if not admin:

        raise HTTPException(
            status_code=404,
            detail="Admin not found"
        )

    return admin

# =========================
# Notification Service
# =========================

def get_notification_service(
    tasks: BackgroundTasks
):

    return NotificationService(
        tasks
    )

NotificationServiceDep = Annotated[
    NotificationService,
    Depends(get_notification_service)
]

# =========================
# User Service
# =========================

def get_user_service(
    db: SessionDep,
    tasks: BackgroundTasks
) -> UserService:

    return UserService(
        model=UserModel,
        session=db,
        tasks=tasks,
        auth_service=AuthService()
    )

UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service)
]

# =========================
# Current User Dependency
# =========================

UserModelDep = Annotated[
    UserModel,
    Depends(get_current_user)
]

# =========================
# Admin Service
# =========================

def get_admin_service(
    db: SessionDep,
    tasks: BackgroundTasks
) -> AdminService:

    return AdminService(
        model=AdminModel,
        session=db,
        auth_service=AuthService(),
        tasks=tasks
    )

AdminServiceDep = Annotated[
    AdminService,
    Depends(get_admin_service)
]

# =========================
# Current Admin Dependency
# =========================

AdminDep = Annotated[
    AdminModel,
    Depends(get_current_admin)
]

# =========================
# History Service
# =========================

def get_history_service(
    db: SessionDep
):

    return HistoryService(
        db
    )

HistoryServiceDep = Annotated[
    HistoryService,
    Depends(get_history_service)
]

# =========================
# Alert Service
# =========================

def get_alert_service(
    session: SessionDep,
    notification: NotificationServiceDep
):

    return AlertService(
        session,
        notification
    )

AlertServiceDep = Annotated[
    AlertService,
    Depends(get_alert_service)
]

# =========================
# Face Recognition Service
# =========================

def get_face_service(
    session: SessionDep,
    tasks: BackgroundTasks
):

    return FaceRecognitionService(
        session,
        tasks
    )

FaceServiceDep = Annotated[
    FaceRecognitionService,
    Depends(get_face_service)
]