# Turin Grad Hub - Backend API

Полная реализация Flask backend для системы управления выпускниками Turin Grad Hub.

## 🚀 Возможности

### ✅ Реализованные функции:

- **Аутентификация и авторизация**
  - Регистрация пользователей с проверкой email, телефона и студенческого ID
  - Вход по email, телефону или студенческому ID
  - JWT токены для доступа
  - Сброс пароля через email
  - SMS верификация (базовая структура)

- **Система верификации**
  - ✅ Email верификация
  - ✅ Административное одобрение пользователей
  - Ведение журнала активности

- **Управление пользователями (Админ)**
  - CRUD операции для пользователей
  - Верификация и блокировка аккаунтов
  - Поиск и фильтрация пользователей
  - Журнал активности системы

- **Профили пользователей**
  - Просмотр и редактирование профиля
  - Управление опытом работы
  - Образовательные цели

- **Справочные данные**
  - Факультеты и направления
  - Компании-работодатели

- **Поиск**
  - Глобальный поиск по системе
  - Расширенный поиск студентов

- **Уведомления**
  - Система уведомлений пользователей
  - Отметка прочтения

## 📁 Структура проекта

```
turin_grad_backend/
├── app.py                 # Главный файл приложения
├── requirements.txt       # Зависимости Python
├── .env.example          # Пример переменных окружения
├── create_admin.py       # Скрипт создания администратора
├── create_sample_data.py # Скрипт создания тестовых данных
├── app/
│   ├── database.py       # Модели базы данных
│   ├── auth/            # Аутентификация
│   ├── admin/           # Административные функции
│   ├── profile/         # Управление профилями
│   ├── students/        # Функции для студентов
│   ├── teachers/        # Функции для преподавателей
│   ├── notifications/   # Система уведомлений
│   ├── dictionaries/    # Справочные данные
│   ├── search/          # Поиск
│   ├── system/          # Системные endpoints
│   └── utils/           # Вспомогательные функции
```

## 🛠 Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Создание администратора
```bash
python create_admin.py
```

### 4. Создание тестовых данных
```bash
python create_sample_data.py
```

### 5. Запуск приложения
```bash
python app.py
```

Приложение будет доступно по адресу: http://127.0.0.1:5000

## 📚 API Endpoints

### Системные
- `GET /api/health` - Проверка состояния системы
- `GET /api/info` - Информация о API
- `GET /api/config` - Конфигурация для клиента

### Аутентификация
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход
- `POST /api/auth/logout` - Выход
- `POST /api/auth/refresh` - Обновление токена
- `POST /api/auth/forgot-password` - Запрос сброса пароля
- `POST /api/auth/reset-password` - Сброс пароля
- `POST /api/auth/send-sms` - Отправка SMS кода
- `POST /api/auth/verify-sms` - Верификация SMS
- `POST /api/auth/verify-email` - Верификация email

### Администрирование
- `GET /api/admin/users` - Список пользователей
- `GET /api/admin/users/:id` - Информация о пользователе
- `POST /api/admin/users` - Создание пользователя
- `PUT /api/admin/users/:id` - Обновление пользователя
- `DELETE /api/admin/users/:id` - Удаление пользователя
- `PATCH /api/admin/users/:id/verify` - Верификация пользователя
- `PATCH /api/admin/users/:id/block` - Блокировка пользователя
- `GET /api/admin/activity-logs` - Журнал активности

### Профиль
- `GET /api/profile` - Получить профиль
- `PUT /api/profile` - Обновить профиль
- `GET /api/profile/work-experience` - Опыт работы
- `POST /api/profile/work-experience` - Добавить опыт работы
- `GET /api/profile/education-goals` - Образовательные цели
- `POST /api/profile/education-goals` - Добавить цель

### Справочники
- `GET /api/dictionaries/faculties` - Факультеты
- `GET /api/dictionaries/directions` - Направления
- `GET /api/dictionaries/companies` - Компании
- `POST /api/dictionaries/companies` - Добавить компанию

### Поиск
- `GET /api/search` - Глобальный поиск
- `GET /api/search/students` - Поиск студентов

### Уведомления
- `GET /api/notifications` - Список уведомлений
- `PATCH /api/notifications/:id/read` - Отметить как прочитанное
- `PATCH /api/notifications/mark-all-read` - Отметить все как прочитанные

### Студенты и преподаватели
- `GET /api/students` - Список студентов
- `GET /api/teachers` - Список преподавателей

## 🔐 Авторизация

Система использует JWT токены. Для доступа к защищенным endpoints необходимо передать токен в заголовке:

```
Authorization: Bearer <token>
```

## 🏗 Роли пользователей

- **Admin** - полный доступ ко всем функциям
- **Teacher** - управление своими студентами и отчеты
- **Student** - просмотр профиля, преподавателей и однокурсников

## 🧪 Тестирование

### Тестовые учетные записи:

**Администратор:**
- Email: `admin@ttpu.uz`
- Пароль: `admin123`

**Преподаватели:**
- Email: `d.karimov@ttpu.uz` / Пароль: `password123`
- Email: `s.nazarova@ttpu.uz` / Пароль: `password123`

**Студенты:**
- Email: `a.rahmonov@student.ttpu.uz` / Пароль: `password123`
- Email: `m.usmanova@student.ttpu.uz` / Пароль: `password123`
- Email: `b.tursunov@student.ttpu.uz` / Пароль: `password123` (неверифицирован)

### Примеры запросов:

```bash
# Вход в систему
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "admin@ttpu.uz", "password": "admin123"}'

# Получение профиля
curl -X GET http://127.0.0.1:5000/api/profile \
  -H "Authorization: Bearer <token>"

# Верификация пользователя (админ)
curl -X PATCH http://127.0.0.1:5000/api/admin/users/<user_id>/verify \
  -H "Authorization: Bearer <admin_token>"
```

## 🗃 База данных

Проект использует SQLite для разработки. Основные таблицы:

- **users** - Пользователи системы
- **work_experiences** - Опыт работы
- **education_goals** - Образовательные цели
- **teacher_students** - Связи преподаватель-студент
- **activity_logs** - Журнал активности
- **notifications** - Уведомления
- **companies** - Компании
- **faculties** - Факультеты
- **directions** - Направления обучения

## 📝 Статус реализации

### ✅ Реализовано (основные функции):
- Аутентификация и авторизация
- Система ролей
- Административное управление пользователями
- Email верификация
- Административное одобрение
- Профили пользователей
- Справочные данные
- Поиск
- Уведомления
- Журнал активности

### 🔄 В разработке / Планируется:
- Загрузка файлов (аватары, CV, дипломы)
- Аналитика и отчеты
- Импорт/экспорт данных
- Расширенная система уведомлений
- Email templates
- Полная интеграция SMS
- API для мобильного приложения

## 🔧 Технологии

- **Flask** 3.0.0 - Web framework
- **SQLAlchemy** 2.0.23 - ORM
- **Flask-JWT-Extended** 4.6.0 - JWT authentication
- **Flask-Mail** 0.9.1 - Email functionality
- **Flask-CORS** 4.0.0 - CORS support
- **bcrypt** 4.1.2 - Password hashing
- **phonenumbers** 8.13.26 - Phone validation
- **pandas** 2.1.4 - Data processing
- **openpyxl** 3.1.2 - Excel support

## 🤝 Разработка

Проект следует принципам:
- RESTful API дизайн
- Роль-ориентированный доступ
- Комплексная валидация данных
- Структурированная обработка ошибок
- Логирование активности
- Модульная архитектура

Общее количество реализованных endpoints: **40+** из запланированных 87.

Основа системы готова и полностью функциональна для разработки и тестирования.