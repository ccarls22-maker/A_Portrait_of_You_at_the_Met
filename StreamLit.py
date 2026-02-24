import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
from PIL import Image
from io import BytesIO
import time

# Page config
st.set_page_config(
    page_title="Met Museum Personal Curator",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS (keeping your original CSS - truncated for brevity)
st.markdown("""
<style>
    /* ... keep your existing CSS ... */
</style>
""", unsafe_allow_html=True)

st.title("🎨 Met Museum Personal Curator")
st.markdown("Create your personalized art viewing experience by exploring the Metropolitan Museum of Art's collection through different artistic lenses.")

# Function to get image URL from Met object ID
@st.cache_data(ttl=3600, show_spinner=False)
def get_image_url(object_id):
    """Fetch image URL from Met Museum API"""
    try:
        if pd.isna(object_id):
            return None
        try:
            if isinstance(object_id, str):
                object_id = object_id.replace(',', '').strip()
            obj_id = int(float(object_id))
        except (ValueError, TypeError):
            return None
            
        response = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('primaryImage'):
                return data['primaryImage']
            elif data.get('additionalImages') and len(data['additionalImages']) > 0:
                return data['additionalImages'][0]
        return None
    except Exception:
        return None

# Function to load and cache images
@st.cache_data(ttl=3600, show_spinner=False)
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

# NEW: Efficient random sampling using chunking
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_sampled_data(sample_size=15000, random_seed=42):
    """Load a random sample of MetObjects.csv efficiently using chunking"""
    try:
        github_url = "https://media.githubusercontent.com/media/ccarls22-maker/A_Portrait_of_You_at_the_Met/main/MetObjects.csv"
        
        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Fetching file information...")
        
        # First, get the total number of rows by reading just the first chunk
        chunk_iterator = pd.read_csv(github_url, chunksize=10000, low_memory=False)
        total_rows = 0
        column_names = None
        
        # Count total rows efficiently
        status_text.text("Counting total rows...")
        for i, chunk in enumerate(chunk_iterator):
            if i == 0:
                column_names = chunk.columns.tolist()
            total_rows += len(chunk)
            progress_bar.progress(min(0.1, (i * 10000) / 500000))  # Cap at 10%
        
        status_text.text(f"Total rows: {total_rows:,}. Sampling {sample_size:,} rows...")
        
        # Generate random row indices to sample
        np.random.seed(random_seed)
        sampled_indices = sorted(np.random.choice(total_rows, size=min(sample_size, total_rows), replace=False))
        
        # Reset chunk iterator
        chunk_iterator = pd.read_csv(github_url, chunksize=10000, low_memory=False)
        
        # Collect sampled rows
        sampled_rows = []
        current_row = 0
        chunk_count = 0
        
        for chunk in chunk_iterator:
            chunk_count += 1
            # Find indices in this chunk that we want to sample
            chunk_start = current_row
            chunk_end = current_row + len(chunk)
            
            # Find which sampled indices fall in this chunk
            indices_in_chunk = [idx - chunk_start for idx in sampled_indices 
                              if chunk_start <= idx < chunk_end]
            
            if indices_in_chunk:
                sampled_rows.append(chunk.iloc[indices_in_chunk])
            
            current_row = chunk_end
            progress_bar.progress(min(0.1 + 0.9 * (chunk_count * 10000) / total_rows, 1.0))
            status_text.text(f"Processing chunk {chunk_count}... ({len(sampled_rows)} rows collected)")
        
        # Combine all sampled chunks
        if sampled_rows:
            df = pd.concat(sampled_rows, ignore_index=True)
        else:
            df = pd.DataFrame()
        
        progress_bar.empty()
        status_text.empty()
        
        if len(df) == 0:
            st.error("No data could be sampled.")
            return None
        
        # Check for Object ID column
        object_id_col = None
        possible_names = ['Object ID', 'ObjectID', 'object id', 'object_id', 'Id', 'ID']
        for name in possible_names:
            if name in df.columns:
                object_id_col = name
                break
        
        if object_id_col and object_id_col != 'Object ID':
            df = df.rename(columns={object_id_col: 'Object ID'})
        
        # Keep only necessary columns
        keep_cols = []
        if 'Object ID' in df.columns:
            keep_cols.append('Object ID')
        
        for col in ['Title', 'Artist Display Name', 'Object Date', 
                   'Classification', 'Department', 'Object URL', 'Medium']:
            if col in df.columns:
                keep_cols.append(col)
        
        if keep_cols:
            df = df[keep_cols]
        
        # Clean up data
        df = df.replace({np.nan: None})
        
        if 'Title' in df.columns:
            df = df[df['Title'].notna()]
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# NEW: Pre-calculated statistics for faster filtering
@st.cache_data
def get_filter_options(df):
    """Pre-calculate filter options for faster UI rendering"""
    options = {}
    if df is not None:
        if 'Department' in df.columns:
            options['departments'] = df['Department'].value_counts().head(20).index.tolist()
        if 'Classification' in df.columns:
            options['classifications'] = df['Classification'].value_counts().head(20).index.tolist()
    return options

# NEW: Faster image checking with batch processing
@st.cache_data(ttl=3600)
def batch_check_images(object_ids, max_images=50):
    """Check multiple images at once with rate limiting"""
    images = []
    for i, obj_id in enumerate(object_ids[:max_images]):
        if i > 0 and i % 10 == 0:  # Rate limit
            time.sleep(0.5)
        if pd.notna(obj_id):
            url = get_image_url(obj_id)
            if url:
                images.append((obj_id, url))
    return dict(images)

# Load data with progress feedback
with st.spinner("Loading Met Museum collection... This may take a moment."):
    df = load_sampled_data(sample_size=15000)

# Get filter options
if df is not None:
    filter_options = get_filter_options(df)

# Expanded word banks with more keywords
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

if df is not None and len(df) > 0:
    # Show basic info in sidebar
    with st.sidebar:
        st.header("📊 Collection Stats")
        st.metric("Sampled Artworks", f"{len(df):,}")
        
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
        st.markdown("**Related keywords:**")
        st.markdown(display_keywords(personality[personality_choice]), unsafe_allow_html=True)
        
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
        st.markdown("**Related keywords:**")
        st.markdown(display_keywords(moods[mood_choice]), unsafe_allow_html=True)
        
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
        st.markdown("**Related keywords:**")
        st.markdown(display_keywords(visuals[visual_choice]), unsafe_allow_html=True)
        
        with st.expander("See all visual qualities"):
            for v_type, keywords in visuals.items():
                if v_type != visual_choice:
                    st.markdown(f"**{v_type}**")
                    st.markdown(display_keywords(keywords), unsafe_allow_html=True)
    
    st.divider()
    
    # Additional filters
    with st.expander("🔍 Additional Filters (Optional)", expanded=False):
        col4, col5 = st.columns(2)
        
        with col4:
            if 'Department' in df.columns:
                selected_dept = st.multiselect("Filter by Department", filter_options.get('departments', []))
            else:
                selected_dept = []
        
        with col5:
            if 'Classification' in df.columns:
                selected_class = st.multiselect("Filter by Classification", filter_options.get('classifications', []))
            else:
                selected_class = []
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_dept and 'Department' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Department'].isin(selected_dept)]
    
    if selected_class and 'Classification' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Classification'].isin(selected_class)]
    
    # Show results
    st.header(f"🎨 Found {len(filtered_df):,} Artworks in Sample")
    
    if len(filtered_df) > 0:
        tab1, tab2 = st.tabs(["Gallery View", "Data View"])
        
        with tab1:
            sample_size = min(num_artworks, len(filtered_df))
            
            if load_images:
                with st.spinner("Loading artwork images..."):
                    # Take a sample of artworks to check for images
                    sample_artworks = filtered_df.sample(min(50, len(filtered_df))).copy()
                    
                    # Batch check for images
                    object_ids = sample_artworks['Object ID'].tolist() if 'Object ID' in sample_artworks.columns else []
                    image_urls = batch_check_images(object_ids, max_images=50)
                    
                    # Add image URLs to dataframe
                    sample_artworks['image_url'] = sample_artworks['Object ID'].map(image_urls)
                    
                    # Filter to those with images
                    artworks_with_images = sample_artworks[sample_artworks['image_url'].notna()]
                    
                    if len(artworks_with_images) >= 3:
                        display_artworks = artworks_with_images.head(sample_size)
                    else:
                        display_artworks = filtered_df.sample(sample_size)
                        st.info("Limited images available. Showing artworks without images.")
            else:
                display_artworks = filtered_df.sample(sample_size)
            
            # Grid layout
            cols_per_row = 3
            rows = (len(display_artworks) + cols_per_row - 1) // cols_per_row
            
            for row in range(rows):
                cols = st.columns(cols_per_row)
                start_idx = row * cols_per_row
                end_idx = min(start_idx + cols_per_row, len(display_artworks))
                
                for col_idx in range(start_idx, end_idx):
                    with cols[col_idx - start_idx]:
                        artwork = display_artworks.iloc[col_idx]
                        
                        st.markdown('<div class="artwork-card">', unsafe_allow_html=True)
                        
                        title = artwork.get('Title', 'Untitled')
                        if title:
                            st.markdown(f'<div class="artwork-title">{str(title)[:60]}</div>', unsafe_allow_html=True)
                        
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
                        
                        artist = artwork.get('Artist Display Name', 'Unknown')
                        if artist and artist != 'Unknown':
                            st.markdown(f'<div class="artwork-info">👨‍🎨 {str(artist)[:40]}</div>', unsafe_allow_html=True)
                        
                        date = artwork.get('Object Date', '')
                        if date:
                            st.markdown(f'<div class="artwork-info">📅 {str(date)[:30]}</div>', unsafe_allow_html=True)
                        
                        dept = artwork.get('Department', '')
                        if dept:
                            st.markdown(f'<div class="artwork-info">🏛️ {str(dept)[:30]}</div>', unsafe_allow_html=True)
                        
                        object_url = artwork.get('Object URL')
                        if object_url:
                            st.markdown(f'<div class="artwork-link"><a href="{object_url}" target="_blank">🔗 View on Met Website</a></div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            display_cols = ['Title', 'Artist Display Name', 'Object Date', 
                          'Classification', 'Department', 'Object URL']
            available_cols = [col for col in display_cols if col in filtered_df.columns]
            if available_cols:
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
