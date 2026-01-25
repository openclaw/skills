#!/usr/bin/env python3
"""
WHO Growth Chart Generator

Generates height-for-age, weight-for-age, and BMI-for-age charts with WHO percentiles
and child data overlay. Downloads WHO reference data on demand from cdn.who.int.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.ticker import FuncFormatter, MultipleLocator
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from scipy import stats, interpolate
from datetime import datetime
from pathlib import Path
import json
import sys
import urllib.request
import ssl

# WHO percentiles to display
PERCENTILES = [5, 15, 50, 85, 95]

# Color scheme for percentile bands
PERCENTILE_COLORS = {
    (5, 15): '#e8f4f8',
    (15, 50): '#d1e8f0',
    (50, 85): '#d1e8f0',
    (85, 95): '#e8f4f8'
}

# WHO CDN base URLs (different bases for 0-5 vs 5-19 data)
WHO_CDN_CHILD = "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators"
WHO_CDN_5_19 = "https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years"

# WHO data file mappings (sex -> age_range -> (base_url, path))
WHO_DATA_FILES = {
    'height': {
        'F': {
            '0-2': (WHO_CDN_CHILD, 'length-height-for-age/tab_lhfa_girls_p_0_2.xlsx'),
            '2-5': (WHO_CDN_CHILD, 'length-height-for-age/tab_lhfa_girls_p_2_5.xlsx'),
            '5-19': (WHO_CDN_5_19, 'height-for-age-(5-19-years)/hfa-girls-perc-who2007-exp.xlsx'),
        },
        'M': {
            '0-2': (WHO_CDN_CHILD, 'length-height-for-age/tab_lhfa_boys_p_0_2.xlsx'),
            '2-5': (WHO_CDN_CHILD, 'length-height-for-age/tab_lhfa_boys_p_2_5.xlsx'),
            '5-19': (WHO_CDN_5_19, 'height-for-age-(5-19-years)/hfa-boys-perc-who2007-exp.xlsx'),
        }
    },
    'weight': {
        'F': {
            '0-5': (WHO_CDN_CHILD, 'weight-for-age/tab_wfa_girls_p_0_5.xlsx'),
        },
        'M': {
            '0-5': (WHO_CDN_CHILD, 'weight-for-age/tab_wfa_boys_p_0_5.xlsx'),
        }
    },
    'bmi': {
        'F': {
            '0-2': (WHO_CDN_CHILD, 'body-mass-index-for-age/tab_bmi_girls_p_0_2.xlsx'),
            '2-5': (WHO_CDN_CHILD, 'body-mass-index-for-age/tab_bmi_girls_p_2_5.xlsx'),
            '5-19': (WHO_CDN_5_19, 'bmi-for-age-(5-19-years)/bmi-girls-perc-who2007-exp.xlsx'),
        },
        'M': {
            '0-2': (WHO_CDN_CHILD, 'body-mass-index-for-age/tab_bmi_boys_p_0_2.xlsx'),
            '2-5': (WHO_CDN_CHILD, 'body-mass-index-for-age/tab_bmi_boys_p_2_5.xlsx'),
            '5-19': (WHO_CDN_5_19, 'bmi-for-age-(5-19-years)/bmi-boys-perc-who2007-exp.xlsx'),
        }
    }
}

BASE_DIR = Path(__file__).parent

def get_base_output_dir():
    """Get the base output directory for charts and cache."""
    # Default to ~/clawd/who-growth-charts (sibling to skills folder)
    try:
        # script is in .../clawd/skills/who-growth-charts/scripts/
        # workspace is ../../../
        workspace_dir = BASE_DIR.parents[2]
        if workspace_dir.name != 'clawd': 
            workspace_dir = Path.home() / 'clawd'
    except IndexError:
            workspace_dir = Path.home() / 'clawd'
    
    return workspace_dir / 'who-growth-charts'

CACHE_DIR = get_base_output_dir() / 'cache'

WHO_EMBLEM_URL = "https://cdn.who.int/media/images/default-source/infographics/who-emblem.png"
_WHO_EMBLEM_IMG = None

def _get_who_emblem_img():
    """Load and cache the WHO emblem from online if needed."""
    global _WHO_EMBLEM_IMG
    if _WHO_EMBLEM_IMG is not None:
        return _WHO_EMBLEM_IMG
    
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    emblem_path = CACHE_DIR / 'who-emblem.png'
    
    if not emblem_path.exists():
        print(f"Downloading WHO emblem...", file=sys.stderr)
        ctx = ssl.create_default_context()
        req = urllib.request.Request(WHO_EMBLEM_URL, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Clawdbot/1.0'
        })
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                emblem_path.write_bytes(response.read())
            print(f"  Cached: {emblem_path.name}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to download WHO emblem: {e}", file=sys.stderr)
            _WHO_EMBLEM_IMG = False
            return None

    try:
        img = mpimg.imread(str(emblem_path))
        _WHO_EMBLEM_IMG = img
        return _WHO_EMBLEM_IMG
    except Exception:
        _WHO_EMBLEM_IMG = False
        return None


def add_who_emblem(ax, loc: str = 'upper left'):
    """Add the WHO emblem inside the chart boundary (no-op if missing)."""
    emblem = _get_who_emblem_img()
    if emblem is None:
        return
    axins = inset_axes(ax, width="10%", height="18%", loc=loc, borderpad=0.8)
    axins.imshow(emblem)
    axins.axis('off')


def ensure_who_data(metric: str, sex: str, age_range: str) -> Path:
    """Download WHO data file if not cached locally."""
    CACHE_DIR.mkdir(exist_ok=True)
    
    # Local filename
    local_file = CACHE_DIR / f"{sex.lower()}_{metric}_{age_range.replace('-', '_')}.xlsx"
    
    if local_file.exists():
        return local_file
    
    # Get URL (base, path) tuple
    url_info = WHO_DATA_FILES.get(metric, {}).get(sex, {}).get(age_range)
    if not url_info:
        raise ValueError(f"No WHO data available for {metric}/{sex}/{age_range}")
    
    base_url, url_path = url_info
    url = f"{base_url}/{url_path}"
    
    print(f"Downloading WHO {metric} data ({sex}, {age_range})...", file=sys.stderr)
    
    # Download with User-Agent header (required by WHO CDN)
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Clawdbot/1.0'
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            data = response.read()
        
        local_file.write_bytes(data)
        print(f"  Cached: {local_file.name}", file=sys.stderr)
        return local_file
    except Exception as e:
        raise RuntimeError(f"Failed to download WHO data from {url}: {e}")


def load_who_height_data(sex='F', max_age_months=None):
    """Load WHO height-for-age data, downloading only needed age ranges."""
    dfs = []
    
    # 0-2 years (0-24 months)
    if max_age_months is None or max_age_months >= 0:
        file_0_2 = ensure_who_data('height', sex, '0-2')
        dfs.append(pd.read_excel(file_0_2, header=0))
    
    # 2-5 years (24-60 months) - only if child is older than 18 months
    if max_age_months is None or max_age_months > 18:
        file_2_5 = ensure_who_data('height', sex, '2-5')
        df_2_5 = pd.read_excel(file_2_5, header=0)
        dfs.append(df_2_5[df_2_5['Month'] >= 24])
    
    # 5-19 years (61-228 months) - only if child is older than 54 months
    if max_age_months is None or max_age_months > 54:
        file_5_19 = ensure_who_data('height', sex, '5-19')
        df_5_19 = pd.read_excel(file_5_19, header=0)
        dfs.append(df_5_19[df_5_19['Month'] >= 61])
    
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values('Month').drop_duplicates(subset='Month')
    df['age_months'] = df['Month']
    
    return df


def load_who_weight_data(sex='F', max_age_months=None):
    """Load WHO weight-for-age data, downloading if needed.
    
    Note: WHO only provides weight-for-age standards up to 5 years (60 months).
    For older children, use BMI-for-age instead.
    """
    # Only one file available: 0-5 years (0-60 months)
    file_0_5 = ensure_who_data('weight', sex, '0-5')
    
    df = pd.read_excel(file_0_5, header=0)
    df['age_months'] = df['Month']
    
    return df


def load_who_bmi_data(sex='F', max_age_months=None):
    """Load WHO BMI-for-age data, downloading only needed age ranges."""
    dfs = []
    
    # 0-2 years (0-24 months)
    if max_age_months is None or max_age_months >= 0:
        file_0_2 = ensure_who_data('bmi', sex, '0-2')
        dfs.append(pd.read_excel(file_0_2, header=0))
    
    # 2-5 years (24-60 months) - only if child is older than 18 months
    if max_age_months is None or max_age_months > 18:
        file_2_5 = ensure_who_data('bmi', sex, '2-5')
        df_2_5 = pd.read_excel(file_2_5, header=0)
        dfs.append(df_2_5[df_2_5['Month'] >= 24])
    
    # 5-19 years (61-228 months) - only if child is older than 54 months
    if max_age_months is None or max_age_months > 54:
        file_5_19 = ensure_who_data('bmi', sex, '5-19')
        df_5_19 = pd.read_excel(file_5_19, header=0)
        dfs.append(df_5_19[df_5_19['Month'] >= 61])
    
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values('Month').drop_duplicates(subset='Month')
    df['age_months'] = df['Month']
    
    return df


def get_age_in_months(birthdate_str):
    """Calculate age in months from birthdate (DD.MM.YYYY format)."""
    birthdate = datetime.strptime(birthdate_str, '%d.%m.%Y')
    now = datetime.now()
    months = (now.year - birthdate.year) * 12 + now.month - birthdate.month
    return months


def calculate_percentile_values(df, percentiles=PERCENTILES):
    """Calculate height/weight values for given percentiles from WHO data."""
    result = {'age_months': df['age_months'].values}
    
    # Check column format (percentile vs z-score)
    if 'P50' in df.columns or 'P 50' in df.columns:
        # Direct percentile columns
        for p in percentiles:
            col_name = f'P{int(p)}' if f'P{int(p)}' in df.columns else f'P {int(p)}'
            if col_name in df.columns:
                result[f'P{int(p)}'] = df[col_name].values
            else:
                # Interpolate from available percentiles
                result[f'P{int(p)}'] = np.nan * np.ones(len(df))
    else:
        # Z-score format - interpolate
        if 'SD5neg' in df.columns:
            z_cols = ['SD5neg', 'SD4neg', 'SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3', 'SD4']
            z_values = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]
        else:
            z_cols = ['SD3neg', 'SD2neg', 'SD1neg', 'SD0', 'SD1', 'SD2', 'SD3']
            z_values = [-3, -2, -1, 0, 1, 2, 3]
        
        for p in percentiles:
            z = stats.norm.ppf(p / 100)
            values = []
            for idx, row in df.iterrows():
                available_cols = [col for col in z_cols if col in df.columns and pd.notna(row.get(col))]
                if len(available_cols) >= 2:
                    age_values = [row[col] for col in available_cols]
                    corresponding_z = [z_values[z_cols.index(col)] for col in available_cols]
                    value = np.interp(z, corresponding_z, age_values)
                    values.append(value)
                else:
                    values.append(np.nan)
            result[f'P{int(p)}'] = values
    
    return pd.DataFrame(result)


def smooth_child_data(ages, values):
    """Apply smooth interpolation to child growth data."""
    if len(ages) < 2:
        return np.array(ages), np.array(values)
    
    sorted_indices = np.argsort(ages)
    ages_sorted = np.array(ages)[sorted_indices]
    values_sorted = np.array(values)[sorted_indices]
    
    if len(ages) >= 4:
        try:
            smoothing = len(ages) * 0.5
            f = interpolate.UnivariateSpline(ages_sorted, values_sorted, s=smoothing, k=min(3, len(ages)-1))
        except:
            f = interpolate.interp1d(ages_sorted, values_sorted, kind='linear')
        
        age_range = np.linspace(ages_sorted.min(), ages_sorted.max(), 200)
        smooth_values = f(age_range)
        return age_range, smooth_values
    elif len(ages) >= 2:
        f = interpolate.interp1d(ages_sorted, values_sorted, kind='linear')
        age_range = np.linspace(ages_sorted.min(), ages_sorted.max(), 50)
        smooth_values = f(age_range)
        return age_range, smooth_values
    else:
        return ages, values


def plot_growth_chart(child_name, birthdate, sex, heights, weights, chart_type='height', output_dir=None):
    """
    Generate WHO growth chart with child data overlay.
    
    Args:
        child_name: Name of the child
        birthdate: Birthdate string (DD.MM.YYYY)
        sex: 'F' or 'M'
        heights: List of (date_str, height_m) tuples (ISO format)
        weights: List of (date_str, weight_kg) tuples (ISO format)
        chart_type: 'height', 'weight', or 'bmi'
        output_dir: Output directory (default: skill data dir)
    
    Returns:
        Path to generated chart image
    """
    # Calculate child's current age + projection buffer
    birthdate_dt = datetime.strptime(birthdate, '%d.%m.%Y')
    current_age = get_age_in_months(birthdate)
    max_chart_age = current_age + 6  # 6 month projection
    
    # Load WHO data (only needed age ranges)
    if chart_type == 'height':
        who_df = load_who_height_data(sex, max_chart_age)
        ylabel = 'Height (cm)'
        unit_multiplier = 100
        title_suffix = 'Height-for-Age'
    elif chart_type == 'bmi':
        who_df = load_who_bmi_data(sex, max_chart_age)
        ylabel = 'BMI (kg/m²)'
        unit_multiplier = 1
        title_suffix = 'BMI-for-Age'
    else:
        who_df = load_who_weight_data(sex, max_chart_age)
        ylabel = 'Weight (kg)'
        unit_multiplier = 1
        title_suffix = 'Weight-for-Age'
    
    percentile_df = calculate_percentile_values(who_df, PERCENTILES)
    
    # Process child data
    child_ages = []
    child_values = []
    
    if chart_type == 'height' and heights:
        data_by_day = {}
        for date_str, value in heights:
            date_dt = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d')
            day_key = date_dt.date()
            age_months = (date_dt.year - birthdate_dt.year) * 12 + date_dt.month - birthdate_dt.month
            age_months += (date_dt.day - birthdate_dt.day) / 30.0
            if day_key not in data_by_day:
                data_by_day[day_key] = []
            data_by_day[day_key].append((age_months, value))
        
        for day, measurements in data_by_day.items():
            child_ages.append(np.mean([m[0] for m in measurements]))
            child_values.append(np.mean([m[1] for m in measurements]) * unit_multiplier)
    
    elif chart_type == 'weight' and weights:
        data_by_day = {}
        for date_str, value in weights:
            date_dt = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d')
            day_key = date_dt.date()
            age_months = (date_dt.year - birthdate_dt.year) * 12 + date_dt.month - birthdate_dt.month
            age_months += (date_dt.day - birthdate_dt.day) / 30.0
            if day_key not in data_by_day:
                data_by_day[day_key] = []
            data_by_day[day_key].append((age_months, value))
        
        for day, measurements in data_by_day.items():
            child_ages.append(np.mean([m[0] for m in measurements]))
            child_values.append(np.mean([m[1] for m in measurements]) * unit_multiplier)
    
    elif chart_type == 'bmi' and heights and weights:
        # Calculate BMI for days with both height and weight
        height_by_day = {}
        for date_str, height in heights:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d')
            day_key = dt.date()
            age_months = (dt.year - birthdate_dt.year) * 12 + dt.month - birthdate_dt.month
            if day_key not in height_by_day:
                height_by_day[day_key] = []
            height_by_day[day_key].append((age_months, height))
        
        weight_by_day = {}
        for date_str, weight in weights:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d')
            day_key = dt.date()
            age_months = (dt.year - birthdate_dt.year) * 12 + dt.month - birthdate_dt.month
            if day_key not in weight_by_day:
                weight_by_day[day_key] = []
            weight_by_day[day_key].append((age_months, weight))
        
        common_days = set(height_by_day.keys()) & set(weight_by_day.keys())
        for day in sorted(common_days):
            avg_height = np.mean([m[1] for m in height_by_day[day]])
            avg_weight = np.mean([m[1] for m in weight_by_day[day]])
            avg_age = np.mean([m[0] for m in height_by_day[day]])
            bmi = avg_weight / (avg_height ** 2)
            child_ages.append(avg_age)
            child_values.append(bmi)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Limit chart x-range
    # - Height/BMI: WHO ref up to 19y (228 months)
    # - Weight: WHO standards exist, but we intentionally cap display at 5y (60 months)
    max_who_age = 228 if chart_type in ['height', 'bmi'] else 60
    max_age = min(current_age + 6, max_who_age)

    # For weight charts we want to *only show the first 5 years*, even for older kids.
    # Also filter child points to avoid y-limits being skewed by out-of-range data.
    if chart_type == 'weight' and child_ages:
        filtered = [(a, v) for a, v in zip(child_ages, child_values) if a <= max_age]
        child_ages = [a for a, _ in filtered]
        child_values = [v for _, v in filtered]

    age_range = percentile_df['age_months'].values
    age_mask = age_range <= max_age
    
    # Plot percentile bands
    for i in range(len(PERCENTILES) - 1):
        p_low, p_high = PERCENTILES[i], PERCENTILES[i + 1]
        color = PERCENTILE_COLORS.get((p_low, p_high), '#e8f4f8')
        ax.fill_between(
            age_range[age_mask],
            percentile_df[f'P{int(p_low)}'].values[age_mask],
            percentile_df[f'P{int(p_high)}'].values[age_mask],
            color=color, alpha=0.6, linewidth=0
        )
    
    # Plot percentile lines
    for p in PERCENTILES:
        label = f'{int(p)}th' if p != 50 else 'Median'
        linewidth = 1.5 if p == 50 else 1.0
        linestyle = '-' if p == 50 else '--'
        ax.plot(
            age_range[age_mask],
            percentile_df[f'P{int(p)}'].values[age_mask],
            color='#0066cc', linewidth=linewidth, linestyle=linestyle,
            alpha=0.7, label=label
        )
    
    # Plot child data
    if child_ages:
        ax.scatter(child_ages, child_values, color='#cc0000', s=50, zorder=5, alpha=0.7, label=f'{child_name} (actual)')
        
        smooth_ages, smooth_values = smooth_child_data(child_ages, child_values)
        past_mask = smooth_ages <= current_age
        future_mask = smooth_ages > current_age
        
        if np.any(past_mask):
            ax.plot(smooth_ages[past_mask], smooth_values[past_mask],
                   color='#cc0000', linewidth=2, zorder=4, label=f'{child_name} (trend)')
        
        if np.any(future_mask) and np.any(past_mask):
            transition_idx = np.where(past_mask)[0][-1]
            future_ages = np.concatenate([[smooth_ages[transition_idx]], smooth_ages[future_mask]])
            future_vals = np.concatenate([[smooth_values[transition_idx]], smooth_values[future_mask]])
            ax.plot(future_ages, future_vals,
                   color='#cc0000', linewidth=2, linestyle='--', zorder=4,
                   label=f'{child_name} (projection)', alpha=0.6)
    
    # Formatting
    ax.set_xlabel('Age (years)', fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
    ax.set_title(f'{child_name} - WHO {title_suffix} Chart', fontsize=14, fontweight='bold')
    
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x/12)}' if x/12 == int(x/12) else f'{x/12:.1f}'))
    ax.xaxis.set_major_locator(MultipleLocator(12))
    
    for month in range(0, int(max_age) + 1, 12):
        ax.axvline(month, color='gray', linewidth=1.2, alpha=0.4, linestyle='-', zorder=0)
    
    ax.grid(True, alpha=0.2, linestyle=':', linewidth=0.5, axis='y')
    ax.legend(loc='lower right', fontsize=9, framealpha=0.9)
    ax.set_xlim(0, max_age)
    
    # Y-axis limits
    if child_values:
        data_min, data_max = min(child_values), max(child_values)
        current_age_idx = np.argmin(np.abs(age_range - current_age))
        who_min = percentile_df[f'P{int(PERCENTILES[0])}'].values[current_age_idx]
        who_max = percentile_df[f'P{int(PERCENTILES[-1])}'].values[current_age_idx]
        ax.set_ylim(min(data_min, who_min) * 0.95, max(data_max, who_max) * 1.05)
    else:
        y_min = percentile_df[f'P{int(PERCENTILES[0])}'].values[age_mask].min() * 0.95
        y_max = percentile_df[f'P{int(PERCENTILES[-1])}'].values[age_mask].max() * 1.05
        ax.set_ylim(y_min, y_max)
    
    plt.tight_layout()

    # WHO emblem (if available)
    add_who_emblem(ax, loc='upper left')
    
    # Save
    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = get_base_output_dir()

    out_dir.mkdir(parents=True, exist_ok=True)
    output_file = out_dir / f'{child_name.lower().replace(" ", "_")}_{chart_type}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    return str(output_file)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate WHO growth charts')
    parser.add_argument('name', help='Child name')
    parser.add_argument('birthdate', help='Birthdate (DD.MM.YYYY)')
    parser.add_argument('--sex', '-s', choices=['F', 'M'], default='F', help='Sex (F/M)')
    parser.add_argument('--type', '-t', choices=['height', 'weight', 'bmi', 'all'], default='all', help='Chart type')
    parser.add_argument('--data', '-d', help='JSON file with heights/weights data')
    parser.add_argument('--output', '-o', help='Output directory')
    
    args = parser.parse_args()
    
    heights, weights = [], []
    if args.data:
        with open(args.data) as f:
            data = json.load(f)
            heights = data.get('heights', [])
            weights = data.get('weights', [])
    
    chart_types = ['height', 'weight', 'bmi'] if args.type == 'all' else [args.type]
    
    for ct in chart_types:
        if ct == 'height' and not heights:
            print(f"Skipping {ct} chart (no height data)", file=sys.stderr)
            continue
        if ct == 'weight' and not weights:
            print(f"Skipping {ct} chart (no weight data)", file=sys.stderr)
            continue
        if ct == 'bmi' and (not heights or not weights):
            print(f"Skipping {ct} chart (need both height and weight)", file=sys.stderr)
            continue
        
        output = plot_growth_chart(
            args.name, args.birthdate, args.sex,
            heights, weights, ct, args.output
        )
        print(f"✓ {output}")


if __name__ == '__main__':
    main()
