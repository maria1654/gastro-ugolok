# Гастро-уголок

Добро пожаловать в **Гастро-уголок** — веб-сайт, посвященный рецептам из различных фильмов, мультфильмов и аниме! Здесь вы найдете пошаговые инструкции по приготовлению блюд, которые вы видели на экране, и сможете окунуться в мир кулинарных приключений вместе с вашими любимыми персонажами.

## О проекте

**Гастро-уголок** — это веб-приложение, разработанное с использованием **FastAPI** для бэкенда и **Jinja2** для рендеринга HTML-шаблонов. Проект позволяет пользователям:

- Просматривать каталог рецептов из разных фильмов, мультфильмов и аниме.
- Регистрироваться и входить в систему для сохранения избранных рецептов.
- Получать случайный рецепт для вдохновения.
- Делиться отзывами и комментариями.

## Функциональность

- **Каталог рецептов**: Просматривайте рецепты по категориям или с помощью поиска.
- **Случайный рецепт**: Получайте случайный рецепт одним нажатием.
- **Личный кабинет**: Регистрация и авторизация пользователей для доступа к дополнительным функциям.

## Технологии

- **Backend**: FastAPI
- **Frontend**: HTML, CSS, Jinja2 Templates
- **База данных**: SQLite
- **Аутентификация**: SessionMiddleware, Passlib для хеширования паролей
- **Деплоймент**: Uvicorn

## Установка и запуск

### Предварительные требования

- Python 3.7 или выше
- Git (для клонирования репозитория)

### Шаги установки

1. **Клонирование репозитория**

   ```bash
   git clone https://github.com/yourusername/gastro-ugolok.git
   cd gastro-ugolok
   ```

2. **Создание и активации виртуального окружения**

   ```bash
   python3 -m venv venv
   # Для Windows
   venv\Scripts\activate
   # Для Linux/MacOS
   source venv/bin/activate
   ```

3. **Установка зависимостей**

   ```bash
   pip install -r requirements.txt
   ```

4. **Настройка переменных окружения**

   Создайте файл `.env` в корневой директории и добавьте следующие переменные:

   ```ini
   SESSION_SECRET_KEY=your_session_secret_key
   SECRET_KEY=your_jwt_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

   Замените `your_session_secret_key` и `your_jwt_secret_key` на ваши собственные секретные ключи.

5. **Запуск приложения**

   ```bash
   uvicorn app.main:app --reload
   ```

   Приложение будет доступно по адресу `http://127.0.0.1:8000`.

## Использование

- Перейдите на `http://127.0.0.1:8000` в вашем браузере.
- Зарегистрируйтесь или войдите в систему для доступа к личному кабинету.
- Просматривайте рецепты в каталоге или получите случайный рецепт.
- Настройте свои предпочтения по использованию файлов cookie.

## Структура проекта

```
gastro-ugolok/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth_router.py
│   │   └── main_router.py
│   └── templates/
│       └── ... (HTML-шаблоны)
├── static/
│   └── ... (CSS, изображения)
├── .env.example
├── db.py
├── requirements.txt
└── README.md
```

## Вклад в проект

Мы рады любому вкладу в развитие **Гастро-уголка**! Если у вас есть идеи по улучшению или вы нашли ошибку, пожалуйста:

1. Форкните репозиторий.
2. Создайте новую ветку для вашей функции (`git checkout -b feature/NewFeature`).
3. Сделайте коммит ваших изменений (`git commit -m 'Add some feature'`).
4. Запушьте ветку (`git push origin feature/NewFeature`).
5. Создайте Pull Request.

## Лицензия

Этот проект лицензирован под лицензией MIT — подробности см. в файле [LICENSE](LICENSE).

## Контакты

- **GitHub**: [maria1654](https://github.com/maria1654)
