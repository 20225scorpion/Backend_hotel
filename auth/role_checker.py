from fastapi import Depends, HTTPException

from auth.auth_bearer import verify_token


def require_role(allowed_roles: list):

    def role_checker(
        user_data: dict = Depends(verify_token)
    ):

        if user_data["rol"] not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="No tienes permisos"
            )

        return user_data

    return role_checker