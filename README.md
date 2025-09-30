# 💰 Finance Tracker - Система отслеживания личных финансов от Ахитео

## 🚀 Быстрый старт

### 1. Подготовка

Создайте Telegram бота через @BotFather и получите токен.

### 2. Настройка

Создайте файл `.env` в корне проекта:

BOT_TOKEN=ваш_токен_от_BotFather


### 3. Запуск

Одной командой запускаем весь проект:

docker-compose up --build


Или в фоновом режиме:

docker-compose up -d --build


### 4. Проверка работы

- 🤖 Telegram бот: Найдите своего бота в Telegram и отправьте `/start`
- 🌐 Backend API: http://localhost:8000/docs
- 📊 Dashboard: http://localhost:8050

## 📱 Использование бота

### Основные команды:
- `/start` - Начать работу
- `/expense` или кнопка "💸 Добавить расход"
- `/income` или кнопка "💵 Добавить доход"
- `/stats` или кнопка "📊 Статистика"
- `/balance` или кнопка "💼 Баланс"
- `/report` или кнопка "📈 Дашборд"

### Процесс добавления расхода:
1. Нажмите "💸 Добавить расход"
2. Введите сумму (например: 500)
3. Выберите категорию из предложенных
4. Добавьте описание или пропустите
5. ✅ Готово!

## 📊 Dashboard

Dashboard автоматически обновляется каждые 30 секунд и включает:

- 📊 Pie Chart - распределение по категориям
- 📈 Line Chart - дневная динамика
- 📉 Area Chart - накопительные расходы
- 🫧 Bubble Chart - частота vs сумма
- ☀️ Sunburst - иерархия расходов
- 🗺️ Treemap - карта категорий
- 🔥 Heatmap - тепловая карта активности
- 📦 Box Plot - распределение сумм
- 🎻 Violin Plot - плотность распределения
- 🎯 Funnel Chart - топовые категории
- 📅 Monthly Trend - месячные тренды
- 📊 Bar Chart - сравнение категорий

## 🛠️ Управление

### Остановка:
docker-compose down


### Перезапуск:
docker-compose restart


### Просмотр логов:
docker-compose logs -f


### Логи отдельного сервиса:
docker-compose logs -f bot
docker-compose logs -f backend
docker-compose logs -f dashboard


## 🏗️ Архитектура

┌─────────────┐ <br>
│ Telegram Bot│ <br>
│ (aiogram)   │ <br>
└──────┬──────┘ <br>
│
▼
┌─────────────┐ ┌──────────────┐
│ Backend │◄────►│ PostgreSQL │
│ (FastAPI) │ │ Database │
└──────┬──────┘ └──────────────┘
│
▼
┌─────────────┐
│ Dashboard │
│ (Plotly Dash│
└─────────────┘

## 💡 Особенности

✅ Полностью асинхронный Telegram бот
✅ RESTful API с автодокументацией
✅ Адаптивный dashboard для мобильных и ПК
✅ Автоматическое определение даты
✅ Интуитивные кнопки с эмодзи
✅ 12+ типов графиков
✅ Real-time обновление данных
✅ Docker-контейнеризация
✅ Запуск одной командой

## 📝 Категории расходов

- 🍔 Еда
- 🚗 Транспорт
- 🏠 Жилье
- 🎬 Развлечения
- 👕 Одежда
- 💊 Здоровье
- 📚 Образование
- 🎁 Подарки
- 💰 Другое

## 🔧 Технологии

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Bot**: aiogram 3.x (асинхронный)
- **Dashboard**: Plotly Dash + Pandas
- **Infrastructure**: Docker + Docker Compose
🎯 Запуск проекта
После создания всех файлов выполните:


# 1. Создайте .env файл с вашим токеном бота
echo "BOT_TOKEN=your_bot_token_here" > .env

# 2. Запустите весь проект одной командой
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build