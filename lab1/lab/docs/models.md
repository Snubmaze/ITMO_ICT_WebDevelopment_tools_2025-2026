# Модели данных

## User (Пользователь)

Таблица: `users`

| Колонка | Тип | Описание |
|---|---|---|
| `id` | UUID (PK) | Генерируется автоматически |
| `email` | String (уникальный) | Идентификатор для входа |
| `password_hash` | String | bcrypt-хэш пароля |
| `full_name` | String | Отображаемое имя |
| `role` | String | `employee` (по умолчанию) или другая роль |
| `is_active` | Boolean | Флаг активности аккаунта |
| `reset_code` | String (nullable) | OTP для сброса пароля |
| `reset_code_expires` | DateTime (nullable) | Срок действия OTP |
| `created_at` | DateTime | UTC, устанавливается автоматически |

**Связи:** один `Profile`, много `Project` (как владелец), много `TeamMember`

## Profile (Профиль)

Таблица: `profiles`

| Колонка | Тип | Описание |
|---|---|---|
| `id` | UUID (PK) | Генерируется автоматически |
| `user_id` | UUID (FK → users, уникальный) | Связь один-к-одному с User |
| `bio` | String (nullable) | Биография в свободной форме |
| `experience` | Integer | Лет опыта (≥ 0) |
| `city` | String (nullable) | Местоположение |
| `github_url` | String (nullable) | URL профиля GitHub |

**Связи:** один `User`, много `ProfileSkill`

## ProfileSkill *(связующая таблица)*

Таблица: `profile_skills`

| Колонка | Тип | Описание |
|---|---|---|
| `profile_id` | UUID (PK, FK → profiles) | |
| `skill_id` | UUID (PK, FK → skills) | |
| `level` | String | `beginner` / `mid` / `expert` |

## Skill (Навык)

Таблица: `skills`

| Колонка | Тип | Описание |
|---|---|---|
| `id` | UUID (PK) | Генерируется автоматически |
| `name` | String (уникальный, макс. 100) | Название навыка |

**Связи:** много `ProfileSkill`, много `ProjectSkill`

## Project (Проект)

Таблица: `projects`

| Колонка | Тип | Описание |
|---|---|---|
| `id` | UUID (PK) | Генерируется автоматически |
| `owner_id` | UUID (FK → users) | Создатель |
| `title` | String | Название проекта |
| `description` | String (nullable) | Описание |
| `status` | String | `open` / `in_progress` / `closed` |
| `deadline` | Date (nullable) | Целевая дата завершения |
| `created_at` | DateTime | UTC, устанавливается автоматически |

**Связи:** один `User` (владелец), много `Team`, много `ProjectSkill`

## ProjectSkill *(связующая таблица)*

Таблица: `project_skills`

| Колонка | Тип | Описание |
|---|---|---|
| `project_id` | UUID (PK, FK → projects) | |
| `skill_id` | UUID (PK, FK → skills) | |

## Team (Команда)

Таблица: `teams`

| Колонка | Тип | Описание |
|---|---|---|
| `id` | UUID (PK) | Генерируется автоматически |
| `project_id` | UUID (FK → projects) | Родительский проект |
| `name` | String | Название команды |
| `description` | String (nullable) | Описание |

**Связи:** один `Project`, много `TeamMember`

## TeamMember *(связующая таблица)*

Таблица: `team_members`

| Колонка | Тип | Описание |
|---|---|---|
| `team_id` | UUID (PK, FK → teams) | |
| `user_id` | UUID (PK, FK → users) | |
| `role` | String | `leader` / `member` / `observer` |

## Каскадное удаление

Все внешние ключи используют `CASCADE` при удалении:

- Удаление **User** удаляет его Profile и принадлежащие ему Projects
- Удаление **Project** удаляет его Teams
- Удаление **Team** удаляет строки TeamMember
- Удаление **Profile** или **Project** удаляет связанные записи навыков
