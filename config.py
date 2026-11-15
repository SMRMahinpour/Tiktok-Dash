import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# =============================================================================
# TELEGRAM ALERTS
# =============================================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# =============================================================================
# TARGET MARKETS (US + UK lead TikTok Shop trend ignition before CA/AU/NZ)
# =============================================================================
DISCOVERY_COUNTRIES = ["US", "GB"]
PRIMARY_HASHTAG_COUNTRY = "US"

# =============================================================================
# HASHTAGS - DIRECT (lighting-specific, no filtering needed)
# =============================================================================
HASHTAGS_DIRECT = [
    "tablelamp", "pendantlight", "walllamp", "sconcelighting",
    "ceilinglight", "lightingfixture", "floorlamp", "chandelier",
    "stringlight", "wallsconce", "bedsidelamp", "pendantlamp",
    "ceilinglamp", "walllight", "desklamp", "nightlight",
    "spiralamp", "minimalistlamp", "modernlamp",
    "mushroomlamp", "sunsetlamp", "cordlesslamp", "rechargeablelamp",
]

# =============================================================================
# HASHTAGS - PAIRED (general, only kept if video mentions lighting)
# =============================================================================
HASHTAGS_PAIRED = [
    "lightingdesign", "modernlighting", "homelighting", "smartlighting",
    "ambientlight", "interiorlighting", "kitchenlighting", "bedroomlighting",
    "livingroomlighting", "homedecor", "interiordesign", "amazonfinds",
    "tiktokmademebuyit", "homedecorfinds", "interiorinspo",
    "roomtransformation", "apartmenttherapy", "homeinspo", "decoratingtips",
    "cozyvibes", "homegadgets", "viralproducts", "livingroomdecor",
    "bedroomdecor", "diningroomdecor", "minimalistdesign",
    "homelightingideas", "tiktokshopfinds", "aliexpressfinds",
    "lightluxury", "nordiclighting",
]

HASHTAGS = HASHTAGS_DIRECT + HASHTAGS_PAIRED

# =============================================================================
# LIGHTING KEYWORDS - used to filter paired hashtags & comment verification
# =============================================================================
LIGHTING_KEYWORDS = [
    "lamp", "lamps", "light", "lights", "lighting", "led", "sconce", "pendant",
    "chandelier", "bulb", "luminaire", "illumination",
    "floor lamp", "desk lamp", "wall light", "ceiling light",
    "table lamp", "bedside lamp", "night light", "mood light",
    "string light", "strip light", "wall lamp", "ceiling lamp",
    "hanging light", "hanging lamp", "fixture", "wall sconce",
    "touch lamp", "dimmable lamp", "cordless lamp", "mushroom lamp",
    "sunset lamp", "galaxy projector", "neon sign", "backlight",
    "copper", "crystal", "fabric", "linen", "acrylic", "ceramic", "brass",
    "scandinavian", "nordic", "japandi", "minimalist", "luxury",
    "tablelamp", "walllamp", "floorlamp", "ceilinglight", "pendantlight",
    "sconcelighting", "lightingdesign", "lightingfixture", "homelighting",
    "modernlighting", "smartlighting", "ambientlight", "interiorlighting",
    "kitchenlighting", "bedroomlighting", "livingroomlighting", "stringlight",
    "wallsconce", "bedsidelamp", "pendantlamp", "ceilinglamp",
    "walllight", "desklamp", "nightlight", "mushroomlamp", "sunsetlamp",
]

# =============================================================================
# AUTOMOTIVE EXCLUSIONS - reject car-related videos
# =============================================================================
AUTOMOTIVE_EXCLUSIONS = [
    "car", "cars", "vehicle", "vehicles", "automotive",
    "car interior", "car light", "car lights", "car lamp", "car lamps",
    "dash cam", "dashboard", "trunk",
    "toyota", "honda", "ford", "chevrolet", "chevy", "nissan", "hyundai", "kia",
    "bmw", "mercedes", "benz", "audi", "porsche",
    "tesla", "rivian", "lucid", "polestar",
    "pickup truck", "pickup trucks", "truck", "trucks", "suv", "sedan", "coupe",
    "f150", "silverado", "tacoma", "ram 1500",
    "lexus", "is350", "es350", "rx350", "nx350",
    "infiniti", "q50", "q60", "gx460",
    "genesis", "gv70", "gv80",
    "acura", "mdx", "rdx", "mazda", "subaru", "outback", "forester", "wrx",
    "volkswagen", "vw", "tiguan", "jetta", "golf gti",
    "cadillac", "gmc", "jeep", "dodge", "chrysler", "buick",
    "mitsubishi", "volvo", "jaguar", "land rover", "range rover",
    "peugeot", "renault", "skoda", "fiat", "alfa romeo",
    "maserati", "ferrari", "lamborghini", "bentley", "rolls royce", "mclaren",
    "carcontent", "carambient", "carambientlights", "carambientlighting",
    "carinterior", "carmods", "carsof", "carsoftiktok", "cartok", "carlife",
    "scania", "daf", "iveco", "peterbilt", "kenworth", "freightliner", "mack",
    "semi truck", "semitruck", "lorry", "trucker", "truckers", "trucklife", "trucktok",
]

# =============================================================================
# RELEVANCE DISAMBIGUATION
# =============================================================================
PRODUCT_TERMS = [
    "lamp", "lamps", "lampshade", "lampshades", "sconce", "sconces",
    "pendant", "pendants", "bulb", "bulbs", "fixture", "fixtures",
    "luminaire", "luminaires", "illumination", "lighting",
    "lampu", "lampe", "lampen", "lámpara", "lampara", "lampada", "leuchte", "leuchten",
    "candeeiro", "veioza",
    "led strip", "led strips", "led light", "led lights", "ledlight",
    "ledlights", "ledstrip", "ledstrips",
    "strip light", "strip lights", "string light", "string lights",
    "stringlight", "stringlights", "fairy light", "fairy lights",
    "fairylight", "fairylights",
    "ceiling light", "ceiling lights", "ceiling lamp", "ceiling lamps",
    "floor lamp", "floor lamps", "table lamp", "table lamps",
    "desk lamp", "desk lamps", "bedside lamp", "bedside lamps",
    "wall lamp", "wall lamps", "wall light", "wall lights",
    "night light", "night lights", "nightlight", "nightlights",
    "mushroom lamp", "mushroom lamps", "mushroomlamp",
    "sunset lamp", "sunset lamps", "sunsetlamp",
    "galaxy projector", "star projector", "galaxyprojector", "starprojector",
    "nebula projector", "aurora projector", "auroraprojector", "sunset projector",
    "sunsetprojector", "ceiling projector", "light projector", "projector light",
    "projector lamp", "nightlight projector", "aurora", "ocean wave",
    "water ripple", "ripple lamp", "neon sign", "neon light",
    "light fixture", "light fixtures", "lightfixture", "lightfixtures",
    "lightbulb", "lightbulbs", "smart bulb", "smart bulbs",
    "chandelier light", "chandelier lights", "chandelierlights",
    "mini chandelier", "minichandelier", "mini lights",
    "gold chandelier", "goldchandelier", "crystal chandelier",
    "crystalchandelier", "crystalchandeliers",
    "tablelamp", "desklamp", "bedsidelamp", "floorlamp", "walllamp",
    "walllight", "ceilinglight", "ceilinglamp", "pendantlight",
    "pendantlamp", "sconcelighting", "lightingfixture", "homelighting",
    "modernlighting", "smartlighting", "interiorlighting", "kitchenlighting",
    "bedroomlighting", "livingroomlighting", "nordiclighting", "lightingdesign",
    "wallsconce", "modernlamp", "minimalistlamp", "spiralamp",
    "lightluxury", "govee",
]

AMBIGUOUS_TERMS = [
    "chandelier", "chandeliers",
    "ambient light", "ambient lights", "ambientlight", "ambient lighting",
    "mood light", "mood lights", "moodlight", "mood lighting",
    "light", "lights",
]

MUSIC_CONTEXT_TERMS = [
    "sia", "cover", "cover song", "lyrics", "lyric", "song", "songs",
    "music", "vocals", "vocal", "karaoke", "remix", "singing", "singer",
    "ado", "minecraft", "playlist", "spotify", "acapella", "concert",
    "live performance", "liveperformance", "performance",
]

STRONG_PRODUCT_TERMS = [
    "table lamp", "tablelamp", "desk lamp", "desklamp",
    "floor lamp", "floorlamp", "wall lamp", "walllamp",
    "wall sconce", "wallsconce", "sconce", "sconces",
    "pendant light", "pendantlight", "pendant lamp", "pendantlamp",
    "ceiling light", "ceilinglight", "ceiling lamp", "ceilinglamp",
    "bedside lamp", "bedsidelamp", "night light", "nightlight",
    "mushroom lamp", "mushroomlamp", "sunset lamp", "sunsetlamp",
    "smart bulb", "smart bulbs", "lightbulb", "lightbulbs",
    "led strip", "led strips", "strip light", "strip lights",
    "galaxy projector", "star projector", "galaxyprojector", "starprojector",
    "nebula projector", "aurora projector", "auroraprojector", "sunset projector",
    "sunsetprojector", "ceiling projector", "light projector", "projector light",
    "projector lamp", "nightlight projector", "aurora", "ocean wave",
    "water ripple", "ripple lamp", "neon sign", "neon light",
    "lampshade", "lampshades", "light fixture", "light fixtures",
    "crystal chandelier", "crystalchandelier", "glass chandelier",
    "murano", "murano glass", "lightingfactory", "designer lamp",
    "designerlamp", "luxury chandelier", "modern chandelier",
    "dining chandelier", "ribbon chandelier", "fireworks ceiling",
    "false ceiling", "falseceiling", "ceiling design",
    "link in bio", "link in my bio", "link in the bio", "shop now",
    "unboxing", "unboxed", "install", "installation", "amazon",
    "tiktok shop", "tiktokshop", "discount code", "buy now", "order now",
    "remote control", "battery operated", "rechargeable", "cordless",
    "dimmable", "color changing", "colour changing", "touch sensor",
    "music sync", "rhythm light",
    "govee", "philips hue", "hue", "ikea", "wayfair", "temu",
    "roomdecor", "homedecor", "interiordesign", "interiorinspo",
    "apartmenttherapy", "roomtransformation", "homedecorfinds",
    "lightingideas", "homelightingideas", "decorating", "homeinspo",
    "cozyvibes", "homegadgets", "viralproducts", "livingroomdecor",
    "bedroomdecor", "diningroomdecor", "minimalistdesign",
    "tiktokshopfinds", "aliexpressfinds", "lightluxury",
    "renovation", "remodel", "makeover", "home renovation",
    "roominspo", "cozyhome", "cozylighting", "apartmentdecor",
    "housedecor", "homedecoration", "homedecorideas", "interiorstyling",
    "led",
]

GLOBAL_PORTABLE_TERMS = [
    "cordless", "rechargeable", "usb", "usb-c", "battery operated",
    "battery powered", "wireless", "portable", "touch lamp", "touch sensor",
    "magnetic", "peel and stick", "no wiring", "no drill",
]

# =============================================================================
# VIDEO AGE & DISCOVERY SETTINGS
# =============================================================================
MAX_AGE_MONTHS = 6
VIDEOS_PER_HASHTAG = 30
TEST_HASHTAGS = ["tablelamp", "tiktokmademebuyit"]
TEST_VIDEOS_PER_HASHTAG = 30

# Parallel Fetching (Upgrade B)
FETCH_CONCURRENCY = 3

# Recent 30-Day Search Discovery (Upgrade A)
RECENT_SEARCH_ENABLED = True
RECENT_SEARCH_QUERIES = [
    "cordless table lamp", "rechargeable lamp", "mushroom lamp",
    "wireless wall sconce", "sunset projection lamp", "aurora water ripple lamp",
    "modern pendant light", "pleated table lamp",
]
RECENT_SEARCH_LIMIT = 20

# Snowball & Ad Intelligence (Option A)
RELATED_SNOWBALL_LIMIT = 5
RELATED_PER_SEED = 15
TOP_ADS_ENABLED = True
TOP_ADS_KEYWORDS = ["lamp", "lighting", "chandelier", "sconce", "led light"]
TOP_ADS_LIMIT = 20

# HTTP timeouts (seconds)
PAGE_LOAD_TIMEOUT = 30
API_CAPTURE_TIMEOUT = 60
STALL_TIMEOUT = 15

# =============================================================================
# LIGHTING PRODUCT CATEGORIES
# =============================================================================
LIGHTING_CATEGORIES = {
    "table_lamp": [
        "table lamp", "desk lamp", "bedside lamp", "accent lamp", "reading lamp",
        "night light", "mood light", "ambient lamp", "cordless lamp", "portable lamp",
        "mini lamp", "small lamp", "touch lamp", "dimmable lamp", "usb lamp",
        "battery lamp", "rechargeable lamp", "coffee table lamp", "side table lamp",
        "mushroom lamp", "donut lamp", "burger lamp", "hamburger lamp",
        "lamp", "lamps", "lampshade", "tablelamp", "desklamp", "bedsidelamp",
        "mushroomlamp", "nightlight", "aesthetic lamp", "minimalist lamp",
        "vintage lamp", "modern lamp", "tiffany lamp", "ceramic lamp",
        "butterfly lamp", "spiral desk lamp", "ring night lamp", "heart lamp",
        "minimalistlamp", "modernlamp", "spiralamp",
    ],
    "pendant_ceiling": [
        "pendant light", "pendant lamp", "hanging light", "chandelier", "drop light",
        "ceiling light", "flush mount", "semi-flush", "recessed", "dome light",
        "ceiling fan", "fan light", "ceiling lamp", "overhead light", "island light",
        "cluster light", "multi-light", "linear suspension", "drum pendant",
        "pendant", "pendantlight", "pendantlamp", "ceilinglight", "ceilinglamp",
        "suspension", "hanging lamp", "led ceiling",
        "cream chandelier", "fabric chandelier", "cloud pendant",
        "fireworks ceiling", "ribbon chandelier", "multi-head pendant",
        "dining chandelier", "nordiclighting", "japandidesign",
    ],
    "wall_sconce": [
        "wall sconce", "wall light", "wall lamp", "sconce", "sconces",
        "half moon light", "halfmoon light", "vanity light", "mirror light",
        "bathroom light", "led mirror", "bedside wall", "headboard light",
        "reading light wall", "corridor light", "hallway light", "stair light",
        "picture light", "walllight", "walllamp", "sconcelighting",
        "wall mounted", "wall decor light", "accent wall light",
        "crystal wall", "bubble wall", "copper wall", "line light", "grille lamp",
        "wallsconce", "crystallamp", "copperlamp", "bubblelamp",
    ],
    "ambient_led": [
        "led strip", "led strips", "strip light", "strip lights", "ledstrip",
        "sunset lamp", "sunsetlamp", "galaxy projector", "star projector",
        "galaxyprojector", "starprojector", "nebula projector", "aurora projector",
        "auroraprojector", "sunset projector", "sunsetprojector", "ceiling projector",
        "light projector", "projector light", "projector lamp", "nightlight projector",
        "aurora", "ocean wave", "water ripple", "ripple lamp",
        "neon sign", "neon light", "tv backlight", "backlight",
        "rgb floor lamp", "corner lamp", "smart bulb", "smart bulbs",
        "smart lighting", "smartlighting", "govee", "philips hue",
        "fairy light", "fairy lights", "string light", "string lights",
        "ambient light", "ambient lighting", "ambientlight", "mood lighting",
        "rgbic", "music sync",
    ],
}

# =============================================================================
# SCORING & THRESHOLDS
# =============================================================================
VELOCITY_HIGH = 500
ENGAGEMENT_HIGH = 5.0
CANDIDATE_MIN_VIEWS = 1000
VIRAL_SAVE_THRESHOLD = 8.0

ALERT_THRESHOLDS = {
    "min_views": 50000,
    "min_engagement_rate": 5.0,
}

# =============================================================================
# COMMENT VERIFICATION (Low-Load HTTP inside main process + D1 sync)
# =============================================================================
COMMENT_FETCH_ENABLED = True
IN_PROCESS_COMMENT_VERIFY = True
VERIFY_ENABLED = True
VERIFY_MAX_PER_RUN = 25
MAX_COMMENTS_PER_VIDEO = 20
BORDERLINE_SCORE_THRESHOLD = 4.5
MIN_LIGHTING_COMMENTS = 3
VERIFY_MIN_COMMENTS = 5
VERIFY_STALE_CLAIM_MINUTES = 30

# =============================================================================
# SCORING WEIGHTS
# =============================================================================
BOOKMARK_WEIGHT = 0.2
SELLER_BONUS = 1.0
AD_BONUS = 1.2
HOOK_BONUS = 0.5
GLOBAL_PORTABLE_BONUS = 0.4
SCALE_BONUS_MAX = 2.5
FRESHNESS_7D_BONUS = 0.8
FRESHNESS_14D_BONUS = 0.4
CLUSTER_BONUS_STEP = 0.35
CLUSTER_BONUS_MAX = 1.05

# =============================================================================
# DATABASE
# =============================================================================
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "scraper.db"))