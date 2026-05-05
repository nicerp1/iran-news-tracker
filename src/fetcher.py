# src/fetcher.py
import feedparser
import json
import time
from datetime import datetime
from typing import List, Dict, Any

class NewsFetcher:
    """دریافت‌کننده اخبار از منابع مختلف"""
    
    # فیدهای RSS خبرگزاری‌ها
    RSS_FEEDS = {
        "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "bbc_persian": "https://feeds.bbci.co.uk/persian/rss.xml",
        "irna": "https://www.irna.ir/rss",
        "mehr": "https://www.mehrnews.com/rss",
        "tasnim": "https://www.tasnimnews.com/rss",
        "isna": "https://www.isna.ir/rss",
        "reuters": "https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best",
    }
    
    # کلمات کلیدی مرتبط با ایران و جنگ
    IRAN_KEYWORDS = [
        "ایران", "Iran", "تهران", "Tehran",
        "جنگ", "war", "حمله", "attack",
        "تنش", "tension", "خاورمیانه", "Middle East",
        "سوریه", "Syria", "عراق", "Iraq",
        "خلیج فارس", "Persian Gulf", "برجام", "JCPOA",
        "تحریم", "sanction", "نفت", "oil"
    ]
    
    def __init__(self):
        self.news_items: List[Dict[str, Any]] = []
    
    def is_relevant(self, text: str) -> bool:
        """بررسی ارتباط خبر با موضوعات مورد نظر"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.IRAN_KEYWORDS)
    
    def fetch_feed(self, source_name: str, url: str) -> List[Dict]:
        """دریافت اخبار از یک فید RSS"""
        items = []
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:  # حداکثر ۲۰ خبر از هر منبع
                title = entry.get('title', '')
                summary = self._clean_summary(entry.get('summary', ''))
                
                # بررسی ارتباط
                if self.is_relevant(title + ' ' + summary):
                    items.append({
                        "title_fa": title,
                        "title_en": self._translate_to_english(title),
                        "summary": [summary[:500]],  # خلاصه اولیه
                        "impact": self._analyze_impact(summary),
                        "tag": self._classify_tag(title, summary),
                        "urgency": self._calculate_urgency(title, summary),
                        "sentiment": self._analyze_sentiment(summary),
                        "source": source_name,
                        "url": entry.get('link', ''),
                        "clean_url": self._clean_url(entry.get('link', '')),
                        "image": self._extract_image(entry),
                        "timestamp": time.time()
                    })
        except Exception as e:
            print(f"خطا در دریافت {source_name}: {e}")
        return items
    
    def _clean_summary(self, html: str) -> str:
        """پاکسازی HTML از خلاصه"""
        import re
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:1000]
    
    def _translate_to_english(self, text: str) -> str:
        """ترجمه ساده - در عمل از API ترجمه استفاده کنید"""
        return text  # TODO: پیاده‌سازی ترجمه واقعی
    
    def _analyze_impact(self, text: str) -> str:
        """تحلیل تأثیر خبر"""
        impact_keywords = {
            "جنگ": "افزایش تنش نظامی",
            "تحریم": "فشار اقتصادی",
            "دیپلماسی": "تغییر در روابط بین‌الملل",
            "نفت": "تأثیر بر بازار انرژی",
        }
        for key, impact in impact_keywords.items():
            if key in text:
                return impact
        return "تأثیر متوسط"
    
    def _classify_tag(self, title: str, summary: str) -> str:
        """طبقه‌بندی خبر"""
        text = title + " " + summary
        if any(k in text for k in ["جنگ", "حمله", "military", "war"]):
            return "نظامی"
        elif any(k in text for k in ["تحریم", "economy", "نفت"]):
            return "تحریم_فشار"
        elif any(k in text for k in ["دیپلماسی", "مذاکره", "برجام"]):
            return "دیپلماسی"
        return "عمومی"
    
    def _calculate_urgency(self, title: str, summary: str) -> int:
        """محاسبه فوریت (۱-۱۰)"""
        urgent_words = ["فوری", "urgent", "breaking", "بحران", "جنگ"]
        text = title + " " + summary
        count = sum(1 for w in urgent_words if w in text.lower())
        return min(10, 5 + count * 2)
    
    def _analyze_sentiment(self, text: str) -> float:
        """تحلیل احساسات (-1 تا 1)"""
        positive = ["پیشرفت", "موفقیت", "دیدار", "توافق"]
        negative = ["جنگ", "حمله", "بحران", "تهدید", "محکوم"]
        
        pos_count = sum(1 for w in positive if w in text)
        neg_count = sum(1 for w in negative if w in text)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return round((pos_count - neg_count) / total, 2)
    
    def _clean_url(self, url: str) -> str:
        """پاکسازی URL از پارامترهای اضافی"""
        if "news.google.com" in url and "?oc=" in url:
            return url.split("?oc=")[0]
        return url
    
    def _extract_image(self, entry) -> str:
        """استخراج تصویر از خبر"""
        # بررسی media_content
        if hasattr(entry, 'media_content') and entry.media_content:
            return entry.media_content[0].get('url', '')
        # بررسی enclosures
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image/'):
                    return enc.get('url', '')
        return None
    
    def fetch_all(self) -> List[Dict[str, Any]]:
        """دریافت همه اخبار"""
        all_news = []
        for source_name, url in self.RSS_FEEDS.items():
            items = self.fetch_feed(source_name, url)
            all_news.extend(items)
            print(f"{source_name}: {len(items)} خبر مرتبط")
        
        # حذف تکراری‌ها بر اساس URL
        seen_urls = set()
        unique_news = []
        for item in all_news:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                unique_news.append(item)
        
        # مرتب‌سازی بر اساس زمان (جدیدترین اول)
        unique_news.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return unique_news


def main():
    fetcher = NewsFetcher()
    news = fetcher.fetch_all()
    
    # ذخیره در فایل JSON
    output_path = "data/news.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ {len(news)} خبر ذخیره شد در {output_path}")


if __name__ == "__main__":
    main()
