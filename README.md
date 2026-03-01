# 📰 AI News Digest Bot

Бот автоматически собирает новости из мира AI, IT, технологий и стартапов каждый день и отправляет красивый дайджест с эмодзи в Telegram.

## Что делает бот

- Собирает новости с 11 RSS-источников (TechCrunch, The Verge, OpenAI Blog, VentureBeat и др.)
- Суммаризирует через GPT-4o-mini на русском языке
- Отправляет структурированный дайджест в Telegram каждый день в 11:00 по Москве

## Настройка (нужно сделать один раз)

### Шаг 1 — Создать Telegram-бота

1. Открой Telegram, найди @BotFather
2. Напиши `/newbot`, придумай имя и username боту
3. Скопируй токен вида `1234567890:ABCdef...` — это `TELEGRAM_TOKEN`
4. Напиши `/start` своему новому боту
5. Открой в браузере: `https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates`
   - Найди в ответе `"id":` под `"chat"` — это твой `TELEGRAM_CHAT_ID`

### Шаг 2 — Добавить секреты в GitHub

1. Открой репозиторий на GitHub
2. Перейди: **Settings → Secrets and variables → Actions**
3. Нажми **New repository secret** и добавь три секрета:
   - `OPENAI_API_KEY` — твой ключ OpenAI
   - `TELEGRAM_TOKEN` — токен бота от BotFather
   - `TELEGRAM_CHAT_ID` — твой ID чата

### Шаг 3 — Запушить код на GitHub

Просто залей все файлы в репозиторий через Cursor или Git.

### Шаг 4 — Проверить работу

Перейди на GitHub → **Actions** → **Daily AI News Digest** → нажми **Run workflow** для ручного теста.

## Источники новостей

| Тема | Источник |
|------|----------|
| 🤖 AI | OpenAI Blog, Google DeepMind, MIT Technology Review, AI News |
| 💻 Tech/IT | TechCrunch, The Verge, Ars Technica, Wired |
| 🚀 Стартапы | VentureBeat, Hacker News, TechCrunch Startups |
