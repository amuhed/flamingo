"""News sources, search keywords, and diaspora city definitions."""

# Albanian media RSS feeds
ALBANIAN_FEEDS = [
    {"name": "Exit News (EN)", "url": "https://exit.al/en/feed/", "lang": "en", "country": "AL"},
    {"name": "Exit News (SQ)", "url": "https://exit.al/feed/", "lang": "sq", "country": "AL"},
    {"name": "Reporter.al", "url": "https://reporter.al/feed/", "lang": "sq", "country": "AL"},
    {"name": "Shqiptarja", "url": "https://shqiptarja.com/rss", "lang": "sq", "country": "AL"},
    {"name": "Top Channel", "url": "https://top-channel.tv/feed/", "lang": "sq", "country": "AL"},
    {"name": "Panorama", "url": "https://www.panorama.com.al/feed/", "lang": "sq", "country": "AL"},
    {"name": "Gazeta Tema", "url": "https://www.gazetatema.net/feed/", "lang": "sq", "country": "AL"},
    {"name": "Albanian Daily News", "url": "https://albaniandailynews.com/feed", "lang": "en", "country": "AL"},
    {"name": "Balkanweb", "url": "https://www.balkanweb.com/feed/", "lang": "sq", "country": "AL"},
]

# International media RSS feeds covering the Balkans
INTERNATIONAL_FEEDS = [
    {"name": "Balkan Insight", "url": "https://balkaninsight.com/feed/", "lang": "en", "country": "INT"},
    {"name": "DW Albanian", "url": "https://rss.dw.com/xml/rss-sq-all", "lang": "sq", "country": "DE"},
    {"name": "DW English", "url": "https://rss.dw.com/xml/rss-en-world", "lang": "en", "country": "DE"},
    {"name": "Euronews Albanian", "url": "https://sq.euronews.com/rss", "lang": "sq", "country": "INT"},
    {"name": "BBC News", "url": "https://feeds.bbci.co.uk/news/world/europe/rss.xml", "lang": "en", "country": "GB"},
    {"name": "Reuters World", "url": "https://www.reutersagency.com/feed/", "lang": "en", "country": "INT"},
    {"name": "VOA Albanian", "url": "https://www.zeriamerikes.com/api/feed", "lang": "sq", "country": "US"},
]

# Google News RSS search queries (multi-language)
GOOGLE_NEWS_SEARCHES = [
    # English
    {"query": "Albania protests 2026", "lang": "en", "hl": "en"},
    {"query": "Albanian diaspora protests", "lang": "en", "hl": "en"},
    {"query": "Albania opposition protests rally", "lang": "en", "hl": "en"},
    # Albanian
    {"query": "protesta Shqiperi 2026", "lang": "sq", "hl": "sq"},
    {"query": "protesta diaspora shqiptare", "lang": "sq", "hl": "sq"},
    {"query": "protesta opozita Tirana", "lang": "sq", "hl": "sq"},
    # Italian
    {"query": "proteste Albania 2026", "lang": "it", "hl": "it"},
    {"query": "diaspora albanese proteste", "lang": "it", "hl": "it"},
    # Greek
    {"query": "Αλβανία διαδηλώσεις 2026", "lang": "el", "hl": "el"},
    {"query": "αλβανική διασπορά διαμαρτυρίες", "lang": "el", "hl": "el"},
    # German
    {"query": "Albanien Proteste 2026", "lang": "de", "hl": "de"},
    {"query": "albanische Diaspora Proteste", "lang": "de", "hl": "de"},
]

# Keywords for filtering articles (lowercase)
FILTER_KEYWORDS = {
    "en": ["protest", "rally", "demonstration", "opposition", "albania", "tirana", "diaspora",
           "unrest", "march", "dissent", "crackdown", "tear gas", "riot"],
    "sq": ["protesta", "proteste", "tubim", "demonstratë", "opozita", "opozitë", "marshim",
           "diaspora", "diasporë", "shqipëri", "tiranë", "revoltë", "gaz lotsjellës"],
    "it": ["protesta", "proteste", "manifestazione", "albania", "opposizione", "diaspora"],
    "el": ["διαδήλωση", "διαμαρτυρία", "αλβανία", "διασπορά", "αντιπολίτευση"],
    "de": ["protest", "demonstration", "albanien", "opposition", "diaspora", "kundgebung"],
}

# Diaspora cities with coordinates and estimated Albanian population
DIASPORA_CITIES = [
    {"city": "New York City", "country": "US", "lat": 40.7128, "lon": -74.0060, "population_est": 150000},
    {"city": "Boston", "country": "US", "lat": 42.3601, "lon": -71.0589, "population_est": 30000},
    {"city": "London", "country": "GB", "lat": 51.5074, "lon": -0.1278, "population_est": 50000},
    {"city": "Athens", "country": "GR", "lat": 37.9838, "lon": 23.7275, "population_est": 250000},
    {"city": "Rome", "country": "IT", "lat": 41.9028, "lon": 12.4964, "population_est": 120000},
    {"city": "Milan", "country": "IT", "lat": 45.4642, "lon": 9.1900, "population_est": 80000},
    {"city": "Brussels", "country": "BE", "lat": 50.8503, "lon": 4.3517, "population_est": 20000},
    {"city": "Munich", "country": "DE", "lat": 48.1351, "lon": 11.5820, "population_est": 25000},
    {"city": "Istanbul", "country": "TR", "lat": 41.0082, "lon": 28.9784, "population_est": 15000},
    {"city": "Zurich", "country": "CH", "lat": 47.3769, "lon": 8.5417, "population_est": 15000},
    {"city": "Tirana", "country": "AL", "lat": 41.3275, "lon": 19.8187, "population_est": None},
]

LANG_NAMES = {
    "en": "English",
    "sq": "Albanian",
    "it": "Italian",
    "el": "Greek",
    "de": "German",
    "fr": "French",
    "tr": "Turkish",
}

COUNTRY_NAMES = {
    "AL": "Albania",
    "US": "United States",
    "GB": "United Kingdom",
    "GR": "Greece",
    "IT": "Italy",
    "DE": "Germany",
    "BE": "Belgium",
    "CH": "Switzerland",
    "TR": "Turkey",
    "FR": "France",
    "AT": "Austria",
    "QA": "Qatar (Al Jazeera)",
    "XK": "Kosovo",
    "MK": "North Macedonia",
    "RS": "Serbia",
    "BG": "Bulgaria",
    "ES": "Spain",
    "PL": "Poland",
    "MT": "Malta",
    "IL": "Israel",
    "CA": "Canada",
    "SG": "Singapore",
    "SA": "Saudi Arabia",
    "UA": "Ukraine",
    "PK": "Pakistan",
    "NG": "Nigeria",
    "MY": "Malaysia",
    "KR": "South Korea",
    "IR": "Iran",
    "IN": "India",
    "ID": "Indonesia",
    "HK": "Hong Kong",
    "CZ": "Czech Republic",
    "BR": "Brazil",
    "AE": "UAE",
    "NL": "Netherlands",
    "INT": "International",
}
