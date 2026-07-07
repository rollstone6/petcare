#!/usr/bin/env python3
"""
Kawaii SVG Avatar Generator for Pet Breeds
==========================================
Generate consistent kawaii-style SVG avatars with systematic feature variation.
Outputs SVG files, optionally converts to PNG/webp via cairosvg.

Usage:
    python generate_avatars.py --breeds-file breeds.json --output-dir ../frontend/public/avatars
    python generate_avatars.py --all  # uses built-in breed definitions
"""

import json
import os
import sys
import argparse
from pathlib import Path

# ============================================================
# EAR SHAPE GENERATORS
# ============================================================

def ears_pointed(fur_color):
    return (
        f'<polygon points="60,65 70,35 80,65" fill="{fur_color}"/>'
        f'<polygon points="140,65 130,35 120,65" fill="{fur_color}"/>'
    )

def ears_floppy(fur_color):
    return (
        f'<ellipse cx="48" cy="110" rx="20" ry="28" fill="{fur_color}" transform="rotate(-15 48 110)"/>'
        f'<ellipse cx="152" cy="110" rx="20" ry="28" fill="{fur_color}" transform="rotate(15 152 110)"/>'
    )

def ears_round(fur_color):
    return (
        f'<circle cx="65" cy="62" r="14" fill="{fur_color}"/>'
        f'<circle cx="135" cy="62" r="14" fill="{fur_color}"/>'
    )

def ears_folded(fur_color):
    return (
        f'<ellipse cx="62" cy="62" rx="16" ry="10" fill="{fur_color}" transform="rotate(-30 62 62)"/>'
        f'<ellipse cx="138" cy="62" rx="16" ry="10" fill="{fur_color}" transform="rotate(30 138 62)"/>'
    )

def ears_curled(fur_color):
    return (
        f'<path d="M58,68 Q50,40 68,50" stroke="{fur_color}" stroke-width="8" fill="none" stroke-linecap="round"/>'
        f'<path d="M142,68 Q150,40 132,50" stroke="{fur_color}" stroke-width="8" fill="none" stroke-linecap="round"/>'
    )

def ears_bat(fur_color):
    return (
        f'<polygon points="55,70 60,30 80,60" fill="{fur_color}"/>'
        f'<polygon points="145,70 140,30 120,60" fill="{fur_color}"/>'
    )

def ears_long_floppy(fur_color):
    return (
        f'<ellipse cx="42" cy="120" rx="18" ry="35" fill="{fur_color}" transform="rotate(-10 42 120)"/>'
        f'<ellipse cx="158" cy="120" rx="18" ry="35" fill="{fur_color}" transform="rotate(10 158 120)"/>'
    )

def ears_big_pointed(fur_color):
    return (
        f'<polygon points="52,72 60,20 82,65" fill="{fur_color}"/>'
        f'<polygon points="148,72 140,20 118,65" fill="{fur_color}"/>'
    )

def ears_long_ears(fur_color):
    """Long upright ears (rabbit, etc.)"""
    return (
        f'<ellipse cx="72" cy="40" rx="12" ry="32" fill="{fur_color}" transform="rotate(-8 72 40)"/>'
        f'<ellipse cx="128" cy="40" rx="12" ry="32" fill="{fur_color}" transform="rotate(8 128 40)"/>'
        f'<ellipse cx="72" cy="40" rx="7" ry="24" fill="#FFB6C1" opacity="0.5" transform="rotate(-8 72 40)"/>'
        f'<ellipse cx="128" cy="40" rx="7" ry="24" fill="#FFB6C1" opacity="0.5" transform="rotate(8 128 40)"/>'
    )

def ears_tiny_round(fur_color):
    """Small round ears (hamster, hedgehog)"""
    return (
        f'<circle cx="70" cy="72" r="10" fill="{fur_color}"/>'
        f'<circle cx="130" cy="72" r="10" fill="{fur_color}"/>'
        f'<circle cx="70" cy="72" r="5" fill="#FFB6C1" opacity="0.5"/>'
        f'<circle cx="130" cy="72" r="5" fill="#FFB6C1" opacity="0.5"/>'
    )

def ears_no_visible(fur_color):
    """No visible external ears (fish, turtle, reptile)"""
    return ""

def ears_crown(fur_color):
    """Crest/crown feathers (bird)"""
    return (
        f'<polygon points="90,50 95,25 100,50" fill="{fur_color}"/>'
        f'<polygon points="100,48 105,20 110,48" fill="{fur_color}" opacity="0.8"/>'
        f'<polygon points="108,52 115,28 118,52" fill="{fur_color}" opacity="0.6"/>'
    )

# Map ear type string to function
EAR_FUNCTIONS = {
    "pointed": ears_pointed,
    "floppy": ears_floppy,
    "round": ears_round,
    "folded": ears_folded,
    "curled": ears_curled,
    "bat": ears_bat,
    "long_floppy": ears_long_floppy,
    "big_pointed": ears_big_pointed,
    "long_ears": ears_long_ears,
    "tiny_round": ears_tiny_round,
    "no_visible": ears_no_visible,
    "crown": ears_crown,
}

# ============================================================
# FEATURE OVERLAY GENERATORS
# ============================================================

def feature_smile(fur_color, face_cx=100, face_cy=115):
    return f'<path d="M96 109 Q100 113 104 109" stroke="#1C1917" stroke-width="1.8" fill="none" stroke-linecap="round"/>'

def feature_tongue(fur_color, face_cx=100, face_cy=115):
    return (
        f'<path d="M96 109 Q100 113 104 109" stroke="#1C1917" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        f'<ellipse cx="100" cy="114" rx="4" ry="5" fill="#F87171"/>'
    )

def feature_mask(fur_color, face_cx=100, face_cy=115):
    return f'<ellipse cx="100" cy="100" rx="40" ry="30" fill="#4B5563" opacity="0.3"/>'

def feature_dark_face(fur_color, face_cx=100, face_cy=115):
    return f'<ellipse cx="100" cy="110" rx="35" ry="25" fill="#1C1917" opacity="0.4"/>'

def feature_fluffy(fur_color, face_cx=100, face_cy=115):
    return f'<circle cx="100" cy="115" r="58" fill="{fur_color}" opacity="0.3"/>'

def feature_beard(fur_color, face_cx=100, face_cy=115):
    return (
        f'<ellipse cx="100" cy="130" rx="20" ry="12" fill="#E5E7EB" opacity="0.8"/>'
        f'<rect x="82" y="82" width="36" height="6" rx="3" fill="#E5E7EB" opacity="0.7"/>'
    )

def feature_long_hair(fur_color, face_cx=100, face_cy=115):
    return f'<ellipse cx="100" cy="130" rx="60" ry="35" fill="{fur_color}" opacity="0.4"/>'

def feature_flat_face(fur_color, face_cx=100, face_cy=115):
    return f'<ellipse cx="100" cy="112" rx="42" ry="35" fill="{fur_color}" opacity="0.3"/>'

def feature_big_eyes(fur_color, face_cx=100, face_cy=115):
    """Override: larger eyes drawn in the main face section"""
    return ""

def feature_tan_marks(fur_color, face_cx=100, face_cy=115):
    return (
        f'<ellipse cx="70" cy="100" rx="10" ry="12" fill="#D97706" opacity="0.4"/>'
        f'<ellipse cx="130" cy="100" rx="10" ry="12" fill="#D97706" opacity="0.4"/>'
        f'<ellipse cx="100" cy="125" rx="20" ry="8" fill="#D97706" opacity="0.3"/>'
    )

def feature_white_collar(fur_color, face_cx=100, face_cy=115):
    return f'<ellipse cx="100" cy="140" rx="35" ry="15" fill="white" opacity="0.6"/>'

def feature_tricolor(fur_color, face_cx=100, face_cy=115):
    return (
        f'<ellipse cx="80" cy="110" rx="18" ry="20" fill="#FEFEFE" opacity="0.4"/>'
        f'<ellipse cx="120" cy="110" rx="18" ry="20" fill="#1C1917" opacity="0.3"/>'
    )

def feature_egg_head(fur_color, face_cx=100, face_cy=115):
    """Elongated egg-shaped head"""
    return ""

def feature_muscular(fur_color, face_cx=100, face_cy=115):
    return f'<ellipse cx="100" cy="115" rx="56" ry="44" fill="{fur_color}" opacity="0.3"/>'

def feature_sad_eyes(fur_color, face_cx=100, face_cy=115):
    return f'<path d="M68 82 Q76 78 84 82" stroke="#1C1917" stroke-width="1.5" fill="none"/><path d="M116 82 Q124 78 132 82" stroke="#1C1917" stroke-width="1.5" fill="none"/>'

def feature_short_legs(fur_color, face_cx=100, face_cy=115):
    return (
        f'<ellipse cx="80" cy="148" rx="10" ry="6" fill="{fur_color}"/>'
        f'<ellipse cx="120" cy="148" rx="10" ry="6" fill="{fur_color}"/>'
    )

def feature_long_body(fur_color, face_cx=100, face_cy=115):
    return f'<ellipse cx="100" cy="150" rx="40" ry="12" fill="{fur_color}" opacity="0.5"/>'

def feature_smile_basic(fur_color, face_cx=100, face_cy=115):
    return f'<path d="M96 109 Q100 112 104 109" stroke="#1C1917" stroke-width="1.5" fill="none" stroke-linecap="round"/>'

def feature_nostrils(fur_color, face_cx=100, face_cy=115):
    """No nose ellipse, just two dot nostrils (for some breeds)"""
    return f'<circle cx="97" cy="105" r="1.5" fill="#1C1917"/><circle cx="103" cy="105" r="1.5" fill="#1C1917"/>'

# Eye color overrides
EYE_COLORS = {
    "default": "#1C1917",
    "blue_eyes": "#60A5FA",
    "green_eyes": "#4ADE80",
    "amber_eyes": "#F59E0B",
    "red_eyes": "#EF4444",
}

# Pattern overlays
def pattern_tabby(fur_color):
    return (
        f'<path d="M80 80 L90 72 L100 80 L110 72 L120 80" stroke="{fur_color}" stroke-width="2" fill="none" opacity="0.4"/>'
        f'<path d="M85 76 L95 68 L105 76 L115 68" stroke="{fur_color}" stroke-width="1.5" fill="none" opacity="0.3"/>'
    )

def pattern_calico(fur_color):
    return (
        f'<circle cx="80" cy="110" r="15" fill="#F97316" opacity="0.4"/>'
        f'<circle cx="120" cy="110" r="15" fill="#1C1917" opacity="0.3"/>'
    )

def pattern_tuxedo(fur_color):
    return (
        f'<ellipse cx="100" cy="130" rx="30" ry="20" fill="#1C1917" opacity="0.4"/>'
        f'<path d="M90 100 L100 140 L110 100" fill="white" opacity="0.3"/>'
    )

def pattern_spotted(fur_color):
    return (
        f'<circle cx="82" cy="100" r="6" fill="#1C1917" opacity="0.3"/>'
        f'<circle cx="118" cy="100" r="6" fill="#1C1917" opacity="0.3"/>'
        f'<circle cx="100" cy="120" r="5" fill="#1C1917" opacity="0.3"/>'
    )

def pattern_ticked(fur_color):
    return (
        f'<ellipse cx="100" cy="115" rx="48" ry="36" fill="{fur_color}" opacity="0.2"/>'
        f'<circle cx="85" cy="105" r="3" fill="#1C1917" opacity="0.15"/>'
        f'<circle cx="115" cy="105" r="3" fill="#1C1917" opacity="0.15"/>'
        f'<circle cx="100" cy="118" r="3" fill="#1C1917" opacity="0.15"/>'
    )

def pattern_hairless(fur_color):
    return (
        f'<path d="M75 95 Q80 90 85 95" stroke="#D4A574" stroke-width="0.5" fill="none" opacity="0.3"/>'
        f'<path d="M115 95 Q120 90 125 95" stroke="#D4A574" stroke-width="0.5" fill="none" opacity="0.3"/>'
    )

def pattern_curly(fur_color):
    return (
        f'<circle cx="80" cy="95" r="8" fill="{fur_color}" opacity="0.2"/>'
        f'<circle cx="120" cy="95" r="8" fill="{fur_color}" opacity="0.2"/>'
        f'<circle cx="100" cy="130" r="8" fill="{fur_color}" opacity="0.2"/>'
    )

def pattern_ear_tufts(fur_color):
    return (
        f'<polygon points="60,50 70,30 75,55" fill="{fur_color}" opacity="0.7"/>'
        f'<polygon points="140,50 130,30 125,55" fill="{fur_color}" opacity="0.7"/>'
    )

def pattern_white_paws(fur_color):
    return (
        f'<ellipse cx="75" cy="148" rx="12" ry="8" fill="white" opacity="0.7"/>'
        f'<ellipse cx="125" cy="148" rx="12" ry="8" fill="white" opacity="0.7"/>'
    )

def pattern_shell(fur_color):
    """Turtle shell pattern on top of head"""
    return (
        f'<ellipse cx="100" cy="85" rx="40" ry="25" fill="#65A30D" opacity="0.5"/>'
        f'<path d="M75 85 L100 65 L125 85" stroke="#4D7C0F" stroke-width="1.5" fill="none" opacity="0.4"/>'
        f'<path d="M80 85 L100 75 L120 85" stroke="#4D7C0F" stroke-width="1" fill="none" opacity="0.3"/>'
    )

def pattern_fins(fur_color):
    """Fish fin overlays"""
    return (
        f'<ellipse cx="55" cy="110" rx="15" ry="20" fill="{fur_color}" opacity="0.4" transform="rotate(-20 55 110)"/>'
        f'<ellipse cx="145" cy="110" rx="15" ry="20" fill="{fur_color}" opacity="0.4" transform="rotate(20 145 110)"/>'
    )

def pattern_wings(fur_color):
    """Bird wing hints"""
    return (
        f'<ellipse cx="50" cy="120" rx="18" ry="22" fill="{fur_color}" opacity="0.3" transform="rotate(-15 50 120)"/>'
        f'<ellipse cx="150" cy="120" rx="18" ry="22" fill="{fur_color}" opacity="0.3" transform="rotate(15 150 120)"/>'
    )

def pattern_cheek_pouches(fur_color):
    """Hamster cheek pouches"""
    return (
        f'<ellipse cx="65" cy="112" rx="15" ry="12" fill="{fur_color}" opacity="0.5"/>'
        f'<ellipse cx="135" cy="112" rx="15" ry="12" fill="{fur_color}" opacity="0.5"/>'
    )

def pattern_spines(fur_color):
    """Hedgehog spines"""
    return (
        f'<polygon points="55,75 50,55 60,72" fill="#8B7355" opacity="0.6"/>'
        f'<polygon points="65,68 62,48 72,66" fill="#8B7355" opacity="0.6"/>'
        f'<polygon points="135,68 138,48 128,66" fill="#8B7355" opacity="0.6"/>'
        f'<polygon points="145,75 150,55 140,72" fill="#8B7355" opacity="0.6"/>'
        f'<polygon points="75,62 75,42 82,60" fill="#8B7355" opacity="0.5"/>'
        f'<polygon points="125,62 125,42 118,60" fill="#8B7355" opacity="0.5"/>'
    )

PATTERN_FUNCTIONS = {
    "tabby": pattern_tabby,
    "calico": pattern_calico,
    "tuxedo": pattern_tuxedo,
    "spotted": pattern_spotted,
    "ticked": pattern_ticked,
    "hairless": pattern_hairless,
    "curly": pattern_curly,
    "ear_tufts": pattern_ear_tufts,
    "white_paws": pattern_white_paws,
    "shell": pattern_shell,
    "fins": pattern_fins,
    "wings": pattern_wings,
    "cheek_pouches": pattern_cheek_pouches,
    "spines": pattern_spines,
}

# ============================================================
# FACE SHAPE VARIATIONS
# ============================================================

def face_standard(fur_color):
    """Standard elliptical face"""
    return f'<ellipse cx="100" cy="115" rx="52" ry="40" fill="{fur_color}"/>'

def face_egg(fur_color):
    """Egg-shaped head (bull terrier)"""
    return f'<ellipse cx="100" cy="112" rx="48" ry="44" fill="{fur_color}"/>'

def face_round(fur_color):
    """Rounder face"""
    return f'<ellipse cx="100" cy="115" rx="50" ry="42" fill="{fur_color}"/>'

def face_small(fur_color):
    """Smaller face (for fish, etc.)"""
    return f'<ellipse cx="100" cy="110" rx="35" ry="30" fill="{fur_color}"/>'

def face_body_round(fur_color):
    """Round body (hamster, hedgehog)"""
    return f'<ellipse cx="100" cy="115" rx="55" ry="45" fill="{fur_color}"/>'

FACE_SHAPES = {
    "standard": face_standard,
    "egg": face_egg,
    "round": face_round,
    "small": face_small,
    "body_round": face_body_round,
}

# ============================================================
# MAIN SVG GENERATOR
# ============================================================

def generate_avatar(breed_config):
    """
    Generate a complete SVG avatar string from a breed configuration dict.
    
    Config keys:
        bg: [light_color, dark_color] - background gradient
        fur: color - main fur/body color
        ears: str - ear type (pointed, floppy, round, folded, curled, bat, long_floppy, big_pointed, long_ears, tiny_round, no_visible, crown)
        feature: str - special feature (smile, tongue, mask, dark_face, fluffy, beard, long_hair, flat_face, big_eyes, tan_marks, white_collar, tricolor, egg_head, muscular, sad_eyes, short_legs, long_body, smile_basic, nostrils)
        eye_color: str (optional) - eye iris color override (default, blue_eyes, green_eyes, amber_eyes, red_eyes)
        pattern: str (optional) - overlay pattern (tabby, calico, tuxedo, spotted, ticked, hairless, curly, ear_tufts, white_paws, shell, fins, wings, cheek_pouches, spines)
        face_shape: str (optional) - face shape variant (standard, egg, round, small, body_round)
        extra_svg: str (optional) - additional SVG elements
    """
    bg_light, bg_dark = breed_config["bg"]
    fur = breed_config["fur"]
    ear_type = breed_config.get("ears", "pointed")
    feature_type = breed_config.get("feature", "smile_basic")
    eye_color_key = breed_config.get("eye_color", "default")
    pattern_type = breed_config.get("pattern", None)
    face_shape = breed_config.get("face_shape", "standard")
    extra_svg = breed_config.get("extra_svg", "")
    
    eye_color = EYE_COLORS.get(eye_color_key, "#1C1917")
    
    # Determine eye size based on feature
    is_big_eyes = feature_type == "big_eyes"
    eye_w = 15 if is_big_eyes else 12
    eye_h = 17 if is_big_eyes else 14
    iris_w = 9 if is_big_eyes else 7
    iris_h = 11 if is_big_eyes else 9
    highlight_r = 2.5 if is_big_eyes else 2
    
    # Build SVG parts
    parts = []
    
    # 1. Background gradient + circle
    parts.append(f'<defs><radialGradient id="bg" cx="50%" cy="40%">'
                 f'<stop offset="0%" stop-color="{bg_light}"/>'
                 f'<stop offset="100%" stop-color="{bg_dark}"/>'
                 f'</radialGradient></defs>')
    parts.append('<circle cx="100" cy="105" r="82" fill="url(#bg)"/>')
    
    # 2. Ears
    ear_fn = EAR_FUNCTIONS.get(ear_type, ears_pointed)
    parts.append(ear_fn(fur))
    
    # 3. Face shape
    face_fn = FACE_SHAPES.get(face_shape, face_standard)
    parts.append(face_fn(fur))
    
    # 4. Pattern overlay (before eyes)
    if pattern_type and pattern_type in PATTERN_FUNCTIONS:
        parts.append(PATTERN_FUNCTIONS[pattern_type](fur))
    
    # 5. Eyes
    parts.append(
        f'<ellipse cx="76" cy="88" rx="{eye_w}" ry="{eye_h}" fill="white"/>'
        f'<ellipse cx="124" cy="88" rx="{eye_w}" ry="{eye_h}" fill="white"/>'
        f'<ellipse cx="76" cy="90" rx="{iris_w}" ry="{iris_h}" fill="{eye_color}"/>'
        f'<ellipse cx="124" cy="90" rx="{iris_w}" ry="{iris_h}" fill="{eye_color}"/>'
        f'<circle cx="73" cy="86" r="{highlight_r}" fill="white"/>'
        f'<circle cx="121" cy="86" r="{highlight_r}" fill="white"/>'
    )
    
    # 6. Nose
    parts.append('<ellipse cx="100" cy="104" rx="5" ry="3.5" fill="#F9A8D4"/>')
    
    # 7. Mouth / feature
    feature_fn = globals().get(f"feature_{feature_type}", feature_smile_basic)
    parts.append(feature_fn(fur))
    
    # 8. Cheeks
    parts.append(
        '<circle cx="62" cy="104" r="7" fill="#FCA5A5" opacity="0.5"/>'
        '<circle cx="138" cy="104" r="7" fill="#FCA5A5" opacity="0.5"/>'
    )
    
    # 9. Extra SVG elements
    if extra_svg:
        parts.append(extra_svg)
    
    # Assemble
    inner = "".join(parts)
    svg = f'<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">{inner}</svg>'
    return svg


def convert_to_png(svg_path, png_path):
    """Convert SVG to PNG using cairosvg"""
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=400, output_height=400)
        return True
    except Exception as e:
        print(f"  PNG conversion failed: {e}")
        return False


def convert_to_webp(png_path, webp_path):
    """Convert PNG to webp using PIL"""
    try:
        from PIL import Image
        img = Image.open(png_path)
        img.save(webp_path, "WEBP", quality=90)
        return True
    except Exception as e:
        print(f"  WebP conversion failed: {e}")
        return False


# ============================================================
# BREED DEFINITIONS
# ============================================================

# All 62 existing breeds
EXISTING_BREEDS = {
    # Dogs
    "金毛犬": {"bg": ["#FEF3C7", "#D97706"], "fur": "#FBBF24", "ears": "floppy", "feature": "smile"},
    "金毛寻回犬": {"bg": ["#FEF3C7", "#F59E0B"], "fur": "#FBBF24", "ears": "floppy", "feature": "tongue"},
    "柴犬": {"bg": ["#FED7AA", "#EA580C"], "fur": "#FDE68A", "ears": "pointed", "feature": "smile"},
    "柯基犬": {"bg": ["#FECACA", "#EF4444"], "fur": "#FDE68A", "ears": "pointed", "feature": "short_legs"},
    "威尔士柯基犬": {"bg": ["#FECACA", "#DC2626"], "fur": "#F59E0B", "ears": "pointed", "feature": "short_legs"},
    "哈士奇": {"bg": ["#DBEAFE", "#3B82F6"], "fur": "#E2E8F0", "ears": "pointed", "feature": "mask"},
    "阿拉斯加犬": {"bg": ["#E0E7FF", "#4338CA"], "fur": "#D1D5DB", "ears": "pointed", "feature": "mask"},
    "阿拉斯加雪橇犬": {"bg": ["#DBEAFE", "#2563EB"], "fur": "#94A3B8", "ears": "pointed", "feature": "mask"},
    "萨摩耶": {"bg": ["#E0E7FF", "#6366F1"], "fur": "#FEFEFE", "ears": "pointed", "feature": "smile"},
    "德国牧羊犬": {"bg": ["#D9F99D", "#65A30D"], "fur": "#B8860B", "ears": "pointed", "feature": "dark_face"},
    "拉布拉多寻回犬": {"bg": ["#FEF3C7", "#CA8A04"], "fur": "#D4A574", "ears": "floppy", "feature": "smile"},
    "边境牧羊犬": {"bg": ["#D1FAE5", "#059669"], "fur": "#1C1917", "ears": "pointed", "feature": "white_collar"},
    "秋田犬": {"bg": ["#FED7AA", "#C2410C"], "fur": "#FBBF24", "ears": "pointed", "feature": "smile"},
    "松狮犬": {"bg": ["#FECACA", "#B91C1C"], "fur": "#92400E", "ears": "round", "feature": "tongue"},
    "罗威纳犬": {"bg": ["#E5E7EB", "#1F2937"], "fur": "#1C1917", "ears": "floppy", "feature": "tan_marks"},
    "杜宾犬": {"bg": ["#D1D5DB", "#111827"], "fur": "#1C1917", "ears": "pointed", "feature": "tan_marks"},
    "法国斗牛犬": {"bg": ["#FEE2E2", "#991B1B"], "fur": "#E5E7EB", "ears": "bat", "feature": "flat_face"},
    "巴哥犬": {"bg": ["#FDE68A", "#B45309"], "fur": "#F5E6D3", "ears": "floppy", "feature": "flat_face"},
    "博美犬": {"bg": ["#FFEDD5", "#EA580C"], "fur": "#FBBF24", "ears": "pointed", "feature": "fluffy"},
    "比熊犬": {"bg": ["#E0E7FF", "#818CF8"], "fur": "#FEFEFE", "ears": "round", "feature": "fluffy"},
    "贵宾犬_泰迪": {"bg": ["#FECDD3", "#BE185D"], "fur": "#92400E", "ears": "floppy", "feature": "fluffy"},
    "吉娃娃": {"bg": ["#FEF3C7", "#D97706"], "fur": "#D4A574", "ears": "pointed", "feature": "big_eyes"},
    "约克夏梗": {"bg": ["#E5E7EB", "#374151"], "fur": "#6B7280", "ears": "pointed", "feature": "long_hair"},
    "马尔济斯犬": {"bg": ["#F0F9FF", "#0284C7"], "fur": "#FEFEFE", "ears": "floppy", "feature": "long_hair"},
    "雪纳瑞犬": {"bg": ["#D1D5DB", "#4B5563"], "fur": "#9CA3AF", "ears": "floppy", "feature": "beard"},
    "中华田园犬": {"bg": ["#FEF3C7", "#CA8A04"], "fur": "#D97706", "ears": "pointed", "feature": "smile"},
    "牛头梗": {"bg": ["#FEF2F2", "#B91C1C"], "fur": "#FEFEFE", "ears": "pointed", "feature": "egg_head", "face_shape": "egg"},
    "喜乐蒂牧羊犬": {"bg": ["#ECFDF5", "#047857"], "fur": "#B8860B", "ears": "pointed", "feature": "long_hair"},
    "卡斯罗犬": {"bg": ["#E5E7EB", "#111827"], "fur": "#1C1917", "ears": "floppy", "feature": "muscular"},
    "大白熊犬": {"bg": ["#F0F9FF", "#0369A1"], "fur": "#FEFEFE", "ears": "floppy", "feature": "fluffy"},
    "巴吉度猎犬": {"bg": ["#FEE2E2", "#991B1B"], "fur": "#D4A574", "ears": "long_floppy", "feature": "sad_eyes"},
    "腊肠犬": {"bg": ["#FEF3C7", "#B45309"], "fur": "#92400E", "ears": "floppy", "feature": "long_body"},
    "比格犬": {"bg": ["#D1FAE5", "#065F46"], "fur": "#D4A574", "ears": "long_floppy", "feature": "tricolor"},
    "西施犬": {"bg": ["#FCE7F3", "#9D174D"], "fur": "#F5E6D3", "ears": "floppy", "feature": "long_hair"},
    
    # Cats
    "布偶猫": {"bg": ["#C7D2FE", "#4338CA"], "fur": "#FEFEFE", "ears": "pointed", "feature": "smile_basic", "eye_color": "blue_eyes", "pattern": "mask"},
    "布偶猫_海双": {"bg": ["#BFDBFE", "#1E40AF"], "fur": "#F5F5F4", "ears": "pointed", "feature": "smile_basic", "eye_color": "blue_eyes", "pattern": "mask"},
    "暹罗猫": {"bg": ["#E0E7FF", "#4F46E5"], "fur": "#FEF9E7", "ears": "pointed", "feature": "smile_basic", "eye_color": "blue_eyes", "pattern": "mask"},
    "暹罗猫_重点色": {"bg": ["#DDD6FE", "#5B21B6"], "fur": "#FEF3C7", "ears": "pointed", "feature": "smile_basic", "eye_color": "blue_eyes", "pattern": "mask"},
    "英国短毛猫": {"bg": ["#BFDBFE", "#2563EB"], "fur": "#E5E7EB", "ears": "round", "feature": "smile_basic"},
    "蓝猫_英短": {"bg": ["#93C5FD", "#1D4ED8"], "fur": "#94A3B8", "ears": "round", "feature": "smile_basic"},
    "英国长毛猫": {"bg": ["#A5B4FC", "#3730A3"], "fur": "#D1D5DB", "ears": "round", "feature": "fluffy"},
    "美国短毛猫": {"bg": ["#D1D5DB", "#4B5563"], "fur": "#E5E7EB", "ears": "pointed", "feature": "smile_basic", "pattern": "tabby"},
    "苏格兰折耳猫": {"bg": ["#FBCFE8", "#BE185D"], "fur": "#D4A574", "ears": "folded", "feature": "smile_basic"},
    "曼基康矮脚猫": {"bg": ["#FDE68A", "#B45309"], "fur": "#FBBF24", "ears": "pointed", "feature": "short_legs"},
    "加拿大无毛猫": {"bg": ["#E5E7EB", "#6B7280"], "fur": "#F5D0C5", "ears": "big_pointed", "feature": "smile_basic", "pattern": "hairless"},
    "斯芬克斯猫_无毛": {"bg": ["#D1D5DB", "#374151"], "fur": "#F0D0C0", "ears": "big_pointed", "feature": "smile_basic", "pattern": "hairless"},
    "德文卷毛猫": {"bg": ["#FED7AA", "#C2410C"], "fur": "#D4A574", "ears": "big_pointed", "feature": "smile_basic", "pattern": "curly"},
    "美国卷耳猫": {"bg": ["#FECDD3", "#9F1239"], "fur": "#E5E7EB", "ears": "curled", "feature": "smile"},
    "缅因猫": {"bg": ["#D9F99D", "#4D7C0F"], "fur": "#92400E", "ears": "pointed", "feature": "smile_basic", "pattern": "ear_tufts"},
    "挪威森林猫": {"bg": ["#A7F3D0", "#047857"], "fur": "#B8860B", "ears": "pointed", "feature": "smile_basic", "pattern": "ear_tufts"},
    "波斯猫": {"bg": ["#FECDD3", "#9F1239"], "fur": "#FEFEFE", "ears": "round", "feature": "flat_face"},
    "异国短毛猫_加菲": {"bg": ["#FED7AA", "#C2410C"], "fur": "#F97316", "ears": "round", "feature": "flat_face"},
    "俄罗斯蓝猫": {"bg": ["#BAE6FD", "#0369A1"], "fur": "#94A3B8", "ears": "pointed", "feature": "smile_basic", "eye_color": "green_eyes"},
    "伯曼猫": {"bg": ["#E0E7FF", "#4338CA"], "fur": "#FEFEFE", "ears": "pointed", "feature": "smile_basic", "pattern": "white_paws"},
    "阿比西尼亚猫": {"bg": ["#FED7AA", "#EA580C"], "fur": "#D97706", "ears": "pointed", "feature": "smile_basic", "pattern": "ticked"},
    "孟加拉豹猫": {"bg": ["#FEF3C7", "#CA8A04"], "fur": "#D97706", "ears": "pointed", "feature": "smile_basic", "pattern": "spotted"},
    "中华田园猫_橘猫": {"bg": ["#FED7AA", "#EA580C"], "fur": "#F97316", "ears": "pointed", "feature": "smile_basic", "pattern": "tabby"},
    "中华田园猫_狸花": {"bg": ["#D1D5DB", "#374151"], "fur": "#6B7280", "ears": "pointed", "feature": "smile_basic", "pattern": "tabby"},
    "中华田园猫_三花": {"bg": ["#FECDD3", "#9F1239"], "fur": "#FEFEFE", "ears": "pointed", "feature": "smile_basic", "pattern": "calico"},
    "中华田园猫_奶牛": {"bg": ["#E5E7EB", "#1F2937"], "fur": "#FEFEFE", "ears": "pointed", "feature": "smile_basic", "pattern": "tuxedo"},
    "银渐层": {"bg": ["#E5E7EB", "#4B5563"], "fur": "#D1D5DB", "ears": "pointed", "feature": "smile_basic", "eye_color": "green_eyes"},
    "金渐层": {"bg": ["#FEF3C7", "#CA8A04"], "fur": "#FBBF24", "ears": "pointed", "feature": "smile_basic", "eye_color": "green_eyes"},
}

# NEW pet breeds to generate
NEW_BREEDS = {
    # Rabbits
    "荷兰垂耳兔": {"bg": ["#FDE68A", "#B45309"], "fur": "#F5E6D3", "ears": "floppy", "feature": "smile_basic", "face_shape": "round"},
    "迷你雷克斯兔": {"bg": ["#E0E7FF", "#6366F1"], "fur": "#8B6914", "ears": "long_ears", "feature": "smile_basic", "face_shape": "round"},
    "安哥拉兔": {"bg": ["#FCE7F3", "#DB2777"], "fur": "#FEFEFE", "ears": "long_ears", "feature": "fluffy", "face_shape": "round"},
    "侏儒兔": {"bg": ["#D1FAE5", "#059669"], "fur": "#D4A574", "ears": "tiny_round", "feature": "big_eyes", "face_shape": "round"},
    "荷兰兔": {"bg": ["#FECACA", "#DC2626"], "fur": "#FEFEFE", "ears": "long_ears", "feature": "smile_basic", "face_shape": "round", "pattern": "tuxedo"},
    
    # Hamsters
    "金丝熊仓鼠": {"bg": ["#FEF3C7", "#D97706"], "fur": "#FBBF24", "ears": "tiny_round", "feature": "smile_basic", "face_shape": "body_round", "pattern": "cheek_pouches"},
    "三线仓鼠": {"bg": ["#E5E7EB", "#6B7280"], "fur": "#D1D5DB", "ears": "tiny_round", "feature": "smile_basic", "face_shape": "body_round", "pattern": "tabby"},
    "一线仓鼠": {"bg": ["#FCE7F3", "#BE185D"], "fur": "#E5E7EB", "ears": "tiny_round", "feature": "smile_basic", "face_shape": "body_round"},
    "罗伯罗夫斯基仓鼠": {"bg": ["#FED7AA", "#EA580C"], "fur": "#D4A574", "ears": "tiny_round", "feature": "big_eyes", "face_shape": "body_round"},
    
    # Birds
    "虎皮鹦鹉": {"bg": ["#D1FAE5", "#047857"], "fur": "#4ADE80", "ears": "crown", "feature": "smile_basic", "face_shape": "small", "pattern": "wings", "eye_color": "default"},
    "玄凤鹦鹉": {"bg": ["#FEF3C7", "#CA8A04"], "fur": "#FDE68A", "ears": "crown", "feature": "smile_basic", "face_shape": "small", "pattern": "wings"},
    "牡丹鹦鹉": {"bg": ["#FECDD3", "#BE185D"], "fur": "#4ADE80", "ears": "crown", "feature": "smile_basic", "face_shape": "small", "pattern": "wings"},
    "金丝雀": {"bg": ["#FEF3C7", "#F59E0B"], "fur": "#FBBF24", "ears": "crown", "feature": "smile_basic", "face_shape": "small", "pattern": "wings"},
    "文鸟": {"bg": ["#F0F9FF", "#0284C7"], "fur": "#E5E7EB", "ears": "crown", "feature": "smile_basic", "face_shape": "small", "pattern": "wings"},
    
    # Fish
    "金鱼": {"bg": ["#BFDBFE", "#1D4ED8"], "fur": "#F97316", "ears": "no_visible", "feature": "smile_basic", "face_shape": "small", "pattern": "fins", "eye_color": "default"},
    "锦鲤": {"bg": ["#DBEAFE", "#2563EB"], "fur": "#FEFEFE", "ears": "no_visible", "feature": "smile_basic", "face_shape": "small", "pattern": "fins", "extra_svg": '<circle cx="85" cy="108" r="8" fill="#EF4444" opacity="0.5"/><circle cx="115" cy="108" r="8" fill="#F97316" opacity="0.5"/>'},
    "斗鱼": {"bg": ["#E0E7FF", "#4F46E5"], "fur": "#7C3AED", "ears": "no_visible", "feature": "smile_basic", "face_shape": "small", "pattern": "fins", "extra_svg": '<ellipse cx="100" cy="140" rx="40" ry="20" fill="#7C3AED" opacity="0.3"/>'},
    "孔雀鱼": {"bg": ["#A7F3D0", "#047857"], "fur": "#34D399", "ears": "no_visible", "feature": "smile_basic", "face_shape": "small", "pattern": "fins", "extra_svg": '<ellipse cx="100" cy="140" rx="35" ry="18" fill="#F59E0B" opacity="0.3"/><ellipse cx="100" cy="140" rx="25" ry="12" fill="#3B82F6" opacity="0.3"/>'},
    
    # Reptiles
    "豹纹守宫": {"bg": ["#FEF3C7", "#CA8A04"], "fur": "#FBBF24", "ears": "no_visible", "feature": "smile_basic", "face_shape": "small", "pattern": "spotted", "eye_color": "amber_eyes"},
    "鬃狮蜥": {"bg": ["#FED7AA", "#C2410C"], "fur": "#D4A574", "ears": "no_visible", "feature": "smile_basic", "face_shape": "small", "extra_svg": '<polygon points="65,95 55,85 68,92" fill="#D4A574" opacity="0.5"/><polygon points="135,95 145,85 132,92" fill="#D4A574" opacity="0.5"/>'},
    
    # Turtle
    "巴西龟": {"bg": ["#D1FAE5", "#065F46"], "fur": "#65A30D", "ears": "no_visible", "feature": "smile_basic", "face_shape": "small", "pattern": "shell"},
    "草龟": {"bg": ["#A7F3D0", "#047857"], "fur": "#8B6914", "ears": "no_visible", "feature": "smile_basic", "face_shape": "small", "pattern": "shell"},
    
    # Hedgehog
    "非洲迷你刺猬": {"bg": ["#FDE68A", "#92400E"], "fur": "#D4A574", "ears": "tiny_round", "feature": "smile_basic", "face_shape": "body_round", "pattern": "spines"},
    
    # Ferret
    "雪貂": {"bg": ["#E5E7EB", "#374151"], "fur": "#F5E6D3", "ears": "tiny_round", "feature": "smile_basic", "face_shape": "standard", "pattern": "mask"},
    
    # Guinea pig
    "豚鼠": {"bg": ["#FED7AA", "#EA580C"], "fur": "#D97706", "ears": "tiny_round", "feature": "smile_basic", "face_shape": "body_round", "extra_svg": '<ellipse cx="80" cy="110" rx="15" ry="12" fill="#FEFEFE" opacity="0.4"/><ellipse cx="120" cy="110" rx="15" ry="12" fill="#1C1917" opacity="0.3"/>'},
    
    # Chinchilla
    "龙猫": {"bg": ["#D1D5DB", "#4B5563"], "fur": "#9CA3AF", "ears": "round", "feature": "big_eyes", "face_shape": "body_round", "pattern": "fluffy"},
    
    # Sugar glider
    "蜜袋鼯": {"bg": ["#E0E7FF", "#6366F1"], "fur": "#D1D5DB", "ears": "round", "feature": "big_eyes", "face_shape": "round", "extra_svg": '<ellipse cx="100" cy="100" rx="15" ry="8" fill="#1C1917" opacity="0.3"/>'},
}


def generate_all(breeds_dict, output_dir, convert_formats=True):
    """Generate SVG (and optionally PNG/webp) for all breeds in the dict."""
    os.makedirs(output_dir, exist_ok=True)
    generated = []
    
    for name, config in breeds_dict.items():
        svg_content = generate_avatar(config)
        svg_path = os.path.join(output_dir, f"{name}.svg")
        
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        print(f"  ✓ {name}.svg")
        generated.append(name)
        
        if convert_formats:
            png_path = os.path.join(output_dir, f"{name}.png")
            if convert_to_png(svg_path, png_path):
                webp_path = os.path.join(output_dir, f"{name}.webp")
                convert_to_webp(png_path, webp_path)
    
    return generated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate kawaii pet breed avatars")
    parser.add_argument("--output-dir", "-o", default="../frontend/public/avatars",
                       help="Output directory for SVG files")
    parser.add_argument("--all", action="store_true", help="Generate all existing breeds")
    parser.add_argument("--new", action="store_true", help="Generate only new breeds")
    parser.add_argument("--both", action="store_true", help="Generate existing + new breeds")
    parser.add_argument("--breeds-file", help="JSON file with breed definitions (overrides built-in)")
    parser.add_argument("--no-convert", action="store_true", help="Skip PNG/webp conversion")
    args = parser.parse_args()
    
    output_dir = args.output_dir
    convert = not args.no_convert
    
    if args.breeds_file:
        with open(args.breeds_file, "r", encoding="utf-8") as f:
            breeds = json.load(f)
        print(f"Loaded {len(breeds)} breeds from {args.breeds_file}")
        generate_all(breeds, output_dir, convert)
    elif args.new:
        print(f"Generating {len(NEW_BREEDS)} NEW breeds...")
        generate_all(NEW_BREEDS, output_dir, convert)
    elif args.both:
        all_breeds = {**EXISTING_BREEDS, **NEW_BREEDS}
        print(f"Generating {len(all_breeds)} breeds (existing + new)...")
        generate_all(all_breeds, output_dir, convert)
    elif args.all:
        print(f"Generating {len(EXISTING_BREEDS)} existing breeds...")
        generate_all(EXISTING_BREEDS, output_dir, convert)
    else:
        print("Usage: --all (existing) | --new (new pets) | --both | --breeds-file <json>")
