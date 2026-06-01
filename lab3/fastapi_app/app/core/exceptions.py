class AppError(Exception):
    def __init__(self, message: str = "Ошибка приложения"):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Не найдено"):
        super().__init__(message)


class AlreadyExistsError(AppError):
    def __init__(self, message: str = "Уже существует"):
        super().__init__(message)


class AuthError(AppError):
    def __init__(self, message: str = "Ошибка аутентификации"):
        super().__init__(message)


class PermissionDeniedError(AppError):
    def __init__(self, message: str = "Недостаточно прав"):
        super().__init__(message)


class ValidationError(AppError):
    def __init__(self, message: str = "Неверный формат данных"):
        super().__init__(message)