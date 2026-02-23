from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.dependencies.auth import require_role
from src.backend.models.user import Role, User
from src.backend.schemas.user import UserResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])


class RoleUpdate(BaseModel):
    role: str


@router.get("/users", response_model=list[UserResponse])
def list_users(
    _current_user: User = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    return db.query(User).all()


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    body: RoleUpdate,
    _current_user: User = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        user.role = Role(body.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(r.value for r in Role)}",
        )

    db.commit()
    db.refresh(user)
    return user
