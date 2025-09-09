from typing import Iterable

from fastapi import Depends, HTTPException, status

from .deps import get_current_user
from .models.user import User


def require_roles(allowed_roles: Iterable[str]):
    def _guard(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return _guard