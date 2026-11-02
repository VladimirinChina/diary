# Личный дневник

Веб-приложение для ведения личного дневника на Django.

## Возможности

- регистрация, вход и выход пользователей
- создание, редактирование и удаление записей (только своих)
- список записей с пагинацией и подробный просмотр
- поиск по заголовку и содержимому
- адаптивный интерфейс на Bootstrap 5
- управление данными через админку Django
- выбор настроения для записи и фильтр по настроению

## Технологии

Python 3.11+, Django, PostgreSQL, Bootstrap 5, Docker, Docker Compose.

## Структура проекта

- `config/` — настройки проекта и корневые маршруты
- `users/` — регистрация, вход, выход
- `entries/` — модель записи, формы, представления, шаблоны
- `templates/` — базовый шаблон и шаблоны аутентификации
- `Dockerfile`, `docker-compose.yaml` — контейнеризация
- `.env.example` — пример переменных окружения

## Запуск в Docker

1. Клонировать репозиторий и перейти в папку проекта.
2. Создать файл окружения: `cp .env.example .env`
3. В `.env` указать `POSTGRES_HOST=db` (для docker compose значение
   задаётся автоматически) и свой `SECRET_KEY`.
4. Запустить: `docker compose up --build`
5. Создать администратора:
   `docker compose exec web python manage.py createsuperuser`
6. Открыть http://localhost:8000 (админка: http://localhost:8000/admin/).

## Локальный запуск без Docker

1. Установить Poetry и зависимости: `poetry install`
2. Поднять PostgreSQL и прописать доступы в `.env`.
3. Применить миграции: `poetry run python manage.py migrate`
4. Запустить: `poetry run python manage.py runserver`

## Тесты и качество кода

- Тесты: `docker compose exec web python manage.py test`
- Стиль: `poetry run flake8 --max-line-length=100 --exclude=migrations .`
- Типы: `poetry run mypy .`
- CI: GitHub Actions (`.github/workflows/ci.yml`) запускает flake8, mypy, тесты и сборку Docker-образа при каждом push и Pull Request.

Перед запуском создай файл окружения: `cp .env.example .env` (переменная `SECRET_KEY` обязательна).

## Права доступа

Все страницы записей доступны только авторизованным пользователям.
Пользователь видит, редактирует и удаляет только свои записи.