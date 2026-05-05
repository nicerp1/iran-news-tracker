# src/fetcher.py
import feedparser
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any

class NewsFetcher:
    """دریافت‌کننده اخبار از منابع مختلف"""
    
    # فیدهای RSS خبرگزاری‌ها
    RSS_FEEDS = {
        # فارسی
        "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "bbc_persian": "https://feeds.bbci.co.uk/persian/rss.xml",
        "irna": "https://www.irna.ir/rss",
        "mehr": "https://www.mehrnews.com/rss",
        "tasnim": "https://www.tasnimnews.com/rss",
        "isna": "https://www.isna.ir/rss",
        "iranintl": "https://iranintl.com/fa/rss",
        
        # انگلیسی
        "reuters": "https://feeds.reuters.com/reuters/worldNews",
        "washington_post": "https://feeds.washingtonpost.com/rss/world",
        "guardian": "https://www.theguardian.com/world/rss",
        "ap": "https://feeds.apnews.com/apnews/topnews",
        "afp": "https://www.afp.com/rss/en/afp/homepage.xml",
    }
    
    # کلمات کلیدی مرتبط با ایران و جنگ
    IRAN_KEYWORDS = [
        "ایران", "Iran", "تهران", "Tehran", "Tehran's",
        "جنگ", "war", "حمله", "attack", "attacked",
        "تنش", "tension", "escalat", "خاورمیانه", "Middle East",
        "سوریه", "Syria", "عراق", "Iraq", "لبنان", "Lebanon",
        "خلیج فارس", "Persian Gulf", "برجام", "JCPOA", "nuclear",
        "تحریم", "sanction", "نفت", "oil", "crude",
        "سپاه", "IRGC", "پاسدار", "Revolutionary Guard",
        "خامنه‌ای", "Khamenei", "پزشکیان", "Pezeshkian",
        "اسرائیل", "Israel", "Israel's", "Israeli",
        "غزه", "Gaza", "حزب‌الله", "Hezbollah", "Hezbollah's",
        "یمن", "Yemen", "حوثی", "Houthi",
        "آمریکا", "America", "United States", "U.S.", "US",
        "اروپا", "Europe", "European", "UN", "ناتو", "NATO",
        "مذاکره", "negotiat", "دیدار", "meeting",
        "پهپاد", "drone", "موشک", "missile", "rocket",
        "نفتکش", "tanker", "کشتی", "ship",
    ]
    
    def __init__(self):
        self.news_items: List[Dict[str, Any]] = []
    
    def is_relevant(self, text: str) -> bool:
        """بررسی ارتباط خبر با موضوعات مورد نظر"""
        text_lower = text.lower()
        match_count = sum(1 for keyword in self.IRAN_KEYWORDS 
                         if keyword.lower() in text_lower)
        return match_count >= 1
    
    def fetch_feed(self, source_name: str, url: str) -> List[Dict]:
        """دریافت اخبار از یک فید RSS"""
        items = []
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:30]:  # حداکثر ۳۰ خبر از هر منبع
                title = entry.get('title', '')
                summary = self._clean_summary(entry.get('summary', ''))
                content = title + ' ' + summary
                
                # بررسی ارتباط
                if self.is_relevant(content):
                    items.append({
                        "title_fa": self._translate_to_persian(title) if self._is_english(source_name) else title,
                        "title_en": self._translate_to_english(title) if not self._is_english(source_name) else title,
                        "summary": [summary[:800]],
                        "impact": self._analyze_impact(content),
                        "tag": self._classify_tag(content),
                        "urgency": self._calculate_urgency(content),
                        "sentiment": self._analyze_sentiment(content),
                        "source": self._get_source_name(source_name),
                        "url": entry.get('link', ''),
                        "clean_url": self._clean_url(entry.get('link', '')),
                        "image": self._extract_image(entry),
                        "timestamp": time.time()
                    })
        except Exception as e:
            print(f"خطا در دریافت {source_name}: {e}")
        return items
    
    def _is_english(self, source: str) -> bool:
        """آیا منبع انگلیسی است؟"""
        english_sources = ["reuters", "washington_post", "guardian", "ap", "afp"]
        return source in english_sources
    
    def _get_source_name(self, source: str) -> str:
        """نام قابل نمایش منبع"""
        names = {
            "aljazeera": "الجزیره",
            "bbc_persian": "BBC فارسی",
            "irna": "ایرنا",
            "mehr": "مهر",
            "tasnim": "تسنیم",
            "isna": "ایسنا",
            "iranintl": "ایران اینترنشنال",
            "reuters": "رویترز",
            "washington_post": "واشنگتن پست",
            "guardian": "گاردین",
            "ap": "آسوشیتدپرس",
            "afp": "فرانس‌پرس",
        }
        return names.get(source, source)
    
    def _clean_summary(self, html: str) -> str:
        """پاکسازی HTML از خلاصه"""
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'&[a-z]+;', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:1500]
    
    def _translate_to_persian(self, text: str) -> str:
        """ترجمه ساده انگلیسی به فارسی - در عمل از API استفاده کنید"""
        translations = {
            "Iran": "ایران",
            "war": "جنگ",
            "attack": "حمله",
            "nuclear": "هسته‌ای",
            "sanctions": "تحریم",
            "oil": "نفت",
            "Gaza": "غزه",
            "Israel": "اسرائیل",
            "Middle East": "خاورمیانه",
            "U.S.": "آمریکا",
            "United States": "آمریکا",
            "Hezbollah": "حزب‌الله",
            "Houthi": "حوثی",
            "Yemen": "یمن",
            "Syria": "سوریه",
            "Iraq": "عراق",
            "Lebanon": "لبنان",
            "missile": "موشک",
            "drone": "پهپاد",
            "negotiations": "مذاکرات",
            "diplomatic": "دیپلماتیک",
            "tension": "تنش",
            "escalation": "تشدید",
            "troops": "نیروها",
            "military": "نظامی",
            "forces": "نیروها",
            "killed": "کشته",
            "dead": "کشته",
            "wounded": "زخمی",
            "injured": "زخمی",
            "ceasefire": "آتش‌بس",
            "deal": "توافق",
            "agreement": "توافق",
            "summit": "نشست",
            "meeting": "دیدار",
            "talks": "مذاکره",
            "nuclear": "هسته‌ای",
            "uranium": "اورانیوم",
            "atomic": "اتمی",
            "strike": "حمله",
            "bombing": "بمباران",
            "clash": "درگیری",
            "conflict": "درگیری",
            "Reuters": "رویترز",
            "Monday": "دوشنبه",
            "Tuesday": "سه‌شنبه",
            "Wednesday": "چهارشنبه",
            "Thursday": "پنج‌شنبه",
            "Friday": "جمعه",
            "Saturday": "شنبه",
            "Sunday": "یکشنبه",
        }
        result = text
        for eng, fa in translations.items():
            result = re.sub(rf'\b{eng}\b', fa, result, flags=re.IGNORECASE)
        return result
    
    def _translate_to_english(self, text: str) -> str:
        """ترجمه ساده فارسی به انگلیسی"""
        return text  # TODO: پیاده‌سازی واقعی
    
    def _analyze_impact(self, text: str) -> str:
        """تحلیل تأثیر خبر"""
        text_lower = text.lower()
        
        if any(k in text_lower for k in ["جنگ", "حمله", "war", "attack", "strike", "bombing"]):
            return "افزایش تنش نظامی و خطر درگیری گسترده"
        elif any(k in text_lower for k in ["تحریم", "sanction", "محدودیت"]):
            return "تشدید فشار اقتصادی و انزوای بین‌المللی"
        elif any(k in text_lower for k in ["هسته‌ای", "nuclear", "اورانیوم", "uranium"]):
            return "پیامدهای جدی برای برنامه هسته‌ای و مذاکرات"
        elif any(k in text_lower for k in ["دیپلماسی", "مذاکره", "negotiat", "توافق", "agreement"]):
            return "احتمال بهبود روابط و کاهش تنش‌ها"
        elif any(k in text_lower for k in ["آتش‌بس", "ceasefire", "پایان"]):
            return "احتمال کاهش بحران و ثبات منطقه‌ای"
        elif any(k in text_lower for k in ["نفت", "oil", "انرژی", "energy"]):
            return "تأثیر مستقیم بر بازار نفت و اقتصاد جهانی"
        elif any(k in text_lower for k in ["پهپاد", "drone", "موشک", "missile"]):
            return "تشدید رقابت تسلیحاتی منطقه‌ای"
        return "تحولات قابل پیگیری در وضعیت منطقه"
    
    def _classify_tag(self, text: str) -> str:
        """طبقه‌بندی خبر"""
        text_lower = text.lower()
        
        if any(k in text_lower for k in ["جنگ", "حمله", "war", "attack", "strike", "military", "نظامی", "درگیری"]):
            return "نظامی"
        elif any(k in text_lower for k in ["تحریم", "sanction", "economy", "اقتصاد", "نفت", "oil"]):
            return "تحریم_فشار"
        elif any(k in text_lower for k in ["دیپلماسی", "مذاکره", "negotiat", "برجام", "توافق", "دیدار"]):
            return "دیپلماسی"
        elif any(k in text_lower for k in ["هسته‌ای", "nuclear", "uranium"]):
            return "هسته‌ای"
        elif any(k in text_lower for k in ["پهپاد", "drone", "موشک", "missile", "تسلیحات", "weapon"]):
            return "تسلیحاتی"
        return "عمومی"
    
    def _calculate_urgency(self, title: str, summary: str) -> int:
        """محاسبه فوریت (۱-۱۰)"""
        text = (title + " " + summary).lower()
        
        urgent_words = {
            "فوری": 3, "urgent": 3, "breaking": 4, "بحران": 3, "crisis": 3,
            "جنگ": 3, "war": 3, "حمله": 3, "attack": 3, "strike": 3,
            "کشته": 2, "killed": 2, "dead": 2, "زخمی": 2, "wounded": 2,
            "انفجار": 2, "explosion": 2, "بمب": 2, "bomb": 2,
            "هشدار": 2, "warning": 2, "تهدید": 2, "threat": 2,
            "آتش‌بس": 1, "ceasefire": 1, "توافق": 1, "agreement": 1,
        }
        
        score = 5  # پایه
        for word, value in urgent_words.items():
            if word in text:
                score += value
        
        return min(10, max(1, score))
    
    def _analyze_sentiment(self, text: str) -> float:
        """تحلیل احساسات (-1 تا 1)"""
        positive = [
            "پیشرفت", "موفقیت", "دیدار", "توافق", "آتش‌بس", "صلح",
            "progress", "success", "agreement", "peace", "ceasefire",
            "meeting", "diplomatic", "cooperation", "support", "deal"
        ]
        negative = [
            "جنگ", "حمله", "بحران", "تهدید", "محکوم", "کشته", "زخمی",
            "war", "attack", "crisis", "threat", "killed", "wounded",
            "tension", "escalation", "sanction", "condemn", "conflict",
            "bombing", "strike", "dead", "injured", "violence"
        ]
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        
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
        if hasattr(entry, 'media_content') and entry.media_content:
            return entry.media_content[0].get('url', '')
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image/'):
                    return enc.get('url', '')
        if hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    return link.get('href', '')
        return None
    
    def fetch_all(self) -> List[Dict[str, Any]]:
        """دریافت همه اخبار"""
        all_news = []
        for source_name, url in self.RSS_FEEDS.items():
            items = self.fetch_feed(source_name, url)
            all_news.extend(items)
            print(f"✓ {source_name}: {len(items)} خبر مرتبط")
        
        # حذف تکراری‌ها بر اساس URL
        seen_urls = set()
        unique_news = []
        for item in all_news:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                unique_news.append(item)
        
        # مرتب‌سازی بر اساس زمان
        unique_news.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return unique_news


def main():
    fetcher = NewsFetcher()
    news = fetcher.fetch_all()
    
    output_path = "data/news.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ {len(news)} خبر ذخیره شد")


if __name__ == "__main__":
    main()
