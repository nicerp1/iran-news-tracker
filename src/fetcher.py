# src/fetcher.py
import feedparser
import json
import time

# فقط چند فید مطمئن
RSS_FEEDS = {
    "bbc_persian": "https://feeds.bbci.co.uk/persian/rss.xml",
    "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "reuters": "https://feeds.reuters.com/reuters/worldNews",
}

# کلمات کلیدی ساده
KEYWORDS = ["iran", "ایران", "war", "جنگ", "gaza", "غزه", "israel", "اسرائیل"]

def is_relevant(title, summary):
    text = (title + " " + summary).lower()
    return any(k.lower() in text for k in KEYWORDS)

def clean_text(html):
    import re
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_all():
    all_news = []
    
    for name, url in RSS_FEEDS.items():
        print(f"📡 در حال دریافت: {name}")
        try:
            feed = feedparser.parse(url)
            print(f"   → {len(feed.entries)} خبر دریافت شد")
            
            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                summary = clean_text(entry.get('summary', ''))
                
                if is_relevant(title, summary):
                    news = {
                        "title_fa": title,
                        "title_en": title,
                        "summary": [summary[:500]],
                        "impact": "در حال بررسی",
                        "tag": "عمومی",
                        "urgency": 5,
                        "sentiment": 0.0,
                        "source": name,
                        "url": entry.get('link', ''),
                        "clean_url": entry.get('link', ''),
                        "image": None,
                        "timestamp": time.time()
                    }
                    all_news.append(news)
                    print(f"   ✓ خبر مرتبط: {title[:50]}...")
                    
        except Exception as e:
            print(f"   ✗ خطا: {e}")
    
    # حذف تکراری
    seen = set()
    unique = []
    for n in all_news:
        if n['url'] not in seen:
            seen.add(n['url'])
            unique.append(n)
    
    print(f"\n📊 جمعاً: {len(unique)} خبر یکتا")
    return unique

if __name__ == "__main__":
    news = fetch_all()
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    print("✅ ذخیره شد!")
