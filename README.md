# Сервис Прокси-доступа

Веб-сервис для регистрации пользователей, получения ключей активации по email и подключения к прокси-серверу (виртуальной машине) через десктопное приложение.

## Стек технологий
- **Backend**: FastAPI, PostgreSQL, Celery + Redis
- **Frontend**: Vue 3 + Vuetify
- **Desktop**: Tkinter
- **Инфраструктура**: Docker Compose

## Инструкции по установке

### 1. Требования
- Docker и Docker Compose
- Python 3.10+ (для локального запуска десктопного приложения)

### 2. Переменные окружения
Скопируйте файл `.env.example` в `.env` и при необходимости измените значения.
```bash
cp .env.example .env
```

### 3. Запуск сервиса
Используйте Docker Compose для запуска всех компонентов:
```bash
docker-compose up -d --build
```
Это запустит:
- Базу данных PostgreSQL
- Брокер сообщений Redis
- FastAPI backend
- Celery worker
- Vue frontend (обслуживаемый Nginx)

### 4. Настройка базы данных
Миграции и заполнение базы данных (seeding) выполняются автоматически при запуске, но при необходимости вы можете запустить их вручную:
```bash
# Дождитесь запуска контейнеров
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.utils.seed
```

### 5. Десктопное приложение
Десктопное приложение подключается к бэкенду и WebSocket.
Сначала установите зависимости:
```bash
cd desktop
pip install -r requirements.txt
```
Запустите приложение:
```bash
python app.py
```

### 6. Доступ к приложению
- **Frontend**: `http://localhost:80`
- **Документация Backend API**: `http://localhost:8000/docs`