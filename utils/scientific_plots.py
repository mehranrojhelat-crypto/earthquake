# scientific_plots.py
"""
نمودارهای علمی و آماده انتشار بر اساس سبک کتاب
Introduction to Python in Earth Science Data Analysis
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

# ---------- تنظیمات کلی سبک کتاب ----------
rcParams['font.size'] = 11
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 13
rcParams['figure.dpi'] = 120
rcParams['savefig.dpi'] = 300          # کیفیت بالا برای مقاله/گزارش
rcParams['savefig.bbox'] = 'tight'

# رنگ‌های پیشنهادی (سبک کتاب)
COLOR_MAIN = '#1f77b4'      # آبی
COLOR_STRONG = '#d62728'    # قرمز برای زلزله‌های قوی
COLOR_EDGE = '#000000'
CMAP = 'YlOrRd'


def plot_descriptive_stats(df, save_prefix="eq"):
    """
    آمار توصیفی کامل + هیستوگرام + boxplot + همبستگی
    مطابق تأکید کتاب روی فهم توزیع قبل از مدل‌سازی
    """
    numeric_cols = ['magnitude', 'depth_km', 'latitude', 'longitude']

    # ---- آمار توصیفی ----
    print("=" * 50)
    print("آمار توصیفی:")
    print(df[numeric_cols].describe().round(2))
    print("\nدرصد زلزله‌های با magnitude ≥ ۵:")
    print((df['magnitude'] >= 5.0).value_counts(normalize=True).round(3) * 100)

    # ---- هیستوگرام magnitude (سبک کتاب) ----
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df['magnitude'], bins='auto', edgecolor=COLOR_EDGE,
            color=COLOR_MAIN, alpha=0.8, density=True)
    ax.set_xlabel(r'Magnitude ($M_w$)')
    ax.set_ylabel('Probability Density')
    ax.set_title('Distribution of Earthquake Magnitudes (Iran, last 10 years)')
    ax.grid(True, alpha=0.3)
    fig.savefig(f'{save_prefix}_hist_magnitude.png', dpi=300)
    plt.close(fig)

    # ---- هیستوگرام تجمعی ----
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df['magnitude'], bins='auto', density=True, histtype='step',
            linewidth=2, cumulative=True, color=COLOR_MAIN)
    ax.set_xlabel(r'Magnitude ($M_w$)')
    ax.set_ylabel('Cumulative Probability')
    ax.set_title('Cumulative Distribution of Magnitudes')
    ax.grid(True, alpha=0.3)
    fig.savefig(f'{save_prefix}_hist_cumulative.png', dpi=300)
    plt.close(fig)

    # ---- Boxplot ----
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    sns.boxplot(y=df['magnitude'], ax=axes[0], color='#c7ddf4')
    axes[0].set_ylabel(r'Magnitude ($M_w$)')
    axes[0].set_title('Boxplot - Magnitude')

    sns.boxplot(y=df['depth_km'], ax=axes[1], color='#ffb3b3')
    axes[1].set_ylabel('Depth [km]')
    axes[1].set_title('Boxplot - Depth')
    fig.tight_layout()
    fig.savefig(f'{save_prefix}_boxplots.png', dpi=300)
    plt.close(fig)

    # ---- ماتریس همبستگی ----
    fig, ax = plt.subplots(figsize=(7, 6))
    corr = df[numeric_cols].corr()
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, square=True, linewidths=0.5, ax=ax)
    ax.set_title('Correlation Matrix')
    fig.tight_layout()
    fig.savefig(f'{save_prefix}_correlation.png', dpi=300)
    plt.close(fig)

    print(f"\nنمودارهای توصیفی ذخیره شدند با پیشوند: {save_prefix}_*.png")


def plot_binary_diagrams(df, save_prefix="eq"):
    """
    نمودارهای باینری به سبک کتاب (فصل ۳ و ۴)
    """
    # ---- Magnitude vs Depth ----
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(df['depth_km'], df['magnitude'],
                    c=df['magnitude'], cmap=CMAP,
                    s=df['magnitude']**2 * 8,   # اندازه متناسب با بزرگی
                    edgecolor=COLOR_EDGE, linewidth=0.4, alpha=0.75)
    ax.set_xlabel('Depth [km]')
    ax.set_ylabel(r'Magnitude ($M_w$)')
    ax.set_title('Magnitude vs Depth')
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label(r'$M_w$')
    ax.grid(True, alpha=0.3)
    fig.savefig(f'{save_prefix}_mag_vs_depth.png', dpi=300)
    plt.close(fig)

    # ---- Latitude vs Longitude با رنگ بر اساس magnitude ----
    fig, ax = plt.subplots(figsize=(9, 7))
    sc = ax.scatter(df['longitude'], df['latitude'],
                    c=df['magnitude'], cmap=CMAP,
                    s=df['magnitude']**2 * 6,
                    edgecolor='k', linewidth=0.3, alpha=0.7)
    ax.set_xlabel('Longitude [°E]')
    ax.set_ylabel('Latitude [°N]')
    ax.set_title('Spatial Distribution of Earthquakes')
    ax.set_aspect('equal')
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label(r'Magnitude ($M_w$)')
    fig.savefig(f'{save_prefix}_spatial_scatter.png', dpi=300)
    plt.close(fig)

    # ---- مقایسه زلزله‌های ضعیف و قوی (مثل برش Zr در کتاب) ----
    strong = df[df['magnitude'] >= 5.0]
    weak = df[df['magnitude'] < 5.0]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(weak['depth_km'], weak['magnitude'],
               c='#a6cee3', s=25, edgecolor='k', linewidth=0.3,
               label=r'$M_w < 5$', alpha=0.7)
    ax.scatter(strong['depth_km'], strong['magnitude'],
               c='#e31a1c', s=45, edgecolor='k', linewidth=0.4,
               label=r'$M_w \geq 5$', alpha=0.8)
    ax.set_xlabel('Depth [km]')
    ax.set_ylabel(r'Magnitude ($M_w$)')
    ax.set_title('Strong vs Weak Earthquakes')
    ax.legend(title='Category', frameon=True, framealpha=0.95)
    ax.grid(True, alpha=0.3)
    fig.savefig(f'{save_prefix}_strong_vs_weak.png', dpi=300)
    plt.close(fig)

    print(f"نمودارهای باینری ذخیره شدند با پیشوند: {save_prefix}_*.png")


def plot_pairplot(df, save_prefix="eq"):
    """
    Pairplot چندمتغیره (سبک کتاب فصل ۴)
    """
    cols = ['magnitude', 'depth_km', 'latitude', 'longitude']
    g = sns.pairplot(df[cols], corner=True, diag_kind='hist',
                     plot_kws={'alpha': 0.5, 's': 15, 'edgecolor': 'none'})
    g.fig.suptitle('Pairwise Relationships', y=1.02)
    g.savefig(f'{save_prefix}_pairplot.png', dpi=300)
    plt.close()
    print(f"Pairplot ذخیره شد: {save_prefix}_pairplot.png")


def run_all_scientific_plots(df):
    """اجرای کامل همه نمودارهای علمی"""
    if df.empty:
        print("داده خالی است.")
        return

    print("شروع تولید نمودارهای علمی (سبک کتاب)...")
    plot_descriptive_stats(df)
    plot_binary_diagrams(df)
    plot_pairplot(df)
    print("✅ همه نمودارهای علمی با DPI=300 ذخیره شدند.")