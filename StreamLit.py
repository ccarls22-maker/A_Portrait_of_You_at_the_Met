import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
from PIL import Image
from io import BytesIO, StringIO
import random
import re
import base64



# Page config
st.set_page_config(
    page_title="Met Museum Personal Curator",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS (keep your existing CSS here)
st.markdown("""
<style>
    /* Your existing CSS - keep it exactly as you had it */
    .stApp {
        background-color: white;
    }
    
    .main > div {
        background-color: white;
    }
    
    section[data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #e0e0e0;
    }
    
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stText,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #1E1E1E !important;
    }
    
    section[data-testid="stSidebar"] .stCheckbox label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #1E1E1E !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] p,
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] p {
        color: #1E1E1E !important;
    }
    
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        color: #1E1E1E !important;
        background-color: white !important;
    }
    
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
        color: #1E1E1E !important;
    }
    
    [data-testid="stMetricLabel"] p, [data-testid="stMetricValue"] p {
        color: #1E1E1E !important;
    }
    
    .stSelectbox label, .stSelectbox div[data-baseweb="select"] span {
        color: #1E1E1E !important;
    }
    
    .stMultiSelect label, .stMultiSelect div[data-baseweb="select"] span {
        color: #1E1E1E !important;
    }
    
    .stSlider label, .stSlider span {
        color: #1E1E1E !important;
    }
    
    .streamlit-expanderHeader {
        color: #1E1E1E !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button p {
        color: #1E1E1E !important;
    }
    
    .stAlert p {
        color: #1E1E1E !important;
    }
    
    .word-cloud {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-top: 5px;
        margin-bottom: 15px;
        font-size: 0.9em;
    }
    .keyword-tag {
        display: inline-block;
        background-color: #e6e9f0;
        padding: 3px 8px;
        margin: 2px;
        border-radius: 12px;
        font-size: 0.85em;
        color: #1E1E1E;
    }
    .filter-header {
        margin-bottom: 5px;
        font-weight: bold;
        color: #1E1E1E;
    }
    .artwork-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
    }
    .artwork-title {
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 5px;
        color: #1E1E1E;
    }
    .artwork-image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px 0;
        min-height: 200px;
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 5px;
    }
    .artwork-image {
        max-width: 100%;
        max-height: 250px;
        object-fit: contain;
        border-radius: 3px;
    }
    .artwork-info {
        font-size: 0.9em;
        color: #4A4A4A;
        margin-top: 10px;
    }
    .artwork-link {
        margin-top: 10px;
        text-align: center;
    }
    .artwork-link a {
        color: #0066CC;
        text-decoration: none;
    }
    .artwork-link a:hover {
        text-decoration: underline;
    }
    .no-image {
        color: #666;
        font-style: italic;
        text-align: center;
        padding: 20px;
    }
    .period-badge {
        display: inline-block;
        background-color: #4A6FA5;
        color: white !important;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .movement-badge {
        display: inline-block;
        background-color: #6B8C9E;
        color: white !important;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75em;
        margin-right: 5px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎨 Met Museum Personal Curator")
st.markdown("Explore art through historical periods, movements, and personal aesthetics - just like a real curator would!")

# ============================================================================
# STEP 1: Define Art Periods and Movements
# ============================================================================

# Ancient Art (Before 800 BCE)
ancient_keywords = ["sacred", "ritual", "afterlife", "ruler", "power", "foundational", "mythological", "hieratic", "ceremonial"]

# Greek/Roman: 800 BCE - 400 CE
greek_roman_keywords = ["idealized", "perfected form", "humanism", "civic", "realism", "portraiture", "mythology", "marble", "bronze", "proportion", "contrapposto", "drapery", "classical"]

# Medieval: 400 - 1350
medieval_keywords = ["glory of god", "religious", "symbolism", "hierarchy", "flat", "gold leaf", "illumination", "manuscript", "gothic", "romanesque", "byzantine", "icon", "devotional", "heavenly"]

# Renaissance: 1350 - 1600
renaissance_keywords = ["humanism", "perspective", "scientific", "individual", "classical", "naturalism", "anatomy", "sfumato", "chiaroscuro", "idealized", "realistic", "three-dimensional", "genius"]

# Baroque: 1600 - 1750
baroque_keywords = ["drama", "tension", "grandeur", "theatrical", "tenebrism", "movement", "emotional", "sensuous", "ornate", "diagonal", "intense", "dynamic", "exuberant"]

# Rococo: 1720-1760 (Late Baroque)
rococo_keywords = ["playful", "decorative", "pastel", "intimate", "romantic", "curvilinear", "ornate", "charming", "aristocratic", "frivolous", "light-hearted", "amorous"]

# Neoclassical: 1750 - 1800
neoclassical_keywords = ["civic virtue", "logic", "order", "moral", "linear", "restrained", "archaeological", "heroic", "patriotic", "didactic", "clean lines", "simplicity"]

# Romantic: 1800 - 1865
romantic_keywords = ["emotion", "sublime", "individual", "dramatic", "untamed nature", "exotic", "medieval", "imaginative", "rebellion", "passion", "awe-inspiring", "moody"]

# Impressionism: 1865 - 1885
impressionism_keywords = ["fleeting", "light", "en plein air", "modern life", "sensory", "spontaneous", "visible brushstroke", "color", "atmosphere", "leisure", "urban", "moment"]

# Post-Impressionism: 1885 - 1910
post_impressionism_keywords = ["symbolic color", "structural", "emotional", "personal", "expressive", "simplified form", "outline", "subjective", "psychological", "intense color"]

# Modern: 1910 - 1960
modern_keywords = ["experimental", "abstraction", "rejection", "fragmented", "multiple perspectives", "simultaneity", "unconscious", "machines", "speed", "geometric", "non-representational"]

# Contemporary: 1960 - Now
contemporary_keywords = ["conceptual", "identity", "globalization", "appropriation", "installation", "performance", "mixed media", "political", "critical", "boundaries", "viewer participation"]

# Create a comprehensive period dictionary
art_periods = {
    "Ancient (Before 800 BCE)": {
        "years": "Before 800 BCE",
        "keywords": ancient_keywords,
        "personality_matches": ["Symbolist", "Classicist"],
        "mood_matches": ["Muted & Naturalistic", "The Inner World"],
        "description": "Sacred ritual, power of rulers, the afterlife, foundational storytelling"
    },
    "Greek/Roman (800 BCE - 400 CE)": {
        "years": "800 BCE - 400 CE",
        "keywords": greek_roman_keywords,
        "personality_matches": ["Classicist", "Realist"],
        "mood_matches": ["Calm & Balanced", "Smooth & Polished"],
        "description": "Human idealism (Greek), civic power & realism (Roman), mythology, perfected form"
    },
    "Medieval (400 - 1350)": {
        "years": "400 - 1350 CE",
        "keywords": medieval_keywords,
        "personality_matches": ["Symbolist", "Romantic"],
        "mood_matches": ["The Inner World", "Ornate & Decorative"],
        "description": "The glory of God, religious narrative, hierarchy over realism, symbolism",
        "movements": ["Byzantine", "Romanesque", "Gothic"]
    },
    "Renaissance (1350 - 1600)": {
        "years": "1350 - 1600",
        "keywords": renaissance_keywords,
        "personality_matches": ["Classicist", "Innovator"],
        "mood_matches": ["Calm & Balanced", "The Human Figure", "Smooth & Polished"],
        "description": "Humanism, rediscovery of classical art, scientific perspective, individual genius",
        "movements": ["Early Renaissance", "High Renaissance", "Mannerism"]
    },
    "Baroque (1600 - 1750)": {
        "years": "1600 - 1750",
        "keywords": baroque_keywords,
        "personality_matches": ["Romantic", "Hedonist"],
        "mood_matches": ["Dynamic & Dramatic", "Warm & Golden", "Ornate & Decorative"],
        "description": "Drama, tension, grandeur, theatrical light, engaging the senses"
    },
    "Rococo (1720 - 1760)": {
        "years": "1720 - 1760",
        "keywords": rococo_keywords,
        "personality_matches": ["Hedonist", "Romantic"],
        "mood_matches": ["Ornate & Decorative", "Warm & Golden", "The Human Figure"],
        "description": "Playful, decorative, intimate, aristocratic pleasure"
    },
    "Neoclassical (1750 - 1800)": {
        "years": "1750 - 1800",
        "keywords": neoclassical_keywords,
        "personality_matches": ["Classicist", "Realist"],
        "mood_matches": ["Calm & Balanced", "Smooth & Polished", "The Human Figure"],
        "description": "Civic virtue, logic, order, classical models from Ancient Greece/Rome"
    },
    "Romantic (1800 - 1865)": {
        "years": "1800 - 1865",
        "keywords": romantic_keywords,
        "personality_matches": ["Romantic", "Symbolist"],
        "mood_matches": ["Dynamic & Dramatic", "Nature & Landscape", "Cool & Ethereal"],
        "description": "Emotion, the sublime in nature, individualism, dramatic rebellion"
    },
    "Impressionism (1865 - 1885)": {
        "years": "1865 - 1885",
        "keywords": impressionism_keywords,
        "personality_matches": ["Hedonist", "Realist"],
        "mood_matches": ["Vibrant & Unnatural", "Textured & Painterly", "Urban & Modern Life"],
        "description": "Modern life, fleeting light, sensory impression, painting en plein air"
    },
    "Post-Impressionism (1885 - 1910)": {
        "years": "1885 - 1910",
        "keywords": post_impressionism_keywords,
        "personality_matches": ["Innovator", "Romantic"],
        "mood_matches": ["Vibrant & Unnatural", "Textured & Painterly", "The Inner World"],
        "description": "Symbolic color, structural form, emotional and personal expression",
        "related": ["Fauvism", "Expressionism"]
    },
    "Modern (1910 - 1960)": {
        "years": "1910 - 1960",
        "keywords": modern_keywords,
        "personality_matches": ["Innovator", "Symbolist"],
        "mood_matches": ["Chaotic & Raw", "The Abstract Idea", "Vibrant & Unnatural"],
        "description": "Experimentation, abstraction, rejecting tradition, art about art itself",
        "movements": ["Cubism", "Futurism", "Dada", "Surrealism", "Abstract Expressionism"]
    },
    "Contemporary (1960 - Now)": {
        "years": "1960 - Present",
        "keywords": contemporary_keywords,
        "personality_matches": ["Innovator", "Realist"],
        "mood_matches": ["The Abstract Idea", "Urban & Modern Life", "Chaotic & Raw"],
        "description": "Conceptualism, identity politics, globalization, questioning boundaries",
        "movements": ["Pop Art", "Minimalism", "Performance Art", "Installation", "Postmodernism"]
    }
}

# ============================================================================
# STEP 2: Personality Archetypes
# ============================================================================

personality = {
    "Classicist": {
        "keywords": ["order", "balance", "clarity", "timeless", "harmony", "symmetry", "ideal", "perfection", "restraint", "tradition", "proportion", "discipline", "rational", "structured"],
        "period_matches": ["Greek/Roman (800 BCE - 400 CE)", "Renaissance (1350 - 1600)", "Neoclassical (1750 - 1800)"]
    },
    "Romantic": {
        "keywords": ["emotion", "imagination", "mystery", "nature", "passion", "drama", "sublime", "intuition", "wild", "longing", "intensity", "fantasy", "awe", "turbulence", "poetic"],
        "period_matches": ["Romantic (1800 - 1865)", "Baroque (1600 - 1750)", "Medieval (400 - 1350)", "Rococo (1720 - 1760)"]
    },
    "Realist": {
        "keywords": ["truth", "authenticity", "grounded", "pragmatic", "observation", "unvarnished", "direct", "honest", "everyday", "ordinary", "candid", "objective", "documentary"],
        "period_matches": ["Greek/Roman (800 BCE - 400 CE)", "Impressionism (1865 - 1885)", "Contemporary (1960 - Now)"]
    },
    "Innovator": {
        "keywords": ["experimental", "abstract", "intellectual", "bold", "unconventional", "avant-garde", "radical", "new", "inventive", "conceptual", "challenging", "progressive", "pioneering"],
        "period_matches": ["Modern (1910 - 1960)", "Contemporary (1960 - Now)", "Post-Impressionism (1885 - 1910)", "Renaissance (1350 - 1600)"]
    },
    "Symbolist": {
        "keywords": ["metaphor", "spiritual", "dream", "mystical", "hidden", "coded", "visionary", "esoteric", "subconscious", "otherworldly", "enigmatic", "poetic", "mythic"],
        "period_matches": ["Medieval (400 - 1350)", "Romantic (1800 - 1865)", "Ancient (Before 800 BCE)", "Post-Impressionism (1885 - 1910)"]
    },
    "Hedonist": {
        "keywords": ["sensual", "decorative", "pleasure", "beauty", "elegance", "ornate", "lush", "indulgent", "playful", "charming", "delightful", "opulent", "graceful", "sumptuous"],
        "period_matches": ["Rococo (1720 - 1760)", "Impressionism (1865 - 1885)", "Baroque (1600 - 1750)"]
    }
}

# ============================================================================
# STEP 3: Moods / Vibes
# ============================================================================

moods = {
    "Dynamic & Dramatic": {
        "keywords": ["energetic", "intense", "theatrical", "bold", "movement", "action", "contrast", "explosive", "vigorous", "lively", "forceful", "passionate"],
        "period_matches": ["Baroque (1600 - 1750)", "Romantic (1800 - 1865)", "Modern (1910 - 1960)"]
    },
    "Calm & Balanced": {
        "keywords": ["serene", "peaceful", "tranquil", "restful", "meditative", "gentle", "soothing", "harmonious", "quiet", "still", "composed", "poised"],
        "period_matches": ["Renaissance (1350 - 1600)", "Neoclassical (1750 - 1800)", "Greek/Roman (800 BCE - 400 CE)"]
    },
    "Chaotic & Raw": {
        "keywords": ["fragmented", "wild", "unrestrained", "expressive", "rough", "spontaneous", "turbulent", "primal", "visceral", "untamed", "emotional", "jagged"],
        "period_matches": ["Modern (1910 - 1960)", "Expressionism", "Abstract Expressionism"]
    },
    "Warm & Golden": {
        "keywords": ["radiant", "glowing", "sunlit", "rich", "golden", "fiery", "warm", "amber", "luminous", "vibrant", "passionate", "cozy"],
        "period_matches": ["Renaissance (1350 - 1600)", "Baroque (1600 - 1750)", "Medieval (400 - 1350)"]
    },
    "Cool & Ethereal": {
        "keywords": ["icy", "silvery", "misty", "pale", "delicate", "airy", "dreamy", "soft", "ghostly", "tranquil", "celestial", "serene"],
        "period_matches": ["Gothic", "Romantic (1800 - 1865)", "Symbolism"]
    },
    "Vibrant & Unnatural": {
        "keywords": ["electric", "neon", "saturated", "bold", "artificial", "psychedelic", "pop", "striking", "flamboyant", "unconventional", "vivid", "dazzling"],
        "period_matches": ["Fauvism", "Pop Art", "Post-Impressionism (1885 - 1910)"]
    },
    "Muted & Naturalistic": {
        "keywords": ["earthy", "subdued", "soft", "gentle", "realistic", "understated", "organic", "subtle", "quiet", "neutral", "faded", "mellow"],
        "period_matches": ["Realism", "Dutch Golden Age", "Ancient (Before 800 BCE)"]
    }
}

# ============================================================================
# STEP 4: Visual Qualities
# ============================================================================

visuals = {
    "The Human Figure": {
        "keywords": ["idealized", "expressive", "deconstructed", "portrait", "body", "anatomy", "gesture", "character", "identity", "emotion", "narrative"],
        "period_matches": ["Greek/Roman (800 BCE - 400 CE)", "Renaissance (1350 - 1600)", "Expressionism", "Cubism"]
    },
    "Nature & Landscape": {
        "keywords": ["sublime", "pastoral", "wild", "scientific", "botanical", "atmospheric", "scenic", "rural", "natural", "expansive", "tranquil", "dramatic"],
        "period_matches": ["Romantic (1800 - 1865)", "Impressionism (1865 - 1885)", "Hudson River School"]
    },
    "The Inner World": {
        "keywords": ["dreamlike", "subconscious", "visionary", "surreal", "symbolic", "psychological", "spiritual", "introspective", "mysterious", "fantastical", "meditative"],
        "period_matches": ["Surrealism", "Symbolism", "Medieval (400 - 1350)"]
    },
    "Urban & Modern Life": {
        "keywords": ["city", "technology", "industrial", "social", "leisure", "critique", "modernity", "bustle", "architecture", "crowd", "nightlife", "contemporary"],
        "period_matches": ["Impressionism (1865 - 1885)", "Ashcan School", "Futurism", "Pop Art"]
    },
    "The Abstract Idea": {
        "keywords": ["form", "color", "geometry", "conceptual", "minimal", "pure", "reduction", "structure", "pattern", "nonrepresentational", "experimental"],
        "period_matches": ["Abstract Expressionism", "Minimalism", "Conceptual Art", "Modern (1910 - 1960)"]
    },
    "Smooth & Polished": {
        "keywords": ["flawless", "marble", "glazed", "refined", "sleek", "seamless", "glossy", "finished", "perfect", "elegant", "pristine"],
        "period_matches": ["Greek/Roman (800 BCE - 400 CE)", "Renaissance (1350 - 1600)", "Neoclassical (1750 - 1800)"]
    },
    "Textured & Painterly": {
        "keywords": ["impasto", "brushwork", "rough", "tactile", "layered", "expressive", "visible", "raw", "dynamic", "gestural", "thick", "lively"],
        "period_matches": ["Impressionism (1865 - 1885)", "Post-Impressionism (1885 - 1910)", "Abstract Expressionism"]
    },
    "Ornate & Decorative": {
        "keywords": ["intricate", "patterned", "detailed", "gilded", "embellished", "curvilinear", "lavish", "baroque", "rococo", "filigree", "ornamental"],
        "period_matches": ["Rococo (1720 - 1760)", "Baroque (1600 - 1750)", "Art Nouveau", "Gothic"]
    }
}

# ============================================================================
# Helper Functions
# ============================================================================

def parse_date_to_year(date_str):
    """Attempt to extract a year from various date formats"""
    if pd.isna(date_str) or not isinstance(date_str, str):
        return None
    
    # Remove common text and try to find numbers
    date_str = str(date_str).lower()
    
    # Handle BCE dates
    if 'bce' in date_str or 'bc' in date_str:
        return -1000
    
    # Try to extract century
    if 'century' in date_str:
        parts = date_str.split()
        for part in parts:
            if part.isdigit():
                century = int(part)
                return (century - 1) * 100 + 50
    
    # Try to find 4-digit years
    years = re.findall(r'\b\d{3,4}\b', date_str)
    if years:
        return int(years[0])
    
    # Try to find ranges like "c. 1500" or "ca. 1500"
    c_match = re.search(r'c\.?\s*(\d{3,4})', date_str)
    if c_match:
        return int(c_match.group(1))
    
    return None

def estimate_period_from_date(date_str):
    """Estimate which art period an artwork belongs to based on its date"""
    year = parse_date_to_year(date_str)
    if year is None:
        return "Unknown"
    
    if year < 0:
        return "Ancient (Before 800 BCE)"
    elif year < 400:
        return "Greek/Roman (800 BCE - 400 CE)"
    elif year < 1350:
        return "Medieval (400 - 1350)"
    elif year < 1600:
        return "Renaissance (1350 - 1600)"
    elif year < 1750:
        if 1720 <= year <= 1760:
            return "Rococo (1720 - 1760)"
        return "Baroque (1600 - 1750)"
    elif year < 1800:
        return "Neoclassical (1750 - 1800)"
    elif year < 1865:
        return "Romantic (1800 - 1865)"
    elif year < 1885:
        return "Impressionism (1865 - 1885)"
    elif year < 1910:
        return "Post-Impressionism (1885 - 1910)"
    elif year < 1960:
        return "Modern (1910 - 1960)"
    else:
        return "Contemporary (1960 - Now)"

def display_keywords(keyword_list):
    """Display keywords as styled tags"""
    html = '<div class="word-cloud">'
    for keyword in keyword_list[:15]:  # Limit to 15 keywords
        html += f'<span class="keyword-tag">{keyword}</span>'
    html += '</div>'
    return html

# ============================================================================
# Data Loading Function - Fixed for LFS and error handling
# ============================================================================

@st.cache_data(ttl=3600)
def get_image_url(object_id):
    """Fetch image URL from Met Museum API"""
    try:
        if pd.isna(object_id):
            return None
        response = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{int(object_id)}", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('primaryImage'):
                return data['primaryImage']
            elif data.get('additionalImages') and len(data['additionalImages']) > 0:
                return data['additionalImages'][0]
        return None
    except:
        return None

@st.cache_data(ttl=3600)
def load_image_from_url(url):
    """Load image from URL"""
    try:
        if url:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                return img
    except:
        pass
    return None

@st.cache_data
def fetch_from_met_api():
    """Fetch artworks directly from Met API"""
    # Get list of object IDs
    response = requests.get("https://collectionapi.metmuseum.org/public/collection/v1/objects")
    object_ids = response.json()['object_ids'][:100]  # First 100
    
    artworks = []
    for obj_id in object_ids:
        data = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}").json()
        artworks.append({
            'Title': data.get('title'),
            'Artist Display Name': data.get('artistDisplayName'),
            'Object Date': data.get('objectDate'),
            # ... other fields
        })
    
    return pd.DataFrame(artworks)

# ============================================================================
# Main App
# ============================================================================

# Load data
with st.spinner("Loading data..."):
    df = load_data()

if df is not None and len(df) > 0:
    # Show basic info in sidebar
    with st.sidebar:
        st.header("📊 Collection Stats")
        st.metric("Total Artworks", f"{len(df):,}")
        
        # Show period distribution if column exists
        if 'estimated_period' in df.columns:
            period_counts = df['estimated_period'].value_counts()
            st.metric("Artworks with Period", f"{period_counts.sum():,}")
        
        st.divider()
        
        st.header("ℹ️ About the Filters")
        st.markdown("""
        **Historical Periods** - Journey through art history
        **Personality Archetypes** - Your foundational artistic lens  
        **Mood/Vibes** - The emotional atmosphere you seek
        **Visual Qualities** - What you want to see in the artwork
        """)
        
        st.divider()
        
        # Add option to toggle image loading
        st.header("🖼️ Settings")
        load_images = st.checkbox("Load artwork images", value=False, 
                                 help="Disable for faster loading (images may be slow)")
        
        # Number of artworks to display
        num_artworks = st.slider("Number of artworks to display", 3, 18, 9, step=3)
    
    # ============================================================================
    # Period Selection
    # ============================================================================
    
    st.header("📜 STEP 1: Choose Your Art Historical Period")
    st.markdown("Start by selecting a broad historical period that interests you.")
    
    # Safely get available periods
    if 'estimated_period' in df.columns:
        available_periods = [p for p in art_periods.keys() 
                           if p in df['estimated_period'].value_counts().index]
    else:
        available_periods = list(art_periods.keys())
    
    if not available_periods:
        available_periods = list(art_periods.keys())
    
    selected_period = st.selectbox(
        "Select an art historical period:",
        available_periods,
        key="period_select"
    )
    
    # Display period information
    period_info = art_periods[selected_period]
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown(f"**📅 Years:** {period_info['years']}")
    with col_info2:
        st.markdown(f"**🎭 Personality Matches:** {', '.join(period_info['personality_matches'])}")
    with col_info3:
        st.markdown(f"**🌊 Mood Matches:** {', '.join(period_info['mood_matches'][:2])}")
    
    st.markdown(f"**📝 Description:** {period_info['description']}")
    
    # Show movements if they exist
    if 'movements' in period_info:
        movements_html = "".join([f'<span class="movement-badge">{m}</span>' for m in period_info['movements']])
        st.markdown(f"**Key Movements:** {movements_html}", unsafe_allow_html=True)
    
    # Show keywords
    st.markdown("**Period Keywords:**")
    st.markdown(display_keywords(period_info['keywords']), unsafe_allow_html=True)
    
    st.divider()
    
    # ============================================================================
    # Personality, Mood, Visual Filters
    # ============================================================================
    
    st.header("🎯 STEP 2: Refine by Personal Aesthetic")
    
    # Create three columns for the main filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p class="filter-header">🎭 PERSONALITY ARCHETYPE</p>', unsafe_allow_html=True)
        personality_choice = st.selectbox(
            "Select your artistic personality:",
            list(personality.keys()),
            label_visibility="collapsed",
            key="personality_select"
        )
        st.markdown("**Related keywords:**")
        st.markdown(display_keywords(personality[personality_choice]["keywords"]), unsafe_allow_html=True)
        
        # Show recommended periods
        rec_periods = personality[personality_choice]["period_matches"]
        if rec_periods:
            period_badges = "".join([f'<span class="period-badge">{p}</span>' for p in rec_periods[:3]])
            st.markdown(f"**Recommended periods:** {period_badges}", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="filter-header">🌊 MOOD & ENERGY</p>', unsafe_allow_html=True)
        mood_choice = st.selectbox(
            "Select your desired mood:",
            list(moods.keys()),
            label_visibility="collapsed",
            key="mood_select"
        )
        st.markdown("**Related keywords:**")
        st.markdown(display_keywords(moods[mood_choice]["keywords"]), unsafe_allow_html=True)
        
        # Show recommended periods
        rec_periods = moods[mood_choice]["period_matches"]
        if rec_periods:
            period_badges = "".join([f'<span class="period-badge">{p}</span>' for p in rec_periods[:3]])
            st.markdown(f"**Often found in:** {period_badges}", unsafe_allow_html=True)
    
    with col3:
        st.markdown('<p class="filter-header">🎨 VISUAL QUALITIES</p>', unsafe_allow_html=True)
        visual_choice = st.selectbox(
            "Select visual qualities:",
            list(visuals.keys()),
            label_visibility="collapsed",
            key="visual_select"
        )
        st.markdown("**Related keywords:**")
        st.markdown(display_keywords(visuals[visual_choice]["keywords"]), unsafe_allow_html=True)
        
        # Show recommended periods
        rec_periods = visuals[visual_choice]["period_matches"]
        if rec_periods:
            period_badges = "".join([f'<span class="period-badge">{p}</span>' for p in rec_periods[:3]])
            st.markdown(f"**Prominent in:** {period_badges}", unsafe_allow_html=True)
    
    st.divider()
    
    # ============================================================================
    # Additional Filters
    # ============================================================================
    
    with st.expander("🔍 Additional Filters (Optional)", expanded=False):
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if 'Department' in df.columns:
                dept_counts = df['Department'].dropna().value_counts().head(20).index.tolist()
                selected_dept = st.multiselect("Filter by Department", dept_counts) if dept_counts else []
            else:
                selected_dept = []
                st.info("Department data not available")
        
        with col5:
            if 'Classification' in df.columns:
                class_counts = df['Classification'].dropna().value_counts().head(20).index.tolist()
                selected_class = st.multiselect("Filter by Classification", class_counts) if class_counts else []
            else:
                selected_class = []
                st.info("Classification data not available")
        
        with col6:
            if 'Culture' in df.columns:
                culture_counts = df['Culture'].dropna().value_counts().head(15).index.tolist()
                selected_culture = st.multiselect("Filter by Culture", culture_counts) if culture_counts else []
            else:
                selected_culture = []
                st.info("Culture data not available")
    
    # ============================================================================
    # Apply Filters
    # ============================================================================
    
    filtered_df = df.copy()
    
    # Apply period filter if column exists
    if 'estimated_period' in filtered_df.columns and selected_period:
        filtered_df = filtered_df[filtered_df['estimated_period'] == selected_period]
    
    # Apply department filter
    if 'selected_dept' in locals() and selected_dept and 'Department' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Department'].isin(selected_dept)]
    
    # Apply classification filter
    if 'selected_class' in locals() and selected_class and 'Classification' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Classification'].isin(selected_class)]
    
    # Apply culture filter
    if 'selected_culture' in locals() and selected_culture and 'Culture' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Culture'].isin(selected_culture)]
    
    # ============================================================================
    # Show Results
    # ============================================================================
    
    st.header(f"🎨 Found {len(filtered_df):,} Artworks in {selected_period if 'estimated_period' in filtered_df.columns else 'Collection'}")
    
    if len(filtered_df) > 0:
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Gallery View", "Data View", "Period Information"])
        
        with tab1:
            # Show sample artworks
            sample_size = min(num_artworks, len(filtered_df))
            display_artworks = filtered_df.sample(sample_size) if len(filtered_df) > sample_size else filtered_df
            
            # Create grid layout
            cols_per_row = 3
            rows = (len(display_artworks) + cols_per_row - 1) // cols_per_row
            
            for row in range(rows):
                cols = st.columns(cols_per_row)
                start_idx = row * cols_per_row
                end_idx = min(start_idx + cols_per_row, len(display_artworks))
                
                for col_idx in range(start_idx, end_idx):
                    with cols[col_idx - start_idx]:
                        artwork = display_artworks.iloc[col_idx]
                        
                        # Create card
                        st.markdown('<div class="artwork-card">', unsafe_allow_html=True)
                        
                        # Title
                        title = artwork.get('Title', 'Untitled')
                        if title and not pd.isna(title):
                            st.markdown(f'<div class="artwork-title">{str(title)[:60]}</div>', unsafe_allow_html=True)
                        
                        # Show period badge if available
                        if 'estimated_period' in artwork and artwork['estimated_period'] and not pd.isna(artwork['estimated_period']):
                            st.markdown(f'<span class="period-badge">{artwork["estimated_period"]}</span>', unsafe_allow_html=True)
                        
                        # Image placeholder
                        st.markdown('<div class="artwork-image-container no-image">🖼️ Image loading disabled for demo</div>', unsafe_allow_html=True)
                        
                        # Artist
                        artist = artwork.get('Artist Display Name', 'Unknown')
                        if artist and not pd.isna(artist) and artist != 'Unknown':
                            st.markdown(f'<div class="artwork-info">👨‍🎨 {str(artist)[:40]}</div>', unsafe_allow_html=True)
                        
                        # Date
                        date = artwork.get('Object Date', '')
                        if date and not pd.isna(date):
                            st.markdown(f'<div class="artwork-info">📅 {str(date)[:30]}</div>', unsafe_allow_html=True)
                        
                        # Culture if available
                        culture = artwork.get('Culture', '')
                        if culture and not pd.isna(culture):
                            st.markdown(f'<div class="artwork-info">🌍 {str(culture)[:30]}</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            # Show data table
            display_cols = ['Title', 'Artist Display Name', 'Object Date']
            if 'estimated_period' in filtered_df.columns:
                display_cols.append('estimated_period')
            display_cols.extend(['Culture', 'Classification', 'Department'])
            
            available_cols = [col for col in display_cols if col in filtered_df.columns]
            if available_cols:
                st.dataframe(
                    filtered_df[available_cols].head(100),
                    use_container_width=True,
                    hide_index=True
                )
                if len(filtered_df) > 100:
                    st.caption(f"Showing first 100 of {len(filtered_df)} artworks")
        
        with tab3:
            # Show detailed period information
            st.subheader(f"📚 About {selected_period}")
            st.markdown(f"**Description:** {period_info['description']}")
            st.markdown(f"**Time Period:** {period_info['years']}")
            
            # Create columns for matched personalities and moods
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**🎭 Compatible Personalities:**")
                for p_type in period_info['personality_matches']:
                    if p_type in personality:
                        st.markdown(f"• **{p_type}** - {', '.join(personality[p_type]['keywords'][:5])}")
            
            with col_b:
                st.markdown("**🌊 Common Moods:**")
                for m_type in period_info['mood_matches']:
                    if m_type in moods:
                        st.markdown(f"• **{m_type}** - {', '.join(moods[m_type]['keywords'][:5])}")
            
            # Show keywords
            st.markdown("**🔑 Period Keywords:**")
            st.markdown(display_keywords(period_info['keywords']), unsafe_allow_html=True)
    
    else:
        st.warning("No artworks found with current filters. Try adjusting your selections or choose a different period.")

else:
    st.error("""
    ⚠️ Could not load the data file. The app is running in demonstration mode with sample data.
    
    To use the full Met Museum collection:
    
    1. Make sure your GitHub repository is public
    2. The file 'MetObjects.csv' should be in the root of your repository
    3. For LFS files, you may need to use the GitHub API approach
    
    📁 **Current status:** Using sample dataset with 10 famous artworks
    """)
