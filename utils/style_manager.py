import streamlit as st
from utils.themes import LIGHT_THEME, DARK_THEME
import os
import base64

import streamlit as st
import base64
import os

def display_header_image(
    image_path="assets/header_banner.png",
    title="Oil & Gas Data Dashboard",
    subtitle="Data-driven insights for exploration, production, and drilling performance",
    height="280px",
):
    """Display a full-width banner image with overlay title and subtitle."""
    if not os.path.exists(image_path):
        st.warning(f"⚠️ Image not found at: {image_path}")
        return

    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_base64 = base64.b64encode(img_bytes).decode()

    st.markdown(
        f"""
        <style>
        .hero-banner {{
            position: relative;
            width: 100%;
            height: {height};
            overflow: hidden;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }}

        .hero-banner img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            filter: brightness(70%);
        }}

        .hero-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            text-align: center;
            padding: 0 10px;
        }}

        .hero-text h1 {{
            font-size: 3.1rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
            text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.5);
        }}

        .hero-text p {{
            font-size: 1.2rem;
            font-weight: 400;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.4);
        }}
        </style>

        <div class="hero-banner">
            <img src="data:image/png;base64,{img_base64}" alt="Header Banner">
            <div class="hero-text">
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def apply_theme(theme="light"):
    """Apply consistent theming across the Streamlit app."""
    theme_dict = LIGHT_THEME if theme == "light" else DARK_THEME

    # Apply global color variables
    st.markdown(
        f"""
        <style>
        :root {{
            --primary-color: {theme_dict['primary_color']};
            --secondary-color: {theme_dict['secondary_color']};
            --background-color: {theme_dict['background']};
            --text-color: {theme_dict['text']};
            --card-bg: {theme_dict['card_bg']};
        }}

        html, body, [class*="css"] {{
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: 'Segoe UI', sans-serif;
        }}

        /* KPI Card styling */
        div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {{
            color: var(--text-color);
        }}

        /* Buttons and widgets */
        .stButton>button {{
            background-color: var(--primary-color);
            color: white;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
        }}

        .stButton>button:hover {{
            background-color: var(--secondary-color);
            color: white;
        }}

        /* Tabs */
        div[data-baseweb="tab-list"] button {{
            background-color: var(--card-bg);
            color: var(--text-color);
            border-radius: 10px;
            margin: 0 3px;
            padding: 8px 16px;
        }}
        div[data-baseweb="tab-list"] button[aria-selected="true"] {{
            background-color: var(--primary-color);
            color: white;
        }}

        /* DataFrame tables */
        .stDataFrame, .stTable {{
            background-color: var(--card-bg);
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_css(file_path="utils/custom.css"):
    """Load custom CSS for layout and spacing."""
    if os.path.exists(file_path):
        with open(file_path) as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)