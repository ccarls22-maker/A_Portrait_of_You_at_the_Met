import streamlit as st
import pandas as pd
import numpy as np
import requests
from PIL import Image
from io import BytesIO
import re
import time

# Page config
st.set_page_config(
    page_title="Met Museum Personal Curator",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
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
    
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
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
        display: flex;
        flex-direction: column;
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
        max-height: 250px;
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 5px;
        overflow: hidden;
    }
    .artwork-image {
        max-width: 100%;
        max-height: 100%;
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
# Art Periods and Movements
# ============================================================================

art_periods = {
    "Ancient (Before 800 BCE)": {
        "years": "Before 800 BCE",
        "keywords": ["sacred", "ritual", "afterlife", "ruler", "power", "foundational", "mythological"],
        "personality_matches": ["Symbolist", "Classicist"],
        "mood_matches": ["Muted & Naturalistic", "The Inner World"],
        "description": "Sacred ritual, power of rulers, the afterlife, foundational storytelling"
    },
    "Greek/Roman (800 BCE - 400 CE)": {
        "years": "800 BCE - 400 CE",
        "keywords": ["idealized", "perfected form", "humanism", "civic", "realism", "mythology", "marble", "classical"],
        "personality_matches": ["Classicist", "Realist"],
        "mood_matches": ["Calm & Balanced", "Smooth & Polished"],
        "description": "Human idealism (Greek), civic power & realism (Roman), mythology, perfected form"
    },
    "Medieval (400 - 1350)": {
        "years": "400 - 1350 CE",
        "keywords": ["religious", "symbolism", "gold leaf", "gothic", "byzantine", "devotional"],
        "personality_matches": ["Symbolist", "Romantic"],
        "mood_matches": ["The Inner World", "Ornate & Decorative"],
        "description": "The glory of God, religious narrative, hierarchy over realism, symbolism",
        "movements": ["Byzantine", "Romanesque", "Gothic"]
    },
    "Renaissance (1350 - 1600)": {
        "years": "1350 - 1600",
        "keywords": ["humanism", "perspective", "scientific", "individual", "classical", "anatomy", "sfumato"],
        "personality_matches": ["Classicist", "Innovator"],
        "mood_matches": ["Calm & Balanced", "The Human Figure", "Smooth & Polished"],
        "description": "Humanism, rediscovery of classical art, scientific perspective, individual genius",
        "movements": ["Early Renaissance", "High Renaissance", "Mannerism"]
    },
    "Baroque (1600 - 1750)": {
        "years": "1600 - 1750",
        "keywords": ["drama", "tension", "grandeur", "theatrical", "movement", "emotional", "ornate"],
        "personality_matches": ["Romantic", "Hedonist"],
        "mood_matches": ["Dynamic & Dramatic", "Warm & Golden", "Ornate & Decorative"],
        "description": "Drama, tension, grandeur, theatrical light, engaging the senses"
    },
    "Rococo (1720 - 1760)": {
        "years": "1720 - 1760",
        "keywords": ["playful", "decorative", "pastel", "intimate", "romantic", "curvilinear", "charming"],
        "personality_matches": ["Hedonist", "Romantic"],
        "mood_matches": ["Ornate & Decorative", "Warm & Golden", "The Human Figure"],
        "description": "Playful, decorative, intimate, aristocratic pleasure"
    },
    "Neoclassical (1750 - 1800)": {
        "years": "1750 - 1800",
        "keywords": ["civic virtue", "logic", "order", "moral", "restrained", "heroic", "simplicity"],
        "personality_matches": ["Classicist", "Realist"],
        "mood_matches": ["Calm & Balanced", "Smooth & Polished", "The Human Figure"],
        "description": "Civic virtue, logic, order, classical models from Ancient Greece/Rome"
    },
    "Romantic (1800 - 1865)": {
        "years": "1800 - 1865",
        "keywords": ["emotion", "sublime", "individual", "dramatic", "nature", "imaginative", "passion"],
        "personality_matches": ["Romantic", "Symbolist"],
        "mood_matches": ["Dynamic & Dramatic", "Nature & Landscape", "Cool & Ethereal"],
        "description": "Emotion, the sublime in nature, individualism, dramatic rebellion"
    },
    "Impressionism (1865 - 1885)": {
        "years": "1865 - 1885",
        "keywords": ["fleeting", "light", "en plein air", "modern life", "spontaneous", "color", "atmosphere"],
        "personality_matches": ["Hedonist", "Realist"],
        "mood_matches": ["Vibrant & Unnatural", "Textured & Painterly", "Urban & Modern Life"],
        "description": "Modern life, fleeting light, sensory impression, painting en plein air"
    },
    "Post-Impressionism (1885 - 1910)": {
        "years": "1885 - 1910",
        "keywords": ["symbolic color", "structural", "emotional", "personal", "expressive", "subjective"],
        "personality_matches": ["Innovator", "Romantic"],
        "mood_matches": ["Vibrant & Unnatural", "Textured & Painterly", "The Inner World"],
        "description": "Symbolic color, structural form, emotional and personal expression",
        "related": ["Fauvism", "Expressionism"]
    },
    "Modern (1910 - 1960)": {
        "years": "1910 - 1960",
        "keywords": ["experimental", "abstraction", "fragmented", "unconscious", "geometric", "non-representational"],
        "personality_matches": ["Innovator", "Symbolist"],
        "mood_matches": ["Chaotic & Raw", "The Abstract Idea", "Vibrant & Unnatural"],
        "description": "Experimentation, abstraction, rejecting tradition, art about art itself",
        "movements": ["Cubism", "Futurism", "Dada", "Surrealism", "Abstract Expressionism"]
    },
    "Contemporary (1960 - Now)": {
        "years": "1960 - Present",
        "keywords": ["conceptual", "identity", "globalization", "installation", "performance", "mixed media", "political"],
        "personality_matches": ["Innovator", "Realist"],
        "mood_matches": ["The Abstract Idea", "Urban & Modern Life", "Chaotic & Raw"],
        "description": "Conceptualism, identity politics, globalization, questioning boundaries",
        "movements": ["Pop Art", "Minimalism", "Performance Art", "Installation", "Postmodernism"]
    }
}

# ============================================================================
# Personality Archetypes
# ============================================================================

personality = {
    "Classicist": {
        "keywords": ["order", "balance", "clarity", "timeless", "harmony", "symmetry", "ideal", "perfection", "restraint", "tradition", "proportion"],
        "period_matches": ["Greek/Roman (800 BCE - 400 CE)", "Renaissance (1350 - 1600)", "Neoclassical (1750 - 1800)"]
    },
    "Romantic": {
        "keywords": ["emotion", "imagination", "mystery", "nature", "passion", "drama", "sublime", "intuition", "wild", "longing", "intensity"],
        "period_matches": ["Romantic (1800 - 1865)", "Baroque (1600 - 1750)", "Medieval (400 - 1350)", "Rococo (1720 - 1760)"]
    },
    "Realist": {
        "keywords": ["truth", "authenticity", "grounded", "pragmatic", "observation", "honest", "everyday", "ordinary", "candid", "objective"],
        "period_matches": ["Greek/Roman (800 BCE - 400 CE)", "Impressionism (1865 - 1885)", "Contemporary (1960 - Now)"]
    },
    "Innovator": {
        "keywords": ["experimental", "abstract", "intellectual", "bold", "unconventional", "avant-garde", "radical", "new", "inventive", "conceptual"],
        "period_matches": ["Modern (1910 - 1960)", "Contemporary (1960 - Now)", "Post-Impressionism (1885 - 1910)", "Renaissance (1350 - 1600)"]
    },
    "Symbolist": {
        "keywords": ["metaphor", "spiritual", "dream", "mystical", "hidden", "coded", "visionary", "subconscious", "otherworldly", "enigmatic"],
        "period_matches": ["Medieval (400 - 1350)", "Romantic (1800 - 1865)", "Ancient (Before 800 BCE)", "Post-Impressionism (1885 - 1910)"]
    },
    "Hedonist": {
        "keywords": ["sensual", "decorative", "pleasure", "beauty", "elegance", "ornate", "lush", "indulgent", "playful", "charming", "opulent"],
        "period_matches": ["Rococo (1720 - 1760)", "Impressionism (1865 - 1885)", "Baroque (1600 - 1750)"]
    }
}

# ============================================================================
# Moods / Vibes
# ============================================================================

moods = {
    "Dynamic & Dramatic": {
        "keywords": ["energetic", "intense", "theatrical", "bold", "movement", "action", "contrast", "explosive", "vigorous", "lively"],
        "period_matches": ["Baroque (1600 - 1750)", "Romantic (1800 - 1865)", "Modern (1910 - 1960)"]
    },
    "Calm & Balanced": {
        "keywords": ["serene", "peaceful", "tranquil", "restful", "meditative", "gentle", "soothing", "harmonious", "quiet", "still"],
        "period_matches": ["Renaissance (1350 - 1600)", "Neoclassical (1750 - 1800)", "Greek/Roman (800 BCE - 400 CE)"]
    },
    "Chaotic & Raw": {
        "keywords": ["fragmented", "wild", "unrestrained", "expressive", "rough", "spontaneous", "turbulent", "primal", "visceral", "emotional"],
        "period_matches": ["Modern (1910 - 1960)", "Expressionism", "Abstract Expressionism"]
    },
    "Warm & Golden": {
        "keywords": ["radiant", "glowing", "sunlit", "rich", "golden", "fiery", "warm", "amber", "luminous", "vibrant"],
        "period_matches": ["Renaissance (1350 - 1600)", "Baroque (1600 - 1750)", "Medieval (400 - 1350)"]
    },
    "Cool & Ethereal": {
        "keywords": ["icy", "silvery", "misty", "pale", "delicate", "airy", "dreamy", "soft", "ghostly", "tranquil", "celestial"],
        "period_matches": ["Gothic", "Romantic (1800 - 1865)", "Symbolism"]
    },
    "Vibrant & Unnatural": {
        "keywords": ["electric", "neon", "saturated", "bold", "artificial", "psychedelic", "pop", "striking", "flamboyant", "vivid"],
        "period_matches": ["Fauvism", "Pop Art", "Post-Impressionism (1885 - 1910)"]
    },
    "Muted & Naturalistic": {
        "keywords": ["earthy", "subdued", "soft", "gentle", "realistic", "understated", "organic", "subtle", "quiet", "neutral", "mellow"],
        "period_matches": ["Realism", "Dutch Golden Age", "Ancient (Before 800 BCE)"]
    }
}

# ============================================================================
# Visual Qualities
# ============================================================================

visuals = {
    "The Human Figure": {
        "keywords": ["idealized", "expressive", "deconstructed", "portrait", "body", "anatomy", "gesture", "character", "identity", "emotion"],
        "period_matches": ["Greek/Roman (800 BCE - 400 CE)", "Renaissance (1350 - 1600)", "Expressionism", "Cubism"]
    },
    "Nature & Landscape": {
        "keywords": ["sublime", "pastoral", "wild", "scientific", "botanical", "atmospheric", "scenic", "rural", "natural", "expansive"],
        "period_matches": ["Romantic (1800 - 1865)", "Impressionism (1865 - 1885)", "Hudson River School"]
    },
    "The Inner World": {
        "keywords": ["dreamlike", "subconscious", "visionary", "surreal", "symbolic", "psychological", "spiritual", "introspective", "mysterious", "fantastical"],
        "period_matches": ["Surrealism", "Symbolism", "Medieval (400 - 1350)"]
    },
    "Urban & Modern Life": {
        "keywords": ["city", "technology", "industrial", "social", "leisure", "critique", "modernity", "bustle", "architecture", "crowd"],
        "period_matches": ["Impressionism (1865 - 1885)", "Ashcan School", "Futurism", "Pop Art"]
    },
    "The Abstract Idea": {
        "keywords": ["form", "color", "geometry", "conceptual", "minimal", "pure", "reduction", "structure", "pattern", "nonrepresentational"],
        "period_matches": ["Abstract Expressionism", "Minimalism", "Conceptual Art", "Modern (1910 - 1960)"]
    },
    "Smooth & Polished": {
        "keywords": ["flawless", "marble", "glazed", "refined", "sleek", "seamless", "glossy", "finished", "perfect", "elegant"],
        "period_matches": ["Greek/Roman (800 BCE - 400 CE)", "Renaissance (1350 - 1600)", "Neoclassical (1750 - 1800)"]
    },
    "Textured & Painterly": {
        "keywords": ["impasto", "brushwork", "rough", "tactile", "layered", "expressive", "visible", "raw", "dynamic", "gestural"],
        "period_matches": ["Impressionism (1865 - 1885)", "Post-Impressionism (1885 - 1910)", "Abstract Expressionism"]
    },
    "Ornate & Decorative": {
        "keywords": ["intricate", "patterned", "detailed", "gilded", "embellished", "curvilinear", "lavish", "baroque", "rococo", "ornamental"],
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
    
    date_str = str(date_str).lower()
    
    # Handle BCE dates
    if 'bce' in date_str or 'bc' in date_str:
        return -1000
    
    # Try to find 4-digit years
    years = re.findall(r'\b\d{3,4}\b', date_str)
    if years:
        return int(years[0])
    
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
    for keyword in keyword_list[:12]:
        html += f'<span class="keyword-tag">{keyword}</span>'
    html += '</div>'
    return html

# ============================================================================
# Data Loading from Met API
# ============================================================================

@st.cache_data(ttl=3600)
def load_image(url):
    """Load image from URL"""
    try:
        if url:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
    except:
        pass
    return None

@st.cache_data(ttl=86400)  # Cache for 24 hours
def load_met_data(num_objects=500):
    """Load data directly from Met Museum API"""
    
    with st.spinner(f"🎨 Fetching {num_objects} artworks from the Met Museum API..."):
        try:
            # First, get list of object IDs that have images
            response = requests.get(
                "https://collectionapi.metmuseum.org/public/collection/v1/search",
                params={
                    "hasImages": True,
                    "q": "*"  # Search everything
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            object_ids = data.get('objectIDs', [])
            if not object_ids:
                st.error("No objects found from API")
                return None
            
            # Limit to requested number
            object_ids = object_ids[:num_objects]
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Fetch details for each object
            artworks = []
            for i, obj_id in enumerate(object_ids):
                status_text.text(f"Fetching artwork {i+1} of {len(object_ids)}...")
                
                try:
                    obj_response = requests.get(
                        f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}",
                        timeout=5
                    )
                    if obj_response.status_code == 200:
                        obj_data = obj_response.json()
                        
                        # Only include if it has an image
                        if obj_data.get('primaryImage'):
                            artworks.append({
                                'Object ID': obj_id,
                                'Title': obj_data.get('title', 'Untitled'),
                                'Artist Display Name': obj_data.get('artistDisplayName', 'Unknown'),
                                'Artist Nationality': obj_data.get('artistNationality', ''),
                                'Artist Begin Date': obj_data.get('artistBeginDate', ''),
                                'Artist End Date': obj_data.get('artistEndDate', ''),
                                'Object Date': obj_data.get('objectDate', ''),
                                'Object Begin Date': obj_data.get('objectBeginDate', 0),
                                'Object End Date': obj_data.get('objectEndDate', 0),
                                'Medium': obj_data.get('medium', ''),
                                'Dimensions': obj_data.get('dimensions', ''),
                                'Classification': obj_data.get('classification', ''),
                                'Department': obj_data.get('department', ''),
                                'Culture': obj_data.get('culture', ''),
                                'Period': obj_data.get('period', ''),
                                'Object URL': obj_data.get('objectURL', ''),
                                'Image URL': obj_data.get('primaryImage', '')
                            })
                except:
                    continue
                
                # Update progress
                progress_bar.progress((i + 1) / len(object_ids))
            
            progress_bar.empty()
            status_text.empty()
            
            if artworks:
                df = pd.DataFrame(artworks)
                
                # Add estimated period
                df['estimated_period'] = df['Object Date'].apply(estimate_period_from_date)
                
                st.success(f"✅ Successfully loaded {len(df)} artworks with images from the Met Museum!")
                return df
            else:
                st.error("No artworks could be loaded")
                return None
                
        except Exception as e:
            st.error(f"Error loading from Met API: {e}")
            return None

# Load the data
df = load_met_data(num_objects=300)  # Start with 300 artworks

if df is not None:
    # Sidebar
    with st.sidebar:
        st.header("📊 Collection Stats")
        st.metric("Total Artworks", f"{len(df):,}")
        
        if 'estimated_period' in df.columns:
            period_counts = df['estimated_period'].value_counts()
            st.metric("Artworks with Period", f"{period_counts.sum():,}")
        
        st.divider()
        
        st.header("ℹ️ About")
        st.markdown("""
        This app uses the **Met Museum API** to fetch real artworks.
        Data is cached for 24 hours for better performance.
        """)
        
        st.divider()
        
        # Settings
        st.header("🖼️ Settings")
        load_images = st.checkbox("Show images", value=True)
        num_artworks = st.slider("Artworks per page", 6, 30, 12, step=3)
    
    # Period Selection
    st.header("📜 STEP 1: Choose Your Art Historical Period")
    
    available_periods = ['All Periods'] + [p for p in art_periods.keys() 
                                          if p in df['estimated_period'].value_counts().index]
    
    selected_period = st.selectbox("Select period:", available_periods)
    
    if selected_period != 'All Periods' and selected_period in art_periods:
        period_info = art_periods[selected_period]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**📅 Years:** {period_info['years']}")
        with col2:
            st.markdown(f"**🎭 Personalities:** {', '.join(period_info['personality_matches'][:2])}")
        with col3:
            st.markdown(f"**🌊 Moods:** {', '.join(period_info['mood_matches'][:2])}")
        st.markdown(f"**📝 {period_info['description']}**")
    
    st.divider()
    
    # Personality, Mood, Visual Filters
    st.header("🎯 STEP 2: Refine by Personal Aesthetic")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        personality_choice = st.selectbox("🎭 Personality:", list(personality.keys()))
        st.markdown(display_keywords(personality[personality_choice]["keywords"]), unsafe_allow_html=True)
    
    with col2:
        mood_choice = st.selectbox("🌊 Mood:", list(moods.keys()))
        st.markdown(display_keywords(moods[mood_choice]["keywords"]), unsafe_allow_html=True)
    
    with col3:
        visual_choice = st.selectbox("🎨 Visual:", list(visuals.keys()))
        st.markdown(display_keywords(visuals[visual_choice]["keywords"]), unsafe_allow_html=True)
    
    st.divider()
    
    # Filter data
    filtered_df = df.copy()
    if selected_period != 'All Periods':
        filtered_df = filtered_df[filtered_df['estimated_period'] == selected_period]
    
    # Display results
    st.header(f"🎨 Found {len(filtered_df)} Artworks")
    
    if len(filtered_df) > 0:
        # Gallery View
        sample_size = min(num_artworks, len(filtered_df))
        display_df = filtered_df.sample(sample_size) if len(filtered_df) > sample_size else filtered_df
        
        # Create grid
        cols_per_row = 3
        for i in range(0, len(display_df), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                idx = i + j
                if idx < len(display_df):
                    artwork = display_df.iloc[idx]
                    
                    with cols[j]:
                        st.markdown('<div class="artwork-card">', unsafe_allow_html=True)
                        
                        # Title
                        title = str(artwork.get('Title', 'Untitled'))
                        st.markdown(f'<div class="artwork-title">{title[:60]}</div>', unsafe_allow_html=True)
                        
                        # Period badge
                        if artwork.get('estimated_period'):
                            st.markdown(f'<span class="period-badge">{artwork["estimated_period"]}</span>', 
                                      unsafe_allow_html=True)
                        
                        # Image
                        if load_images and artwork.get('Image URL'):
                            img = load_image(artwork['Image URL'])
                            if img:
                                st.markdown('<div class="artwork-image-container">', unsafe_allow_html=True)
                                st.image(img, use_container_width=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="artwork-image-container no-image">🖼️ Image unavailable</div>', 
                                          unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="artwork-image-container no-image">🖼️ No image available</div>', 
                                      unsafe_allow_html=True)
                        
                        # Artist
                        artist = artwork.get('Artist Display Name', 'Unknown')
                        if artist and artist != 'Unknown':
                            st.markdown(f'<div class="artwork-info">👨‍🎨 {artist[:40]}</div>', unsafe_allow_html=True)
                        
                        # Date
                        date = artwork.get('Object Date', '')
                        if date:
                            st.markdown(f'<div class="artwork-info">📅 {date[:30]}</div>', unsafe_allow_html=True)
                        
                        # Culture
                        culture = artwork.get('Culture', '')
                        if culture:
                            st.markdown(f'<div class="artwork-info">🌍 {culture[:30]}</div>', unsafe_allow_html=True)
                        
                        # Link
                        url = artwork.get('Object URL', '')
                        if url:
                            st.markdown(f'<div class="artwork-link"><a href="{url}" target="_blank">🔗 View at Met</a></div>', 
                                      unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("No artworks found for this period. Try another selection.")

else:
    st.error("""
    ⚠️ Could not load data from the Met API.
    
    This could be due to:
    - API rate limiting
    - Network connectivity issues
    
    Please try again in a few minutes.
    """)
