from rest_framework.permissions import BasePermission


class IsActiveAndStaffPermission(BasePermission):
    """
    Доступ только для активных сотрудников

    Условия:
    - пользователь авторизован;
    - пользователь активен;
    - пользователь является сотрудником (is_staff=True)
    """

    def has_permission(self, request, view):
        user = request.user

        # Проверяем, что пользователь авторизован, активен и является сотрудником
        return bool(user and user.is_authenticated and user.is_active and user.is_staff)
