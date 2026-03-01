import os
import feedparser
import requests
from datetime import datetime, timezone, timedelta
from openai import OpenAI

# ── Настройки ──────────────────────────────────────────────────────────────
OPENAI_API_KEY  = os.environ["OPENAI_API_KEY"]
TELEGRAM_TOKEN  = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ── RSS-источники (AI / IT / Tech / Startups) ─────────────────────────────
RSS_FEEDS = [
    # AI
    ("OpenAI Blog",            "https://openai.com/blog/rss/"),
    ("Google DeepMind",        "https://deepmind.google/blog/rss.xml"),
    ("MIT Technology Review",  "https://www.technologyreview.com/feed/"),
    ("AI News (artificialintelligence-news)", "https://www.artificialintelligence-news.com/feed/"),
    # Tech / IT
    ("TechCrunch",             "https://techcrunch.com/feed/"),
    ("The Verge",              "https://www.theverge.com/rss/index.xml"),
    ("Ars Technica",           "https://feeds.arstechnica.com/arstechnica/index"),
    ("Wired",                  "https://www.wired.com/feed/rss"),
    # Startups
    ("VentureBeat",            "https://venturebeat.com/feed/"),
    ("Hacker News Top",        "https://news.ycombinator.com/rss"),
    ("TechCrunch Startups",    "https://techcrunch.com/category/startups/feed/"),
]

MAX_ARTICLES_PER_FEED = 5   # сколько статей берём из каждого источника
MAX_TOTAL_ARTICLES    = 40  # потолок для GPT-запроса


def fetch_recent_articles() -> list[dict]:
    """Собирает статьи за последние 24 часа со всех RSS-лент."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    articles = []

    for source_name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= MAX_ARTICLES_PER_FEED:
                    break

                # Пробуем определить дату публикации
                pub = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    pub = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

                # Если дата неизвестна — берём статью (лучше лишнее, чем ничего)
                if pub is None or pub >= cutoff:
                    articles.append({
                        "source": source_name,
                        "title":  entry.get("title", "Без заголовка"),
                        "link":   entry.get("link", ""),
                        "summary": entry.get("summary", "")[:300],
                    })
                    count += 1
        except Exception as e:
            print(f"[WARN] {source_name}: {e}")

    return articles[:MAX_TOTAL_ARTICLES]


def summarize_with_gpt(articles: list[dict]) -> str:
    """Отправляет список новостей в GPT и получает красивый дайджест на русском."""
    if not articles:
        return "📭 Сегодня свежих новостей не найдено."

    # Формируем компактный список для GPT
    news_text = ""
    for i, a in enumerate(articles, 1):
        news_text += f"{i}. [{a['source']}] {a['title']}\n"
        if a["summary"]:
            news_text += f"   {a['summary'][:200]}\n"
        news_text += f"   🔗 {a['link']}\n\n"

    prompt = f"""Ты — редактор технологического дайджеста. 
Тебе дан список новостей из мира AI, IT, технологий и стартапов за последние 24 часа.

Сделай структурированный дайджест на РУССКОМ языке:
1. Раздели новости на тематические блоки: 🤖 Искусственный интеллект, 💻 Технологии и IT, 🚀 Стартапы и бизнес, 🌐 Другое
2. В каждом блоке — краткое (1-2 предложения) описание самых важных новостей с эмодзи
3. Оставляй ссылку на источник для каждой новости
4. В конце — короткий вывод "🔥 Главное за сегодня" (2-3 самые важные новости)
5. Используй много эмодзи, чтобы было интересно читать
6. Максимум 4000 символов (ограничение Telegram)

Вот новости:
{news_text}"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.7,
    )
    return response.choices[0].message.content


def send_telegram_message(text: str) -> None:
    """Отправляет сообщение в Telegram. Разбивает, если длиннее 4096 символов."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    chunk_size = 4000

    # Заголовок дайджеста
    date_str = datetime.now().strftime("%d.%m.%Y")
    header = f"📰 Технодайджест {date_str}\n\n"

    full_text = header + text

    # Разбиваем на части, если слишком длинное
    chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]

    for chunk in chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "disable_web_page_preview": True,
        }
        resp = requests.post(url, json=payload, timeout=30)
        if not resp.ok:
            print(f"[ERROR] Telegram response: {resp.status_code} — {resp.text}")
        resp.raise_for_status()


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Собираю новости...")
    articles = fetch_recent_articles()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Найдено статей: {len(articles)}")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Отправляю в GPT для суммаризации...")
    digest = summarize_with_gpt(articles)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Отправляю в Telegram...")
    send_telegram_message(digest)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Готово! Дайджест отправлен.")


if __name__ == "__main__":
    main()
