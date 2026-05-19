# API пользователей

Базовый путь: `/api/users`

---

## Получить текущего пользователя

`GET /api/users/me`

Требует аутентификации.

**Ответ:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Alice Smith",
  "role": "employee",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Список всех пользователей

`GET /api/users`

Возвращает список всех зарегистрированных пользователей.

**Ответ:** `200 OK`

```json
[
  {
    "id": "...",
    "email": "user@example.com",
    "full_name": "Alice Smith",
    "role": "employee",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```
