import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
from PIL import Image
from io import BytesIO

# Page config
st.set_page_config(
    page_title="Met Museum Personal Curator",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS (keeping your original CSS exactly as is)
st.markdown("""
<style>
    /* Make the entire app background white */
    .stApp {
        background-color: white;
    }
    
    /* Make the main content area white */
    .main > div {
        background-color: white;
    }
    
    /* Style the sidebar to be white with dark text */
    section[data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #e0e0e0;  /* Optional: adds a subtle border */
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
    
    /* Style sidebar widgets */
    section[data-testid="stSidebar"] .stCheckbox label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #1E1E1E !important;
    }
    
    /* Style sidebar metric */
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] p,
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] p {
        color: #1E1E1E !important;
    }
    
    /* Style sidebar expander */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        color: #1E1E1E !important;
        background-color: white !important;
    }
    
    /* Style all text for white background */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
        color: #1E1E1E !important;
    }
    
    /* Style for metric labels and values */
    [data-testid="stMetricLabel"] p, [data-testid="stMetricValue"] p {
        color: #1E1E1E !important;
    }
    
    /* Style for selectbox labels and text */
    .stSelectbox label, .stSelectbox div[data-baseweb="select"] span {
        color: #1E1E1E !important;
    }
    
    /* Style for multiselect text */
    .stMultiSelect label, .stMultiSelect div[data-baseweb="select"] span {
        color: #1E1E1E !important;
    }
    
    /* Style for slider text */
    .stSlider label, .stSlider span {
        color: #1E1E1E !important;
    }
    
    /* Style for expander text */
    .streamlit-expanderHeader {
        color: #1E1E1E !important;
    }
    
    /* Style for tab text */
    .stTabs [data-baseweb="tab-list"] button p {
        color: #1E1E1E !important;
    }
    
    /* Style for info/warning/error messages */
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
</style>
""", unsafe_allow_html=True)

st.title("🎨 Met Museum Personal Curator")
st.markdown("Create your personalized art viewing experience by exploring the Metropolitan Museum of Art's collection through different artistic lenses.")

# Function to get image URL from Met object ID
# NEW: Load data from GitHub using the correct LFS URL
# NEW: Load data from GitHub with multiple fallback options
@st.cache_data
def load_data_from_github():
    """Load MetObjects.csv from GitHub repository with multiple fallback options"""
    
    # List of possible URLs to try (in order of preference)
    urls_to_try = [
        "https://media.githubusercontent.com/media/ccarls22-maker/A_Portrait_of_You_at_the_Met/main/MetObjects.csv",
        "https://raw.githubusercontent.com/ccarls22-maker/A_Portrait_of_You_at_the_Met/main/MetObjects.csv",
        "https://github.com/ccarls22-maker/A_Portrait_of_You_at_the_Met/raw/main/MetObjects.csv"
    ]
    
    for url in urls_to_try:
        try:
            with st.spinner(f"Trying to load from: {url.split('/')[-1]}"):
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Check if we got an LFS pointer (small file starting with "version")
                first_chunk = next(response.iter_lines()).decode('utf-8', errors='ignore')
                if first_chunk.startswith('version https://git-lfs'):
                    st.warning("Got LFS pointer, trying next URL...")
                    continue
                
                # Reset the response stream
                response = requests.get(url, stream=True, timeout=60)
                
                # Load CSV - increase nrows for more artworks
                df = pd.read_csv(response.raw, 
                               nrows=100000,  # Try 100,000 rows
                               low_memory=False,
                               on_bad_lines='skip')
                
                # Keep necessary columns
                needed_cols = ['Object ID', 'Title', 'Artist Display Name', 'Object Date', 
                              'Classification', 'Department', 'Object URL', 'Medium']
                
                available_cols = [col for col in needed_cols if col in df.columns]
                if available_cols:
                    df = df[available_cols]
                
                # Clean up
                df = df.replace({np.nan: None})
                if 'Title' in df.columns:
                    df = df[df['Title'].notna()]
                
                st.success(f"✅ Successfully loaded {len(df):,} artworks!")
                return df
                
        except Exception as e:
            st.warning(f"URL {url} failed: {str(e)[:50]}...")
            continue
    
    st.error("All download attempts failed.")
    return None
        
# Load data from GitHub instead of local file
df = load_data_from_github()

# Fallback to original local file method if GitHub fails
if df is None:
    st.warning("GitHub download failed. Trying local file...")
    try:
        file_path = r"C:\Users\court\Downloads\Data_Clubs_Project_1\archive\MetObjects.csv"
        if os.path.exists(file_path):
            usecols = ['Object ID', 'Title', 'Artist Display Name', 'Object Date', 
                      'Classification', 'Department', 'Object URL', 'Medium']
            df = pd.read_csv(file_path, usecols=lambda x: x in usecols, low_memory=False, nrows=50000)
            df = df.replace({np.nan: None})
        else:
            st.error("Local file not found either.")
    except Exception as e:
        st.error(f"Error loading local file: {e}")

# Rest of your original code remains exactly the same from here onward
if df is not None:
    # Show basic info in sidebar
    with st.sidebar:
        st.header("📊 Collection Stats")
        st.metric("Total Artworks", f"{len(df):,}")
        
        st.divider()
        
        st.header("ℹ️ About the Filters")
        st.markdown("""
        **Personality Archetypes** - Your foundational artistic lens
        **Mood/Vibes** - The emotional atmosphere you seek
        **Visual Qualities** - What you want to see in the artwork
        """)
        
        st.divider()
        
        # Add option to toggle image loading
        st.header("🖼️ Settings")
        load_images = st.checkbox("Load artwork images", value=True, 
                                 help="Disable if the app is running slowly")
        
        # Number of artworks to display
        num_artworks = st.slider("Number of artworks to display", 3, 18, 9, step=3)
    
    # Expanded word banks with more keywords (your original)
    personality = {
        "Classicist": ["order", "balance", "clarity", "timeless", "harmony", "symmetry", "ideal", "perfection", "restraint", "tradition", "proportion", "discipline", "rational", "structured"],
        "Romantic": ["emotion", "imagination", "mystery", "nature", "passion", "drama", "sublime", "intuition", "wild", "longing", "intensity", "fantasy", "awe", "turbulence", "poetic"],
        "Realist": ["truth", "authenticity", "grounded", "pragmatic", "observation", "unvarnished", "direct", "honest", "everyday", "ordinary", "candid", "objective", "documentary"],
        "Innovator": ["experimental", "abstract", "intellectual", "bold", "unconventional", "avant-garde", "radical", "new", "inventive", "conceptual", "challenging", "progressive", "pioneering"],
        "Symbolist": ["metaphor", "spiritual", "dream", "mystical", "hidden", "coded", "visionary", "esoteric", "subconscious", "otherworldly", "enigmatic", "poetic", "mythic"],
        "Hedonist": ["sensual", "decorative", "pleasure", "beauty", "elegance", "ornate", "lush", "indulgent", "playful", "charming", "delightful", "opulent", "graceful", "sumptuous"]
    }
    
    moods = {
        "Dynamic & Dramatic": ["energetic", "intense", "theatrical", "bold", "movement", "action", "contrast", "explosive", "vigorous", "lively", "forceful", "passionate"],
        "Calm & Balanced": ["serene", "peaceful", "tranquil", "restful", "meditative", "gentle", "soothing", "harmonious", "quiet", "still", "composed", "poised"],
        "Chaotic & Raw": ["fragmented", "wild", "unrestrained", "expressive", "rough", "spontaneous", "turbulent", "primal", "visceral", "untamed", "emotional", "jagged"],
        "Warm & Golden": ["radiant", "glowing", "sunlit", "rich", "golden", "fiery", "warm", "amber", "luminous", "vibrant", "passionate", "cozy"],
        "Cool & Ethereal": ["icy", "silvery", "misty", "pale", "delicate", "airy", "dreamy", "soft", "ghostly", "tranquil", "celestial", "serene"],
        "Vibrant & Unnatural": ["electric", "neon", "saturated", "bold", "artificial", "psychedelic", "pop", "striking", "flamboyant", "unconventional", "vivid", "dazzling"],
        "Muted & Naturalistic": ["earthy", "subdued", "soft", "gentle", "realistic", "understated", "organic", "subtle", "quiet", "neutral", "faded", "mellow"]
    }
    
    visuals = {
        "The Human Figure": ["idealized", "expressive", "deconstructed", "portrait", "body", "anatomy", "gesture", "character", "identity", "emotion", "narrative"],
        "Nature & Landscape": ["sublime", "pastoral", "wild", "scientific", "botanical", "atmospheric", "scenic", "rural", "natural", "expansive", "tranquil", "dramatic"],
        "The Inner World": ["dreamlike", "subconscious", "visionary", "surreal", "symbolic", "psychological", "spiritual", "introspective", "mysterious", "fantastical", "meditative"],
        "Urban & Modern Life": ["city", "technology", "industrial", "social", "leisure", "critique", "modernity", "bustle", "architecture", "crowd", "nightlife", "contemporary"],
        "The Abstract Idea": ["form", "color", "geometry", "conceptual", "minimal", "pure", "reduction", "structure", "pattern", "nonrepresentational", "experimental"],
        "Smooth & Polished": ["flawless", "marble", "glazed", "refined", "sleek", "seamless", "glossy", "finished", "perfect", "elegant", "pristine"],
        "Textured & Painterly": ["impasto", "brushwork", "rough", "tactile", "layered", "expressive", "visible", "raw", "dynamic", "gestural", "thick", "lively"],
        "Ornate & Decorative": ["intricate", "patterned", "detailed", "gilded", "embellished", "curvilinear", "lavish", "baroque", "rococo", "filigree", "ornamental"]
    }
    
    def display_keywords(keyword_list):
        """Display keywords as styled tags"""
        html = '<div class="word-cloud">'
        for keyword in keyword_list:
            html += f'<span class="keyword-tag">{keyword}</span>'
        html += '</div>'
        return html
    
    # Main interface
    st.header("🎯 Choose Your Preferences")
    
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
        # Show keywords for selected personality
        st.markdown("**Related keywords:**")
        st.markdown(display_keywords(personality[personality_choice]), unsafe_allow_html=True)
        
        # Show all other personalities in an expander
        with st.expander("See all personality types"):
            for p_type, keywords in personality.items():
                if p_type != personality_choice:
                    st.markdown(f"**{p_type}**")
                    st.markdown(display_keywords(keywords), unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="filter-header">🌊 MOOD & ENERGY</p>', unsafe_allow_html=True)
        mood_choice = st.selectbox(
            "Select your desired mood:",
            list(moods.keys()),
            label_visibility="collapsed",
            key="mood_select"
        )
        # Show keywords for selected mood
        st.markdown("**Related keywords:**")
        st.markdown(display_keywords(moods[mood_choice]), unsafe_allow_html=True)
        
        # Show all other moods in an expander
        with st.expander("See all mood types"):
            for m_type, keywords in moods.items():
                if m_type != mood_choice:
                    st.markdown(f"**{m_type}**")
                    st.markdown(display_keywords(keywords), unsafe_allow_html=True)
    
    with col3:
        st.markdown('<p class="filter-header">🎨 VISUAL QUALITIES</p>', unsafe_allow_html=True)
        visual_choice = st.selectbox(
            "Select visual qualities:",
            list(visuals.keys()),
            label_visibility="collapsed",
            key="visual_select"
        )
        # Show keywords for selected visual quality
        st.markdown("**Related keywords:**")
        st.markdown(display_keywords(visuals[visual_choice]), unsafe_allow_html=True)
        
        # Show all other visual qualities in an expander
        with st.expander("See all visual qualities"):
            for v_type, keywords in visuals.items():
                if v_type != visual_choice:
                    st.markdown(f"**{v_type}**")
                    st.markdown(display_keywords(keywords), unsafe_allow_html=True)
    
    st.divider()
    
    # Simplified additional filters - REMOVED date range
    with st.expander("🔍 Additional Filters (Optional)", expanded=False):
        col4, col5 = st.columns(2)
        
        with col4:
            if 'Department' in df.columns:
                # Get top 20 departments by count
                dept_counts = df['Department'].value_counts().head(20).index.tolist()
                selected_dept = st.multiselect("Filter by Department", dept_counts)
        
        with col5:
            if 'Classification' in df.columns:
                # Get top 20 classifications
                class_counts = df['Classification'].value_counts().head(20).index.tolist()
                selected_class = st.multiselect("Filter by Classification", class_counts)
    
    # Apply filters
    filtered_df = df.copy()
    
    # Apply department filter
    if 'selected_dept' in locals() and selected_dept:
        filtered_df = filtered_df[filtered_df['Department'].isin(selected_dept)]
    
    # Apply classification filter
    if 'selected_class' in locals() and selected_class:
        filtered_df = filtered_df[filtered_df['Classification'].isin(selected_class)]
    
    # Show results
    st.header(f"🎨 Found {len(filtered_df):,} Artworks")
    
    if len(filtered_df) > 0:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Gallery View", "Data View"])
        
        with tab1:
            # Show sample artworks in a grid
            sample_size = min(num_artworks, len(filtered_df))
            
            # Try to get artworks with images first if load_images is True
            if load_images:
                with st.spinner("Loading artwork images..."):
                    # Take a sample
                    sample_artworks = filtered_df.sample(min(50, len(filtered_df))).copy()
                    
                    # Try to get images for a subset
                    artworks_with_images = []
                    
                    # Create progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, (_, artwork) in enumerate(sample_artworks.iterrows()):
                        status_text.text(f"Checking for images: {idx+1}/{len(sample_artworks)}")
                        
                        if pd.notna(artwork.get('Object ID')):
                            img_url = get_image_url(artwork['Object ID'])
                            if img_url:
                                artwork_dict = artwork.to_dict()
                                artwork_dict['image_url'] = img_url
                                artworks_with_images.append(artwork_dict)
                        
                        # Update progress
                        progress_bar.progress((idx + 1) / len(sample_artworks))
                        
                        # Break if we have enough
                        if len(artworks_with_images) >= sample_size:
                            break
                    
                    # Clean up progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # If we found images, use those
                    if len(artworks_with_images) >= 3:
                        display_artworks = pd.DataFrame(artworks_with_images[:sample_size])
                    else:
                        # Fall back to random sample without images
                        display_artworks = filtered_df.sample(sample_size)
                        st.info("Limited images available. Showing artworks without images.")
            
            else:
                # If load_images is False, just show random sample
                display_artworks = filtered_df.sample(sample_size)
            
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
                        if title:
                            st.markdown(f'<div class="artwork-title">{str(title)[:60]}</div>', unsafe_allow_html=True)
                        
                        # Image
                        if load_images and 'image_url' in artwork and artwork['image_url']:
                            img = load_image_from_url(artwork['image_url'])
                            if img:
                                st.markdown('<div class="artwork-image-container">', unsafe_allow_html=True)
                                st.image(img, use_container_width=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="artwork-image-container no-image">🖼️ Image unavailable</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="artwork-image-container no-image">🖼️ No image available</div>', unsafe_allow_html=True)
                        
                        # Artist
                        artist = artwork.get('Artist Display Name', 'Unknown')
                        if artist and artist != 'Unknown':
                            st.markdown(f'<div class="artwork-info">👨‍🎨 {str(artist)[:40]}</div>', unsafe_allow_html=True)
                        
                        # Date
                        date = artwork.get('Object Date', '')
                        if date:
                            st.markdown(f'<div class="artwork-info">📅 {str(date)[:30]}</div>', unsafe_allow_html=True)
                        
                        # Department/Classification
                        dept = artwork.get('Department', '')
                        if dept:
                            st.markdown(f'<div class="artwork-info">🏛️ {str(dept)[:30]}</div>', unsafe_allow_html=True)
                        
                        # Link
                        object_url = artwork.get('Object URL')
                        if object_url:
                            st.markdown(f'<div class="artwork-link"><a href="{object_url}" target="_blank">🔗 View on Met Website</a></div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            # Show data table
            display_cols = ['Title', 'Artist Display Name', 'Object Date', 
                          'Classification', 'Department', 'Object URL']
            available_cols = [col for col in display_cols if col in filtered_df.columns]
            st.dataframe(
                filtered_df[available_cols].head(100),
                use_container_width=True,
                hide_index=True
            )
            if len(filtered_df) > 100:
                st.caption(f"Showing first 100 of {len(filtered_df)} artworks")
    else:
        st.warning("No artworks found with current filters. Try adjusting your selections.")

else:
    st.error("""
    ⚠️ Could not load the data file from GitHub. Please check:
    1. Your GitHub repository is public
    2. The file 'MetObjects.csv' exists in the root of your repository
    3. You have a stable internet connection
    """)
