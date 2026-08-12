"""
Codon Category Tracking Lab
===========================
A focused explorer for tracking how exact starting codons move through
amino-acid property categories across generations.

Run: python category_tracking.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math, os, collections, fractions, threading

from engine.exact_tracking import run_simulation as _engine_run_simulation
from engine.genetic_code import (
    AA_AROMATIC as _AA_AROMATIC,
    AA_FULL as _AA_FULL,
    AA_PROPERTIES as _AA_PROPERTIES,
    AA_SMALL as _AA_SMALL,
    ALL_AAS as _ALL_AAS,
    BASES as _BASES,
    CODON_COUNT_GROUPS as _CODON_COUNT_GROUPS,
    CODON_COUNT_MAP as _CODON_COUNT_MAP,
    CODON_TABLE as _CODON_TABLE,
    PROPERTY_LABELS as _PROPERTY_LABELS,
    STOP_CODONS as _STOP_CODONS,
    VALID_CODONS as _VALID_CODONS,
    count_codons_for_aa as _engine_count_codons_for_aa,
    get_codon_count as _engine_get_codon_count,
    get_primary_group as _engine_get_primary_group,
    get_primary_group_name as _engine_get_primary_group_name,
)
from engine.mutation_matrix import (
    PRESET_AC as _PRESET_AC,
    PRESET_AG as _PRESET_AG,
    PRESET_AT as _PRESET_AT,
    build_substitution_matrix as _engine_build_substitution_matrix,
)
from engine.sampled_tracking import run_experiment as _engine_run_experiment
from engine.summaries import (
    convergence_generation as _engine_convergence_generation,
    convergence_text as _engine_convergence_text,
    property_stop_counter as _engine_property_stop_counter,
)

# ─────────────────────────────────────────────────────────────────────────────
# Biological data
# ─────────────────────────────────────────────────────────────────────────────

BASES = _BASES
STOP_CODONS = _STOP_CODONS
CODON_TABLE = _CODON_TABLE
AA_FULL = _AA_FULL
VALID_CODONS = _VALID_CODONS
ALL_AAS = _ALL_AAS

AA_COLORS = [
    "#5DCAA5","#7F77DD","#EF9F27","#D4537E","#378ADD","#639922",
    "#D85A30","#1D9E75","#BA7517","#E24B4A","#534AB7",
    "#0F6E56","#993556","#854F0B","#185FA5","#3B6D11","#72243E",
    "#888780","#993C1D","#0C447C","#5599AA",
]
AA_COLOR_MAP = {aa: AA_COLORS[i % len(AA_COLORS)] for i, aa in enumerate(ALL_AAS)}

AA_PROPERTIES = _AA_PROPERTIES

_PROPERTY_GROUP_COLORS = {
    "hydrophobic": "#E8822A",
    "polar_uncharged": "#378ADD",
    "pos_charged": "#5DCAA5",
    "neg_charged": "#D4537E",
    "special": "#9B59B6",
}
PROPERTY_GROUPS = {
    key: (label, _PROPERTY_GROUP_COLORS[key])
    for key, label in _PROPERTY_LABELS.items()
}

PROPERTY_GROUP_BG = {
    "hydrophobic":     "#FEF0E6",
    "polar_uncharged": "#E8F4FD",
    "pos_charged":     "#E8F8F5",
    "neg_charged":     "#FDEBF0",
    "special":         "#F5EEF8",
}

AA_AROMATIC = _AA_AROMATIC
AA_SMALL = _AA_SMALL

def get_primary_group(aa):
    return _engine_get_primary_group(aa)

def get_primary_group_name(aa):
    return _engine_get_primary_group_name(aa)

def property_stop_counter(stop_data):
    """Stop totals grouped by starting biochemical property."""
    return _engine_property_stop_counter(stop_data)

def property_color_map_by_name():
    return {name: col for name, col in PROPERTY_GROUPS.values()}

def convergence_generation(series, threshold=1e-4):
    return _engine_convergence_generation(series, threshold).to_legacy_tuple()

def convergence_text(series, threshold=1e-4):
    return _engine_convergence_text(series, threshold)

def count_codons_for_aa(aa):
    return _engine_count_codons_for_aa(aa)

CODON_COUNT_MAP = _CODON_COUNT_MAP
CODON_COUNT_GROUPS = _CODON_COUNT_GROUPS

CODON_COUNT_COLORS = {1:"#D4537E",2:"#378ADD",3:"#EF9F27",4:"#5DCAA5",6:"#9B59B6"}
CODON_COUNT_BG     = {1:"#FDEBF0",2:"#E8F4FD",3:"#FEF9E7",4:"#E8F8F5",6:"#F5EEF8"}

def get_codon_count(aa):
    return _engine_get_codon_count(aa)

BG       = "#F6F8F1"
BG_PANEL = "#FEFFFB"
BG_RAIL  = "#E8EFE2"
BG_SOFT  = "#F0F4EA"
INK      = "#18212B"
MUTED    = "#667068"
RULE     = "#CBD6C5"
ACCENT   = "#146C72"

# ── Fixed preset probability ──────────────────────────────────────────────────
PRESET_AT = _PRESET_AT
PRESET_AG = _PRESET_AG
PRESET_AC = _PRESET_AC
PRESET_COLOR  = "#7A4E8A"   # preset = plum
USER_COLOR    = ACCENT      # user = teal
STOP_COLOR    = "#B84242"

# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────

def lighten_hex(hex_color, factor=0.55):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    r2 = int(r + (255-r)*factor)
    g2 = int(g + (255-g)*factor)
    b2 = int(b + (255-b)*factor)
    return f"#{r2:02X}{g2:02X}{b2:02X}"


def _text_px(text, size=8, mono=False):
    """Quick canvas text width estimate for collision-safe chart labels."""
    return len(str(text)) * size * (0.64 if mono else 0.56)


def _fit_text(text, max_px, size=8, mono=False, min_chars=3):
    """Shorten text so it fits inside the requested pixel budget."""
    text = str(text)
    if max_px <= 0:
        return ""
    if _text_px(text, size, mono) <= max_px:
        return text
    max_chars = max(min_chars, int(max_px / (size * (0.64 if mono else 0.56))))
    if max_chars >= len(text):
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return text[:max_chars-3] + "..."


def _chart_title(canvas, W, y, text, font=("Helvetica", 11, "bold")):
    canvas.create_text(W//2, y, text=_fit_text(text, W-18, font[1]),
                       font=font, fill="#222", anchor="center")


def _safe_value_label(canvas, x_right, y, text, color, chart_left, chart_right,
                      bar_w, font=("Helvetica", 8)):
    """Place a bar value label without letting it collide with the legend/edge."""
    text = str(text)
    size = font[1]
    width = _text_px(text, size)
    if x_right + 5 + width <= chart_right:
        canvas.create_text(x_right+5, y, text=text, anchor="w",
                           font=font, fill=color)
    elif bar_w > width + 12:
        canvas.create_text(x_right-5, y, text=text, anchor="e",
                           font=font, fill="white")
    else:
        canvas.create_text(chart_right, y, text=_fit_text(text, chart_right-chart_left, size),
                           anchor="e", font=font, fill=color)


def parse_prob(s):
    s = s.strip()
    try:
        if '/' in s:
            num, den = s.split('/', 1)
            return float(num.strip()) / float(den.strip())
        if s.endswith('%'):
            return float(s[:-1]) / 100.0
        return float(s)
    except Exception:
        raise ValueError(f"Cannot parse probability: '{s}'")


def build_substitution_matrix(p_at, p_ag, p_ac):
    return _engine_build_substitution_matrix(p_at, p_ag, p_ac)

# ─────────────────────────────────────────────────────────────────────────────
# Scrollable frame helper
# ─────────────────────────────────────────────────────────────────────────────

def make_scrollable(parent, bg=None):
    bg = bg or "#ffffff"
    outer = tk.Frame(parent, bg=bg)
    vsb = tk.Scrollbar(outer, orient="vertical")
    vsb.pack(side="right", fill="y")
    cv = tk.Canvas(outer, bg=bg, highlightthickness=0, yscrollcommand=vsb.set)
    cv.pack(side="left", fill="both", expand=True)
    vsb.config(command=cv.yview)
    inner = tk.Frame(cv, bg=bg)
    win_id = cv.create_window((0, 0), window=inner, anchor="nw")

    def _on_inner(e):  cv.configure(scrollregion=cv.bbox("all"))
    def _on_canvas(e): cv.itemconfig(win_id, width=e.width)
    inner.bind("<Configure>", _on_inner)
    cv.bind("<Configure>", _on_canvas)

    def _mw(e):
        if e.num == 4:   cv.yview_scroll(-1, "units")
        elif e.num == 5: cv.yview_scroll(1,  "units")
        else:            cv.yview_scroll(int(-1*(e.delta/120)), "units")

    for w in (cv, inner):
        w.bind("<MouseWheel>", _mw)
        w.bind("<Button-4>",   _mw)
        w.bind("<Button-5>",   _mw)
    return outer, inner

# ─────────────────────────────────────────────────────────────────────────────
# Simulation
# ─────────────────────────────────────────────────────────────────────────────

def run_simulation(n_generations, sub_matrix, start_weights=None):
    return _engine_run_simulation(
        n_generations,
        sub_matrix,
        start_weights,
    ).to_legacy_tuple()


def run_experiment(n_generations, sub_matrix, start_weights):
    return _engine_run_experiment(
        n_generations,
        sub_matrix,
        start_weights,
    ).to_legacy_tuple()

# ─────────────────────────────────────────────────────────────────────────────
# Chart helpers
# ─────────────────────────────────────────────────────────────────────────────

def draw_bar_chart(canvas, weight_counter, title, color_map=None,
                   top_n=21, x_label="", count_counter=None,
                   normalize=False, filter_aa_set=None,
                   bar_color_override=None):
    canvas.delete("all")
    W = canvas.winfo_width(); H = canvas.winfo_height()
    if W < 50 or H < 50: return

    if filter_aa_set is not None:
        weight_counter = type(weight_counter)(
            {k: v for k, v in weight_counter.items() if k in filter_aa_set})

    items = weight_counter.most_common(top_n)
    if not items:
        canvas.create_text(W//2, H//2, text="No data.", fill="#aaa",
                           font=("Helvetica", 11)); return

    total = sum(weight_counter.values()) or 1
    if normalize:
        items = [(lbl, 100.0*val/total) for lbl,val in items]
        items.sort(key=lambda x: -x[1])
        badge = "  [% of total]"; fmt = lambda v: f"{v:.1f}%"
        x_footer = "% of group total"
    else:
        items = [(lbl, val/total) for lbl,val in items]
        items.sort(key=lambda x: -x[1])
        badge = "  [probability 0–1]"; fmt = lambda v: f"{v:.4f}"
        x_footer = "Probability  (0 = impossible, 1 = certain)"

    label_px = max((_text_px(lbl, 9, True) for lbl, _ in items), default=120)
    value_px = max((_text_px(fmt(val), 8) for _, val in items), default=70)
    pad_l = int(min(230, max(92, label_px + 18)))
    pad_r = int(min(190, max(105, value_px + 42)))
    if W - pad_l - pad_r < 120:
        pad_l = min(pad_l, max(68, W//4))
        pad_r = min(pad_r, max(72, W//5))
    pad_t=40; pad_b=28
    n = len(items)
    bar_h = max(12, min(26, (H-pad_t-pad_b)//max(n,1)-4))
    gap   = max(2, (H-pad_t-pad_b-n*bar_h)//max(n+1,1))
    max_v = items[0][1] or 1
    chart_w = max(20, W-pad_l-pad_r)
    chart_right = pad_l + chart_w

    _chart_title(canvas, W, 16, title+badge)
    for i,(label,val) in enumerate(items):
        bw  = max(2, int(val/max_v*chart_w))
        y   = pad_t + i*(bar_h+gap)
        if bar_color_override:
            color = bar_color_override
        elif color_map:
            color = color_map.get(label, "#378ADD")
        else:
            color = "#378ADD"
        canvas.create_rectangle(pad_l, y, pad_l+bw, y+bar_h, fill=color, outline="")
        safe_label = _fit_text(label, pad_l-12, 9, True)
        canvas.create_text(pad_l-6, y+bar_h//2, text=safe_label,
                           anchor="e", font=("Courier",9), fill="#333")
        cnt_str = (f"  n={count_counter[label]}" if count_counter else "")
        _safe_value_label(canvas, pad_l+bw, y+bar_h//2, fmt(val)+cnt_str,
                          "#444", pad_l, chart_right, bw, font=("Helvetica",8))

    canvas.create_line(pad_l, H-pad_b, chart_right, H-pad_b, fill="#ccc", width=1)
    canvas.create_line(pad_l, pad_t,   pad_l,   H-pad_b, fill="#ccc", width=1)
    for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
        tx = pad_l + int(frac*chart_w)
        canvas.create_line(tx, H-pad_b, tx, H-pad_b+4, fill="#bbb")
        tick_val = frac*(100 if normalize else 1)
        tick_str = f"{tick_val:.0f}%" if normalize else f"{tick_val:.2f}"
        canvas.create_text(tx, H-pad_b+6, text=tick_str,
                           anchor="n", font=("Helvetica",7), fill="#999")
    canvas.create_text(W//2, H-8, text=x_footer,
                       font=("Helvetica",8), fill="#888", anchor="center")


def draw_codon_bar_chart(canvas, weight_counter, title, top_n=30,
                          count_counter=None, normalize=False, filter_aa_set=None):
    codon_filter = None
    if filter_aa_set is not None:
        codon_filter = {c for c in weight_counter if CODON_TABLE.get(c,"?") in filter_aa_set}
    color_map = {c: AA_COLOR_MAP.get(CODON_TABLE.get(c,"?"), "#888") for c in weight_counter}
    draw_bar_chart(canvas, weight_counter, title, color_map=color_map,
                   top_n=top_n, x_label="Probability",
                   count_counter=count_counter, normalize=normalize,
                   filter_aa_set=codon_filter)


def draw_stacked_bar_chart(canvas, data, title, x_label="Starting AA group",
                           normalize=False):
    canvas.delete("all")
    W = canvas.winfo_width(); H = canvas.winfo_height()
    if W < 50 or H < 50: return
    start_aas = sorted(data.keys())
    if not start_aas: return
    all_fin_aas = sorted(set(fa for row in data.values() for fa in row),
                         key=lambda a: -sum(data[sa].get(a,0) for sa in start_aas))
    pad_l=50
    pad_r=min(210, max(120, int(max((_text_px(fa, 8) for fa in all_fin_aas[:18]), default=60)+42)))
    if W - pad_l - pad_r < 160:
        pad_r = max(92, W//5)
    pad_t=40; pad_b=60
    chart_w = max(30, W-pad_l-pad_r); chart_h = H-pad_t-pad_b
    bar_w   = max(8, chart_w//max(len(start_aas),1)-4)
    badge   = "  [% per start AA]" if normalize else "  [probability 0–1 per start AA]"
    y_ticks = [(0,"0%"),(0.25,"25%"),(0.5,"50%"),(0.75,"75%"),(1.0,"100%")] if normalize \
              else [(0,"0.0"),(0.25,"0.25"),(0.5,"0.5"),(0.75,"0.75"),(1.0,"1.0")]
    _chart_title(canvas, W, 16, title+badge)
    for bi, sa in enumerate(start_aas):
        x = pad_l + bi*(chart_w//len(start_aas)) + (chart_w//len(start_aas)-bar_w)//2
        total = sum(data[sa].values()) or 1
        y_cursor = pad_t + chart_h
        for fa in all_fin_aas:
            fval = data[sa].get(fa, 0)
            if fval <= 0: continue
            prob  = fval/total
            seg_h = max(1, int(prob*chart_h))
            col   = AA_COLOR_MAP.get(fa, "#888")
            canvas.create_rectangle(x, y_cursor-seg_h, x+bar_w, y_cursor,
                                    fill=col, outline="white", width=1)
            y_cursor -= seg_h
        canvas.create_text(x+bar_w//2, pad_t+chart_h+6, text=sa[:3],
                           anchor="n", font=("Courier",7), fill="#333")
    canvas.create_line(pad_l, pad_t, pad_l, pad_t+chart_h, fill="#ccc", width=1)
    for frac, lbl in y_ticks:
        ty = int(pad_t+chart_h-frac*chart_h)
        canvas.create_line(pad_l-3, ty, pad_l, ty, fill="#bbb")
        canvas.create_text(pad_l-5, ty, text=lbl, anchor="e",
                           font=("Helvetica",7), fill="#888")
    lx = W-pad_r+10
    canvas.create_text(lx, pad_t, text=_fit_text("Final AA", pad_r-16, 8), anchor="nw",
                       font=("Helvetica",8,"bold"), fill="#333")
    for li, fa in enumerate(all_fin_aas[:18]):
        col = AA_COLOR_MAP.get(fa, "#888"); ly = pad_t+16+li*14
        canvas.create_rectangle(lx, ly, lx+10, ly+10, fill=col, outline="")
        canvas.create_text(lx+13, ly, text=_fit_text(fa, pad_r-30, 8), anchor="nw",
                           font=("Helvetica",8), fill="#333")
    canvas.create_text(W//2, H-12, text=x_label,
                       font=("Helvetica",8), fill="#888", anchor="center")


# ─── NEW: Multi-series line chart (per-generation convergence) ───────────────

def draw_line_chart(canvas, series, title, x_label="Generation",
                    y_label="Probability", top_n=8, normalize=False):
    """
    series: dict {label: [v0, v1, ..., v_{N-1}]}  one value per generation.
    Draws the top_n series (by final value) as coloured lines so you can see
    how each amino acid's share rises/falls across generations (convergence).
    """
    canvas.delete("all")
    W = canvas.winfo_width(); H = canvas.winfo_height()
    if W < 60 or H < 60: return
    if not series:
        canvas.create_text(W//2, H//2, text="No data", fill="#aaa",
                           font=("Helvetica",11)); return

    n_gen = max((len(v) for v in series.values()), default=0)
    if n_gen < 2:
        canvas.create_text(W//2, H//2,
                           text="Need ≥ 2 generations to show a trend",
                           fill="#aaa", font=("Helvetica",10)); return

    # Per-generation normalisation so each column sums to 1 (share view)
    norm_series = {}
    col_tot = [0.0]*n_gen
    for lbl, vals in series.items():
        for g in range(n_gen):
            col_tot[g] += (vals[g] if g < len(vals) else 0)
    for lbl, vals in series.items():
        norm_series[lbl] = [
            ((vals[g] if g < len(vals) else 0) / col_tot[g]) if col_tot[g] > 0 else 0
            for g in range(n_gen)
        ]

    # Pick top_n series by their peak share
    ranked = sorted(norm_series.items(), key=lambda kv: -max(kv[1]))
    shown = ranked[:top_n]

    legend_px = max((_text_px(f"{lbl} {vals[-1]:.2f}", 8) for lbl, vals in shown),
                    default=90)
    pad_l=54; pad_r=int(min(190, max(120, legend_px + 34))); pad_t=36; pad_b=40
    if W - pad_l - pad_r < 140:
        pad_r = max(95, W//5)
    plot_w = max(30, W - pad_l - pad_r)
    plot_h = H - pad_t - pad_b
    max_y = max((max(v) for _, v in shown), default=1) or 1
    # round max_y up a little for headroom
    max_y = min(1.0, max_y * 1.1)

    badge = "  [share per generation]"
    _chart_title(canvas, W, 14, title+badge)

    # Axes
    canvas.create_line(pad_l, pad_t, pad_l, pad_t+plot_h, fill="#ccc")
    canvas.create_line(pad_l, pad_t+plot_h, pad_l+plot_w, pad_t+plot_h, fill="#ccc")

    # Y ticks
    for frac in [0, 0.25, 0.5, 0.75, 1.0]:
        yy = pad_t + plot_h - frac*plot_h
        val = frac*max_y
        canvas.create_line(pad_l-3, yy, pad_l, yy, fill="#bbb")
        canvas.create_text(pad_l-5, yy, text=f"{val:.2f}",
                           anchor="e", font=("Helvetica",7), fill="#999")

    # X ticks (a handful)
    n_ticks = min(n_gen, 8)
    for t in range(n_ticks):
        g = int(t*(n_gen-1)/max(n_ticks-1,1))
        xx = pad_l + (g/(n_gen-1))*plot_w if n_gen > 1 else pad_l
        canvas.create_line(xx, pad_t+plot_h, xx, pad_t+plot_h+3, fill="#bbb")
        canvas.create_text(xx, pad_t+plot_h+5, text=str(g+1),
                           anchor="n", font=("Helvetica",7), fill="#999")

    # Lines
    for lbl, vals in shown:
        col = AA_COLOR_MAP.get(lbl, "#888")
        pts = []
        for g in range(n_gen):
            x = pad_l + (g/(n_gen-1))*plot_w if n_gen > 1 else pad_l
            y = pad_t + plot_h - (vals[g]/max_y)*plot_h
            pts.extend([x, y])
        if len(pts) >= 4:
            canvas.create_line(*pts, fill=col, width=2, smooth=True)

    # Legend
    lx = W - pad_r + 8
    canvas.create_text(lx, pad_t-4, text=_fit_text("Final share", pad_r-12, 8), anchor="nw",
                       font=("Helvetica",8,"bold"), fill="#333")
    for i,(lbl, vals) in enumerate(shown):
        col = AA_COLOR_MAP.get(lbl, "#888")
        ly = pad_t + 12 + i*15
        canvas.create_line(lx, ly+5, lx+14, ly+5, fill=col, width=3)
        legend_text = _fit_text(f"{lbl} {vals[-1]:.2f}", pad_r-28, 8)
        canvas.create_text(lx+18, ly+5, text=legend_text,
                           anchor="w", font=("Helvetica",8), fill="#333")

    canvas.create_text(pad_l+plot_w//2, H-10, text=x_label,
                       font=("Helvetica",8), fill="#888", anchor="center")


# ─── NEW: Retention line chart (share over generations, custom colours) ──────

def draw_retention_lines(canvas, series, title, color_map=None,
                         x_label="Generation", highlight=None,
                         show_share=True, marker_gen=None, marker_label=None,
                         marker_color="#111", integer_values=False):
    """
    series: dict {label: [v0, v1, ..., v_{N-1}]} raw weights per generation.
    Draws each label's SHARE (per-generation normalised to sum=1) as a line,
    so you can see how mass redistributes across categories/AAs over time.
    color_map: dict label->hex. highlight: a label to draw thicker (the
    'started here' series). Returns nothing.
    """
    canvas.delete("all")
    W = canvas.winfo_width(); H = canvas.winfo_height()
    if W < 60 or H < 60: return
    if not series:
        canvas.create_text(W//2, H//2, text="No data", fill="#aaa",
                           font=("Helvetica",11)); return
    N = max((len(v) for v in series.values()), default=0)
    if N < 1:
        canvas.create_text(W//2, H//2, text="No data", fill="#aaa",
                           font=("Helvetica",11)); return

    # Per-generation share normalisation
    col_tot = [0.0]*N
    for vals in series.values():
        for g in range(N):
            col_tot[g] += (vals[g] if g < len(vals) else 0)
    norm = {}
    for lbl, vals in series.items():
        if show_share:
            norm[lbl] = [((vals[g] if g < len(vals) else 0)/col_tot[g]) if col_tot[g] > 0 else 0
                         for g in range(N)]
        else:
            norm[lbl] = [(vals[g] if g < len(vals) else 0) for g in range(N)]

    legend_texts = []
    for lbl, vals in norm.items():
        star = " < start" if (highlight is not None and lbl == highlight) else ""
        legend_texts.append(f"{lbl} {vals[-1]*100:.0f}%{star}" if show_share
                            else (f"{lbl} {int(round(vals[-1]))}{star}" if integer_values
                                  else f"{lbl} {vals[-1]:.2f}{star}"))
    legend_px = max((_text_px(t, 8) for t in legend_texts), default=110)
    pad_l=54; pad_r=int(min(220, max(140, legend_px + 34))); pad_t=34; pad_b=40
    if W - pad_l - pad_r < 140:
        pad_r = max(105, W//5)
    plot_w = max(30, W - pad_l - pad_r)
    plot_h = H - pad_t - pad_b
    max_y = max((max(v) for v in norm.values()), default=1) or 1
    if show_share:
        max_y = min(1.0, max_y*1.1)
    else:
        max_y = max_y*1.1

    badge = "  [share per generation]" if show_share else "  [weight]"
    _chart_title(canvas, W, 14, title+badge)

    canvas.create_line(pad_l, pad_t, pad_l, pad_t+plot_h, fill="#ccc")
    canvas.create_line(pad_l, pad_t+plot_h, pad_l+plot_w, pad_t+plot_h, fill="#ccc")

    for frac in [0, 0.25, 0.5, 0.75, 1.0]:
        yy = pad_t + plot_h - frac*plot_h
        canvas.create_line(pad_l-3, yy, pad_l, yy, fill="#bbb")
        if show_share:
            lab = f"{int(frac*100)}%"
        elif integer_values:
            lab = f"{int(round(frac*max_y))}"
        else:
            lab = f"{frac*max_y:.2f}"
        canvas.create_text(pad_l-5, yy, text=lab,
                           anchor="e", font=("Helvetica",7), fill="#999")
        if 0 < frac < 1:
            canvas.create_line(pad_l, yy, pad_l+plot_w, yy, fill="#f3f3f3")

    n_ticks = min(N, 8)
    for t in range(n_ticks):
        g = int(t*(N-1)/max(n_ticks-1,1)) if N > 1 else 0
        xx = pad_l + (g/(N-1))*plot_w if N > 1 else pad_l
        canvas.create_line(xx, pad_t+plot_h, xx, pad_t+plot_h+3, fill="#bbb")
        canvas.create_text(xx, pad_t+plot_h+5, text=str(g+1),
                           anchor="n", font=("Helvetica",7), fill="#999")

    def _x(g): return pad_l + (g/(N-1))*plot_w if N > 1 else pad_l

    # Order: highlight last so it's on top; legend ranked by final value
    ranked = sorted(norm.items(), key=lambda kv: -kv[1][-1])
    for lbl, vals in ranked:
        col = (color_map or {}).get(lbl, "#888")
        width = 3 if (highlight is not None and lbl == highlight) else 2
        dash = () if (highlight is None or lbl == highlight) else (1, 0)
        pts = []
        for g in range(N):
            pts.extend([_x(g), pad_t + plot_h - (vals[g]/max_y)*plot_h])
        if len(pts) >= 4:
            canvas.create_line(*pts, fill=col, width=width, smooth=True)

    if marker_gen is not None and 1 <= marker_gen <= N:
        mx = _x(marker_gen - 1)
        canvas.create_line(mx, pad_t, mx, pad_t+plot_h,
                           fill=marker_color, width=2, dash=(5, 3))
        canvas.create_oval(mx-4, pad_t+5, mx+4, pad_t+13,
                           fill=marker_color, outline="")
        label = marker_label or f"No more change gen {marker_gen}"
        label = _fit_text(label, max(100, plot_w//2), 8)
        anchor = "w" if mx < pad_l + plot_w*0.62 else "e"
        tx = mx + 8 if anchor == "w" else mx - 8
        canvas.create_text(tx, pad_t+9, text=label, anchor=anchor,
                           font=("Helvetica",8,"bold"), fill=marker_color)

    # Legend
    lx = W - pad_r + 8
    canvas.create_text(lx, pad_t-4, text=_fit_text("Final share", pad_r-12, 8), anchor="nw",
                       font=("Helvetica",8,"bold"), fill="#333")
    for i,(lbl, vals) in enumerate(ranked[:12]):
        col = (color_map or {}).get(lbl, "#888")
        ly = pad_t + 12 + i*15
        w = 4 if (highlight is not None and lbl == highlight) else 3
        canvas.create_line(lx, ly+5, lx+14, ly+5, fill=col, width=w)
        star = " < start" if (highlight is not None and lbl == highlight) else ""
        if show_share:
            txt = f"{lbl} {vals[-1]*100:.0f}%{star}"
        elif integer_values:
            txt = f"{lbl} {int(round(vals[-1]))}{star}"
        else:
            txt = f"{lbl} {vals[-1]:.2f}{star}"
        canvas.create_text(lx+18, ly+5, text=_fit_text(txt, pad_r-30, 8),
                           anchor="w", font=("Helvetica",8), fill="#333")

    canvas.create_text(pad_l+plot_w//2, H-10, text=x_label,
                       font=("Helvetica",8), fill="#888", anchor="center")


def draw_stop_event_chart(canvas, new_stops, cumulative_stops, title,
                          integer_values=True, marker_gen=None):
    """Small companion chart for stop events, separate from live categories."""
    canvas.delete("all")
    W = canvas.winfo_width(); H = canvas.winfo_height()
    if W < 80 or H < 80:
        return
    N = max(len(new_stops), len(cumulative_stops))
    if N < 1:
        canvas.create_text(W//2, H//2, text="No stop data", fill="#aaa",
                           font=("Helvetica",10))
        return

    pad_l = 54; pad_r = 110; pad_t = 30; pad_b = 34
    plot_w = max(40, W-pad_l-pad_r)
    plot_h = max(30, H-pad_t-pad_b)
    max_y = max(new_stops + cumulative_stops + [1])
    if not integer_values:
        max_y *= 1.08

    _chart_title(canvas, W, 14, title, font=("Helvetica",9,"bold"))
    canvas.create_line(pad_l, pad_t, pad_l, pad_t+plot_h, fill="#ccc")
    canvas.create_line(pad_l, pad_t+plot_h, pad_l+plot_w, pad_t+plot_h, fill="#ccc")
    for frac in [0, 0.5, 1.0]:
        yy = pad_t + plot_h - frac*plot_h
        lab_val = frac*max_y
        lab = str(int(round(lab_val))) if integer_values else f"{lab_val:.2f}"
        canvas.create_line(pad_l-3, yy, pad_l, yy, fill="#bbb")
        canvas.create_text(pad_l-5, yy, text=lab, anchor="e",
                           font=("Helvetica",7), fill="#888")
        if 0 < frac < 1:
            canvas.create_line(pad_l, yy, pad_l+plot_w, yy, fill="#f3f3f3")

    def _x(g):
        return pad_l + (g/(N-1))*plot_w if N > 1 else pad_l
    def _y(v):
        return pad_t + plot_h - (v/max_y)*plot_h if max_y > 0 else pad_t+plot_h

    bar_w = max(2, min(14, int(plot_w/max(N, 1)*0.55)))
    for g, val in enumerate(new_stops):
        x = _x(g)
        canvas.create_rectangle(x-bar_w//2, _y(val), x+bar_w//2, pad_t+plot_h,
                                fill="#E74C3C", outline="")

    pts = []
    for g, val in enumerate(cumulative_stops):
        pts.extend([_x(g), _y(val)])
    if len(pts) >= 4:
        canvas.create_line(*pts, fill="#8E44AD", width=2, smooth=True)

    if marker_gen is not None and 1 <= marker_gen <= N:
        mx = _x(marker_gen-1)
        canvas.create_line(mx, pad_t, mx, pad_t+plot_h,
                           fill="#111", width=1, dash=(4, 3))

    lx = W-pad_r+10
    canvas.create_rectangle(lx, pad_t+2, lx+10, pad_t+12,
                            fill="#E74C3C", outline="")
    canvas.create_text(lx+14, pad_t+7, text="new stops", anchor="w",
                       font=("Helvetica",8), fill="#333")
    canvas.create_line(lx, pad_t+24, lx+12, pad_t+24,
                       fill="#8E44AD", width=2)
    canvas.create_text(lx+14, pad_t+24, text="cumulative", anchor="w",
                       font=("Helvetica",8), fill="#333")

    n_ticks = min(N, 6)
    for t in range(n_ticks):
        g = int(t*(N-1)/max(n_ticks-1, 1)) if N > 1 else 0
        x = _x(g)
        canvas.create_line(x, pad_t+plot_h, x, pad_t+plot_h+3, fill="#aaa")
        canvas.create_text(x, pad_t+plot_h+5, text=str(g+1),
                           anchor="n", font=("Helvetica",7), fill="#888")


# ─── NEW: Survival curve (surviving probability + #AAs across generations) ───

def draw_survival_curve(canvas, surv_weight, n_aas, title,
                        start_total=1.0, n_gen=None):
    """
    Two lines vs generation:
      - surviving probability (as % of starting total)  [blue, left axis]
      - number of distinct AAs still present            [orange, right axis]
    surv_weight: list of surviving weight per generation (len = N)
    n_aas:       list of distinct-AA counts per generation (len = N)
    Marks the half-life generation (where survival first drops below 50%).
    """
    canvas.delete("all")
    W = canvas.winfo_width(); H = canvas.winfo_height()
    if W < 60 or H < 60: return
    N = len(surv_weight)
    if N < 1:
        canvas.create_text(W//2, H//2, text="No data", fill="#aaa",
                           font=("Helvetica",11)); return

    pad_l=52; pad_r=64; pad_t=34; pad_b=42
    if W - pad_l - pad_r < 120:
        pad_r = 48
    plot_w = max(30, W - pad_l - pad_r)
    plot_h = H - pad_t - pad_b

    # Survival as fraction of starting total
    start_total = start_total or 1
    surv_frac = [w / start_total for w in surv_weight]
    max_aa = max(n_aas) if n_aas else 1
    max_aa = max(max_aa, 1)

    _chart_title(canvas, W, 14, title)

    # Axes
    canvas.create_line(pad_l, pad_t, pad_l, pad_t+plot_h, fill="#ccc")
    canvas.create_line(pad_l, pad_t+plot_h, pad_l+plot_w, pad_t+plot_h, fill="#ccc")
    canvas.create_line(pad_l+plot_w, pad_t, pad_l+plot_w, pad_t+plot_h, fill="#ccc")

    # Left Y axis (survival %) — blue
    for frac in [0, 0.25, 0.5, 0.75, 1.0]:
        yy = pad_t + plot_h - frac*plot_h
        canvas.create_line(pad_l-3, yy, pad_l, yy, fill="#bbb")
        canvas.create_text(pad_l-5, yy, text=f"{int(frac*100)}%",
                           anchor="e", font=("Helvetica",7), fill="#185FA5")
        if 0 < frac < 1:
            canvas.create_line(pad_l, yy, pad_l+plot_w, yy, fill="#f0f0f0")

    # Right Y axis (#AAs) — orange
    for frac in [0, 0.5, 1.0]:
        yy = pad_t + plot_h - frac*plot_h
        val = int(round(frac*max_aa))
        canvas.create_line(pad_l+plot_w, yy, pad_l+plot_w+3, yy, fill="#bbb")
        canvas.create_text(pad_l+plot_w+5, yy, text=str(val),
                           anchor="w", font=("Helvetica",7), fill="#E8822A")

    # X ticks
    n_ticks = min(N, 8)
    for t in range(n_ticks):
        g = int(t*(N-1)/max(n_ticks-1,1)) if N > 1 else 0
        xx = pad_l + (g/(N-1))*plot_w if N > 1 else pad_l
        canvas.create_line(xx, pad_t+plot_h, xx, pad_t+plot_h+3, fill="#bbb")
        canvas.create_text(xx, pad_t+plot_h+5, text=str(g+1),
                           anchor="n", font=("Helvetica",7), fill="#999")

    def _x(g): return pad_l + (g/(N-1))*plot_w if N > 1 else pad_l

    # Survival line (blue, left axis)
    if N >= 2:
        pts = []
        for g in range(N):
            pts.extend([_x(g), pad_t + plot_h - surv_frac[g]*plot_h])
        canvas.create_line(*pts, fill="#185FA5", width=2, smooth=True)
    else:
        canvas.create_oval(_x(0)-3, pad_t+plot_h-surv_frac[0]*plot_h-3,
                           _x(0)+3, pad_t+plot_h-surv_frac[0]*plot_h+3,
                           fill="#185FA5", outline="")

    # #AA line (orange, right axis)
    if N >= 2:
        pts = []
        for g in range(N):
            yv = (n_aas[g]/max_aa) if max_aa else 0
            pts.extend([_x(g), pad_t + plot_h - yv*plot_h])
        canvas.create_line(*pts, fill="#E8822A", width=2, smooth=True, dash=(4,2))

    # Half-life marker: first generation where survival < 50%
    half_g = None
    for g in range(N):
        if surv_frac[g] < 0.5:
            half_g = g; break
    if half_g is not None:
        hx = _x(half_g)
        canvas.create_line(hx, pad_t, hx, pad_t+plot_h, fill="#C0392B", dash=(3,3))
        marker = _fit_text(f"50% by gen {half_g+1}", max(58, plot_w//4), 7)
        canvas.create_text(hx, pad_t+2,
                           text=marker,
                           anchor="n", font=("Helvetica",7,"bold"), fill="#C0392B")
    else:
        msg = f"survival never drops below 50% (ends at {surv_frac[-1]*100:.1f}%)"
        canvas.create_text(pad_l+plot_w//2, pad_t+8,
                           text=_fit_text(msg, plot_w-8, 7),
                           anchor="n", font=("Helvetica",7,"bold"), fill="#3B6D11")

    # Legend
    canvas.create_line(pad_l+6, pad_t+4, pad_l+22, pad_t+4, fill="#185FA5", width=3)
    canvas.create_text(pad_l+25, pad_t+4, text="surviving %",
                       anchor="w", font=("Helvetica",7), fill="#185FA5")
    canvas.create_line(pad_l+110, pad_t+4, pad_l+126, pad_t+4,
                       fill="#E8822A", width=3, dash=(4,2))
    canvas.create_text(pad_l+129, pad_t+4, text="# distinct AAs",
                       anchor="w", font=("Helvetica",7), fill="#E8822A")

    canvas.create_text(pad_l+plot_w//2, H-8, text="Generation",
                       font=("Helvetica",8), fill="#888", anchor="center")


# ─── NEW: Survival comparison (User vs Preset overlaid) ──────────────────────

def draw_survival_compare(canvas, surv_u, aas_u, surv_p, aas_p,
                          start_u=1.0, start_p=1.0, title="Survival — User vs Preset"):
    """
    Overlay two models' survival curves on one set of axes.
      User survival %    : solid blue        (left axis)
      Preset survival %  : solid purple      (left axis)
      User #AAs          : dashed blue       (right axis)
      Preset #AAs        : dashed purple     (right axis)
    Marks each model's half-life generation.
    """
    canvas.delete("all")
    W = canvas.winfo_width(); H = canvas.winfo_height()
    if W < 60 or H < 60: return
    N = max(len(surv_u), len(surv_p))
    if N < 1:
        canvas.create_text(W//2, H//2, text="No data", fill="#aaa",
                           font=("Helvetica",11)); return

    pad_l=52; pad_r=76; pad_t=34; pad_b=42
    if W - pad_l - pad_r < 120:
        pad_r = 54
    plot_w = max(30, W - pad_l - pad_r)
    plot_h = H - pad_t - pad_b

    su = [w/(start_u or 1) for w in surv_u]
    sp = [w/(start_p or 1) for w in surv_p]
    max_aa = max((max(aas_u) if aas_u else 1), (max(aas_p) if aas_p else 1), 1)

    _chart_title(canvas, W, 14, title)

    # Axes
    canvas.create_line(pad_l, pad_t, pad_l, pad_t+plot_h, fill="#ccc")
    canvas.create_line(pad_l, pad_t+plot_h, pad_l+plot_w, pad_t+plot_h, fill="#ccc")
    canvas.create_line(pad_l+plot_w, pad_t, pad_l+plot_w, pad_t+plot_h, fill="#ccc")

    for frac in [0, 0.25, 0.5, 0.75, 1.0]:
        yy = pad_t + plot_h - frac*plot_h
        canvas.create_line(pad_l-3, yy, pad_l, yy, fill="#bbb")
        canvas.create_text(pad_l-5, yy, text=f"{int(frac*100)}%",
                           anchor="e", font=("Helvetica",7), fill="#555")
        if 0 < frac < 1:
            canvas.create_line(pad_l, yy, pad_l+plot_w, yy, fill="#f0f0f0")
    for frac in [0, 0.5, 1.0]:
        yy = pad_t + plot_h - frac*plot_h
        canvas.create_text(pad_l+plot_w+5, yy, text=str(int(round(frac*max_aa))),
                           anchor="w", font=("Helvetica",7), fill="#E8822A")

    n_ticks = min(N, 8)
    for t in range(n_ticks):
        g = int(t*(N-1)/max(n_ticks-1,1)) if N > 1 else 0
        xx = pad_l + (g/(N-1))*plot_w if N > 1 else pad_l
        canvas.create_line(xx, pad_t+plot_h, xx, pad_t+plot_h+3, fill="#bbb")
        canvas.create_text(xx, pad_t+plot_h+5, text=str(g+1),
                           anchor="n", font=("Helvetica",7), fill="#999")

    def _x(g, n): return pad_l + (g/(n-1))*plot_w if n > 1 else pad_l

    def _line(vals, n, color, dash=None, scale=1.0):
        if len(vals) < 2: return
        pts = []
        for g in range(len(vals)):
            y = pad_t + plot_h - (vals[g]/scale)*plot_h
            pts.extend([_x(g, n), y])
        canvas.create_line(*pts, fill=color, width=2, smooth=True,
                           **({"dash": dash} if dash else {}))

    # Survival % (left axis, scale=1.0 since already fraction)
    _line(su, len(su), USER_COLOR,   scale=1.0)
    _line(sp, len(sp), PRESET_COLOR, scale=1.0)
    # #AAs (right axis, scale=max_aa)
    _line(aas_u, len(aas_u), USER_COLOR,   dash=(4,2), scale=max_aa)
    _line(aas_p, len(aas_p), PRESET_COLOR, dash=(4,2), scale=max_aa)

    # Half-life markers
    def _half(frac_list, n):
        for g, v in enumerate(frac_list):
            if v < 0.5: return g
        return None
    for frac_list, n, col, name in [(su, len(su), USER_COLOR, "User"),
                                     (sp, len(sp), PRESET_COLOR, "Preset")]:
        hg = _half(frac_list, n)
        if hg is not None:
            hx = _x(hg, n)
            canvas.create_line(hx, pad_t, hx, pad_t+plot_h, fill=col, dash=(2,3))
            canvas.create_text(hx, pad_t+2, text=_fit_text(f"{name} 50%@{hg+1}", 58, 6),
                               anchor="n", font=("Helvetica",6,"bold"), fill=col)

    # Legend
    items = [("User survival", USER_COLOR, None),
             ("Preset survival", PRESET_COLOR, None),
             ("User #AAs", USER_COLOR, (4,2)),
             ("Preset #AAs", PRESET_COLOR, (4,2))]
    for i,(lbl,col,dash) in enumerate(items):
        ly = pad_t + 4 + i*12
        canvas.create_line(pad_l+6, ly, pad_l+22, ly, fill=col, width=3,
                           **({"dash": dash} if dash else {}))
        canvas.create_text(pad_l+25, ly, text=lbl, anchor="w",
                           font=("Helvetica",7), fill=col)

    canvas.create_text(pad_l+plot_w//2, H-8, text="Generation",
                       font=("Helvetica",8), fill="#888", anchor="center")


# ─── NEW: Side-by-side comparison bar chart ──────────────────────────────────

def draw_comparison_bar_chart(canvas, counter_a, counter_b,
                               label_a="User", label_b="Preset",
                               color_a=USER_COLOR, color_b=PRESET_COLOR,
                               title="Comparison", top_n=21, normalize=False):
    """
    Draw two sets of horizontal bars side by side (interleaved) for the same
    set of labels, so the viewer can compare counter_a vs counter_b directly.
    """
    canvas.delete("all")
    W = canvas.winfo_width(); H = canvas.winfo_height()
    if W < 50 or H < 50: return

    # Union of keys
    all_keys = sorted(set(list(counter_a.keys())+list(counter_b.keys())),
                      key=lambda k: -(counter_a.get(k,0)+counter_b.get(k,0)))
    all_keys = all_keys[:top_n]
    if not all_keys:
        canvas.create_text(W//2, H//2, text="No data", fill="#aaa",
                           font=("Helvetica",11)); return

    total_a = sum(counter_a.values()) or 1
    total_b = sum(counter_b.values()) or 1

    def norm(c, tot, k): return (c.get(k,0)/tot)*100 if normalize else c.get(k,0)/tot

    max_v = max((max(norm(counter_a,total_a,k) for k in all_keys) if counter_a else 0),
                (max(norm(counter_b,total_b,k) for k in all_keys) if counter_b else 0)) or 1

    label_px = max((_text_px(k, 9, True) for k in all_keys), default=110)
    value_px = max((_text_px(f"{max_v:.4f}", 7), _text_px("100.0%", 7)), default=44)
    pad_l=int(min(230, max(110, label_px+18)))
    pad_r=int(min(120, max(54, value_px+24)))
    if W - pad_l - pad_r < 140:
        pad_l = min(pad_l, max(72, W//4))
        pad_r = min(pad_r, max(44, W//7))
    pad_t=50; pad_b=30
    n = len(all_keys)
    pair_h  = max(22, min(42, (H-pad_t-pad_b)//max(n,1)-2))
    bar_h   = max(8,  pair_h//2-2)
    gap_pair= max(2,  pair_h - 2*bar_h - 1)
    chart_w = max(20, W-pad_l-pad_r)
    chart_right = pad_l + chart_w

    badge = "  [% of total]" if normalize else "  [probability 0–1]"
    _chart_title(canvas, W, 16, title+badge)

    # Legend
    lx = W//2-110
    canvas.create_rectangle(lx, 28, lx+14, 38, fill=color_a, outline="")
    canvas.create_text(lx+17, 33, text=_fit_text(label_a, 95, 8), anchor="w",
                       font=("Helvetica",8,"bold"), fill=color_a)
    canvas.create_rectangle(lx+120, 28, lx+134, 38, fill=color_b, outline="")
    canvas.create_text(lx+137, 33, text=_fit_text(label_b, 95, 8), anchor="w",
                       font=("Helvetica",8,"bold"), fill=color_b)

    fmt = (lambda v: f"{v:.1f}%") if normalize else (lambda v: f"{v:.4f}")

    for i, key in enumerate(all_keys):
        va = norm(counter_a, total_a, key)
        vb = norm(counter_b, total_b, key)
        y_base = pad_t + i*(pair_h + gap_pair)

        # Label
        canvas.create_text(pad_l-6, y_base+pair_h//2,
                           text=_fit_text(str(key), pad_l-12, 9, True),
                           anchor="e", font=("Courier",9), fill="#333")

        # Bar A
        bw_a = max(2, int(va/max_v*chart_w)) if va > 0 else 0
        canvas.create_rectangle(pad_l, y_base, pad_l+bw_a, y_base+bar_h,
                                fill=color_a, outline="")
        if va > 0:
            _safe_value_label(canvas, pad_l+bw_a, y_base+bar_h//2, fmt(va),
                              color_a, pad_l, chart_right, bw_a,
                              font=("Helvetica",7))

        # Bar B
        y_b = y_base + bar_h + 1
        bw_b = max(2, int(vb/max_v*chart_w)) if vb > 0 else 0
        canvas.create_rectangle(pad_l, y_b, pad_l+bw_b, y_b+bar_h,
                                fill=color_b, outline="")
        if vb > 0:
            _safe_value_label(canvas, pad_l+bw_b, y_b+bar_h//2, fmt(vb),
                              color_b, pad_l, chart_right, bw_b,
                              font=("Helvetica",7))

    canvas.create_line(pad_l, pad_t, pad_l, H-pad_b, fill="#ccc", width=1)
    canvas.create_line(pad_l, H-pad_b, chart_right, H-pad_b, fill="#ccc", width=1)
    for frac in [0, 0.25, 0.5, 0.75, 1.0]:
        tx = pad_l + int(frac*chart_w)
        canvas.create_line(tx, H-pad_b, tx, H-pad_b+4, fill="#bbb")
        tick_val = frac*(100 if normalize else 1)
        tick_str = f"{tick_val:.0f}%" if normalize else f"{tick_val:.2f}"
        canvas.create_text(tx, H-pad_b+6, text=tick_str,
                           anchor="n", font=("Helvetica",7), fill="#999")


# ─────────────────────────────────────────────────────────────────────────────
# Probability input panel
# ─────────────────────────────────────────────────────────────────────────────

class ProbInputPanel(tk.Frame):
    PAIRS = [
        ("A→T  (= G↔C)", "AT", "#7A4E8A"),
        ("A→G  (= T↔C)", "AG", "#C88719"),
        ("A→C  (= T↔G)", "AC", "#B84242"),
    ]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self.vars = {}
        self._build()

    def _build(self):
        tk.Label(self, text="3 free parameters  (A→T, A→G, A→C)",
                 bg=BG, font=("Segoe UI",10,"bold"), fg=INK
                 ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,2))
        tk.Label(self, text="Must sum to 1.0   (fractions OK: 1/3, decimals, %)",
                 bg=BG, font=("Segoe UI",8), fg=MUTED
                 ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0,8))
        for ri, (label, key, col) in enumerate(self.PAIRS):
            tk.Label(self, text=label, bg=BG, fg=col,
                     font=("Consolas",11,"bold")
                     ).grid(row=ri+2, column=0, sticky="w", padx=(0,8), pady=3)
            var = tk.StringVar(value="1/3")
            self.vars[key] = var
            e = tk.Entry(self, textvariable=var, width=8,
                         font=("Consolas",12), relief="solid", bd=1,
                         bg=BG_PANEL, fg=INK, insertbackground=INK)
            e.grid(row=ri+2, column=1, padx=(0,6), pady=3)
            e.bind("<FocusOut>", lambda ev: self._validate())
            e.bind("<Return>",   lambda ev: self._validate())

        self.sum_lbl = tk.Label(self, text="Σ = ?", bg=BG,
                                font=("Segoe UI",10,"bold"), fg=MUTED)
        self.sum_lbl.grid(row=5, column=0, columnspan=3, sticky="w", pady=(6,2))

        tk.Label(self, text="Implied rates for all bases:",
                 bg=BG, font=("Segoe UI",8,"bold"), fg=INK
                 ).grid(row=6, column=0, columnspan=3, sticky="w", pady=(6,1))
        self.derived_lbl = tk.Label(self, text="", bg=BG,
                                    font=("Consolas",8), fg=MUTED, justify="left")
        self.derived_lbl.grid(row=7, column=0, columnspan=3, sticky="w")

        tk.Button(self, text="Reset to 1/3", command=self._reset,
                  relief="solid", bd=1, padx=6, pady=2,
                  font=("Segoe UI",9), bg=BG_PANEL, fg=INK
                  ).grid(row=8, column=0, columnspan=3, pady=(8,0), sticky="w")
        self.after(200, self._validate)

    def _validate(self):
        vals = {}; total = 0.0; ok = True
        for _, key, _ in self.PAIRS:
            try:
                v = parse_prob(self.vars[key].get())
                if v < 0: raise ValueError
                vals[key] = v; total += v
            except Exception: ok = False
        if not ok:
            self.sum_lbl.config(text="Σ = ERROR", fg=STOP_COLOR)
            self.derived_lbl.config(text=""); return
        diff = abs(total-1.0)
        if diff < 1e-6:
            self.sum_lbl.config(text="Σ = 1.000  ✓", fg="#3E6B34")
        else:
            self.sum_lbl.config(
                text=f"Σ = {total:.4f}  ✗  (off by {total-1:+.4f})", fg=STOP_COLOR)
        at, ag, ac = vals.get("AT",0), vals.get("AG",0), vals.get("AC",0)
        lines = [f"A→C={ac:.4f}  A→G={ag:.4f}  A→T={at:.4f}",
                 f"C→A={ac:.4f}  C→G={at:.4f}  C→T={ag:.4f}",
                 f"G→A={ag:.4f}  G→C={at:.4f}  G→T={ac:.4f}",
                 f"T→A={at:.4f}  T→C={ag:.4f}  T→G={ac:.4f}"]
        self.derived_lbl.config(text="\n".join(lines))

    def _reset(self):
        for key in self.vars: self.vars[key].set("1/3")
        self._validate()

    def get_matrix(self):
        vals = {}; total = 0.0
        for _, key, _ in self.PAIRS:
            try:
                v = parse_prob(self.vars[key].get())
                if v < 0: raise ValueError
                vals[key] = v; total += v
            except Exception as ex:
                return None, f"Invalid probability for {key}: {ex}"
        if abs(total-1.0) > 0.001:
            return None, f"A→T+A→G+A→C = {total:.4f}, must equal 1.0"
        return build_substitution_matrix(vals["AT"], vals["AG"], vals["AC"]), None


# ─────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────

def show_help(parent, key):
    texts = {
        "comparison": (
            "Comparison Mode",
            """WHAT IT SHOWS
Runs the SAME simulation twice — once with your chosen
substitution probabilities, once with the fixed preset:
  Preset: A→T = 1/6,  A→G = 2/3,  A→C = 1/6

Both runs use exactly the same number of copies and
the same number of generations (whatever you set in
the left panel), so the comparison is fair.

TABS IN COMPARISON MODE

  Final AAs comparison
    Side-by-side horizontal bars showing final amino
    acid probabilities for User (blue) vs Preset (purple).
    Each AA has two bars so you can see which final
    distribution is reached by each probability model.

  Stop codons comparison
    Same layout, for stop codon absorption probability.
    Shows TAA / TAG / TGA probability for each model.

  Categories comparison
    Grouped bars by biochemical property (Hydrophobic,
    Polar, Charged, Special).  Quickly shows which
    property classes become more or less reachable
    under the two probability models.

  Start codon map — User
    Heatmap: row=starting codon, column=final codon.
    Cell intensity = probability.  Only User model.

  Start codon map — Preset
    Same heatmap for the Preset model.

HOW TO USE
1. Set your probabilities in the left panel.
2. Set copies and generations.
3. Press ▶ Run.
4. Switch between 'Your probability' / 'Preset' /
   'Compare both' using the toggle in the top bar.
   All tabs update immediately — no re-run needed."""
        ),
    }
    title, body = texts.get(key, ("Help", "No help text yet."))
    win = tk.Toplevel(parent)
    win.title(f"Help: {title}")
    win.configure(bg=BG); win.resizable(False, False); win.grab_set()
    tk.Label(win, text=f"📊  {title}", font=("Helvetica",13,"bold"),
             bg=BG, fg=ACCENT).pack(padx=20, pady=(16,4), anchor="w")
    tk.Frame(win, bg=ACCENT, height=2).pack(fill="x", padx=20, pady=(0,10))
    txt = tk.Text(win, wrap="word", font=("Helvetica",10), bg=BG, fg="#333",
                  relief="flat", width=56, height=28, padx=12, pady=8, cursor="arrow")
    txt.insert("1.0", body.strip()); txt.config(state="disabled")
    txt.pack(padx=16, pady=(0,8), fill="both", expand=True)
    tk.Button(win, text="Close", command=win.destroy,
              relief="solid", bd=1, padx=20, pady=4,
              font=("Helvetica",10)).pack(pady=(0,16))
    win.update_idletasks()
    px,py = parent.winfo_rootx(), parent.winfo_rooty()
    pw,ph = parent.winfo_width(), parent.winfo_height()
    ww,wh = win.winfo_width(), win.winfo_height()
    win.geometry(f"+{px+(pw-ww)//2}+{py+(ph-wh)//2}")


# ─────────────────────────────────────────────────────────────────────────────
# Main Application
# ─────────────────────────────────────────────────────────────────────────────

class MutationExplorerApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Codon Category Tracking Lab")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(1120, 760)
        self.geometry("1320x900")

        # Results storage: two slots — user and preset
        self._res_user   = None   # full results tuple (sim+exp) for user probs
        self._res_preset = None   # full results tuple for preset probs
        self._params     = None
        self._fs = False

        self._build_ui()
        self.bind("<F11>",    lambda e: self._toggle_fs())
        self.bind("<Escape>", lambda e: self._exit_fs())

    # ─────────────────────────────────────────────────────────────────────
    # UI construction
    # ─────────────────────────────────────────────────────────────────────

    def _configure_ttk_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=BG_RAIL, foreground=INK,
                        padding=(16, 8),
                        font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", BG_PANEL)],
                  foreground=[("selected", ACCENT)])
        style.configure("Treeview",
                        background=BG_PANEL, fieldbackground=BG_PANEL,
                        foreground=INK, rowheight=24,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading",
                        background=BG_RAIL, foreground=INK,
                        font=("Segoe UI", 9, "bold"))
        style.map("Treeview",
                  background=[("selected", "#CFE4DD")],
                  foreground=[("selected", INK)])
        style.configure("TCombobox", padding=4, font=("Segoe UI", 9))

    def _codon_rail(self, parent):
        rail = tk.Frame(parent, bg=BG_RAIL, relief="solid", bd=1)
        rail.pack(fill="x", pady=(0, 10))
        tk.Label(rail, text="Triplet population tracking",
                 bg=BG_RAIL, fg=INK,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=8, pady=(6, 3))
        chips = tk.Frame(rail, bg=BG_RAIL)
        chips.pack(anchor="w", padx=8, pady=(0, 7))
        for base, color in [("A", "#146C72"), ("C", "#7A4E8A"),
                            ("G", "#C88719"), ("T", STOP_COLOR)]:
            tk.Label(chips, text=base, bg=color, fg="white",
                     font=("Consolas", 11, "bold"),
                     width=3, relief="flat").pack(side="left", padx=(0, 5))
        tk.Label(chips, text="exact codon copies -> category counts",
                 bg=BG_RAIL, fg=MUTED,
                 font=("Segoe UI", 8)).pack(side="left", padx=(3, 0))

    def _build_ui(self):
        self._configure_ttk_style()

        # ── Left control panel — scrollable ──
        left_outer = tk.Frame(self, bg=BG, width=340)
        left_outer.pack(side="left", fill="y", padx=(14,0), pady=14)
        left_outer.pack_propagate(False)

        # Scrollbar on the right of the left panel
        left_vsb = tk.Scrollbar(left_outer, orient="vertical")
        left_vsb.pack(side="right", fill="y")

        left_canvas = tk.Canvas(left_outer, bg=BG, highlightthickness=0,
                                yscrollcommand=left_vsb.set, width=318)
        left_canvas.pack(side="left", fill="both", expand=True)
        left_vsb.config(command=left_canvas.yview)

        # The actual inner frame that holds all controls
        left = tk.Frame(left_canvas, bg=BG)
        left_win = left_canvas.create_window((0, 0), window=left, anchor="nw")

        def _left_configure(e):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        def _left_canvas_resize(e):
            left_canvas.itemconfig(left_win, width=e.width)

        left.bind("<Configure>", _left_configure)
        left_canvas.bind("<Configure>", _left_canvas_resize)

        def _left_mw(e):
            if e.num == 4:   left_canvas.yview_scroll(-1, "units")
            elif e.num == 5: left_canvas.yview_scroll(1,  "units")
            else:            left_canvas.yview_scroll(int(-1*(e.delta/120)), "units")

        left_canvas.bind("<MouseWheel>", _left_mw)
        left_canvas.bind("<Button-4>",   _left_mw)
        left_canvas.bind("<Button-5>",   _left_mw)
        left.bind("<MouseWheel>", _left_mw)
        left.bind("<Button-4>",   _left_mw)
        left.bind("<Button-5>",   _left_mw)

        tk.Label(left, text="Category Tracking Lab",
                 font=("Segoe UI", 16, "bold"), bg=BG, fg=INK
                 ).pack(anchor="w", pady=(0, 2))
        tk.Label(left,
                 text="Follow exact codon populations as they move between amino-acid property classes.",
                 font=("Segoe UI", 8), bg=BG, fg=MUTED,
                 wraplength=292, justify="left"
                 ).pack(anchor="w", pady=(0, 8))
        self._codon_rail(left)

        # Generations
        gf = tk.LabelFrame(left, text="Generations  (1–2000)",
                           bg=BG, font=("Segoe UI",10,"bold"), fg=INK)
        gf.pack(fill="x", pady=(0,6))
        self.gen_var = tk.IntVar(value=10)
        tk.Spinbox(gf, from_=1, to=2000, textvariable=self.gen_var,
                   width=7, font=("Consolas",13), relief="solid", bd=1).pack(padx=8, pady=6)

        # Copies
        cf = tk.LabelFrame(left, text="Starting copies per codon",
                           bg=BG, font=("Segoe UI",10,"bold"), fg=INK)
        cf.pack(fill="x", pady=(0,6))
        self.copies_var = tk.IntVar(value=100)
        tk.Spinbox(cf, from_=1, to=9999, textvariable=self.copies_var,
                   width=7, font=("Consolas",13), relief="solid", bd=1).pack(padx=8, pady=(6,2))
        tk.Label(cf, text="Both User & Preset runs use the same value.",
                 bg=BG, font=("Segoe UI",8), fg=MUTED, wraplength=292,
                 justify="left").pack(padx=8, pady=(0,6), anchor="w")

        # Probability panel
        pf = tk.LabelFrame(left, text="Your substitution probabilities",
                           bg=BG, font=("Segoe UI",10,"bold"), fg=INK)
        pf.pack(fill="x", pady=(0,6))
        self.prob_panel = ProbInputPanel(pf)
        self.prob_panel.pack(padx=8, pady=6, fill="x")

        # Preset probability panel — editable, defaults to 1/6, 2/3, 1/6
        pr = tk.LabelFrame(left, text="Preset substitution probabilities",
                           bg=BG, font=("Segoe UI",10,"bold"), fg=PRESET_COLOR)
        pr.pack(fill="x", pady=(0,6))
        tk.Label(pr,
                 text="Runs alongside your probabilities for comparison.\n"
                      "Edit below — defaults to A→T=1/6, A→G=2/3, A→C=1/6.",
                 bg=BG, font=("Segoe UI",8), fg=MUTED, wraplength=292,
                 justify="left").pack(padx=8, pady=(6,2), anchor="w")
        self.preset_panel = ProbInputPanel(pr)
        # Set default values: A→T=1/6, A→G=2/3, A→C=1/6
        self.preset_panel.vars["AT"].set("1/6")
        self.preset_panel.vars["AG"].set("2/3")
        self.preset_panel.vars["AC"].set("1/6")
        self.preset_panel.pack(padx=8, pady=(0,6), fill="x")
        tk.Button(pr, text="Reset to default (1/6, 2/3, 1/6)",
                  command=self._reset_preset,
                  relief="solid", bd=1, padx=6, pady=2,
                  font=("Segoe UI",8), fg=PRESET_COLOR, bg=BG_PANEL
                  ).pack(padx=8, pady=(0,8), anchor="w")

        # Run button
        tk.Button(left, text="▶  Run category simulation",
                  command=self._run,
                  relief="solid", bd=1, padx=12, pady=8,
                  font=("Segoe UI",12,"bold"),
                  bg=ACCENT, fg="white", activebackground="#0F575C",
                  activeforeground="white").pack(fill="x", pady=(0,6))

        # Export
        self.pdf_btn = tk.Button(left, text="⬇  Export PDF",
                                 command=self._export,
                                 relief="solid", bd=1, padx=12, pady=5,
                                 font=("Segoe UI",10), state="disabled",
                                 bg=BG_PANEL, fg=INK)
        self.pdf_btn.pack(fill="x", pady=(0,6))

        self.status_lbl = tk.Label(left, text="Set parameters and press Run.",
                                   bg=BG, fg=MUTED, font=("Segoe UI",9),
                                   wraplength=292, justify="left")
        self.status_lbl.pack(anchor="w", pady=(4,0))

        info_frm = tk.LabelFrame(left, text="Info", bg=BG,
                                 font=("Segoe UI",9,"bold"), fg=INK)
        info_frm.pack(fill="x", pady=(8,0))
        tk.Label(info_frm,
                 text=("• 61 starting codons (no stops)\n"
                       "• Both runs: same copies & generations\n"
                       "• Main readout: category counts by generation\n"
                       "• Stops are shown separately\n"
                       "• F11 = full-screen"),
                 bg=BG, fg=MUTED, font=("Segoe UI",8),
                 justify="left", anchor="w").pack(padx=8, pady=5, anchor="w")

        # ── Right: mode toggle bar + notebook ──
        right = tk.Frame(self, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=14, pady=14)

        # Propagate left-panel mousewheel to all children added later
        def _bind_left_scroll(widget):
            widget.bind("<MouseWheel>", _left_mw)
            widget.bind("<Button-4>",   _left_mw)
            widget.bind("<Button-5>",   _left_mw)
            for child in widget.winfo_children():
                _bind_left_scroll(child)

        # Re-bind after UI is idle (all children exist)
        self.after(300, lambda: _bind_left_scroll(left))

        # Mode toggle bar
        mode_bar = tk.Frame(right, bg=BG_RAIL, relief="solid", bd=1)
        mode_bar.pack(fill="x", pady=(0,6))
        tk.Label(mode_bar, text="View:",
                 bg=BG_RAIL, font=("Segoe UI",10,"bold"), fg=INK
                 ).pack(side="left", padx=(10,6), pady=6)

        self._mode_var = tk.StringVar(value="user")
        modes = [
            ("Your probability", "user",    USER_COLOR),
            ("Preset",           "preset",  PRESET_COLOR),
            ("Compare both",     "compare", "#3E6B34"),
        ]
        for label, val, col in modes:
            tk.Radiobutton(mode_bar, text=label, variable=self._mode_var,
                           value=val, bg=BG_RAIL, fg=col,
                           selectcolor="#D7E6DF",
                           font=("Segoe UI",10,"bold"),
                           command=self._on_mode_change
                           ).pack(side="left", padx=4)

        tk.Button(mode_bar, text=" ? ", command=lambda: show_help(self, "comparison"),
                  relief="solid", bd=1, padx=4, pady=0,
                  font=("Segoe UI",9,"bold"),
                  bg=BG_PANEL, fg=ACCENT, cursor="hand2"
                  ).pack(side="right", padx=8, pady=4)

        # Keep all original tab frames available internally because the copied
        # builder methods reuse them, but only expose the category-focused tabs.
        self._ALL_TAB_SINGLE = [
            ("enc_aa",    "Encountered AAs"),
            ("enc_codon", "Encountered Codons"),
            ("fin_aa",    "Final AAs"),
            ("fin_codon", "Final Codons"),
            ("categories","Categories"),
            ("codon_map", "Start Codon Map"),
            ("start_end", "Start → End"),
            ("sampled",   "Sampled Results"),
            ("stops",     "Stop Codons ⚠"),
            ("codon_stop","Per-Codon Stops"),
            ("per_gen",   "Per Generation"),
            ("stacked",   "Final by Start AA"),
            ("table",     "Summary Table"),
            ("tracking",  "Category Tracking"),
        ]
        self._ALL_TAB_COMPARE = [
            ("compare_fin",      "⚖ Final AAs"),
            ("compare_stops",    "⚖ Stop Codons"),
            ("compare_cats",     "⚖ Categories"),
            ("compare_deg",      "⚖ Codon Degeneracy"),
            ("compare_codon_map","⚖ Start → End Map"),
            ("compare_pergen",   "⚖ Per Generation"),
            ("compare_summary",  "⚖ Summary Table"),
            ("compare_tracking", "⚖ Category Tracking"),
        ]
        self._TAB_SINGLE = [
            ("tracking", "Category Tracking"),
        ]
        self._TAB_COMPARE = [
            ("compare_tracking", "⚖ Category Tracking"),
        ]
        self._right_frame = right

        # Notebook
        self.nb = ttk.Notebook(right)
        self.nb.pack(fill="both", expand=True)

        # Pre-create all tab frames (not yet added to notebook)
        self._tabs = {}
        for key, label in self._ALL_TAB_SINGLE + self._ALL_TAB_COMPARE:
            self._tabs[key] = tk.Frame(self.nb, bg=BG_PANEL)

        self._apply_tab_set("user")   # adds only single-mode tabs
        self._show_placeholder_all()

    def _show_placeholder_all(self):
        for f in self._tabs.values():
            for w in f.winfo_children(): w.destroy()
            tk.Label(f, text="Run a category simulation to see results.",
                     fg=MUTED, bg=BG_PANEL, font=("Segoe UI",11)
                     ).place(relx=0.5, rely=0.5, anchor="center")

    def _apply_tab_set(self, mode):
        """Remove all tabs from the notebook, then add only the ones for this mode."""
        # Remove every currently-attached tab
        for tab_id in self.nb.tabs():
            self.nb.forget(tab_id)

        if mode == "compare":
            tab_list = self._TAB_COMPARE
        else:
            tab_list = self._TAB_SINGLE

        for key, label in tab_list:
            self.nb.add(self._tabs[key], text=label)

    def _toggle_fs(self):
        self._fs = not self._fs
        self.attributes("-fullscreen", self._fs)

    def _exit_fs(self):
        self._fs = False
        self.attributes("-fullscreen", False)

    def _reset_preset(self):
        """Reset preset panel to default values (A→T=1/6, A→G=2/3, A→C=1/6)."""
        self.preset_panel.vars["AT"].set("1/6")
        self.preset_panel.vars["AG"].set("2/3")
        self.preset_panel.vars["AC"].set("1/6")
        self.preset_panel._validate()

    # ─────────────────────────────────────────────────────────────────────
    # Mode switch
    # ─────────────────────────────────────────────────────────────────────

    def _on_mode_change(self):
        mode = self._mode_var.get()
        self._apply_tab_set(mode)
        if self._res_user is None: return
        self._repopulate()

    def _repopulate(self):
        mode = self._mode_var.get()
        p_at2 = self._params.get("p_at2", PRESET_AT)
        p_ag2 = self._params.get("p_ag2", PRESET_AG)
        p_ac2 = self._params.get("p_ac2", PRESET_AC)
        preset_label = f"Preset (T={p_at2:.3f} G={p_ag2:.3f} C={p_ac2:.3f})"
        if mode == "user":
            self._populate_single(self._res_user[0], self._res_user[1],
                                  self._params["n_generations"],
                                  color_hint=USER_COLOR, label="User")
        elif mode == "preset":
            self._populate_single(self._res_preset[0], self._res_preset[1],
                                  self._params["n_generations"],
                                  color_hint=PRESET_COLOR, label=preset_label)
        else:
            self._populate_single(self._res_user[0], self._res_user[1],
                                  self._params["n_generations"],
                                  color_hint=USER_COLOR, label="User")
            self._populate_compare()

    # ─────────────────────────────────────────────────────────────────────
    # Run
    # ─────────────────────────────────────────────────────────────────────

    def _run(self):
        try:
            n_gen = int(self.gen_var.get())
            if not 1 <= n_gen <= 2000: raise ValueError
        except Exception:
            messagebox.showerror("Input error", "Generations must be 1–2000."); return

        matrix_user, err = self.prob_panel.get_matrix()
        if err:
            messagebox.showerror("Probability error", err); return

        try:
            copies = int(self.copies_var.get())
            if copies < 1: raise ValueError
        except Exception:
            messagebox.showerror("Input error", "Copies must be ≥ 1."); return

        matrix_preset, err2 = self.preset_panel.get_matrix()
        if err2:
            messagebox.showerror("Preset probability error", err2); return
        start_weights = {c: float(copies) for c in VALID_CODONS}

        # Read preset values for display/params
        p_at2 = parse_prob(self.preset_panel.vars["AT"].get())
        p_ag2 = parse_prob(self.preset_panel.vars["AG"].get())
        p_ac2 = parse_prob(self.preset_panel.vars["AC"].get())

        self.status_lbl.config(
            text=f"Running {n_gen} gen(s) for both probability sets…", fg=ACCENT)
        self.update()

        at = parse_prob(self.prob_panel.vars["AT"].get())
        ag = parse_prob(self.prob_panel.vars["AG"].get())
        ac = parse_prob(self.prob_panel.vars["AC"].get())

        params = {"n_generations": n_gen,
                  "sub_probs_user":   matrix_user,
                  "sub_probs_preset": matrix_preset,
                  "p_at": at, "p_ag": ag, "p_ac": ac,
                  "p_at2": p_at2, "p_ag2": p_ag2, "p_ac2": p_ac2,
                  "start_copies": copies}

        def worker():
            # Run the four independent passes in parallel threads.
            # (NumPy-free pure-Python loops release the GIL poorly, but the
            #  experiment sampling and dict work still overlap usefully; on a
            #  free-threaded build this scales near-linearly.)
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=4) as ex:
                fu_sim = ex.submit(run_simulation, n_gen, matrix_user,   start_weights)
                fu_exp = ex.submit(run_experiment, n_gen, matrix_user,   start_weights)
                fp_sim = ex.submit(run_simulation, n_gen, matrix_preset, start_weights)
                fp_exp = ex.submit(run_experiment, n_gen, matrix_preset, start_weights)
                sim_user   = fu_sim.result()
                exp_user   = fu_exp.result()
                sim_preset = fp_sim.result()
                exp_preset = fp_exp.result()
            self.after(0, lambda: self._on_done(
                (sim_user, exp_user), (sim_preset, exp_preset), params))

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self, res_user, res_preset, params):
        self._res_user   = res_user
        self._res_preset = res_preset
        self._params     = params

        stats_u = res_user[0][8]   # (..., stats[8], stop_data[9], track_data[10])
        n_stop_u = sum(1 for r in res_user[1][0] if r["hit_stop"])
        n_total  = len(res_user[1][0])

        p_at2 = params.get("p_at2", PRESET_AT)
        p_ag2 = params.get("p_ag2", PRESET_AG)
        p_ac2 = params.get("p_ac2", PRESET_AC)
        self.status_lbl.config(
            text=(f"Done!  User: {stats_u['unique_aas_seen']} AAs, "
                  f"{n_stop_u}/{n_total} stops.  "
                  f"Preset (T={p_at2:.3f} G={p_ag2:.3f} C={p_ac2:.3f}) also complete."),
            fg="#3B6D11")
        self.pdf_btn.config(state="normal")
        self._repopulate()

    # ─────────────────────────────────────────────────────────────────────
    # Tab helpers
    # ─────────────────────────────────────────────────────────────────────

    def _clear(self, key):
        for w in self._tabs[key].winfo_children(): w.destroy()

    def _scrollable_tab(self, key):
        """Returns inner scrollable frame for the given tab key."""
        tab = self._tabs[key]
        outer, inner = make_scrollable(tab, bg=BG_PANEL)
        outer.pack(fill="both", expand=True)
        return inner

    def _canvas(self, parent, height=440):
        return self._scroll_chart(parent, lambda _cv: None, height=height,
                                  min_w=900, min_h=height)

    def _live_canvas(self, parent, render_fn, height=440, delay=80):
        """
        Create a canvas that redraws on resize and once after layout settles.
        `render_fn(canvas)` does the drawing. Returns the canvas.
        Collapses the repeated 'make canvas + bind Configure + after()' pattern.
        """
        return self._scroll_chart(parent, render_fn, height=height,
                                  min_w=900, min_h=height, delay=delay)

    def _scroll_chart(self, parent, render_fn, height=440,
                      min_w=900, min_h=None, delay=80):
        """
        Create a chart canvas wrapped in BOTH horizontal and vertical scrollbars.

        The chart is drawn larger than the viewport, so every chart has real
        horizontal and vertical scroll range even when the window is resized.
        `render_fn(canvas)` does the drawing and may read canvas.winfo_width()
        / winfo_height(), which here reflect the enlarged drawing area, not
        just the viewport.

        Returns the inner drawing canvas.
        """
        if min_h is None:
            min_h = height
        holder = tk.Frame(parent, bg=BG_PANEL)
        holder.pack(fill="both", expand=True, padx=4, pady=4)

        hsb = tk.Scrollbar(holder, orient="horizontal")
        hsb.pack(side="bottom", fill="x")
        vsb = tk.Scrollbar(holder, orient="vertical")
        vsb.pack(side="right", fill="y")

        # Outer viewport canvas that actually scrolls
        view = tk.Canvas(holder, bg=BG_PANEL, highlightthickness=0,
                         height=height, xscrollcommand=hsb.set,
                         yscrollcommand=vsb.set)
        view.pack(side="left", fill="both", expand=True)
        hsb.config(command=view.xview)
        vsb.config(command=view.yview)

        # Inner drawing canvas (the chart) placed inside the viewport
        draw = tk.Canvas(view, bg=BG_PANEL, highlightthickness=0)
        win_id = view.create_window((0, 0), window=draw, anchor="nw")

        state = {"w": 0, "h": 0}

        def _do_render():
            vw = max(view.winfo_width(), 10)
            vh = max(view.winfo_height(), 10)
            # Keep a real scroll range in both directions for every chart.
            # Without this, charts whose min size fits the visible viewport
            # show scrollbars that cannot actually move.
            dw = max(vw + 160, min_w)
            dh = max(vh + 120, min_h)
            if (dw, dh) != (state["w"], state["h"]):
                draw.config(width=dw, height=dh)
                view.itemconfig(win_id, width=dw, height=dh)
                view.config(scrollregion=(0, 0, dw, dh))
                state["w"], state["h"] = dw, dh
            render_fn(draw)

        def _on_configure(ev=None):
            _do_render()

        view.bind("<Configure>", _on_configure)

        # Mouse-wheel: vertical normally, horizontal with Shift
        def _mw(e):
            if e.num == 4:   view.yview_scroll(-1, "units")
            elif e.num == 5: view.yview_scroll(1,  "units")
            else:            view.yview_scroll(int(-1*(e.delta/120)), "units")
        def _mw_h(e):
            if e.num == 6:   view.xview_scroll(-1, "units")
            elif e.num == 7: view.xview_scroll(1,  "units")
            else:            view.xview_scroll(int(-1*(e.delta/120)), "units")
        for w in (view, draw):
            w.bind("<MouseWheel>", _mw)            # Windows / macOS vertical
            w.bind("<Shift-MouseWheel>", _mw_h)    # Windows / macOS horizontal
            # X11 (Linux) uses button events for the wheel; these sequences are
            # invalid on Windows tkinter and raise TclError, so bind defensively.
            for seq, fn in (("<Button-4>", _mw), ("<Button-5>", _mw),
                            ("<Button-6>", _mw_h), ("<Button-7>", _mw_h)):
                try:
                    w.bind(seq, fn)
                except tk.TclError:
                    pass

        self.after(delay, _do_render)
        return draw

    def _make_norm_toggle(self, parent, on_change):
        bar = tk.Frame(parent, bg="#F5F5F0", relief="solid", bd=1)
        bar.pack(fill="x", padx=6, pady=(2,2))
        nv = tk.BooleanVar(value=False)
        tk.Label(bar, text="Display:", bg="#F5F5F0",
                 font=("Helvetica",8,"bold")).pack(side="left", padx=(8,4))
        tk.Radiobutton(bar, text="Probability (0–1)", variable=nv, value=False,
                       bg="#F5F5F0", font=("Helvetica",8),
                       command=on_change).pack(side="left")
        tk.Radiobutton(bar, text="Percentage (%)", variable=nv, value=True,
                       bg="#F5F5F0", font=("Helvetica",8),
                       command=on_change).pack(side="left", padx=(0,8))
        return nv

    def _make_filter_toolbar(self, parent, on_change, is_codon_chart=False):
        bar = tk.Frame(parent, bg="#F0F4FA", relief="solid", bd=1)
        bar.pack(fill="x", padx=6, pady=(2,4))
        norm_var = tk.BooleanVar(value=False)
        tk.Label(bar, text="Display:", bg="#F0F4FA",
                 font=("Helvetica",9,"bold")).pack(side="left", padx=(8,4))
        tk.Radiobutton(bar, text="Probability (0–1)", variable=norm_var, value=False,
                       bg="#F0F4FA", font=("Helvetica",9),
                       command=on_change).pack(side="left")
        tk.Radiobutton(bar, text="Percentage (%)", variable=norm_var, value=True,
                       bg="#F0F4FA", font=("Helvetica",9),
                       command=on_change).pack(side="left", padx=(0,16))
        tk.Label(bar, text="# codons:", bg="#F0F4FA",
                 font=("Helvetica",9,"bold")).pack(side="left", padx=(0,4))
        deg_var = tk.StringVar(value="all")
        for lbl,val,bg in [("All","all",BG_PANEL),("1","1",CODON_COUNT_BG[1]),
                            ("2","2",CODON_COUNT_BG[2]),("3","3",CODON_COUNT_BG[3]),
                            ("4","4",CODON_COUNT_BG[4]),("6","6",CODON_COUNT_BG[6])]:
            tk.Radiobutton(bar, text=lbl, variable=deg_var, value=val, bg=bg,
                           font=("Helvetica",9), command=on_change
                           ).pack(side="left", padx=1)
        hint = tk.Label(bar, text="", bg="#F0F4FA", font=("Helvetica",8), fg="#555")
        hint.pack(side="left", padx=(8,4))
        def _upd(*_):
            v = deg_var.get()
            if v=="all": hint.config(text="")
            else: hint.config(text=f"({', '.join(CODON_COUNT_GROUPS.get(int(v),[]))})")
        deg_var.trace_add("write", _upd)
        return norm_var, deg_var

    def _get_filter_set(self, deg_var):
        v = deg_var.get()
        if v == "all": return None
        return set(CODON_COUNT_GROUPS.get(int(v), []))

    def _header(self, parent, text, sub="", help_key=None):
        row = tk.Frame(parent, bg=BG_PANEL)
        row.pack(fill="x", padx=10, pady=(8,2))
        tk.Frame(row, bg=ACCENT, width=4, height=18).pack(side="left", padx=(0,7))
        tk.Label(row, text=text, font=("Segoe UI",11,"bold"),
                 bg=BG_PANEL, fg=INK).pack(side="left")
        if help_key:
            tk.Button(row, text=" ? ", command=lambda k=help_key: show_help(self, k),
                      relief="solid", bd=1, padx=4, pady=0,
                      font=("Segoe UI",9,"bold"), bg=BG_SOFT, fg=ACCENT,
                      cursor="hand2").pack(side="left", padx=(8,0))
        if sub:
            tk.Label(parent, text=sub, font=("Segoe UI",8),
                     bg=BG_PANEL, fg=MUTED).pack(anchor="w", padx=21)

    def _legend(self, parent, text, bg=BG_SOFT, fg=INK):
        """One-line explanation banner."""
        tk.Label(parent, text="ℹ  " + text, bg=bg, fg=fg,
                 font=("Segoe UI", 8), anchor="w",
                 relief="solid", bd=1, padx=8, pady=4,
                 wraplength=980, justify="left"
                 ).pack(fill="x", padx=8, pady=(0, 5))

    def _popout_window(self, title, build_fn, w=900, h=680):
        """Open a detached scrollable pop-out window."""
        win = tk.Toplevel(self)
        win.title(f"Pop-out: {title}")
        win.geometry(f"{w}x{h}"); win.configure(bg=BG_PANEL); win.resizable(True, True)
        tk.Frame(win, bg=ACCENT, height=2).pack(fill="x")
        outer, inner = make_scrollable(win, bg=BG_PANEL)
        outer.pack(fill="both", expand=True)
        build_fn(inner)

    def _popout_btn(self, parent, title, build_fn, w=900, h=680):
        tk.Button(parent, text="⧆  Pop out",
                  command=lambda: self._popout_window(title, build_fn, w, h),
                  relief="solid", bd=1, padx=6, pady=2,
                  font=("Segoe UI", 8), bg=BG_SOFT, fg=ACCENT,
                  cursor="hand2").pack(anchor="e", padx=8, pady=(0, 2))

    def _sort_table(self, tv, col, reverse):
        data = [(tv.set(k,col),k) for k in tv.get_children("")]
        try:    data.sort(key=lambda t: float(t[0].strip('%')), reverse=reverse)
        except: data.sort(reverse=reverse)
        for i,(_,k) in enumerate(data): tv.move(k,"",i)
        tv.heading(col, command=lambda c=col: self._sort_table(tv,c,not reverse))

    # ─────────────────────────────────────────────────────────────────────
    # Populate: single-mode tabs
    # ─────────────────────────────────────────────────────────────────────

    def _populate_single(self, results, experiment, n_gen,
                         color_hint=USER_COLOR, label="User"):
        (enc_codon, enc_aa, enc_codon_cnt, enc_aa_cnt,
         fin_codon, fin_aa, per_gen_aa, start_to_fin, stats, stop_data,
         track_data) = results
        records, samp_fin_codon, samp_fin_aa, samp_start_to_fin = experiment

        mode_badge = f"  [{label}]"

        # ── 1. Encountered AAs ────────────────────────────────────────────
        self._clear("enc_aa")
        f = self._scrollable_tab("enc_aa")
        self._header(f, f"Encountered amino acids{mode_badge}",
                     "Accumulated probability across all starts & generations.")
        self._legend(f, "Each bar = one AA. Length = total probability weight summed "
                     "across ALL starting codons and ALL generations. n = visit count.")
        def _build_enc_aa_po(frm):
            self._scroll_chart(frm, lambda cv: draw_bar_chart(cv, enc_aa,
                f"Encountered AAs{mode_badge}", color_map=AA_COLOR_MAP, top_n=21,
                count_counter=enc_aa_cnt), height=600, min_w=900, min_h=680)
        self._popout_btn(f, "Encountered AAs", _build_enc_aa_po)
        _n, _d = self._make_filter_toolbar(f, lambda: _rdr_enc_aa())
        def _rdr_enc_aa_cv(c):
            draw_bar_chart(c, enc_aa, f"Encountered AAs{mode_badge}",
                color_map=AA_COLOR_MAP, top_n=21,
                count_counter=enc_aa_cnt,
                normalize=_n.get(), filter_aa_set=self._get_filter_set(_d))
        _c_enc_aa = self._scroll_chart(f, _rdr_enc_aa_cv, height=500,
                                       min_w=720, min_h=560)
        def _rdr_enc_aa(ev=None): _rdr_enc_aa_cv(_c_enc_aa)

        # ── 2. Encountered Codons ─────────────────────────────────────────
        self._clear("enc_codon")
        f2 = self._scrollable_tab("enc_codon")
        self._header(f2, f"Encountered codons{mode_badge}")
        self._legend(f2, "Each bar = one codon, coloured by its amino acid. "
                     "Length = probability summed over all starts and all generations.")
        def _build_ec_po(frm):
            self._scroll_chart(frm, lambda cv: draw_codon_bar_chart(cv, enc_codon,
                f"Encountered codons{mode_badge}", top_n=61, count_counter=enc_codon_cnt),
                height=900, min_w=900, min_h=1100)
        self._popout_btn(f2, "Encountered Codons", _build_ec_po, h=750)
        _n2, _d2 = self._make_filter_toolbar(f2, lambda: _rdr_enc_codon(), is_codon_chart=True)
        def _rdr_enc_codon_cv(c2):
            draw_codon_bar_chart(c2, enc_codon, f"Encountered codons{mode_badge}",
                top_n=61, count_counter=enc_codon_cnt,
                normalize=_n2.get(), filter_aa_set=self._get_filter_set(_d2))
        _c_enc_cod = self._scroll_chart(f2, _rdr_enc_codon_cv, height=560,
                                        min_w=720, min_h=1000)
        def _rdr_enc_codon(ev=None): _rdr_enc_codon_cv(_c_enc_cod)

        # ── 3. Final AAs ──────────────────────────────────────────────────
        self._clear("fin_aa")
        f3 = self._scrollable_tab("fin_aa")
        self._header(f3, f"Final amino acids — generation {n_gen}{mode_badge}",
                     "Paths that hit a stop codon are excluded.")
        self._legend(f3, f"Snapshot at generation {n_gen}. "
                     "Bar = probability of the population landing on this AA at the final step. "
                     "Stop-absorbed probability is excluded.")
        def _build_fa_po(frm):
            self._scroll_chart(frm, lambda cv: draw_bar_chart(cv, fin_aa,
                f"Final AAs (gen {n_gen}){mode_badge}", color_map=AA_COLOR_MAP, top_n=21),
                height=560, min_w=900, min_h=680)
        self._popout_btn(f3, f"Final AAs gen {n_gen}", _build_fa_po)
        _n3, _d3 = self._make_filter_toolbar(f3, lambda: _rdr_fin_aa())
        def _rdr_fin_aa_cv(c3):
            draw_bar_chart(c3, fin_aa, f"Final AAs (gen {n_gen}){mode_badge}",
                color_map=AA_COLOR_MAP, top_n=21,
                normalize=_n3.get(), filter_aa_set=self._get_filter_set(_d3))
        _c_fin_aa = self._scroll_chart(f3, _rdr_fin_aa_cv, height=500,
                                       min_w=720, min_h=560)
        def _rdr_fin_aa(ev=None): _rdr_fin_aa_cv(_c_fin_aa)

        # ── 4. Final Codons ───────────────────────────────────────────────
        self._clear("fin_codon")
        f4 = self._scrollable_tab("fin_codon")
        self._header(f4, f"Final codons — generation {n_gen}{mode_badge}")
        self._legend(f4, f"Snapshot at generation {n_gen}. "
                     "Which specific codons does the population land on? "
                     "Coloured by amino acid. Stop-absorbed probability excluded.")
        def _build_fc_po(frm):
            self._scroll_chart(frm, lambda cv: draw_codon_bar_chart(cv, fin_codon,
                f"Final codons (gen {n_gen}){mode_badge}", top_n=61),
                height=900, min_w=900, min_h=1100)
        self._popout_btn(f4, f"Final Codons gen {n_gen}", _build_fc_po, h=750)
        _n4, _d4 = self._make_filter_toolbar(f4, lambda: _rdr_fin_codon(), is_codon_chart=True)
        def _rdr_fin_codon_cv(c4):
            draw_codon_bar_chart(c4, fin_codon, f"Final codons (gen {n_gen}){mode_badge}",
                top_n=61,
                normalize=_n4.get(), filter_aa_set=self._get_filter_set(_d4))
        _c_fin_cod = self._scroll_chart(f4, _rdr_fin_codon_cv, height=560,
                                        min_w=720, min_h=1000)
        def _rdr_fin_codon(ev=None): _rdr_fin_codon_cv(_c_fin_cod)

        # ── 5. Categories ─────────────────────────────────────────────────
        self._clear("categories")
        raw5 = self._tabs["categories"]
        outer5, f5 = make_scrollable(raw5, bg=BG_PANEL)
        outer5.pack(fill="both", expand=True)
        self._header(f5, f"Category analysis{mode_badge}")
        self._legend(f5, "Groups AAs by biochemical property or codon degeneracy. "
                     "Left chart = encountered (all gens). Right = final snapshot. "
                     "Use filters to drill down.", bg="#E8EEF8")
        self._build_categories_tab(f5, enc_aa, fin_aa, enc_codon, fin_codon, n_gen)

        # ── 6. Start Codon Map (NEW) ──────────────────────────────────────
        self._clear("codon_map")
        raw6 = self._tabs["codon_map"]
        outer6, f6 = make_scrollable(raw6, bg=BG_PANEL)
        outer6.pack(fill="both", expand=True)
        self._legend(f6, "Select a start codon to see its final AA bar chart and ranked table "
                     "of all final codons it reaches.", bg="#E8EEF8")
        self._build_codon_map_tab(f6, start_to_fin, n_gen, label=label,
                                   color_hint=color_hint)

        # ── 7. Start → End ────────────────────────────────────────────────
        self._clear("start_end")
        f7 = self._tabs["start_end"]
        self._header(f7, f"Start → End mapping{mode_badge}",
                     "Select a starting codon from the list.")
        self._legend(f7, "Left: theoretical final AA distribution (exact probability). "
                     "Right: actual sampled counts from random walks. "
                     "Table: each individual copy's outcome (green=survived, red=hit stop).")
        recs_ref = self._build_start_end_tab(f7, start_to_fin, samp_start_to_fin)
        recs_ref.extend(records)

        # ── 8. Sampled ────────────────────────────────────────────────────
        self._clear("sampled")
        raw8 = self._tabs["sampled"]
        outer8, f8 = make_scrollable(raw8, bg=BG_PANEL)
        outer8.pack(fill="both", expand=True)
        self._header(f8, f"Sampled results{mode_badge}")
        self._legend(f8, "Actual random walks — each copy picked one random mutation per generation. "
                     "Green rows survived to gen N; red rows hit a stop codon early. "
                     "Charts show the empirical (not theoretical) distribution.")
        self._build_sampled_tab(f8, records, samp_fin_codon, samp_fin_aa,
                                samp_start_to_fin, n_gen)

        # ── 9. Stop codons ────────────────────────────────────────────────
        self._clear("stops")
        raw9 = self._tabs["stops"]
        outer9, f9 = make_scrollable(raw9, bg=BG_PANEL)
        outer9.pack(fill="both", expand=True)
        self._header(f9, f"Stop codon analysis{mode_badge}")
        self._legend(f9, "Tracks every mutation that produced a stop codon (TAA, TAG, TGA). "
                     "Shows which starting AAs, which codons, and which stop codon were hit. "
                     "Stop probability = weight removed from the live pool.", bg="#FDEDEC")
        self._build_stops_tab(f9, stop_data, stats, n_gen, per_gen_aa)

        # ── 9b. Per-codon stop analysis ───────────────────────────────────
        self._clear("codon_stop")
        raw9b = self._tabs["codon_stop"]
        outer9b, f9b = make_scrollable(raw9b, bg=BG_PANEL)
        outer9b.pack(fill="both", expand=True)
        self._header(f9b, f"Per-codon stop analysis{mode_badge}")
        self._legend(f9b,
            "Select any starting codon to see: total stop probability from that codon, "
            "which of the 3 stop codons (TAA/TAG/TGA) it hits most, "
            "and the exact mutation paths that produced stops.",
            bg="#FDEDEC")
        self._build_per_codon_stop_tab(f9b, stop_data, n_gen)

        # ── 10. Per generation ────────────────────────────────────────────
        self._clear("per_gen")
        raw10 = self._tabs["per_gen"]
        outer10, f10 = make_scrollable(raw10, bg=BG_PANEL)
        outer10.pack(fill="both", expand=True)
        self._header(f10, f"Per-generation AA distribution{mode_badge}")
        self._legend(f10, "Snapshot per generation: how much probability arrived at each AA "
                     "at this exact generation. Filter by # codons, and see the category "
                     "(property) breakdown below. Use ← → arrow keys or the spinner to step through.")
        self.gen_sel = self._build_per_gen_view(f10, per_gen_aa, n_gen, mode_badge)

        # ── 11. Stacked ───────────────────────────────────────────────────
        self._clear("stacked")
        raw11 = self._tabs["stacked"]
        outer11, f11 = make_scrollable(raw11, bg=BG_PANEL)
        outer11.pack(fill="both", expand=True)
        self._header(f11, f"Final AA by starting AA group{mode_badge}")
        self._legend(f11, "Stacked bars: each bar = one starting amino acid. "
                     "Coloured segments = final amino acids reached. "
                     "Shorter bar = more probability lost to stop codons.")
        saa_data = collections.defaultdict(lambda: collections.Counter())
        for sc, fd in start_to_fin.items():
            saa = CODON_TABLE.get(sc,"?")
            for fc, w in fd.items(): saa_data[saa][CODON_TABLE.get(fc,"?")] += w
        def _rdr_stack_cv(c11):
            draw_stacked_bar_chart(c11, dict(saa_data),
                f"Final AA by start AA{mode_badge}", normalize=_nv_stk.get())
        _nv_stk = self._make_norm_toggle(f11, lambda: _rdr_stack())
        _c_stk = self._scroll_chart(f11, _rdr_stack_cv, height=460,
                                    min_w=820, min_h=480)
        def _rdr_stack(ev=None): _rdr_stack_cv(_c_stk)

        # ── 12. Summary table ─────────────────────────────────────────────
        self._clear("table")
        raw12 = self._tabs["table"]
        outer12, f12 = make_scrollable(raw12, bg=BG_PANEL)
        outer12.pack(fill="both", expand=True)
        self._legend(f12, "All AAs ranked by encountered probability. "
                     "Compare Enc. vs Final: high enc + low final = transient; "
                     "low enc + high final = attractor. Click any column header to sort.", bg="#E8EEF8")
        self._build_summary_table(f12, enc_aa, enc_aa_cnt, fin_aa, stats, n_gen)

        # ── 13. Category Tracking ─────────────────────────────────────────
        self._clear("tracking")
        raw13 = self._tabs["tracking"]
        outer13, f13 = make_scrollable(raw13, bg=BG_PANEL)
        outer13.pack(fill="both", expand=True)
        self._header(f13, f"Category & amino-acid tracking{mode_badge}")
        self._build_tracking_view(f13, track_data, n_gen, mode_badge, records, stop_data)

    # ─────────────────────────────────────────────────────────────────────
    # Reusable per-generation view  (used by single-mode and compare)
    # ─────────────────────────────────────────────────────────────────────

    def _build_per_gen_view(self, parent, per_gen_aa, n_gen, mode_badge=""):
        """
        Builds a complete per-generation explorer into `parent`:
          - generation spinner + ← → navigation
          - #codon degeneracy filter (All / 1 / 2 / 3 / 4 / 6)
          - normalise toggle
          - top chart: AA distribution at the selected generation
          - bottom chart: category (property) analysis at the selected generation
        `per_gen_aa` is a list of Counters (one per generation).
        Returns the IntVar holding the selected generation.
        """
        # Control row: generation spinner
        ctrl = tk.Frame(parent, bg=BG_PANEL)
        ctrl.pack(anchor="w", padx=8, pady=(2,4))
        tk.Label(ctrl, text="Generation: ", bg=BG_PANEL,
                 font=("Helvetica",9)).pack(side="left")
        gen_sel = tk.IntVar(value=1)
        spin = tk.Spinbox(ctrl, from_=1, to=n_gen, textvariable=gen_sel,
                          width=6, font=("Courier",11))
        spin.pack(side="left")
        tk.Label(ctrl, text="  (use ← → arrow keys to step)", bg=BG_PANEL,
                 font=("Helvetica",8), fg="#888").pack(side="left")

        # Filter toolbar: normalise + #codon degeneracy
        norm_var, deg_var = self._make_filter_toolbar(parent, lambda: _render())

        # AA distribution chart
        tk.Label(parent, text="Amino acid distribution at this generation:",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg="#333"
                 ).pack(anchor="w", padx=8, pady=(4,1))
        c_aa = self._scroll_chart(parent, lambda cv: _render(), height=440,
                                  min_w=720, min_h=460)

        # Category analysis chart
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(4,4))
        tk.Label(parent, text="Category analysis at this generation "
                 "(grouped by biochemical property):",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,1))
        self._legend(parent, "Hydrophobic / Polar / Charged / Special groups. "
                     "Bold bar = group total; indented bars = individual AAs in that group.",
                     bg="#E8EEF8")
        c_cat = self._scroll_chart(parent, lambda cv: _render(), height=420,
                                   min_w=720, min_h=520)

        # Convergence line chart (whole-run trend, not generation-specific)
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(4,4))
        tk.Label(parent, text="Convergence across all generations "
                 "(how each AA's share evolves):",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,1))
        self._legend(parent, "Each line = one amino acid's share at each generation. "
                     "Flat lines on the right = the distribution has converged "
                     "(reached steady state). Rising/falling lines = still changing.",
                     bg="#E8EEF8")
        c_line = self._scroll_chart(parent, lambda cv: _render(), height=340,
                                    min_w=760, min_h=340)

        def _render(ev=None):
            g = gen_sel.get() - 1
            if not (0 <= g < len(per_gen_aa)):
                return
            gen_counter = per_gen_aa[g]
            fset = self._get_filter_set(deg_var)

            # Top: AA bar chart (with degeneracy filter)
            draw_bar_chart(c_aa, gen_counter, f"AAs at gen {g+1}{mode_badge}",
                           color_map=AA_COLOR_MAP, top_n=21,
                           normalize=norm_var.get(), filter_aa_set=fset)

            # Middle: category (property) grouped analysis
            sel_aas = ([aa for aa in ALL_AAS
                        if (fset is None or aa in fset)])
            g_order = list(PROPERTY_GROUPS.keys())
            g_names = {k: v[0] for k, v in PROPERTY_GROUPS.items()}
            g_cols  = {k: v[1] for k, v in PROPERTY_GROUPS.items()}
            g_bgs   = PROPERTY_GROUP_BG
            by_group = {grp: collections.Counter() for grp in g_order}
            for aa in sel_aas:
                grp = get_primary_group(aa)
                if grp in by_group:
                    by_group[grp][aa] = gen_counter.get(aa, 0)
            self._draw_grouped_bars(
                c_cat, by_group, g_order, g_names, g_cols, g_bgs,
                f"Category analysis at gen {g+1}",
                codon_counter=None, normalize=norm_var.get())

            # Convergence line chart (respects degeneracy filter)
            series = {}
            for aa in sel_aas:
                series[aa] = [per_gen_aa[gg].get(aa, 0) for gg in range(len(per_gen_aa))]
            draw_line_chart(c_line, series,
                            f"AA share over generations{mode_badge}",
                            top_n=8)

        spin.config(command=_render)
        spin.bind("<Return>", _render)
        # Arrow-key navigation (bound to the toplevel; harmless to rebind)
        self.bind("<Right>", lambda e: (gen_sel.set(min(n_gen, gen_sel.get()+1)), _render()))
        self.bind("<Left>",  lambda e: (gen_sel.set(max(1, gen_sel.get()-1)), _render()))
        self.after(90, _render)
        return gen_sel

    # ─────────────────────────────────────────────────────────────────────
    # Reusable category/AA tracking view (single-mode and compare)
    # ─────────────────────────────────────────────────────────────────────

    def _build_tracking_view(self, parent, track_data, n_gen, mode_badge="",
                             sample_records=None, stop_data=None):
        """
        Builds the category/AA evolution tracker into `parent`:

          A. Retention overview — for each starting biochemical category, the
             share of its probability that is STILL in that category at the
             final generation (bar chart, sorted).
          B. Per-category evolution — pick a starting category; a line chart
             shows how that category's mass redistributes across ALL categories
             over the generations (the 'started here' line is highlighted).
          C. Stay-in-same-category curve — one line per starting category, the
             self-retention share vs generation.
          D. Stay-in-same-AA curve — one line per starting AA, self-retention
             share vs generation (top movers highlighted).

        `track_data` has keys 'per_gen_cat_from' and 'per_gen_aa_from'.
        """
        pgc = track_data["per_gen_cat_from"]   # [gen]{start_grp}{cur_grp}=w
        pga = track_data["per_gen_aa_from"]    # [gen]{start_aa}{cur_aa}=w
        pgcod = track_data.get("per_gen_aa_codon_from", [])  # [gen]{start_aa}{cur_codon}=w
        pscod = track_data.get("per_gen_codon_from", [])  # [gen]{start_codon}{cur_codon}=w
        pstop_cat = track_data.get("per_gen_stop_cat_from", [])
        pstop_aa = track_data.get("per_gen_stop_aa_from", [])
        pstop_codon = track_data.get("per_gen_stop_codon_from", [])
        pstop_codon_to = track_data.get("per_gen_stop_codon_to", [])
        N = len(pgc)

        cat_keys   = list(PROPERTY_GROUPS.keys())
        cat_names  = {k: PROPERTY_GROUPS[k][0] for k in cat_keys}
        cat_colors = {PROPERTY_GROUPS[k][0]: PROPERTY_GROUPS[k][1] for k in cat_keys}
        stop_line_label = "Stop codon"
        cat_colors[stop_line_label] = "#C0392B"
        # also map raw-key -> colour for internal use
        cat_colors_raw = {k: PROPERTY_GROUPS[k][1] for k in cat_keys}

        def _cum_stop(per_gen_stop, start_key, gen):
            return sum(per_gen_stop[g].get(start_key, 0.0)
                       for g in range(min(gen, len(per_gen_stop)-1)+1)) if per_gen_stop else 0.0

        def _cat_series_with_stop(start_key, live_fn, stop_series):
            series = {cat_names[k]: [] for k in cat_keys}
            series[stop_line_label] = []
            for gen in range(N):
                live_by_cat = live_fn(gen)
                # Use the stop mass produced in this generation only, so the
                # stop line is a current-generation fraction rather than a
                # cumulative fraction from all earlier generations.
                stop_w = (stop_series[gen].get(start_key, 0.0)
                          if stop_series and gen < len(stop_series) else 0.0)
                denom = sum(live_by_cat.values()) + stop_w
                if denom <= 0:
                    for name in series:
                        series[name].append(0.0)
                    continue
                for k in cat_keys:
                    series[cat_names[k]].append(live_by_cat.get(k, 0.0) / denom)
                series[stop_line_label].append(stop_w / denom)
            return series

        def _self_share(per_gen, start_key, gen):
            """share of start_key's mass that is STILL in start_key at gen."""
            d = per_gen[gen].get(start_key, {})
            tot = sum(d.values())
            return (d.get(start_key, 0)/tot) if tot > 0 else 0.0

        def _aa_flow_summary(aa, gen):
            """
            Destination summary for one starting AA at one generation.
            Uses codon-level tracking when available, then falls back to AA-level
            tracking for older result objects.
            """
            gen = min(max(gen, 0), max(N-1, 0))
            start_cat = get_primary_group(aa)
            codon_dist = {}
            if gen < len(pgcod):
                codon_dist = pgcod[gen].get(aa, {}) or {}

            aa_dist = collections.Counter()
            cat_dist = collections.Counter({k: 0.0 for k in cat_keys})
            if codon_dist:
                for codon, w in codon_dist.items():
                    dest_aa = CODON_TABLE.get(codon, "?")
                    aa_dist[dest_aa] += w
                    dk = get_primary_group(dest_aa)
                    if dk in cat_dist:
                        cat_dist[dk] += w
            else:
                for dest_aa, w in pga[gen].get(aa, {}).items():
                    aa_dist[dest_aa] += w
                    dk = get_primary_group(dest_aa)
                    if dk in cat_dist:
                        cat_dist[dk] += w

            total = sum(cat_dist.values()) or sum(aa_dist.values()) or 1.0
            same_cat = cat_dist.get(start_cat, 0.0) / total
            same_aa = aa_dist.get(aa, 0.0) / total
            return {
                "aa": aa,
                "start_cat": start_cat,
                "codon_dist": codon_dist,
                "aa_dist": aa_dist,
                "cat_dist": cat_dist,
                "total": total,
                "same_cat": same_cat,
                "same_aa": same_aa,
            }

        def _codon_flow_summary(start_codon, gen):
            """Destination summary for one exact 3-base starting codon."""
            gen = min(max(gen, 0), max(N-1, 0))
            start_aa = CODON_TABLE.get(start_codon, "?")
            start_cat = get_primary_group(start_aa)
            codon_dist = {}
            if gen < len(pscod):
                codon_dist = pscod[gen].get(start_codon, {}) or {}

            aa_dist = collections.Counter()
            cat_dist = collections.Counter({k: 0.0 for k in cat_keys})
            for codon, w in codon_dist.items():
                dest_aa = CODON_TABLE.get(codon, "?")
                aa_dist[dest_aa] += w
                dk = get_primary_group(dest_aa)
                if dk in cat_dist:
                    cat_dist[dk] += w

            total = sum(codon_dist.values()) or sum(aa_dist.values()) or 1.0
            same_codon = codon_dist.get(start_codon, 0.0) / total
            same_aa = aa_dist.get(start_aa, 0.0) / total
            same_cat = cat_dist.get(start_cat, 0.0) / total
            return {
                "codon": start_codon,
                "aa": start_aa,
                "start_cat": start_cat,
                "codon_dist": codon_dist,
                "aa_dist": aa_dist,
                "cat_dist": cat_dist,
                "total": total,
                "same_codon": same_codon,
                "same_aa": same_aa,
                "same_cat": same_cat,
            }

        # ── Stop property overview ───────────────────────────────────────
        if stop_data is not None:
            stop_prop = property_stop_counter(stop_data)
            if stop_prop:
                tk.Label(parent,
                         text="Stop hits by starting property:",
                         font=("Helvetica",10,"bold"), bg=BG_PANEL, fg="#A32D2D"
                         ).pack(anchor="w", padx=8, pady=(2,2))
                self._legend(parent,
                    "Bars group stop probability by the biochemical property of "
                    "the original amino acid/codon. This answers which property "
                    "classes most often terminate as stop codons.",
                    bg="#FDEDEC")
                _stop_prop_norm = self._make_norm_toggle(parent, lambda: _render_stop_prop())
                def _draw_stop_prop_cv(cv):
                    draw_bar_chart(cv, stop_prop,
                                   f"Stop probability by starting property{mode_badge}",
                                   color_map=property_color_map_by_name(),
                                   top_n=len(PROPERTY_GROUPS),
                                   normalize=_stop_prop_norm.get())
                _c_stop_prop = self._scroll_chart(parent, _draw_stop_prop_cv,
                                                  height=260, min_w=860, min_h=360)
                def _render_stop_prop(ev=None):
                    _draw_stop_prop_cv(_c_stop_prop)

        # ── A. Retention overview (final generation) ─────────────────────
        self._legend(parent,
            "How well does each starting biochemical category 'hold' its "
            "probability? Bars show the share of each category's mass that is "
            "STILL in the same category at the final generation.", bg="#E8EEF8")
        tk.Label(parent, text="A.  Category self-retention at final generation:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(2,2))
        c_ret = self._scroll_chart(parent,
            lambda cv: self._draw_retention_overview(cv, pgc, cat_keys, cat_names,
                                                     cat_colors_raw, N, mode_badge),
            height=240, min_w=900, min_h=360)

        # ── B. Per-category evolution ────────────────────────────────────
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))
        tk.Label(parent, text="B.  Where does a starting category's mass go?",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,2))
        self._legend(parent,
            "Pick a starting category. Each line tracks the share of that "
            "category's mass that sits in a given category at each generation. "
            "The bold line is the category it started in (self-retention).",
            bg="#E8EEF8")
        sel_row = tk.Frame(parent, bg=BG_PANEL); sel_row.pack(anchor="w", padx=8, pady=(0,2))
        tk.Label(sel_row, text="Starting category:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        cat_var = tk.StringVar(value=cat_names[cat_keys[0]])
        cat_menu = ttk.Combobox(sel_row, textvariable=cat_var, state="readonly",
                                values=[cat_names[k] for k in cat_keys],
                                font=("Helvetica",10), width=22)
        cat_menu.pack(side="left", padx=(6,0))
        cat_conv_lbl = tk.Label(sel_row, text="", bg=BG_PANEL,
                                font=("Helvetica",8,"bold"), fg="#555")
        cat_conv_lbl.pack(side="left", padx=(12,0))

        def _render_evo(cv):
            # resolve display name -> raw key
            disp = cat_var.get()
            start_key = next((k for k in cat_keys if cat_names[k] == disp), cat_keys[0])
            series = _cat_series_with_stop(
                start_key,
                lambda gen: pgc[gen].get(start_key, {}),
                pstop_cat)
            cat_conv_lbl.config(text=convergence_text(series))
            draw_retention_lines(cv, series,
                                 f"{disp} → category/stop over generations{mode_badge}",
                                 color_map=cat_colors, highlight=cat_names[start_key])
        c_evo = self._scroll_chart(parent, _render_evo,
                                   height=320, min_w=1000, min_h=460)
        cat_menu.bind("<<ComboboxSelected>>", lambda e: _render_evo(c_evo))

        # Sections C-F were removed to keep this tab focused on category-level
        # flow and exact-codon destinations.

        # ── G. Category transition matrix ──────────────────────────────────
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))
        tk.Label(parent,
                 text="G.  Category transition matrix — full cross-category flow at any generation:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,2))
        self._legend(parent,
            "Grid: row = starting category, column = destination category. "
            "Each cell = % of starting-category mass that ended in the destination "
            "category at the selected generation. Diagonal cells (bold border) = "
            "self-retention. Cells are shaded by destination colour, intensity = fraction.",
            bg="#E8EEF8")

        g_ctrl = tk.Frame(parent, bg=BG_PANEL)
        g_ctrl.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(g_ctrl, text="Generation:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        g_gen_var = tk.IntVar(value=N)
        g_gen_spin = tk.Spinbox(g_ctrl, from_=1, to=max(N,1), textvariable=g_gen_var,
                                 width=5, font=("Courier",11))
        g_gen_spin.pack(side="left", padx=(4,0))

        def _render_g(cv):
            cv.delete("all")
            W = cv.winfo_width(); H = cv.winfo_height()
            if W < 100 or H < 100 or N < 1: return
            gen = min(g_gen_var.get()-1, N-1)
            n_cats = len(cat_keys)
            lbl_w = 148; lbl_h = 30; margin = 20
            cell_w = max(80, (W-lbl_w-margin)//n_cats)
            cell_h = max(36, (H-lbl_h-50)//n_cats)
            pad_l = lbl_w; pad_t = lbl_h + 28
            _chart_title(cv, W, 14,
                         f"Category transition matrix - gen {gen+1}{mode_badge}",
                         font=("Helvetica",10,"bold"))
            cv.create_text(pad_l + n_cats*cell_w//2, pad_t-8,
                           text="→  Destination category",
                           anchor="s", font=("Helvetica",8,"bold"), fill="#555")
            for ci, ck in enumerate(cat_keys):
                x = pad_l + ci*cell_w + cell_w//2
                cv.create_text(x, pad_t-4, text=_fit_text(cat_names[ck], cell_w-6, 8),
                               anchor="s", font=("Helvetica",8,"bold"),
                               fill=cat_colors_raw[ck])
            for ri, rk in enumerate(cat_keys):
                y = pad_t + ri*cell_h + cell_h//2
                cv.create_text(pad_l-4, y, text=_fit_text(cat_names[rk], pad_l-10, 8),
                               anchor="e", font=("Helvetica",8,"bold"),
                               fill=cat_colors_raw[rk])
            for ri, rk in enumerate(cat_keys):
                d = pgc[gen].get(rk, {})
                tot = sum(d.values()) or 1
                for ci, ck in enumerate(cat_keys):
                    frac = d.get(ck, 0)/tot
                    x = pad_l + ci*cell_w; y = pad_t + ri*cell_h
                    base = cat_colors_raw[ck]
                    r2, g2, b2 = int(base[1:3],16), int(base[3:5],16), int(base[5:7],16)
                    fade = 1 - frac*0.88
                    lr = int(r2 + (255-r2)*fade)
                    lg = int(g2 + (255-g2)*fade)
                    lb = int(b2 + (255-b2)*fade)
                    fill_c = f"#{lr:02X}{lg:02X}{lb:02X}"
                    bw = 3 if ri == ci else 1
                    border_c = cat_colors_raw[rk] if ri == ci else "#ccc"
                    cv.create_rectangle(x, y, x+cell_w, y+cell_h,
                                        fill=fill_c, outline=border_c, width=bw)
                    pct = f"{frac*100:.1f}%" if frac > 0.002 else "—"
                    lum = (lr*299 + lg*587 + lb*114)//1000
                    fg = "#111" if lum > 130 else "#eee"
                    cv.create_text(x+cell_w//2, y+cell_h//2, text=pct,
                                   anchor="center", font=("Helvetica",9,"bold"), fill=fg)

        c_g = self._scroll_chart(parent, _render_g,
                                 height=280, min_w=980, min_h=420)

        def _refresh_g(ev=None): _render_g(c_g)
        g_gen_spin.config(command=_refresh_g); g_gen_spin.bind("<Return>", _refresh_g)
        self.after(130, _refresh_g)

        # ── H. All-AA category/codon summary ──────────────────────────────
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))
        tk.Label(parent,
                 text="H.  All amino acids — category and codon destination summary:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,2))
        self._legend(parent,
            "Pick any generation and optionally one starting category. Each AA row "
            "shows its codons, the share still in the same category, the share still "
            "encoding the same AA, and where its codon probability moved by category.",
            bg="#E8EEF8")

        h_ctrl = tk.Frame(parent, bg=BG_PANEL)
        h_ctrl.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(h_ctrl, text="Starting category:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        h_cat_values = ["All categories"] + [cat_names[k] for k in cat_keys]
        h_cat_var = tk.StringVar(value=h_cat_values[0])
        h_cat_menu = ttk.Combobox(h_ctrl, textvariable=h_cat_var, state="readonly",
                                  values=h_cat_values, font=("Helvetica",10), width=22)
        h_cat_menu.pack(side="left", padx=(6,12))
        tk.Label(h_ctrl, text="Generation:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        h_gen_var = tk.IntVar(value=N)
        h_gen_spin = tk.Spinbox(h_ctrl, from_=1, to=max(N,1), textvariable=h_gen_var,
                                width=5, font=("Courier",11))
        h_gen_spin.pack(side="left", padx=(4,12))
        tk.Label(h_ctrl, text="Sort:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        h_sort_var = tk.StringVar(value="Same category")
        h_sort_menu = ttk.Combobox(h_ctrl, textvariable=h_sort_var, state="readonly",
                                   values=["Same category", "Same AA", "AA name"],
                                   font=("Helvetica",10), width=14)
        h_sort_menu.pack(side="left", padx=(6,0))

        def _h_selected_aas():
            disp = h_cat_var.get()
            if disp == "All categories":
                aas = list(ALL_AAS)
            else:
                sk = next((k for k in cat_keys if cat_names[k] == disp), cat_keys[0])
                aas = [aa for aa in ALL_AAS if get_primary_group(aa) == sk]
            gen = min(h_gen_var.get()-1, N-1)
            rows = [_aa_flow_summary(aa, gen) for aa in aas]
            sort_by = h_sort_var.get()
            if sort_by == "Same AA":
                rows.sort(key=lambda r: (-r["same_aa"], r["aa"]))
            elif sort_by == "AA name":
                rows.sort(key=lambda r: r["aa"])
            else:
                rows.sort(key=lambda r: (-r["same_cat"], r["aa"]))
            return rows, gen

        def _render_h_chart(cv):
            cv.delete("all")
            W = cv.winfo_width(); H = cv.winfo_height()
            if W < 100 or H < 100 or N < 1: return
            rows, gen = _h_selected_aas()
            if not rows:
                cv.create_text(W//2, H//2, text="No amino acids match this category",
                               fill="#aaa", font=("Helvetica",11)); return

            pad_l=190; pad_r=180; pad_t=38; pad_b=28
            chart_w = W-pad_l-pad_r
            n = len(rows)
            bar_h = max(14, min(26, (H-pad_t-pad_b)//max(n,1)-4))
            gap = max(2, (H-pad_t-pad_b-n*bar_h)//max(n+1,1))
            _chart_title(cv, W, 16,
                         f"AA -> destination categories at gen {gen+1}{mode_badge}",
                         font=("Helvetica",10,"bold"))
            cv.create_text(pad_l+chart_w+8, pad_t-17,
                           text=_fit_text("same cat / same AA", pad_r-12, 8),
                           anchor="w", font=("Helvetica",8,"bold"), fill="#555")
            for i, row in enumerate(rows):
                aa = row["aa"]; total = row["total"]
                start_col = cat_colors_raw.get(row["start_cat"], "#888")
                codons = "/".join(c for c, a in sorted(CODON_TABLE.items())
                                  if a == aa and c not in STOP_CODONS)
                y = pad_t + i*(bar_h+gap)
                cv.create_text(pad_l-6, y+bar_h//2,
                               text=_fit_text(f"{aa}  {codons}", pad_l-12, 8, True),
                               anchor="e", font=("Courier",8,"bold"), fill=start_col)
                x_cur = pad_l
                for cat_k in cat_keys:
                    frac = row["cat_dist"].get(cat_k, 0.0) / total
                    if frac <= 0: continue
                    bw = max(1, int(frac*chart_w))
                    col = cat_colors_raw[cat_k]
                    cv.create_rectangle(x_cur, y, x_cur+bw, y+bar_h,
                                        fill=col, outline="white", width=1)
                    if bw > 28:
                        cv.create_text(x_cur+bw//2, y+bar_h//2,
                                       text=f"{frac*100:.0f}%",
                                       anchor="center", font=("Helvetica",7),
                                       fill="white")
                    x_cur += bw
                cv.create_text(pad_l+chart_w+8, y+bar_h//2,
                               text=_fit_text(f"{row['same_cat']*100:.1f}% / {row['same_aa']*100:.1f}%",
                                              pad_r-12, 8),
                               anchor="w", font=("Helvetica",8), fill="#444")

            cv.create_line(pad_l, H-pad_b, pad_l+chart_w, H-pad_b, fill="#ccc")
            for frac in [0,0.25,0.5,0.75,1.0]:
                tx = pad_l+int(frac*chart_w)
                cv.create_line(tx, H-pad_b, tx, H-pad_b+4, fill="#bbb")
                cv.create_text(tx, H-pad_b+6, text=f"{int(frac*100)}%",
                               anchor="n", font=("Helvetica",7), fill="#999")
            lx = W-pad_r+8; ly0 = pad_t + max(0, n*(bar_h+gap)) + 4
            if ly0 + len(cat_keys)*15 > H-pad_b:
                ly0 = pad_t
            cv.create_text(lx, ly0, text=_fit_text("Destination", pad_r-16, 8), anchor="nw",
                           font=("Helvetica",8,"bold"), fill="#333")
            for li, k in enumerate(cat_keys):
                ly = ly0 + 15 + li*15
                cv.create_rectangle(lx, ly, lx+9, ly+9,
                                    fill=cat_colors_raw[k], outline="")
                cv.create_text(lx+12, ly, text=_fit_text(cat_names[k], pad_r-28, 7),
                               anchor="nw", font=("Helvetica",7), fill="#333")

        c_h = self._scroll_chart(parent, _render_h_chart,
                                 height=420, min_w=1100, min_h=620)

        self._legend(parent,
            "Table rows are sortable. Destination columns are category shares. "
            "Top destination AAs/codons show the strongest specific routes from "
            "that starting AA at the selected generation.",
            bg="#E8EEF8")
        h_tbl_f = tk.Frame(parent, bg=BG_PANEL, height=280)
        h_tbl_f.pack(fill="both", expand=True, padx=6, pady=(0,4))
        h_tbl_f.pack_propagate(False)
        h_vsb = tk.Scrollbar(h_tbl_f); h_vsb.pack(side="right", fill="y")
        h_hsb = tk.Scrollbar(h_tbl_f, orient="horizontal"); h_hsb.pack(side="bottom", fill="x")
        h_cat_cols = [cat_names[k][:10] for k in cat_keys]
        h_cols = (["aa","full","codons","start_cat","same_cat","same_aa"] +
                  h_cat_cols + ["top_aas","top_codons"])
        h_tv = ttk.Treeview(h_tbl_f, columns=h_cols, show="headings", height=10,
                            yscrollcommand=h_vsb.set, xscrollcommand=h_hsb.set)
        h_vsb.config(command=h_tv.yview); h_hsb.config(command=h_tv.xview)
        h_tv.pack(fill="both", expand=True)
        h_headings = [
            ("aa","AA",55), ("full","Full name",135), ("codons","Codons",185),
            ("start_cat","Start category",135), ("same_cat","Same cat %",85),
            ("same_aa","Same AA %",80),
        ]
        for cid, head, width in h_headings:
            h_tv.heading(cid, text=head,
                         command=lambda c=cid: self._sort_table(h_tv, c, False))
            h_tv.column(cid, width=width, anchor="center" if cid != "full" else "w")
        for k, cid in zip(cat_keys, h_cat_cols):
            h_tv.heading(cid, text=cat_names[k],
                         command=lambda c=cid: self._sort_table(h_tv, c, False))
            h_tv.column(cid, width=90, anchor="center")
        for cid, head, width in [("top_aas","Top destination AAs",210),
                                 ("top_codons","Top destination codons",260)]:
            h_tv.heading(cid, text=head,
                         command=lambda c=cid: self._sort_table(h_tv, c, False))
            h_tv.column(cid, width=width, anchor="w")
        h_tv.tag_configure("hi", background="#D5F5E3")
        h_tv.tag_configure("med", background="#FEF9E7")
        h_tv.tag_configure("lo", background="#FDEDEC")

        def _pct_list(counter, total, limit=4):
            items = sorted(counter.items(), key=lambda kv: -kv[1])[:limit]
            return ", ".join(f"{k}:{100*v/total:.1f}%" for k, v in items if v > 0)

        def _refresh_h_tbl():
            for item in h_tv.get_children():
                h_tv.delete(item)
            rows, _gen = _h_selected_aas()
            for row in rows:
                aa = row["aa"]; total = row["total"]
                start_cat = row["start_cat"]
                codons = ", ".join(c for c, a in sorted(CODON_TABLE.items())
                                   if a == aa and c not in STOP_CODONS)
                top_codons = _pct_list(collections.Counter(row["codon_dist"]), total, 5)
                if not top_codons:
                    top_codons = "(codon-level data unavailable)"
                top_aas = _pct_list(row["aa_dist"], total, 5)
                vals = [
                    aa, AA_FULL.get(aa, aa), codons, cat_names[start_cat],
                    f"{100*row['same_cat']:.1f}%", f"{100*row['same_aa']:.1f}%",
                ]
                vals += [f"{100*row['cat_dist'].get(k,0.0)/total:.1f}%"
                         for k in cat_keys]
                vals += [top_aas, top_codons]
                sp = row["same_cat"]
                tag = "hi" if sp >= 0.60 else ("med" if sp >= 0.30 else "lo")
                h_tv.insert("", "end", values=vals, tags=(tag,))

        def _refresh_h(ev=None):
            _render_h_chart(c_h)
            _refresh_h_tbl()

        h_cat_menu.bind("<<ComboboxSelected>>", _refresh_h)
        h_sort_menu.bind("<<ComboboxSelected>>", _refresh_h)
        h_gen_spin.config(command=_refresh_h); h_gen_spin.bind("<Return>", _refresh_h)
        self.after(150, _refresh_h)

        # ── I. Exact codon-triplet category tracking ──────────────────────
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))
        tk.Label(parent,
                 text="I.  Exact codon triplets — category tracking per starting codon:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,2))
        self._legend(parent,
            "This view does not merge synonymous codons. Each row is one exact "
            "starting triplet, such as GCT or GCC. It shows where that codon's "
            "probability moved by biochemical category, plus same-codon, same-AA, "
            "and same-category retention.",
            bg="#E8EEF8")

        i_ctrl = tk.Frame(parent, bg=BG_PANEL)
        i_ctrl.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(i_ctrl, text="Starting category:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        i_cat_values = ["All categories"] + [cat_names[k] for k in cat_keys]
        i_cat_var = tk.StringVar(value=i_cat_values[0])
        i_cat_menu = ttk.Combobox(i_ctrl, textvariable=i_cat_var, state="readonly",
                                  values=i_cat_values, font=("Helvetica",10), width=22)
        i_cat_menu.pack(side="left", padx=(6,12))
        tk.Label(i_ctrl, text="AA:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        i_aa_values = ["All AAs"] + ALL_AAS
        i_aa_var = tk.StringVar(value=i_aa_values[0])
        i_aa_menu = ttk.Combobox(i_ctrl, textvariable=i_aa_var, state="readonly",
                                 values=i_aa_values, font=("Helvetica",10), width=9)
        i_aa_menu.pack(side="left", padx=(6,12))
        tk.Label(i_ctrl, text="Generation:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        i_gen_var = tk.IntVar(value=N)
        i_gen_spin = tk.Spinbox(i_ctrl, from_=1, to=max(N,1), textvariable=i_gen_var,
                                width=5, font=("Courier",11))
        i_gen_spin.pack(side="left", padx=(4,12))
        tk.Label(i_ctrl, text="Sort:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        i_sort_var = tk.StringVar(value="Same category")
        i_sort_menu = ttk.Combobox(i_ctrl, textvariable=i_sort_var, state="readonly",
                                   values=["Same category", "Same AA", "Same codon", "Codon"],
                                   font=("Helvetica",10), width=14)
        i_sort_menu.pack(side="left", padx=(6,0))

        def _i_selected_rows():
            disp_cat = i_cat_var.get()
            aa_filter = i_aa_var.get()
            if disp_cat == "All categories":
                cat_filter = None
            else:
                cat_filter = next((k for k in cat_keys if cat_names[k] == disp_cat), None)
            gen = min(i_gen_var.get()-1, N-1)
            codons = []
            for codon in VALID_CODONS:
                aa = CODON_TABLE.get(codon, "?")
                if cat_filter is not None and get_primary_group(aa) != cat_filter:
                    continue
                if aa_filter != "All AAs" and aa != aa_filter:
                    continue
                codons.append(codon)
            rows = [_codon_flow_summary(codon, gen) for codon in codons]
            sort_by = i_sort_var.get()
            if sort_by == "Same AA":
                rows.sort(key=lambda r: (-r["same_aa"], r["codon"]))
            elif sort_by == "Same codon":
                rows.sort(key=lambda r: (-r["same_codon"], r["codon"]))
            elif sort_by == "Codon":
                rows.sort(key=lambda r: r["codon"])
            else:
                rows.sort(key=lambda r: (-r["same_cat"], r["codon"]))
            return rows, gen

        def _render_i_chart(cv):
            cv.delete("all")
            W = cv.winfo_width(); H = cv.winfo_height()
            if W < 100 or H < 100 or N < 1: return
            rows, gen = _i_selected_rows()
            if not rows:
                cv.create_text(W//2, H//2, text="No codons match this filter",
                               fill="#aaa", font=("Helvetica",11)); return
            pad_l=130; pad_r=210; pad_t=38; pad_b=28
            chart_w = max(40, W-pad_l-pad_r)
            n = len(rows)
            bar_h = max(11, min(23, (H-pad_t-pad_b)//max(n,1)-3))
            gap = max(1, (H-pad_t-pad_b-n*bar_h)//max(n+1,1))
            _chart_title(cv, W, 16,
                         f"Start codon -> destination categories at gen {gen+1}{mode_badge}",
                         font=("Helvetica",10,"bold"))
            cv.create_text(pad_l+chart_w+8, pad_t-17,
                           text=_fit_text("same codon / AA / cat", pad_r-12, 8),
                           anchor="w", font=("Helvetica",8,"bold"), fill="#555")
            for i, row in enumerate(rows):
                codon = row["codon"]; aa = row["aa"]; total = row["total"]
                start_col = AA_COLOR_MAP.get(aa, "#888")
                y = pad_t + i*(bar_h+gap)
                cv.create_text(pad_l-6, y+bar_h//2,
                               text=_fit_text(f"{codon} {aa}", pad_l-12, 8, True),
                               anchor="e", font=("Courier",8,"bold"), fill=start_col)
                x_cur = pad_l
                for cat_k in cat_keys:
                    frac = row["cat_dist"].get(cat_k, 0.0) / total
                    if frac <= 0: continue
                    bw = max(1, int(frac*chart_w))
                    col = cat_colors_raw[cat_k]
                    cv.create_rectangle(x_cur, y, x_cur+bw, y+bar_h,
                                        fill=col, outline="white", width=1)
                    if bw > 30 and bar_h >= 14:
                        cv.create_text(x_cur+bw//2, y+bar_h//2,
                                       text=f"{frac*100:.0f}%",
                                       anchor="center", font=("Helvetica",7),
                                       fill="white")
                    x_cur += bw
                tail = (f"{row['same_codon']*100:.1f}% / "
                        f"{row['same_aa']*100:.1f}% / "
                        f"{row['same_cat']*100:.1f}%")
                cv.create_text(pad_l+chart_w+8, y+bar_h//2,
                               text=_fit_text(tail, pad_r-12, 8),
                               anchor="w", font=("Helvetica",8), fill="#444")
            cv.create_line(pad_l, H-pad_b, pad_l+chart_w, H-pad_b, fill="#ccc")
            for frac in [0,0.25,0.5,0.75,1.0]:
                tx = pad_l+int(frac*chart_w)
                cv.create_line(tx, H-pad_b, tx, H-pad_b+4, fill="#bbb")
                cv.create_text(tx, H-pad_b+6, text=f"{int(frac*100)}%",
                               anchor="n", font=("Helvetica",7), fill="#999")
            lx = W-pad_r+8
            ly0 = pad_t + min(n*(bar_h+gap)+4, max(0, H-pad_b-90))
            if ly0 + len(cat_keys)*15 > H-pad_b:
                ly0 = pad_t
            cv.create_text(lx, ly0, text=_fit_text("Destination", pad_r-16, 8),
                           anchor="nw", font=("Helvetica",8,"bold"), fill="#333")
            for li, k in enumerate(cat_keys):
                ly = ly0 + 15 + li*15
                cv.create_rectangle(lx, ly, lx+9, ly+9,
                                    fill=cat_colors_raw[k], outline="")
                cv.create_text(lx+12, ly, text=_fit_text(cat_names[k], pad_r-28, 7),
                               anchor="nw", font=("Helvetica",7), fill="#333")

        c_i = self._scroll_chart(parent, _render_i_chart,
                                 height=430, min_w=1100, min_h=1320)

        self._legend(parent,
            "Codon table: one row per exact starting triplet. Destination category "
            "columns are shares of surviving probability at the selected generation. "
            "Top destination codons keeps the codon-level detail visible.",
            bg="#E8EEF8")
        i_tbl_f = tk.Frame(parent, bg=BG_PANEL, height=300)
        i_tbl_f.pack(fill="both", expand=True, padx=6, pady=(0,4))
        i_tbl_f.pack_propagate(False)
        i_vsb = tk.Scrollbar(i_tbl_f); i_vsb.pack(side="right", fill="y")
        i_hsb = tk.Scrollbar(i_tbl_f, orient="horizontal"); i_hsb.pack(side="bottom", fill="x")
        i_cat_cols = [cat_names[k][:10] for k in cat_keys]
        i_cols = (["codon","aa","full","start_cat","same_codon","same_aa","same_cat"] +
                  i_cat_cols + ["top_codons","top_aas"])
        i_tv = ttk.Treeview(i_tbl_f, columns=i_cols, show="headings", height=11,
                            yscrollcommand=i_vsb.set, xscrollcommand=i_hsb.set)
        i_vsb.config(command=i_tv.yview); i_hsb.config(command=i_tv.xview)
        i_tv.pack(fill="both", expand=True)
        for cid, head, width, anchor in [
            ("codon","Start codon",85,"center"),
            ("aa","AA",55,"center"),
            ("full","Full name",135,"w"),
            ("start_cat","Start category",135,"center"),
            ("same_codon","Same codon %",95,"center"),
            ("same_aa","Same AA %",80,"center"),
            ("same_cat","Same cat %",85,"center"),
        ]:
            i_tv.heading(cid, text=head,
                         command=lambda c=cid: self._sort_table(i_tv, c, False))
            i_tv.column(cid, width=width, anchor=anchor)
        for k, cid in zip(cat_keys, i_cat_cols):
            i_tv.heading(cid, text=cat_names[k],
                         command=lambda c=cid: self._sort_table(i_tv, c, False))
            i_tv.column(cid, width=90, anchor="center")
        for cid, head, width in [("top_codons","Top destination codons",280),
                                 ("top_aas","Top destination AAs",210)]:
            i_tv.heading(cid, text=head,
                         command=lambda c=cid: self._sort_table(i_tv, c, False))
            i_tv.column(cid, width=width, anchor="w")
        i_tv.tag_configure("hi", background="#D5F5E3")
        i_tv.tag_configure("med", background="#FEF9E7")
        i_tv.tag_configure("lo", background="#FDEDEC")

        def _refresh_i_tbl():
            for item in i_tv.get_children():
                i_tv.delete(item)
            rows, _gen = _i_selected_rows()
            for row in rows:
                total = row["total"]; codon = row["codon"]; aa = row["aa"]
                top_codons = _pct_list(collections.Counter(row["codon_dist"]), total, 6)
                if not top_codons:
                    top_codons = "(no surviving codon mass)"
                vals = [
                    codon, aa, AA_FULL.get(aa, aa), cat_names[row["start_cat"]],
                    f"{100*row['same_codon']:.1f}%",
                    f"{100*row['same_aa']:.1f}%",
                    f"{100*row['same_cat']:.1f}%",
                ]
                vals += [f"{100*row['cat_dist'].get(k,0.0)/total:.1f}%"
                         for k in cat_keys]
                vals += [top_codons, _pct_list(row["aa_dist"], total, 5)]
                sp = row["same_cat"]
                tag = "hi" if sp >= 0.60 else ("med" if sp >= 0.30 else "lo")
                i_tv.insert("", "end", values=vals, tags=(tag,))

        tk.Label(parent,
                 text="Selected codon spotlight — category distribution over generations:",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(4,2))
        i_spot_row = tk.Frame(parent, bg=BG_PANEL)
        i_spot_row.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(i_spot_row, text="Start codon:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        i_codon_var = tk.StringVar(value=VALID_CODONS[0])
        i_codon_menu = ttk.Combobox(i_spot_row, textvariable=i_codon_var,
                                    state="readonly", values=VALID_CODONS,
                                    font=("Helvetica",10), width=8)
        i_codon_menu.pack(side="left", padx=(6,12))
        tk.Label(i_spot_row, text="Destination gen:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        i_dest_gen_var = tk.IntVar(value=N)
        i_dest_gen_spin = tk.Spinbox(i_spot_row, from_=1, to=max(N,1),
                                     textvariable=i_dest_gen_var, width=5,
                                     font=("Courier",11))
        i_dest_gen_spin.pack(side="left", padx=(4,12))
        tk.Label(i_spot_row, text="Display:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        i_spot_mode_var = tk.StringVar(value="Sampled copies")
        i_spot_mode_menu = ttk.Combobox(
            i_spot_row, textvariable=i_spot_mode_var, state="readonly",
            values=["Sampled copies", "Exact probability"],
            font=("Helvetica",10), width=16)
        i_spot_mode_menu.pack(side="left", padx=(6,12))
        i_conv_lbl = tk.Label(i_spot_row, text="", bg=BG_PANEL,
                              font=("Helvetica",8,"bold"), fg="#555")
        i_conv_lbl.pack(side="left", padx=(0,0))

        def _cumulative_stop_codons(start_codon, gen):
            out = collections.Counter()
            if not pstop_codon_to:
                total = _cum_stop(pstop_codon, start_codon, gen)
                if total:
                    out["Stop"] = total
                return out
            last = min(gen, len(pstop_codon_to)-1)
            for gg in range(last+1):
                for stop_codon, w in pstop_codon_to[gg].get(start_codon, {}).items():
                    out[stop_codon] += w
            return out

        def _render_i_destination_hist(cv):
            cv.delete("all")
            W = cv.winfo_width(); H = cv.winfo_height()
            if W < 100 or H < 100 or N < 1: return
            start_codon = i_codon_var.get()
            start_aa = CODON_TABLE.get(start_codon, "?")
            gen = min(max(i_dest_gen_var.get()-1, 0), N-1)
            live = collections.Counter(pscod[gen].get(start_codon, {})) if gen < len(pscod) else collections.Counter()
            stops = _cumulative_stop_codons(start_codon, gen)
            if not live and not stops:
                cv.create_text(W//2, H//2, text="No destination codons at this generation",
                               fill="#aaa", font=("Helvetica",11)); return

            stop_panel_w = 220
            pad_l=130; pad_r=stop_panel_w+30; pad_t=42; pad_b=36
            chart_w = max(80, W-pad_l-pad_r)
            chart_right = pad_l + chart_w
            rows = sorted(live.items(), key=lambda kv: -kv[1])
            n = max(len(rows), 1)
            bar_h = max(12, min(24, (H-pad_t-pad_b)//n - 3))
            gap = max(2, (H-pad_t-pad_b-len(rows)*bar_h)//max(len(rows)+1, 1))
            max_live = max((v for _, v in rows), default=1) or 1
            _chart_title(cv, W, 16,
                         f"{start_codon} ({start_aa}) -> destination codons at gen {gen+1}",
                         font=("Helvetica",10,"bold"))
            cv.create_text(pad_l, pad_t-16, text="Live destination codons at selected generation",
                           anchor="w", font=("Helvetica",8,"bold"), fill="#333")

            for i, (dest_codon, w) in enumerate(rows):
                dest_aa = CODON_TABLE.get(dest_codon, "?")
                y = pad_t + i*(bar_h+gap)
                label = f"{dest_codon} {dest_aa}"
                col = AA_COLOR_MAP.get(dest_aa, "#888")
                bw = max(2, int((w/max_live)*chart_w)) if w > 0 else 0
                cv.create_rectangle(pad_l, y, pad_l+bw, y+bar_h,
                                    fill=col, outline="")
                cv.create_text(pad_l-6, y+bar_h//2,
                               text=_fit_text(label, pad_l-12, 8, True),
                               anchor="e", font=("Courier",8,"bold"), fill="#333")
                _safe_value_label(cv, pad_l+bw, y+bar_h//2, f"{w:.5f}",
                                  "#444", pad_l, chart_right, bw,
                                  font=("Helvetica",8))

            cv.create_line(pad_l, H-pad_b, chart_right, H-pad_b, fill="#ccc")
            for frac in [0, 0.25, 0.5, 0.75, 1.0]:
                tx = pad_l + int(frac*chart_w)
                cv.create_line(tx, H-pad_b, tx, H-pad_b+4, fill="#bbb")
                cv.create_text(tx, H-pad_b+6, text=f"{frac*max_live:.3f}",
                               anchor="n", font=("Helvetica",7), fill="#999")

            sx = chart_right + 28
            sw = max(80, W-sx-24)
            cv.create_text(sx, pad_t-16,
                           text="Cumulative stop codons",
                           anchor="w", font=("Helvetica",8,"bold"), fill="#A32D2D")
            stop_rows = [(c, stops.get(c, 0.0)) for c in ("TAA", "TAG", "TGA")]
            max_stop = max((v for _, v in stop_rows), default=1) or 1
            stop_colors = {"TAA":"#E74C3C", "TAG":"#8E44AD", "TGA":"#E67E22"}
            for i, (stop_codon, w) in enumerate(stop_rows):
                y = pad_t + i*42
                bw = max(2, int((w/max_stop)*sw)) if w > 0 else 0
                cv.create_text(sx, y+10, text=stop_codon,
                               anchor="w", font=("Courier",9,"bold"),
                               fill=stop_colors[stop_codon])
                cv.create_rectangle(sx+46, y, sx+46+bw, y+22,
                                    fill=stop_colors[stop_codon], outline="")
                cv.create_text(sx+50+bw, y+11, text=f"{w:.5f}",
                               anchor="w", font=("Helvetica",8), fill="#444")
            cv.create_text(sx, pad_t+140,
                           text="Stop bars are cumulative up to this generation.",
                           anchor="w", font=("Helvetica",8,"italic"), fill="#777")

        c_i_dest = self._scroll_chart(parent, _render_i_destination_hist,
                                      height=440, min_w=1100, min_h=1300)

        def _sampled_codon_series(codon):
            records_for_codon = [r for r in (sample_records or [])
                                 if r.get("start") == codon]
            series = {cat_names[k]: [] for k in cat_keys}
            series[stop_line_label] = []
            for gen_idx in range(N):
                gen_num = gen_idx + 1
                live_by_cat = collections.Counter()
                stop_now = 0
                for rec in records_for_codon:
                    path = rec.get("path") or [rec.get("start"), rec.get("final")]
                    stop_gen = rec.get("stop_gen")
                    if rec.get("hit_stop") and stop_gen is not None and gen_num >= stop_gen:
                        if gen_num == stop_gen:
                            stop_now += 1
                        continue
                    idx = min(gen_num, len(path)-1)
                    cur_codon = path[idx]
                    cur_aa = CODON_TABLE.get(cur_codon, "Stop")
                    if cur_aa == "Stop":
                        stop_now += 1
                        continue
                    cur_cat = get_primary_group(cur_aa)
                    if cur_cat in cat_keys:
                        live_by_cat[cur_cat] += 1
                for k in cat_keys:
                    series[cat_names[k]].append(live_by_cat.get(k, 0))
                series[stop_line_label].append(stop_now)
            return series, len(records_for_codon)

        def _sampled_live_vector(codon, gen):
            series, n_records = _sampled_codon_series(codon)
            if not n_records:
                return [0.0 for _ in cat_keys], 0.0, 0.0
            live_counts = [series[cat_names[k]][gen] for k in cat_keys]
            live_total = sum(live_counts)
            stop_now = series[stop_line_label][gen]
            if live_total <= 0:
                return [0.0 for _ in cat_keys], 0.0, float(stop_now)
            return [v / live_total for v in live_counts], float(live_total), float(stop_now)

        def _sampled_codon_scores(codon, stop_weight):
            scores = []
            for gen in range(1, N):
                prev_vec, prev_live, _prev_stop = _sampled_live_vector(codon, gen-1)
                cur_vec, cur_live, cur_stop = _sampled_live_vector(codon, gen)
                shape_change = _js_distance(prev_vec, cur_vec) if prev_live > 0 and cur_live > 0 else 0.0
                stop_loss = min(1.0, max(0.0, cur_stop / prev_live)) if prev_live > 0 else 0.0
                scores.append(shape_change + stop_weight * stop_loss)
            return scores

        def _category_only_series(series):
            return {cat_names[k]: list(series.get(cat_names[k], [])) for k in cat_keys}

        def _stop_arrays_from_series(series):
            new_stops = list(series.get(stop_line_label, []))
            cumulative = []
            running = 0
            for val in new_stops:
                running += val
                cumulative.append(running)
            return new_stops, cumulative

        def _sampled_count_vectors(codon):
            series, n_records = _sampled_codon_series(codon)
            vectors = []
            for gen in range(N):
                vectors.append(tuple(series[cat_names[k]][gen] for k in cat_keys))
            return vectors, series, n_records

        def _sampled_no_more_change(codon):
            vectors, _series, n_records = _sampled_count_vectors(codon)
            if not n_records or not vectors:
                return None, "no sampled copies"
            for idx, vec in enumerate(vectors):
                if all(future == vec for future in vectors[idx:]):
                    if sum(vec) == 0:
                        return idx + 1, "all stopped"
                    return idx + 1, "category counts stable"
            return None, "still changing"

        def _codon_live_category_weight_series(codon):
            series = {cat_names[k]: [] for k in cat_keys}
            for gen in range(N):
                live_by_cat = _codon_flow_summary(codon, gen)["cat_dist"]
                for k in cat_keys:
                    series[cat_names[k]].append(live_by_cat.get(k, 0.0))
            return series

        def _render_i_spot(cv):
            codon = i_codon_var.get()
            aa = CODON_TABLE.get(codon, "?")
            sampled_mode = i_spot_mode_var.get() == "Sampled copies"
            if sampled_mode:
                full_series, n_sampled = _sampled_codon_series(codon)
                series = _category_only_series(full_series)
                markov_gen, markov_note = _sampled_no_more_change(codon)
                markov_score = 0
            else:
                threshold = _markov_threshold()
                stop_weight = _markov_stop_weight()
                series = _codon_live_category_weight_series(codon)
                n_sampled = None
                scores = _codon_markov_scores(codon, stop_weight)
                markov_gen, markov_score = _score_convergence_generation(scores, threshold)
                markov_note = f"max future change {markov_score:.5f}"
            if markov_gen is None:
                i_conv_lbl.config(
                    text=f"No more change: > {N} ({markov_note})")
                marker_label = None
            else:
                i_conv_lbl.config(
                    text=f"No more change gen {markov_gen} ({markov_note})")
                marker_label = f"No more change gen {markov_gen}"
            if sampled_mode and not n_sampled:
                cv.delete("all")
                cv.create_text(cv.winfo_width()//2, cv.winfo_height()//2,
                               text=f"No sampled copies for {codon}",
                               fill="#aaa", font=("Helvetica",11))
                i_conv_lbl.config(text="No sampled copies for this codon")
                return
            if sampled_mode:
                i_conv_lbl.config(
                    text=i_conv_lbl.cget("text") + f" | counts shown, n={n_sampled}")
            title_suffix = "sampled copies" if sampled_mode else "surviving-only probability"
            draw_retention_lines(cv, series,
                                 f"{codon} ({aa}) category distribution - {title_suffix}{mode_badge}",
                                 color_map=cat_colors,
                                 highlight=cat_names.get(get_primary_group(aa)),
                                 marker_gen=markov_gen,
                                 marker_label=marker_label,
                                 marker_color="#111",
                                 show_share=not sampled_mode,
                                 integer_values=sampled_mode)

        c_i_spot = self._scroll_chart(parent, _render_i_spot,
                                      height=520, min_w=1100, min_h=720)

        tk.Label(parent,
                 text="Selected codon stop behavior — separate from live categories:",
                 font=("Helvetica",8,"bold"), bg=BG_PANEL, fg="#A32D2D"
                 ).pack(anchor="w", padx=8, pady=(0,2))

        def _render_i_stop(cv):
            codon = i_codon_var.get()
            sampled_mode = i_spot_mode_var.get() == "Sampled copies"
            if sampled_mode:
                full_series, n_sampled = _sampled_codon_series(codon)
                new_stops, cumulative = _stop_arrays_from_series(full_series)
                marker_gen, _note = _sampled_no_more_change(codon)
                title = f"{codon} stop events - sampled integer counts"
                integer_values = True
                if not n_sampled:
                    cv.delete("all")
                    cv.create_text(cv.winfo_width()//2, cv.winfo_height()//2,
                                   text=f"No sampled copies for {codon}",
                                   fill="#aaa", font=("Helvetica",10))
                    return
            else:
                new_stops = [
                    pstop_codon[g].get(codon, 0.0) if g < len(pstop_codon) else 0.0
                    for g in range(N)
                ]
                cumulative = []
                running = 0.0
                for val in new_stops:
                    running += val
                    cumulative.append(running)
                scores = _codon_markov_scores(codon, _markov_stop_weight())
                marker_gen, _delta = _score_convergence_generation(scores, _markov_threshold())
                title = f"{codon} stop events - exact probability weights"
                integer_values = False
            draw_stop_event_chart(cv, new_stops, cumulative, title,
                                  integer_values=integer_values,
                                  marker_gen=marker_gen)

        c_i_stop = self._scroll_chart(parent, _render_i_stop,
                                      height=220, min_w=900, min_h=300)

        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))
        tk.Label(parent,
                 text="Compare two starting codons — compact category tracking:",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,2))
        self._legend(parent,
            "In User or Preset mode, compare two exact starting codons under the "
            "same probability setting. Each side uses the selected Display mode.",
            bg="#E8EEF8")
        cmp_cod_row = tk.Frame(parent, bg=BG_PANEL)
        cmp_cod_row.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(cmp_cod_row, text="Codon A:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        cmp_codon_a_var = tk.StringVar(value=i_codon_var.get())
        cmp_codon_a_menu = ttk.Combobox(cmp_cod_row, textvariable=cmp_codon_a_var,
                                        state="readonly", values=VALID_CODONS,
                                        font=("Helvetica",10), width=8)
        cmp_codon_a_menu.pack(side="left", padx=(6,12))
        tk.Label(cmp_cod_row, text="Codon B:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        cmp_codon_b_var = tk.StringVar(value=VALID_CODONS[1] if len(VALID_CODONS) > 1 else VALID_CODONS[0])
        cmp_codon_b_menu = ttk.Combobox(cmp_cod_row, textvariable=cmp_codon_b_var,
                                        state="readonly", values=VALID_CODONS,
                                        font=("Helvetica",10), width=8)
        cmp_codon_b_menu.pack(side="left", padx=(6,12))
        cmp_cod_info = tk.Label(cmp_cod_row, text="", bg=BG_PANEL,
                                font=("Helvetica",8,"bold"), fg="#555")
        cmp_cod_info.pack(side="left")

        cmp_cod_panes = tk.Frame(parent, bg=BG_PANEL)
        cmp_cod_panes.pack(fill="both", expand=True, padx=4, pady=(0,6))
        cmp_cod_left = tk.Frame(cmp_cod_panes, bg=BG_PANEL, relief="solid", bd=1)
        cmp_cod_left.pack(side="left", fill="both", expand=True, padx=(0,3))
        cmp_cod_right = tk.Frame(cmp_cod_panes, bg=BG_PANEL, relief="solid", bd=1)
        cmp_cod_right.pack(side="left", fill="both", expand=True, padx=(3,0))
        tk.Label(cmp_cod_left, text="Codon A", bg="#E6F1FB", fg=ACCENT,
                 font=("Helvetica",9,"bold")).pack(fill="x")
        tk.Label(cmp_cod_right, text="Codon B", bg="#EAF3DE", fg="#3B6D11",
                 font=("Helvetica",9,"bold")).pack(fill="x")

        def _render_compact_codon(cv, codon, panel_label):
            sampled_mode = i_spot_mode_var.get() == "Sampled copies"
            aa = CODON_TABLE.get(codon, "?")
            if sampled_mode:
                full_series, n_sampled = _sampled_codon_series(codon)
                series = _category_only_series(full_series)
                marker_gen, note = _sampled_no_more_change(codon)
                if not n_sampled:
                    cv.delete("all")
                    cv.create_text(cv.winfo_width()//2, cv.winfo_height()//2,
                                   text=f"No sampled copies for {codon}",
                                   fill="#aaa", font=("Helvetica",10))
                    return
                title = f"{panel_label}: {codon} ({aa}) counts | {note}, n={n_sampled}"
                draw_retention_lines(cv, series, title,
                                     color_map=cat_colors,
                                     highlight=cat_names.get(get_primary_group(aa)),
                                     show_share=False, integer_values=True,
                                     marker_gen=marker_gen,
                                     marker_label=f"gen {marker_gen}" if marker_gen else None,
                                     marker_color="#111")
            else:
                series = _codon_live_category_weight_series(codon)
                title = f"{panel_label}: {codon} ({aa}) exact surviving-category share"
                draw_retention_lines(cv, series, title,
                                     color_map=cat_colors,
                                     highlight=cat_names.get(get_primary_group(aa)),
                                     show_share=True)

        def _render_compact_stop(cv, codon):
            sampled_mode = i_spot_mode_var.get() == "Sampled copies"
            if sampled_mode:
                full_series, _n_sampled = _sampled_codon_series(codon)
                new_stops, cumulative = _stop_arrays_from_series(full_series)
                marker_gen, _note = _sampled_no_more_change(codon)
                draw_stop_event_chart(cv, new_stops, cumulative,
                                      f"{codon} stops", integer_values=True,
                                      marker_gen=marker_gen)
            else:
                new_stops = [
                    pstop_codon[g].get(codon, 0.0) if g < len(pstop_codon) else 0.0
                    for g in range(N)
                ]
                cumulative = []
                running = 0.0
                for val in new_stops:
                    running += val
                    cumulative.append(running)
                draw_stop_event_chart(cv, new_stops, cumulative,
                                      f"{codon} stops", integer_values=False)

        cmp_a_cat = self._scroll_chart(cmp_cod_left,
            lambda cv: _render_compact_codon(cv, cmp_codon_a_var.get(), "A"),
            height=300, min_w=620, min_h=360)
        cmp_a_stop = self._scroll_chart(cmp_cod_left,
            lambda cv: _render_compact_stop(cv, cmp_codon_a_var.get()),
            height=150, min_w=560, min_h=190)
        cmp_b_cat = self._scroll_chart(cmp_cod_right,
            lambda cv: _render_compact_codon(cv, cmp_codon_b_var.get(), "B"),
            height=300, min_w=620, min_h=360)
        cmp_b_stop = self._scroll_chart(cmp_cod_right,
            lambda cv: _render_compact_stop(cv, cmp_codon_b_var.get()),
            height=150, min_w=560, min_h=190)

        def _refresh_codon_compare(ev=None):
            a = cmp_codon_a_var.get(); b = cmp_codon_b_var.get()
            cmp_cod_info.config(text=f"{a} vs {b} | {i_spot_mode_var.get()}")
            _render_compact_codon(cmp_a_cat, a, "A")
            _render_compact_stop(cmp_a_stop, a)
            _render_compact_codon(cmp_b_cat, b, "B")
            _render_compact_stop(cmp_b_stop, b)

        tk.Label(parent,
                 text="No more category change — generation for each starting codon:",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(6,2))
        self._legend(parent,
            "Default sampled mode uses integer copy counts. A codon reaches "
            "'no more change' at the first generation where all live category "
            "counts stay exactly the same for the rest of the run. If all copies "
            "hit stop, the row is labeled all stopped. Stops do not decide this "
            "metric.",
            bg="#E8EEF8")
        i_markov_row = tk.Frame(parent, bg=BG_PANEL)
        i_markov_row.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(i_markov_row, text="Exact threshold:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        i_markov_thresh_var = tk.StringVar(value="0.0001")
        i_markov_thresh_entry = tk.Entry(i_markov_row,
                                         textvariable=i_markov_thresh_var,
                                         width=10, font=("Courier",10))
        i_markov_thresh_entry.pack(side="left", padx=(6,12))
        i_markov_stop_weight_var = tk.StringVar(value="0.0")
        tk.Label(i_markov_row, text="Data:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        i_markov_data_var = tk.StringVar(value="Sampled copies")
        i_markov_data_menu = ttk.Combobox(
            i_markov_row, textvariable=i_markov_data_var, state="readonly",
            values=["Sampled copies", "Exact probability"],
            font=("Helvetica",10), width=16)
        i_markov_data_menu.pack(side="left", padx=(6,12))
        tk.Label(i_markov_row, text="Sort:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        i_markov_sort_var = tk.StringVar(value="No more change")
        i_markov_sort_menu = ttk.Combobox(
            i_markov_row, textvariable=i_markov_sort_var, state="readonly",
            values=["No more change", "Codon", "AA", "Category"],
            font=("Helvetica",10), width=16)
        i_markov_sort_menu.pack(side="left", padx=(6,12))
        i_markov_status = tk.Label(i_markov_row, text="", bg=BG_PANEL,
                                   font=("Helvetica",8,"bold"), fg="#555")
        i_markov_status.pack(side="left", padx=(0,0))

        def _markov_threshold():
            try:
                val = float(i_markov_thresh_var.get())
                if val <= 0:
                    raise ValueError
                return val
            except (TypeError, ValueError):
                i_markov_status.config(text="Using 0.0001; threshold must be positive.")
                return 1e-4

        def _markov_stop_weight():
            return 0.0

        def _js_distance(p, q):
            """Jensen-Shannon distance for two already-normalized distributions."""
            def _kl(a, b):
                total = 0.0
                for av, bv in zip(a, b):
                    if av > 0 and bv > 0:
                        total += av * math.log2(av / bv)
                return total
            m = [(a + b) / 2.0 for a, b in zip(p, q)]
            return math.sqrt(max(0.0, 0.5 * _kl(p, m) + 0.5 * _kl(q, m)))

        def _codon_live_vector(codon, gen):
            live_by_cat = _codon_flow_summary(codon, gen)["cat_dist"]
            live_total = sum(live_by_cat.values())
            if live_total <= 0:
                return [0.0 for _ in cat_keys], 0.0
            return [live_by_cat.get(k, 0.0) / live_total for k in cat_keys], live_total

        def _codon_markov_scores(codon, stop_weight):
            scores = []
            series = _codon_live_category_weight_series(codon)
            for gen in range(1, N):
                max_delta = 0.0
                for vals in series.values():
                    prev = vals[gen-1] if gen-1 < len(vals) else 0.0
                    cur = vals[gen] if gen < len(vals) else 0.0
                    max_delta = max(max_delta, abs(cur - prev))
                scores.append(max_delta)
            return scores

        def _score_convergence_generation(scores, threshold):
            if not scores:
                return None, 0.0
            for idx, _score in enumerate(scores):
                future_max = max(scores[idx:] or [0.0])
                if future_max <= threshold:
                    return idx + 1, future_max
            return None, scores[-1]

        def _codon_markov_rows():
            threshold = _markov_threshold()
            stop_weight = _markov_stop_weight()
            sampled_mode = i_markov_data_var.get() == "Sampled copies"
            rows = []
            for codon in VALID_CODONS:
                aa = CODON_TABLE.get(codon, "?")
                start_cat = get_primary_group(aa)
                if sampled_mode:
                    gen, note = _sampled_no_more_change(codon)
                    delta = 0.0
                    scores = []
                else:
                    scores = _codon_markov_scores(codon, stop_weight)
                    gen, delta = _score_convergence_generation(scores, threshold)
                    note = f"max future change {delta:.5f}"
                rows.append({
                    "codon": codon,
                    "aa": aa,
                    "cat": start_cat,
                    "cat_name": cat_names.get(start_cat, start_cat),
                    "gen": gen,
                    "delta": delta,
                    "scores": scores,
                    "note": note,
                    "n_sampled": sum(1 for r in (sample_records or [])
                                     if r.get("start") == codon) if sampled_mode else None,
                })
            sort_by = i_markov_sort_var.get()
            if sort_by == "Codon":
                rows.sort(key=lambda r: r["codon"])
            elif sort_by == "AA":
                rows.sort(key=lambda r: (r["aa"], r["codon"]))
            elif sort_by == "Category":
                rows.sort(key=lambda r: (r["cat_name"], r["aa"], r["codon"]))
            else:
                rows.sort(key=lambda r: (r["gen"] is None,
                                         r["gen"] if r["gen"] is not None else N+1,
                                         r["codon"]))
            return rows, threshold, stop_weight, sampled_mode

        def _render_i_markov(cv):
            cv.delete("all")
            W = cv.winfo_width(); H = cv.winfo_height()
            if W < 100 or H < 100 or N < 1:
                return
            rows, threshold, stop_weight, sampled_mode = _codon_markov_rows()
            stable = [r for r in rows if r["gen"] is not None]
            if stable:
                min_gen = min(r["gen"] for r in stable)
                max_gen = max(r["gen"] for r in stable)
                i_markov_status.config(
                    text=f"{len(stable)}/{len(rows)} stable; min gen {min_gen}, max gen {max_gen}")
            else:
                i_markov_status.config(text=f"No codons stable below {threshold:g}.")

            pad_l = 126; pad_r = 220; pad_t = 42; pad_b = 42
            chart_w = max(80, W-pad_l-pad_r)
            chart_right = pad_l + chart_w
            n = len(rows)
            bar_h = max(11, min(22, (H-pad_t-pad_b)//max(n,1)-3))
            gap = max(1, (H-pad_t-pad_b-n*bar_h)//max(n+1,1))
            axis_max = max(1, N)
            data_label = "sampled copies" if sampled_mode else "exact probability"
            _chart_title(cv, W, 16,
                         f"No-more-category-change generation per codon - {data_label}{mode_badge}",
                         font=("Helvetica",10,"bold"))
            subtitle = ("Sampled: live category counts unchanged forever"
                        if sampled_mode else
                        f"Exact: future category-weight change < {threshold:g}")
            cv.create_text(pad_l, pad_t-16, text=subtitle,
                           anchor="w", font=("Helvetica",8,"bold"), fill="#555")
            cv.create_text(chart_right+10, pad_t-16,
                           text="Start property / status",
                           anchor="w", font=("Helvetica",8,"bold"), fill="#555")

            for i, row in enumerate(rows):
                y = pad_t + i*(bar_h+gap)
                codon = row["codon"]; aa = row["aa"]
                col = cat_colors_raw.get(row["cat"], "#888")
                label = f"{codon} {aa}"
                cv.create_text(pad_l-6, y+bar_h//2,
                               text=_fit_text(label, pad_l-12, 8, True),
                               anchor="e", font=("Courier",8,"bold"), fill=col)
                if row["gen"] is None:
                    bw = chart_w
                    fill = "#B0B0B0"
                    value_text = f"> {N}"
                    outline = "#777"
                else:
                    bw = max(2, int((row["gen"]/axis_max)*chart_w))
                    fill = col
                    value_text = f"gen {row['gen']}"
                    outline = ""
                cv.create_rectangle(pad_l, y, pad_l+bw, y+bar_h,
                                    fill=fill, outline=outline)
                _safe_value_label(cv, pad_l+bw, y+bar_h//2, value_text,
                                  "#444", pad_l, chart_right, bw,
                                  font=("Helvetica",8))
                if sampled_mode:
                    right_text = (f"{row['cat_name']}  {row.get('note', '')}  "
                                  f"n={row.get('n_sampled') or 0}")
                else:
                    right_text = f"{row['cat_name']}  {row.get('note', '')}"
                cv.create_text(chart_right+10, y+bar_h//2,
                               text=_fit_text(right_text, pad_r-18, 8),
                               anchor="w", font=("Helvetica",8), fill="#444")

            cv.create_line(pad_l, H-pad_b, chart_right, H-pad_b,
                           fill="#ccc", width=1)
            tick_count = min(axis_max, 8)
            for t in range(tick_count + 1):
                gen_val = round(t*axis_max/max(tick_count, 1))
                x = pad_l + int((gen_val/axis_max)*chart_w)
                cv.create_line(x, H-pad_b, x, H-pad_b+5, fill="#aaa")
                cv.create_text(x, H-pad_b+7, text=str(gen_val),
                               anchor="n", font=("Helvetica",7), fill="#777")

        c_i_markov = self._scroll_chart(parent, _render_i_markov,
                                        height=430, min_w=1100, min_h=1320)

        i_markov_tbl_f = tk.Frame(parent, bg=BG_PANEL, height=260)
        i_markov_tbl_f.pack(fill="both", expand=True, padx=6, pady=(0,6))
        i_markov_tbl_f.pack_propagate(False)
        i_markov_vsb = tk.Scrollbar(i_markov_tbl_f)
        i_markov_vsb.pack(side="right", fill="y")
        i_markov_hsb = tk.Scrollbar(i_markov_tbl_f, orient="horizontal")
        i_markov_hsb.pack(side="bottom", fill="x")
        i_markov_cols = ["codon", "aa", "category", "no_more_change", "status", "copies"]
        i_markov_tv = ttk.Treeview(i_markov_tbl_f, columns=i_markov_cols,
                                   show="headings", height=8,
                                   yscrollcommand=i_markov_vsb.set,
                                   xscrollcommand=i_markov_hsb.set)
        i_markov_vsb.config(command=i_markov_tv.yview)
        i_markov_hsb.config(command=i_markov_tv.xview)
        i_markov_tv.pack(fill="both", expand=True)
        for cid, head, width, anchor in [
            ("codon", "Start codon", 95, "center"),
            ("aa", "AA", 70, "center"),
            ("category", "Start category", 150, "center"),
            ("no_more_change", "No more change gen", 140, "center"),
            ("status", "Status", 240, "w"),
            ("copies", "Copies", 80, "center"),
        ]:
            i_markov_tv.heading(cid, text=head,
                                command=lambda c=cid: self._sort_table(i_markov_tv, c, False))
            i_markov_tv.column(cid, width=width, anchor=anchor)
        i_markov_tv.tag_configure("stopped", background="#FDEDEC", foreground="#A32D2D")
        i_markov_tv.tag_configure("stable", background="#D5F5E3")
        i_markov_tv.tag_configure("late", background="#FEF9E7")

        def _refresh_i_markov_table():
            for item in i_markov_tv.get_children():
                i_markov_tv.delete(item)
            rows, _threshold, _stop_weight, sampled_mode = _codon_markov_rows()
            for row in rows:
                gen_txt = f"{row['gen']}" if row["gen"] is not None else f"> {N}"
                note = row.get("note", "")
                if sampled_mode:
                    copies_txt = row.get("n_sampled") or 0
                else:
                    copies_txt = "exact"
                tag = "stopped" if note == "all stopped" else (
                    "stable" if row["gen"] is not None and row["gen"] <= max(1, N//2)
                    else "late")
                i_markov_tv.insert("", "end", values=[
                    row["codon"], row["aa"], row["cat_name"],
                    gen_txt, note, copies_txt,
                ], tags=(tag,))

        def _refresh_i(ev=None):
            _render_i_chart(c_i)
            _refresh_i_tbl()

        i_cat_menu.bind("<<ComboboxSelected>>", _refresh_i)
        i_aa_menu.bind("<<ComboboxSelected>>", _refresh_i)
        i_sort_menu.bind("<<ComboboxSelected>>", _refresh_i)
        i_gen_spin.config(command=_refresh_i); i_gen_spin.bind("<Return>", _refresh_i)
        def _refresh_i_selected(ev=None):
            self.after_idle(lambda: (
                _render_i_destination_hist(c_i_dest),
                _render_i_spot(c_i_spot),
                _render_i_stop(c_i_stop),
                _refresh_codon_compare()))
        i_codon_menu.bind("<<ComboboxSelected>>", _refresh_i_selected)
        i_spot_mode_menu.bind("<<ComboboxSelected>>", _refresh_i_selected)
        i_codon_var.trace_add("write", lambda *_: _refresh_i_selected())
        i_spot_mode_var.trace_add("write", lambda *_: _refresh_i_selected())
        cmp_codon_a_menu.bind("<<ComboboxSelected>>", _refresh_codon_compare)
        cmp_codon_b_menu.bind("<<ComboboxSelected>>", _refresh_codon_compare)
        cmp_codon_a_var.trace_add("write", lambda *_: _refresh_codon_compare())
        cmp_codon_b_var.trace_add("write", lambda *_: _refresh_codon_compare())
        i_dest_gen_spin.config(command=_refresh_i_selected)
        i_dest_gen_spin.bind("<Return>", _refresh_i_selected)
        def _refresh_i_markov(ev=None):
            _render_i_markov(c_i_markov)
            _refresh_i_markov_table()
            _render_i_spot(c_i_spot)
            _render_i_stop(c_i_stop)
        i_markov_sort_menu.bind("<<ComboboxSelected>>", _refresh_i_markov)
        i_markov_data_menu.bind("<<ComboboxSelected>>", _refresh_i_markov)
        i_markov_thresh_entry.bind("<Return>", _refresh_i_markov)
        tk.Button(i_markov_row, text="Update", command=_refresh_i_markov,
                  bg=ACCENT, fg="white", relief="flat",
                  font=("Helvetica",8,"bold")).pack(side="left", padx=(8,0))
        self.after(170, lambda: (_refresh_i(), _refresh_i_selected(),
                                 _refresh_codon_compare(), _refresh_i_markov()))

        # ── J. Requested summary tables ───────────────────────────────────
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))
        tk.Label(parent,
                 text="J.  Summary tables — start category to generation snapshot:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,2))

        self._legend(parent,
            "AA table: one row per starting amino acid, showing its start category "
            "and dominant destination category at the selected generation.",
            bg="#E8EEF8")
        j_aa_ctrl = tk.Frame(parent, bg=BG_PANEL)
        j_aa_ctrl.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(j_aa_ctrl, text="AA summary generation:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        j_aa_gen_var = tk.IntVar(value=N)
        j_aa_gen_spin = tk.Spinbox(j_aa_ctrl, from_=1, to=max(N,1),
                                   textvariable=j_aa_gen_var, width=5,
                                   font=("Courier",11))
        j_aa_gen_spin.pack(side="left", padx=(6,12))
        tk.Label(j_aa_ctrl, text="Sort:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        j_aa_sort_var = tk.StringVar(value="AA")
        j_aa_sort_menu = ttk.Combobox(j_aa_ctrl, textvariable=j_aa_sort_var,
                                      state="readonly",
                                      values=["AA", "End category", "Same category", "Same AA"],
                                      font=("Helvetica",10), width=15)
        j_aa_sort_menu.pack(side="left", padx=(6,0))

        j_aa_tbl_f = tk.Frame(parent, bg=BG_PANEL, height=230)
        j_aa_tbl_f.pack(fill="both", expand=True, padx=6, pady=(0,6))
        j_aa_tbl_f.pack_propagate(False)
        j_aa_vsb = tk.Scrollbar(j_aa_tbl_f); j_aa_vsb.pack(side="right", fill="y")
        j_aa_hsb = tk.Scrollbar(j_aa_tbl_f, orient="horizontal"); j_aa_hsb.pack(side="bottom", fill="x")
        j_aa_cols = ["aa","full","start_cat","end_cat","end_pct",
                     "same_cat","same_aa","top_aa","top_codons"]
        j_aa_tv = ttk.Treeview(j_aa_tbl_f, columns=j_aa_cols, show="headings",
                               height=8, yscrollcommand=j_aa_vsb.set,
                               xscrollcommand=j_aa_hsb.set)
        j_aa_vsb.config(command=j_aa_tv.yview); j_aa_hsb.config(command=j_aa_tv.xview)
        j_aa_tv.pack(fill="both", expand=True)
        for cid, head, width, anchor in [
            ("aa","AA",55,"center"), ("full","Full name",130,"w"),
            ("start_cat","Start category",135,"center"),
            ("end_cat","Dominant end category",155,"center"),
            ("end_pct","End cat %",80,"center"),
            ("same_cat","Same cat %",85,"center"),
            ("same_aa","Same AA %",80,"center"),
            ("top_aa","Top destination AAs",210,"w"),
            ("top_codons","Top destination codons",260,"w"),
        ]:
            j_aa_tv.heading(cid, text=head,
                            command=lambda c=cid: self._sort_table(j_aa_tv, c, False))
            j_aa_tv.column(cid, width=width, anchor=anchor)
        j_aa_tv.tag_configure("hi", background="#D5F5E3")
        j_aa_tv.tag_configure("med", background="#FEF9E7")
        j_aa_tv.tag_configure("lo", background="#FDEDEC")

        def _refresh_j_aa(ev=None):
            for item in j_aa_tv.get_children():
                j_aa_tv.delete(item)
            gen = min(j_aa_gen_var.get()-1, N-1)
            rows = []
            for aa in ALL_AAS:
                row = _aa_flow_summary(aa, gen)
                total = row["total"]
                end_cat = max(cat_keys, key=lambda k: row["cat_dist"].get(k, 0.0))
                end_pct = row["cat_dist"].get(end_cat, 0.0) / total
                row["end_cat"] = end_cat
                row["end_pct"] = end_pct
                rows.append(row)
            sort_by = j_aa_sort_var.get()
            if sort_by == "End category":
                rows.sort(key=lambda r: (cat_names[r["end_cat"]], r["aa"]))
            elif sort_by == "Same category":
                rows.sort(key=lambda r: (-r["same_cat"], r["aa"]))
            elif sort_by == "Same AA":
                rows.sort(key=lambda r: (-r["same_aa"], r["aa"]))
            else:
                rows.sort(key=lambda r: r["aa"])
            for row in rows:
                aa = row["aa"]; total = row["total"]
                vals = [
                    aa, AA_FULL.get(aa, aa), cat_names[row["start_cat"]],
                    cat_names[row["end_cat"]], f"{100*row['end_pct']:.1f}%",
                    f"{100*row['same_cat']:.1f}%", f"{100*row['same_aa']:.1f}%",
                    _pct_list(row["aa_dist"], total, 5),
                    _pct_list(collections.Counter(row["codon_dist"]), total, 5)
                    or "(codon-level data unavailable)",
                ]
                sp = row["same_cat"]
                tag = "hi" if sp >= 0.60 else ("med" if sp >= 0.30 else "lo")
                j_aa_tv.insert("", "end", values=vals, tags=(tag,))

        j_aa_gen_spin.config(command=_refresh_j_aa)
        j_aa_gen_spin.bind("<Return>", _refresh_j_aa)
        j_aa_sort_menu.bind("<<ComboboxSelected>>", _refresh_j_aa)

        self._legend(parent,
            "Codon-copy table: choose a starting codon and generation. Each row is "
            "one sampled duplicate/copy of that exact codon. If that copy has hit "
            "a stop by the selected generation, the row says so.",
            bg="#E8EEF8")
        j_copy_ctrl = tk.Frame(parent, bg=BG_PANEL)
        j_copy_ctrl.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(j_copy_ctrl, text="Start codon:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        j_copy_codon_var = tk.StringVar(value=VALID_CODONS[0])
        j_copy_codon_menu = ttk.Combobox(j_copy_ctrl, textvariable=j_copy_codon_var,
                                         state="readonly", values=VALID_CODONS,
                                         font=("Helvetica",10), width=8)
        j_copy_codon_menu.pack(side="left", padx=(6,12))
        tk.Label(j_copy_ctrl, text="Snapshot generation:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        j_copy_gen_var = tk.IntVar(value=N)
        j_copy_gen_spin = tk.Spinbox(j_copy_ctrl, from_=1, to=max(N,1),
                                     textvariable=j_copy_gen_var, width=5,
                                     font=("Courier",11))
        j_copy_gen_spin.pack(side="left", padx=(6,12))
        j_copy_info = tk.Label(j_copy_ctrl, text="", bg=BG_PANEL,
                               font=("Helvetica",8), fg="#555")
        j_copy_info.pack(side="left")

        j_copy_tbl_f = tk.Frame(parent, bg=BG_PANEL, height=280)
        j_copy_tbl_f.pack(fill="both", expand=True, padx=6, pady=(0,6))
        j_copy_tbl_f.pack_propagate(False)
        j_copy_vsb = tk.Scrollbar(j_copy_tbl_f); j_copy_vsb.pack(side="right", fill="y")
        j_copy_hsb = tk.Scrollbar(j_copy_tbl_f, orient="horizontal"); j_copy_hsb.pack(side="bottom", fill="x")
        j_copy_cols = ["copy","start","start_aa","start_cat","gen",
                       "current","current_aa","current_cat","status",
                       "final","final_aa","stop_gen"]
        j_copy_tv = ttk.Treeview(j_copy_tbl_f, columns=j_copy_cols, show="headings",
                                 height=10, yscrollcommand=j_copy_vsb.set,
                                 xscrollcommand=j_copy_hsb.set)
        j_copy_vsb.config(command=j_copy_tv.yview); j_copy_hsb.config(command=j_copy_tv.xview)
        j_copy_tv.pack(fill="both", expand=True)
        for cid, head, width, anchor in [
            ("copy","Copy #",65,"center"), ("start","Start codon",90,"center"),
            ("start_aa","Start AA",70,"center"), ("start_cat","Start category",135,"center"),
            ("gen","Gen",50,"center"), ("current","Codon at gen",95,"center"),
            ("current_aa","AA at gen",75,"center"), ("current_cat","Category at gen",135,"center"),
            ("status","Status",145,"center"), ("final","Final codon",90,"center"),
            ("final_aa","Final AA",70,"center"), ("stop_gen","Stop gen",70,"center"),
        ]:
            j_copy_tv.heading(cid, text=head,
                              command=lambda c=cid: self._sort_table(j_copy_tv, c, False))
            j_copy_tv.column(cid, width=width, anchor=anchor)
        j_copy_tv.tag_configure("stop", background="#FDEDEC", foreground="#A32D2D")
        j_copy_tv.tag_configure("same", background="#D5F5E3")
        j_copy_tv.tag_configure("move", background="#FEF9E7")
        j_copy_tv.tag_configure("odd", background="#FAFAFA")

        def _record_at_generation(record, gen_num):
            path = record.get("path") or [record.get("start"), record.get("final")]
            stop_gen = record.get("stop_gen")
            if record.get("hit_stop") and stop_gen is not None and gen_num >= stop_gen:
                codon = record.get("final")
                return codon, "Stop", "Stop", f"hit stop at gen {stop_gen}"
            idx = min(gen_num, len(path)-1)
            codon = path[idx]
            aa = CODON_TABLE.get(codon, "Stop")
            cat = "Stop" if aa == "Stop" else cat_names.get(get_primary_group(aa), "?")
            return codon, aa, cat, "live"

        def _refresh_j_copy(ev=None):
            for item in j_copy_tv.get_children():
                j_copy_tv.delete(item)
            records_for_table = sample_records or []
            sc = j_copy_codon_var.get()
            gen_num = min(max(j_copy_gen_var.get(), 1), N)
            rows = [r for r in records_for_table if r.get("start") == sc]
            stopped_by_gen = sum(1 for r in rows
                                 if r.get("hit_stop") and r.get("stop_gen") is not None
                                 and r["stop_gen"] <= gen_num)
            j_copy_info.config(
                text=f"{len(rows)} sampled duplicate(s); {stopped_by_gen} stopped by gen {gen_num}")
            if not rows:
                j_copy_tv.insert("", "end",
                                 values=["-", sc, CODON_TABLE.get(sc,"?"),
                                         cat_names.get(get_primary_group(CODON_TABLE.get(sc,"?")), "?"),
                                         gen_num, "-", "-", "-", "no sampled copies", "-", "-", "-"],
                                 tags=("odd",))
                return
            for i, r in enumerate(rows):
                cur_codon, cur_aa, cur_cat, status = _record_at_generation(r, gen_num)
                saa = r.get("start_aa", CODON_TABLE.get(sc, "?"))
                start_cat_name = cat_names.get(get_primary_group(saa), "?")
                if status.startswith("hit stop"):
                    tag = "stop"
                elif cur_codon == sc:
                    tag = "same"
                elif cur_aa == saa:
                    tag = "move"
                else:
                    tag = "odd" if i % 2 else ""
                j_copy_tv.insert("", "end", values=[
                    r.get("copy", i+1), sc, saa, start_cat_name, gen_num,
                    cur_codon, cur_aa, cur_cat, status,
                    r.get("final", "-"), r.get("final_aa", "-"),
                    r.get("stop_gen") if r.get("hit_stop") else "-",
                ], tags=(tag,))

        j_copy_codon_menu.bind("<<ComboboxSelected>>", _refresh_j_copy)
        j_copy_gen_spin.config(command=_refresh_j_copy)
        j_copy_gen_spin.bind("<Return>", _refresh_j_copy)
        self.after(190, lambda: (_refresh_j_aa(), _refresh_j_copy()))

    def _draw_retention_overview(self, canvas, pgc, cat_keys, cat_names,
                                 cat_colors_raw, N, mode_badge):
        """Bar chart: final-generation self-retention share per start category.
        Each bar is an independent 0-1 share (not normalised against the others)."""
        canvas.delete("all")
        W = canvas.winfo_width(); H = canvas.winfo_height()
        if W < 50 or H < 50 or N < 1:
            return
        gen = N - 1
        rows = []
        for k in cat_keys:
            d = pgc[gen].get(k, {})
            tot = sum(d.values())
            share = (d.get(k, 0)/tot) if tot > 0 else 0.0
            rows.append((cat_names[k], share, cat_colors_raw[k]))
        rows.sort(key=lambda r: -r[1])

        pad_l=150; pad_r=70; pad_t=36; pad_b=28
        n = len(rows)
        bar_h = max(14, min(34, (H-pad_t-pad_b)//max(n,1)-6))
        gap = max(4, (H-pad_t-pad_b-n*bar_h)//max(n+1,1))
        chart_w = W-pad_l-pad_r

        _chart_title(canvas, W, 16,
                     f"Self-retention at gen {N}{mode_badge}  "
                     "[share staying in same category]")
        for i,(name,share,col) in enumerate(rows):
            y = pad_t + i*(bar_h+gap)
            bw = max(2, int(share*chart_w))
            canvas.create_rectangle(pad_l, y, pad_l+bw, y+bar_h, fill=col, outline="")
            canvas.create_text(pad_l-6, y+bar_h//2,
                               text=_fit_text(name, pad_l-12, 9), anchor="e",
                               font=("Helvetica",9), fill="#333")
            _safe_value_label(canvas, pad_l+bw, y+bar_h//2, f"{share*100:.1f}%",
                              "#444", pad_l, pad_l+chart_w, bw,
                              font=("Helvetica",8,"bold"))
        # Axis 0-100%
        canvas.create_line(pad_l, H-pad_b, pad_l+chart_w, H-pad_b, fill="#ccc")
        for frac in [0,0.25,0.5,0.75,1.0]:
            tx = pad_l+int(frac*chart_w)
            canvas.create_line(tx, H-pad_b, tx, H-pad_b+4, fill="#bbb")
            canvas.create_text(tx, H-pad_b+6, text=f"{int(frac*100)}%",
                               anchor="n", font=("Helvetica",7), fill="#999")

    # ─────────────────────────────────────────────────────────────────────
    # NEW: Per-starting-codon map tab
    # ─────────────────────────────────────────────────────────────────────

    def _build_codon_map_tab(self, parent, start_to_fin, n_gen,
                              label="User", color_hint=USER_COLOR):
        """
        Three sub-views in this tab:
          1. Heatmap grid (start × final codon)
          2. Per-codon bar charts — select a start codon, see its final distribution
          3. Top-N final codons for each start (ranked list)
        """
        self._header(parent,
                     f"Start codon → Final codon map  [{label}]",
                     f"Gen {n_gen}.  Select a starting codon to see its final distribution.")

        # ── Per-codon detail ──────────────────────────────────────────────
        tk.Label(parent, text="Per-starting-codon final distribution — select a codon:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=10, pady=(2,4))

        detail_row = tk.Frame(parent, bg=BG_PANEL)
        detail_row.pack(fill="both", expand=True, padx=6, pady=(0,6))

        # Left: listbox
        lf = tk.Frame(detail_row, bg=BG_PANEL, width=130)
        lf.pack(side="left", fill="y"); lf.pack_propagate(False)
        sb_lf = tk.Scrollbar(lf); sb_lf.pack(side="right", fill="y")
        lb = tk.Listbox(lf, yscrollcommand=sb_lf.set, font=("Courier",10),
                        selectmode="single", bg="white",
                        selectbackground=color_hint, selectforeground="white",
                        relief="solid", bd=1)
        lb.pack(fill="both", expand=True)
        sb_lf.config(command=lb.yview)
        for c in VALID_CODONS:
            aa = CODON_TABLE.get(c,"?")
            lb.insert("end", f"{c}  {aa}")

        # Right: bar chart + ranked table
        rf = tk.Frame(detail_row, bg=BG_PANEL)
        rf.pack(side="left", fill="both", expand=True, padx=(6,0))

        self._map_info_lbl = tk.Label(rf,
            text="Select a codon on the left to see its final distribution.",
            bg=BG_PANEL, font=("Helvetica",9), fg="#888")
        self._map_info_lbl.pack(anchor="w", padx=6, pady=(2,2))

        c_detail = self._scroll_chart(rf,
            lambda cv: on_select_codon() if lb.curselection() else None,
            height=280, min_w=680, min_h=520)

        # Ranked table
        tk.Label(rf, text="Top final codons & AAs:",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg="#333"
                 ).pack(anchor="w", padx=6)
        tbl_f = tk.Frame(rf, bg=BG_PANEL, height=120)
        tbl_f.pack(fill="x", padx=4, pady=(0,6)); tbl_f.pack_propagate(False)
        vsb_t = tk.Scrollbar(tbl_f); vsb_t.pack(side="right", fill="y")
        tv = ttk.Treeview(tbl_f,
             columns=["rank","final_codon","final_aa","prob","prob_pct"],
             show="headings", height=5, yscrollcommand=vsb_t.set)
        vsb_t.config(command=tv.yview)
        tv.pack(fill="both", expand=True)
        for cid,head,w in [("rank","#",40),("final_codon","Final codon",100),
                            ("final_aa","Final AA",90),("prob","Probability",110),
                            ("prob_pct","Prob. %",80)]:
            tv.heading(cid, text=head); tv.column(cid, width=w, anchor="center")
        tv.tag_configure("odd", background="#F8F8F8")

        _nv_map = tk.BooleanVar(value=False)
        norm_bar = tk.Frame(parent, bg="#F5F5F0", relief="solid", bd=1)
        norm_bar.pack(fill="x", padx=6, pady=(0,4))

        def on_select_codon(ev=None):
            sel = lb.curselection()
            if not sel: return
            sc  = VALID_CODONS[sel[0]]
            saa = CODON_TABLE.get(sc,"?")
            fin = start_to_fin.get(sc, collections.Counter())
            tot = sum(fin.values()) or 1
            # Expected distance from start: probability-weighted mean Hamming
            # distance (# base differences, 0–3) between start codon and each
            # surviving final codon.
            def _hamming(a, b):
                return sum(1 for x, y in zip(a, b) if x != y)
            exp_dist = sum(w * _hamming(sc, fc) for fc, w in fin.items()) / tot
            self._map_info_lbl.config(
                text=f"Start: {sc} ({saa})  →  {len(fin)} final codons reached. "
                     f"Surviving probability: {tot:.4f}   "
                     f"│  Expected distance from start: {exp_dist:.3f} base(s)")
            # Bar chart of final AAs
            aa_dist = collections.Counter()
            for fc, w in fin.items():
                aa_dist[CODON_TABLE.get(fc,"?")] += w
            draw_bar_chart(c_detail, aa_dist,
                           f"{sc}→final AAs  [{label}]",
                           color_map=AA_COLOR_MAP, top_n=21,
                           normalize=_nv_map.get(),
                           bar_color_override=None)
            # Ranked table
            for item in tv.get_children(): tv.delete(item)
            for rank,(fc,w) in enumerate(sorted(fin.items(),key=lambda x:-x[1]),1):
                faa = CODON_TABLE.get(fc,"?")
                tag = "odd" if rank%2 else ""
                tv.insert("","end",
                    values=[rank, fc, faa, f"{w/tot:.5f}", f"{100*w/tot:.2f}%"],
                    tags=(tag,))

        _nv_map.trace_add("write", lambda *_: on_select_codon())

        # Build norm toggle inline in norm_bar
        tk.Label(norm_bar, text="Display:", bg="#F5F5F0",
                 font=("Helvetica",8,"bold")).pack(side="left", padx=(8,4))
        tk.Radiobutton(norm_bar, text="Probability (0–1)", variable=_nv_map, value=False,
                       bg="#F5F5F0", font=("Helvetica",8),
                       command=lambda: on_select_codon() if lb.curselection() else None
                       ).pack(side="left")
        tk.Radiobutton(norm_bar, text="Percentage (%)", variable=_nv_map, value=True,
                       bg="#F5F5F0", font=("Helvetica",8),
                       command=lambda: on_select_codon() if lb.curselection() else None
                       ).pack(side="left")

        lb.bind("<<ListboxSelect>>", on_select_codon)
        lb.selection_set(0)
        self.after(150, lambda: on_select_codon())

    # ─────────────────────────────────────────────────────────────────────
    # Comparison tabs
    # ─────────────────────────────────────────────────────────────────────

    def _populate_compare(self):
        if self._res_user is None or self._res_preset is None: return

        sim_u, exp_u = self._res_user
        sim_p, exp_p = self._res_preset
        n_gen = self._params["n_generations"]

        (enc_cod_u, enc_aa_u, enc_cnt_u, enc_aa_cnt_u,
         fin_cod_u, fin_aa_u, per_gen_aa_u, s2f_u, stats_u, stop_u,
         track_u) = sim_u
        (enc_cod_p, enc_aa_p, enc_cnt_p, enc_aa_cnt_p,
         fin_cod_p, fin_aa_p, per_gen_aa_p, s2f_p, stats_p, stop_p,
         track_p) = sim_p

        # ── helper: codon-count filter for compare charts ─────────────────
        def _filter_by_deg(counter, deg_val):
            """Return a filtered counter keeping only AAs with deg_val codons."""
            if deg_val == "all": return counter
            keep = set(CODON_COUNT_GROUPS.get(int(deg_val), []))
            return type(counter)({k: v for k,v in counter.items() if k in keep})

        def _deg_toolbar(parent, redraw_fn):
            """Adds a normalise toggle + codon-count filter bar. Returns (norm_var, deg_var)."""
            bar = tk.Frame(parent, bg="#F0F4FA", relief="solid", bd=1)
            bar.pack(fill="x", padx=6, pady=(2,4))
            nv = tk.BooleanVar(value=False)
            tk.Label(bar, text="Display:", bg="#F0F4FA",
                     font=("Helvetica",9,"bold")).pack(side="left", padx=(8,4))
            tk.Radiobutton(bar, text="Probability (0–1)", variable=nv, value=False,
                           bg="#F0F4FA", font=("Helvetica",9),
                           command=redraw_fn).pack(side="left")
            tk.Radiobutton(bar, text="Percentage (%)", variable=nv, value=True,
                           bg="#F0F4FA", font=("Helvetica",9),
                           command=redraw_fn).pack(side="left", padx=(0,16))
            tk.Label(bar, text="# codons:", bg="#F0F4FA",
                     font=("Helvetica",9,"bold")).pack(side="left", padx=(0,4))
            dv = tk.StringVar(value="all")
            for lbl,val,bg in [("All","all",BG_PANEL),("1","1",CODON_COUNT_BG[1]),
                                ("2","2",CODON_COUNT_BG[2]),("3","3",CODON_COUNT_BG[3]),
                                ("4","4",CODON_COUNT_BG[4]),("6","6",CODON_COUNT_BG[6])]:
                tk.Radiobutton(bar, text=lbl, variable=dv, value=val, bg=bg,
                               font=("Helvetica",9), command=redraw_fn).pack(side="left", padx=1)
            return nv, dv

        # ═══════════════════════════════════════════════════════════════════
        # TAB 1 — ⚖ Final AAs
        # ═══════════════════════════════════════════════════════════════════
        self._clear("compare_fin")
        raw = self._tabs["compare_fin"]
        outer, f = make_scrollable(raw, bg=BG_PANEL)
        outer.pack(fill="both", expand=True)
        self._header(f, f"⚖  Final AA comparison — User vs Preset  (gen {n_gen})")
        self._legend(f,
            "Paired bars per amino acid: top bar = User probability (blue), "
            "bottom bar = Preset probability (purple). Sorted by combined weight.")

        def _build_fin_aa_compare(frm):
            _nv = tk.BooleanVar(value=False)
            _dv = tk.StringVar(value="all")
            def _draw(cv_local):
                fu = _filter_by_deg(fin_aa_u, _dv.get())
                fp = _filter_by_deg(fin_aa_p, _dv.get())
                draw_comparison_bar_chart(cv_local, fu, fp,
                    label_a="User", label_b="Preset",
                    color_a=USER_COLOR, color_b=PRESET_COLOR,
                    title=f"Final AA — User vs Preset (gen {n_gen})",
                    top_n=21, normalize=_nv.get())
            def _rdr(ev=None):
                _draw(cv)
            _nv2, _dv2 = _deg_toolbar(frm, _rdr)
            _nv = _nv2; _dv = _dv2
            cv = self._scroll_chart(frm, _draw, height=560,
                                    min_w=900, min_h=680)

        _nv_cmp, _dv_cmp = _deg_toolbar(f, lambda: None)  # placeholder, replaced below
        # rebuild with real redraw
        for w in f.winfo_children():  # remove placeholder toolbar
            if isinstance(w, tk.Frame) and w.cget("bg") == "#F0F4FA":
                w.destroy(); break

        def _rdr_cmp_cv(c_cmp):
            fu = _filter_by_deg(fin_aa_u, _dv_cmp.get())
            fp = _filter_by_deg(fin_aa_p, _dv_cmp.get())
            draw_comparison_bar_chart(c_cmp, fu, fp,
                label_a="User", label_b="Preset",
                color_a=USER_COLOR, color_b=PRESET_COLOR,
                title=f"Final AA — User vs Preset (gen {n_gen})",
                top_n=21, normalize=_nv_cmp.get())
        def _rdr_cmp(ev=None): _rdr_cmp_cv(_c_cmp)

        _nv_cmp, _dv_cmp = _deg_toolbar(f, _rdr_cmp)

        # pop-out button
        tk.Button(f, text="⧆ Pop out", command=lambda: self._popout_window(
            "Final AA Comparison", _build_fin_aa_compare),
            relief="solid", bd=1, padx=6, pady=2,
            font=("Helvetica",8), bg="#EAF3DE", fg="#3B6D11", cursor="hand2"
            ).pack(anchor="e", padx=8, pady=(0,2))

        _c_cmp = self._scroll_chart(f, _rdr_cmp_cv, height=560, min_w=720, min_h=620)

        # Difference table
        self._legend(f, "Table below: sorted by absolute difference. "
                "Blue rows = User favours this AA; purple rows = Preset favours it.",
                bg="#EEF4FF")
        tk.Label(f, text="Probability difference (User – Preset) per AA:",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg="#333"
                 ).pack(anchor="w", padx=8, pady=(4,1))
        tbl_f = tk.Frame(f, bg=BG_PANEL, height=180)
        tbl_f.pack(fill="x", padx=6, pady=(0,8)); tbl_f.pack_propagate(False)
        vsb_d = tk.Scrollbar(tbl_f); vsb_d.pack(side="right", fill="y")
        tv_d  = ttk.Treeview(tbl_f,
            columns=["aa","full","n_cod","user_p","preset_p","diff","favors"],
            show="headings", yscrollcommand=vsb_d.set)
        vsb_d.config(command=tv_d.yview); tv_d.pack(fill="both", expand=True)
        tv_d.tag_configure("user_fav",   background="#D6EAF8")
        tv_d.tag_configure("preset_fav", background="#E8DAEF")
        tv_d.tag_configure("neutral",    background="#F8F8F8")
        for cid,head,w in [("aa","AA",55),("full","Full name",140),("n_cod","# codons",75),
                            ("user_p","User prob.",100),("preset_p","Preset prob.",100),
                            ("diff","Diff",85),("favors","Favors",80)]:
            tv_d.heading(cid, text=head,
                         command=lambda c=cid: self._sort_table(tv_d,c,False))
            tv_d.column(cid, width=w, anchor="center")
        tu = sum(fin_aa_u.values()) or 1; tp2 = sum(fin_aa_p.values()) or 1
        all_aa = sorted(set(list(fin_aa_u.keys())+list(fin_aa_p.keys())))
        diffs = [(aa, fin_aa_u.get(aa,0)/tu, fin_aa_p.get(aa,0)/tp2) for aa in all_aa]
        diffs.sort(key=lambda x: -abs(x[1]-x[2]))
        for aa, pu, pp in diffs:
            diff = pu-pp
            tag = "user_fav" if diff>0.001 else ("preset_fav" if diff<-0.001 else "neutral")
            favors = "User" if diff>0.001 else ("Preset" if diff<-0.001 else "Equal")
            tv_d.insert("","end", values=[aa, AA_FULL.get(aa,aa),
                CODON_COUNT_MAP.get(aa,"?"),
                f"{pu:.4f}", f"{pp:.4f}", f"{diff:+.4f}", favors], tags=(tag,))

        # ═══════════════════════════════════════════════════════════════════
        # TAB 2 — ⚖ Stop Codons
        # ═══════════════════════════════════════════════════════════════════
        self._clear("compare_stops")
        raw2 = self._tabs["compare_stops"]
        outer2, f2 = make_scrollable(raw2, bg=BG_PANEL)
        outer2.pack(fill="both", expand=True)
        self._header(f2, "⚖  Stop codon comparison — User vs Preset")
        self._legend(f2,
            "Shows total probability absorbed by stop codons for each model. "
            "Higher stop probability = more paths terminate early.")

        n_u = sum(stop_u["by_stop_codon"].values())
        n_p2 = sum(stop_p["by_stop_codon"].values())
        total_start = self._params["start_copies"] * len(VALID_CODONS)
        stop_prop_u = property_stop_counter(stop_u)
        stop_prop_p = property_stop_counter(stop_p)

        strip2 = tk.Frame(f2, bg="#FDEDEC", relief="solid", bd=1)
        strip2.pack(fill="x", padx=6, pady=(4,6))
        for i,(l,v) in enumerate([
            ("Start prob.", str(total_start)),
            ("User stop", f"{n_u:.3f}  ({100*n_u/total_start:.1f}%)"),
            ("Preset stop", f"{n_p2:.3f}  ({100*n_p2/total_start:.1f}%)")]):
            tk.Label(strip2,text=l,bg="#FDEDEC",font=("Helvetica",8,"bold"),fg="#A32D2D"
                     ).grid(row=0,column=i*2,padx=(12,2),pady=5)
            tk.Label(strip2,text=v,bg="#f5c6c6",font=("Courier",9,"bold"),fg="#A32D2D",
                     relief="solid",bd=1,padx=6).grid(row=0,column=i*2+1,padx=(0,10),pady=5)

        def _build_stops_compare(frm):
            _nv = tk.BooleanVar(value=False)
            def _draw1(c):
                draw_comparison_bar_chart(c, stop_u["by_stop_codon"], stop_p["by_stop_codon"],
                    label_a="User", label_b="Preset", color_a=USER_COLOR, color_b=PRESET_COLOR,
                    title="Stop codon (TAA/TAG/TGA) — User vs Preset", top_n=3, normalize=_nv.get())
            def _draw2(c):
                draw_comparison_bar_chart(c, stop_u["by_start_aa"], stop_p["by_start_aa"],
                    label_a="User", label_b="Preset", color_a=USER_COLOR, color_b=PRESET_COLOR,
                    title="Stop prob. by starting AA", top_n=21, normalize=_nv.get())
            def _drawp(c):
                draw_comparison_bar_chart(c, stop_prop_u, stop_prop_p,
                    label_a="User", label_b="Preset", color_a=USER_COLOR, color_b=PRESET_COLOR,
                    title="Stop prob. by starting property", top_n=len(PROPERTY_GROUPS),
                    normalize=_nv.get())
            def _rdr(ev=None):
                _draw1(cv1); _draw2(cv2); _drawp(cvp)
            nv2 = self._make_norm_toggle(frm, _rdr); _nv = nv2
            tk.Button(frm, text="ℹ Which stop codon was hit (TAA / TAG / TGA)",
                      bg="#FEF0E6", font=("Helvetica",8,"italic"), relief="flat").pack(anchor="w",padx=6)
            cv1 = self._scroll_chart(frm, _draw1, height=160,
                                     min_w=640, min_h=220)
            tk.Label(frm, text="ℹ Stop probability grouped by the starting amino acid",
                     bg="#FEF0E6", font=("Helvetica",8,"italic")).pack(anchor="w",padx=6)
            cv2 = self._scroll_chart(frm, _draw2, height=420,
                                     min_w=900, min_h=620)
            tk.Label(frm, text="ℹ Stop probability grouped by starting biochemical property",
                     bg="#FEF0E6", font=("Helvetica",8,"italic")).pack(anchor="w",padx=6)
            cvp = self._scroll_chart(frm, _drawp, height=260,
                                     min_w=720, min_h=320)
            self.after(80, _rdr)

        _nv_stp = self._make_norm_toggle(f2, lambda: None)

        def _draw_stp_cv(c_stp):
            draw_comparison_bar_chart(c_stp, stop_u["by_stop_codon"], stop_p["by_stop_codon"],
                label_a="User", label_b="Preset", color_a=USER_COLOR, color_b=PRESET_COLOR,
                title="Stop codon (TAA/TAG/TGA) — User vs Preset", top_n=3, normalize=_nv_stp.get())
        def _draw_saa_cv(c_saa):
            draw_comparison_bar_chart(c_saa, stop_u["by_start_aa"], stop_p["by_start_aa"],
                label_a="User", label_b="Preset", color_a=USER_COLOR, color_b=PRESET_COLOR,
                title="Stop prob. by starting AA", top_n=21, normalize=_nv_stp.get())
        def _draw_sprop_cv(c_prop):
            draw_comparison_bar_chart(c_prop, stop_prop_u, stop_prop_p,
                label_a="User", label_b="Preset", color_a=USER_COLOR, color_b=PRESET_COLOR,
                title="Stop prob. by starting property", top_n=len(PROPERTY_GROUPS),
                normalize=_nv_stp.get())
        def _rdr_stp(ev=None):
            _draw_stp_cv(c_stp); _draw_saa_cv(_c_saa); _draw_sprop_cv(_c_sprop)

        # redo toggle
        for w in f2.winfo_children():
            if isinstance(w, tk.Frame) and w.cget("bg") == "#F5F5F0":
                w.destroy(); break
        _nv_stp = self._make_norm_toggle(f2, _rdr_stp)

        tk.Button(f2, text="⧆ Pop out", command=lambda: self._popout_window(
            "Stop Codon Comparison", _build_stops_compare),
            relief="solid", bd=1, padx=6, pady=2,
            font=("Helvetica",8), bg="#EAF3DE", fg="#3B6D11", cursor="hand2"
            ).pack(anchor="e", padx=8, pady=(0,2))

        self._legend(f2, "Which of the 3 stop codons (TAA=ochre, TAG=amber, TGA=opal) "
                "was reached and with what probability.", bg="#FEF0E6")
        c_stp = self._scroll_chart(f2, _draw_stp_cv, height=160,
                                   min_w=640, min_h=220)

        self._legend(f2, "Stop probability grouped by the starting amino acid — "
                "which starting AAs are most 'dangerous' (adjacent to stop codons).", bg="#FEF0E6")
        _c_saa = self._scroll_chart(f2, _draw_saa_cv, height=440, min_w=720, min_h=560)

        self._legend(f2, "Stop probability grouped by starting biochemical property.", bg="#FEF0E6")
        _c_sprop = self._scroll_chart(f2, _draw_sprop_cv, height=280, min_w=680, min_h=300)

        # ── Survival comparison across generations ──
        tk.Frame(f2, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(6,4))
        self._legend(f2,
            "Survival curves overlaid: solid = surviving probability, dashed = number "
            "of distinct AAs still present. Blue = User, purple = Preset. "
            "Vertical marks show each model's half-life generation.", bg="#FEF0E6")
        surv_u = [sum(per_gen_aa_u[gg].values()) for gg in range(len(per_gen_aa_u))]
        aas_u  = [sum(1 for v in per_gen_aa_u[gg].values() if v > 0)
                  for gg in range(len(per_gen_aa_u))]
        surv_p = [sum(per_gen_aa_p[gg].values()) for gg in range(len(per_gen_aa_p))]
        aas_p  = [sum(1 for v in per_gen_aa_p[gg].values() if v > 0)
                  for gg in range(len(per_gen_aa_p))]
        def _draw_survc_cv(c_survc):
            draw_survival_compare(c_survc, surv_u, aas_u, surv_p, aas_p,
                                  start_u=total_start, start_p=total_start,
                                  title="Survival across generations — User vs Preset")
        self._scroll_chart(f2, _draw_survc_cv, height=340, min_w=760, min_h=340)

        # ═══════════════════════════════════════════════════════════════════
        # TAB 3 — ⚖ Categories  (property groups + codon degeneracy + start→end maps)
        # ═══════════════════════════════════════════════════════════════════
        self._clear("compare_cats")
        raw3 = self._tabs["compare_cats"]
        outer3, f3 = make_scrollable(raw3, bg=BG_PANEL)
        outer3.pack(fill="both", expand=True)
        self._header(f3, "⚖  Category comparison — User vs Preset")
        self._legend(f3,
            "Final probability grouped three ways: "
            "biochemical property | codon degeneracy | per-codon start→end map. "
            "Blue = User, Purple = Preset.")

        def _cat_totals(fin_aa):
            tot = collections.Counter()
            for aa, w in fin_aa.items():
                tot[get_primary_group(aa)] += w
            return tot

        def _deg_totals(fin_aa):
            tot = collections.Counter()
            for aa, w in fin_aa.items():
                n = get_codon_count(aa)
                tot[f"{n} codon{'s' if n>1 else ''}"] += w
            return tot

        # ── Section A: Property categories ──────────────────────────────
        sep_lbl = tk.Label(f3, text="A.  Biochemical property groups",
                 font=("Helvetica",10,"bold"), bg="#E6F1FB", fg=ACCENT, anchor="w",
                 relief="solid", bd=1, padx=8, pady=4)
        sep_lbl.pack(fill="x", padx=6, pady=(6,2))
        self._legend(f3, "Each bar group = one property class (Hydrophobic, Polar, etc.). "
                "Compares the total final probability landing in that class.", bg="#E8EEF8")

        def _build_prop_compare(frm):
            _nv = tk.BooleanVar(value=False)
            def _draw(cv_local):
                cat_u = _cat_totals(fin_aa_u)
                cat_p = _cat_totals(fin_aa_p)
                lmap  = {k: PROPERTY_GROUPS[k][0] for k in PROPERTY_GROUPS}
                cu = collections.Counter({lmap[k]:v for k,v in cat_u.items()})
                cp = collections.Counter({lmap[k]:v for k,v in cat_p.items()})
                draw_comparison_bar_chart(cv_local, cu, cp,
                    label_a="User", label_b="Preset", color_a=USER_COLOR, color_b=PRESET_COLOR,
                    title="Final prob. by AA property", top_n=10, normalize=_nv.get())
            def _rdr(ev=None):
                _draw(cv)
            nv2 = self._make_norm_toggle(frm, _rdr); _nv = nv2
            cv = self._scroll_chart(frm, _draw, height=280,
                                    min_w=720, min_h=340)

        _nv_prop = self._make_norm_toggle(f3, lambda: None)
        cat_u_d = _cat_totals(fin_aa_u); cat_p_d = _cat_totals(fin_aa_p)
        lmap = {k:PROPERTY_GROUPS[k][0] for k in PROPERTY_GROUPS}
        cu_disp = collections.Counter({lmap[k]:v for k,v in cat_u_d.items()})
        cp_disp = collections.Counter({lmap[k]:v for k,v in cat_p_d.items()})

        def _rdr_prop_cv(c_prop):
            draw_comparison_bar_chart(c_prop, cu_disp, cp_disp,
                label_a="User", label_b="Preset", color_a=USER_COLOR, color_b=PRESET_COLOR,
                title="Final prob. by AA property", top_n=10, normalize=_nv_prop.get())
        def _rdr_prop(ev=None): _rdr_prop_cv(_c_prop)

        for w in f3.winfo_children():
            if isinstance(w, tk.Frame) and w.cget("bg") == "#F5F5F0":
                w.destroy(); break
        _nv_prop = self._make_norm_toggle(f3, _rdr_prop)
        tk.Button(f3, text="⧆ Pop out", command=lambda: self._popout_window(
            "Property Category Comparison", _build_prop_compare, h=420),
            relief="solid",bd=1,padx=6,pady=2,font=("Helvetica",8),
            bg="#EAF3DE",fg="#3B6D11",cursor="hand2").pack(anchor="e",padx=8,pady=(0,2))
        _c_prop = self._scroll_chart(f3, _rdr_prop_cv, height=280, min_w=560, min_h=300)

        # Per-AA within each property group
        tk.Label(f3, text="Per-AA within each property group:",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg="#333"
                 ).pack(anchor="w", padx=8, pady=(4,2))
        for prop_key, (prop_name, prop_col) in PROPERTY_GROUPS.items():
            aas_in_group = [aa for aa in ALL_AAS if get_primary_group(aa)==prop_key]
            if not aas_in_group: continue
            sub_u = collections.Counter({aa: fin_aa_u.get(aa,0) for aa in aas_in_group})
            sub_p = collections.Counter({aa: fin_aa_p.get(aa,0) for aa in aas_in_group})
            gf = tk.LabelFrame(f3, text=prop_name, bg=BG_PANEL,
                               font=("Helvetica",9,"bold"), fg=prop_col)
            gf.pack(fill="both", expand=True, padx=6, pady=(0,4))
            _su = sub_u; _sp = sub_p
            def _rdr_g_cv(cc, cu=_su, cp=_sp, pn=prop_name, pc=prop_col):
                draw_comparison_bar_chart(cc, cu, cp,
                    label_a="User", label_b="Preset",
                    color_a=USER_COLOR, color_b=pc,
                    title=pn, top_n=10, normalize=_nv_prop.get())
            self._scroll_chart(gf, _rdr_g_cv, height=150, min_w=480, min_h=170)

        # ── Section B and C are now their own tabs ────────────────────────
        # (populated below)

        # ═══════════════════════════════════════════════════════════════════
        # TAB 4 — ⚖ Codon Degeneracy  (was Section B)
        # ═══════════════════════════════════════════════════════════════════
        self._clear("compare_deg")
        raw4 = self._tabs["compare_deg"]
        outer4, f4 = make_scrollable(raw4, bg=BG_PANEL)
        outer4.pack(fill="both", expand=True)
        self._populate_compare_deg(f4, fin_aa_u, fin_aa_p, self._legend, n_gen)

        # ═══════════════════════════════════════════════════════════════════
        # TAB 5 — ⚖ Start → End Map  (was Section C)
        # ═══════════════════════════════════════════════════════════════════
        self._clear("compare_codon_map")
        raw5 = self._tabs["compare_codon_map"]
        outer5, f5 = make_scrollable(raw5, bg=BG_PANEL)
        outer5.pack(fill="both", expand=True)
        self._populate_compare_codon_map(f5, s2f_u, s2f_p, self._legend, n_gen)

        # ═══════════════════════════════════════════════════════════════════
        # TAB 6 — ⚖ Per Generation  (User vs Preset, side by side)
        # ═══════════════════════════════════════════════════════════════════
        self._clear("compare_pergen")
        raw6 = self._tabs["compare_pergen"]
        outer6, f6 = make_scrollable(raw6, bg=BG_PANEL)
        outer6.pack(fill="both", expand=True)
        self._populate_compare_pergen(f6, per_gen_aa_u, per_gen_aa_p, self._legend, n_gen)

        # ═══════════════════════════════════════════════════════════════════
        # TAB 7 — ⚖ Summary Table  (every AA: User vs Preset, all metrics)
        # ═══════════════════════════════════════════════════════════════════
        self._clear("compare_summary")
        raw7 = self._tabs["compare_summary"]
        outer7, f7 = make_scrollable(raw7, bg=BG_PANEL)
        outer7.pack(fill="both", expand=True)
        self._populate_compare_summary(
            f7, enc_aa_u, fin_aa_u, stop_u, enc_aa_p, fin_aa_p, stop_p,
            self._legend, n_gen)

        # ═══════════════════════════════════════════════════════════════════
        # TAB 8 — ⚖ Category Tracking  (User vs Preset, side by side)
        # ═══════════════════════════════════════════════════════════════════
        self._clear("compare_tracking")
        raw8 = self._tabs["compare_tracking"]
        outer8, f8 = make_scrollable(raw8, bg=BG_PANEL)
        outer8.pack(fill="both", expand=True)
        self._populate_compare_tracking(f8, track_u, track_p, n_gen, stop_u, stop_p,
                                        exp_u[0], exp_p[0])


    # ─────────────────────────────────────────────────────────────────────
    # Compare: Category Tracking tab
    # ─────────────────────────────────────────────────────────────────────

    def _populate_compare_tracking(self, parent, track_u, track_p, n_gen,
                                   stop_u=None, stop_p=None,
                                   records_u=None, records_p=None):
        """
        Side-by-side self-retention comparison between User and Preset.
          - Same-category retention: User (solid) vs Preset (dashed), one
            colour per category, on one chart.
          - Same-AA retention: a selectable AA, User vs Preset lines.
        """
        self._header(parent, "⚖  Category & AA tracking — User vs Preset")
        self._legend(parent,
            "Compares how 'conservative' each model is. Solid = User, dashed = "
            "Preset. Higher line = mutations stay within the same category / AA "
            "more often under that model.", bg="#E8EEF8")

        pgc_u = track_u["per_gen_cat_from"]; pgc_p = track_p["per_gen_cat_from"]
        pga_u = track_u["per_gen_aa_from"];  pga_p = track_p["per_gen_aa_from"]
        pstop_aa_u = track_u.get("per_gen_stop_aa_from", [])
        pstop_aa_p = track_p.get("per_gen_stop_aa_from", [])
        N = min(len(pgc_u), len(pgc_p))
        cat_keys  = list(PROPERTY_GROUPS.keys())
        cat_names = {k: PROPERTY_GROUPS[k][0] for k in cat_keys}
        cat_colraw = {k: PROPERTY_GROUPS[k][1] for k in cat_keys}
        stop_line_label = "Stop codon"

        def _self(per_gen, key, g):
            d = per_gen[g].get(key, {}); t = sum(d.values())
            return (d.get(key,0)/t) if t > 0 else 0.0

        def _cum_stop_cmp(per_gen_stop, start_key, gen):
            return sum(per_gen_stop[g].get(start_key, 0.0)
                       for g in range(min(gen, len(per_gen_stop)-1)+1)) if per_gen_stop else 0.0

        pscod_u = track_u.get("per_gen_codon_from", [])
        pscod_p = track_p.get("per_gen_codon_from", [])
        pstop_codon_u = track_u.get("per_gen_stop_codon_from", [])
        pstop_codon_p = track_p.get("per_gen_stop_codon_from", [])

        tk.Label(parent, text="Selected exact codon — User vs Preset:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(2,2))
        self._legend(parent,
            "Default sampled mode uses integer copies. Category charts show live "
            "category counts; stop charts underneath show new and cumulative stops.",
            bg="#E8EEF8")
        cmp_cod_ctrl = tk.Frame(parent, bg=BG_PANEL)
        cmp_cod_ctrl.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(cmp_cod_ctrl, text="Start codon:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        cmp_cod_var = tk.StringVar(value=VALID_CODONS[0])
        cmp_cod_menu = ttk.Combobox(cmp_cod_ctrl, textvariable=cmp_cod_var,
                                    state="readonly", values=VALID_CODONS,
                                    font=("Helvetica",10), width=8)
        cmp_cod_menu.pack(side="left", padx=(6,12))
        tk.Label(cmp_cod_ctrl, text="Display:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        cmp_data_var = tk.StringVar(value="Sampled copies")
        cmp_data_menu = ttk.Combobox(cmp_cod_ctrl, textvariable=cmp_data_var,
                                     state="readonly",
                                     values=["Sampled copies", "Exact probability"],
                                     font=("Helvetica",10), width=16)
        cmp_data_menu.pack(side="left", padx=(6,12))
        cmp_cod_info = tk.Label(cmp_cod_ctrl, text="", bg=BG_PANEL,
                                font=("Helvetica",8,"bold"), fg="#555")
        cmp_cod_info.pack(side="left")

        def _cmp_sampled_series(records, codon):
            records_for_codon = [r for r in (records or []) if r.get("start") == codon]
            series = {cat_names[k]: [] for k in cat_keys}
            series[stop_line_label] = []
            for gen_idx in range(N):
                gen_num = gen_idx + 1
                live_by_cat = collections.Counter()
                stop_now = 0
                for rec in records_for_codon:
                    path = rec.get("path") or [rec.get("start"), rec.get("final")]
                    stop_gen = rec.get("stop_gen")
                    if rec.get("hit_stop") and stop_gen is not None and gen_num >= stop_gen:
                        if gen_num == stop_gen:
                            stop_now += 1
                        continue
                    idx = min(gen_num, len(path)-1)
                    cur_codon = path[idx]
                    cur_aa = CODON_TABLE.get(cur_codon, "Stop")
                    if cur_aa == "Stop":
                        stop_now += 1
                        continue
                    cur_cat = get_primary_group(cur_aa)
                    if cur_cat in cat_keys:
                        live_by_cat[cur_cat] += 1
                for k in cat_keys:
                    series[cat_names[k]].append(live_by_cat.get(k, 0))
                series[stop_line_label].append(stop_now)
            return series, len(records_for_codon)

        def _cmp_category_only(series):
            return {cat_names[k]: list(series.get(cat_names[k], [])) for k in cat_keys}

        def _cmp_stop_arrays(series):
            new_stops = list(series.get(stop_line_label, []))
            cumulative = []
            running = 0
            for val in new_stops:
                running += val
                cumulative.append(running)
            return new_stops, cumulative

        def _cmp_no_more_change(series, n_records):
            if not n_records:
                return None, "no sampled copies"
            vectors = [
                tuple(series[cat_names[k]][gen] for k in cat_keys)
                for gen in range(N)
            ]
            for idx, vec in enumerate(vectors):
                if all(future == vec for future in vectors[idx:]):
                    return idx + 1, "all stopped" if sum(vec) == 0 else "category counts stable"
            return None, "still changing"

        def _cmp_exact_category_series(pscod, codon):
            series = {cat_names[k]: [] for k in cat_keys}
            for gen in range(N):
                dist = pscod[gen].get(codon, {}) if gen < len(pscod) else {}
                by_cat = collections.Counter()
                for cur_codon, w in dist.items():
                    aa = CODON_TABLE.get(cur_codon, "?")
                    ck = get_primary_group(aa)
                    if ck in cat_keys:
                        by_cat[ck] += w
                for k in cat_keys:
                    series[cat_names[k]].append(by_cat.get(k, 0.0))
            return series

        def _cmp_render_side(cv, codon, label, records, pscod, color):
            sampled_mode = cmp_data_var.get() == "Sampled copies"
            aa = CODON_TABLE.get(codon, "?")
            if sampled_mode:
                full_series, n_records = _cmp_sampled_series(records, codon)
                marker_gen, note = _cmp_no_more_change(full_series, n_records)
                if not n_records:
                    cv.delete("all")
                    cv.create_text(cv.winfo_width()//2, cv.winfo_height()//2,
                                   text=f"No sampled copies for {codon}",
                                   fill="#aaa", font=("Helvetica",10))
                    return
                draw_retention_lines(
                    cv, _cmp_category_only(full_series),
                    f"{label}: {codon} ({aa}) counts | {note}, n={n_records}",
                    color_map={cat_names[k]: cat_colraw[k] for k in cat_keys},
                    highlight=cat_names.get(get_primary_group(aa)),
                    show_share=False, integer_values=True,
                    marker_gen=marker_gen,
                    marker_label=f"gen {marker_gen}" if marker_gen else None,
                    marker_color=color)
            else:
                draw_retention_lines(
                    cv, _cmp_exact_category_series(pscod, codon),
                    f"{label}: {codon} ({aa}) exact surviving-category share",
                    color_map={cat_names[k]: cat_colraw[k] for k in cat_keys},
                    highlight=cat_names.get(get_primary_group(aa)),
                    show_share=True)

        def _cmp_render_stop(cv, codon, label, records, pstop_codon):
            sampled_mode = cmp_data_var.get() == "Sampled copies"
            if sampled_mode:
                full_series, n_records = _cmp_sampled_series(records, codon)
                new_stops, cumulative = _cmp_stop_arrays(full_series)
                marker_gen, _note = _cmp_no_more_change(full_series, n_records)
                draw_stop_event_chart(cv, new_stops, cumulative,
                                      f"{label}: {codon} stops",
                                      integer_values=True, marker_gen=marker_gen)
            else:
                new_stops = [
                    pstop_codon[g].get(codon, 0.0) if g < len(pstop_codon) else 0.0
                    for g in range(N)
                ]
                cumulative = []
                running = 0.0
                for val in new_stops:
                    running += val
                    cumulative.append(running)
                draw_stop_event_chart(cv, new_stops, cumulative,
                                      f"{label}: {codon} stops",
                                      integer_values=False)

        cmp_panes = tk.Frame(parent, bg=BG_PANEL)
        cmp_panes.pack(fill="both", expand=True, padx=4, pady=(0,6))
        cmp_user_pane = tk.Frame(cmp_panes, bg=BG_PANEL, relief="solid", bd=1)
        cmp_user_pane.pack(side="left", fill="both", expand=True, padx=(0,3))
        cmp_preset_pane = tk.Frame(cmp_panes, bg=BG_PANEL, relief="solid", bd=1)
        cmp_preset_pane.pack(side="left", fill="both", expand=True, padx=(3,0))
        tk.Label(cmp_user_pane, text="User probability", bg="#E6F1FB",
                 fg=USER_COLOR, font=("Helvetica",9,"bold")).pack(fill="x")
        tk.Label(cmp_preset_pane, text="Preset probability", bg="#F5EEF8",
                 fg=PRESET_COLOR, font=("Helvetica",9,"bold")).pack(fill="x")
        cmp_user_cat = self._scroll_chart(cmp_user_pane,
            lambda cv: _cmp_render_side(cv, cmp_cod_var.get(), "User", records_u, pscod_u, USER_COLOR),
            height=360, min_w=700, min_h=460)
        cmp_user_stop = self._scroll_chart(cmp_user_pane,
            lambda cv: _cmp_render_stop(cv, cmp_cod_var.get(), "User", records_u, pstop_codon_u),
            height=170, min_w=620, min_h=220)
        cmp_preset_cat = self._scroll_chart(cmp_preset_pane,
            lambda cv: _cmp_render_side(cv, cmp_cod_var.get(), "Preset", records_p, pscod_p, PRESET_COLOR),
            height=360, min_w=700, min_h=460)
        cmp_preset_stop = self._scroll_chart(cmp_preset_pane,
            lambda cv: _cmp_render_stop(cv, cmp_cod_var.get(), "Preset", records_p, pstop_codon_p),
            height=170, min_w=620, min_h=220)

        def _refresh_cmp_codon(ev=None):
            codon = cmp_cod_var.get()
            cmp_cod_info.config(text=f"{codon} | {cmp_data_var.get()}")
            _cmp_render_side(cmp_user_cat, codon, "User", records_u, pscod_u, USER_COLOR)
            _cmp_render_stop(cmp_user_stop, codon, "User", records_u, pstop_codon_u)
            _cmp_render_side(cmp_preset_cat, codon, "Preset", records_p, pscod_p, PRESET_COLOR)
            _cmp_render_stop(cmp_preset_stop, codon, "Preset", records_p, pstop_codon_p)

        cmp_cod_menu.bind("<<ComboboxSelected>>", _refresh_cmp_codon)
        cmp_data_menu.bind("<<ComboboxSelected>>", _refresh_cmp_codon)
        cmp_cod_var.trace_add("write", lambda *_: _refresh_cmp_codon())
        cmp_data_var.trace_add("write", lambda *_: _refresh_cmp_codon())
        self.after(120, _refresh_cmp_codon)

        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))

        if stop_u is not None and stop_p is not None:
            tk.Label(parent, text="Stop hits by starting property — User vs Preset:",
                     font=("Helvetica",10,"bold"), bg=BG_PANEL, fg="#A32D2D"
                     ).pack(anchor="w", padx=8, pady=(2,2))
            self._legend(parent,
                "Paired bars group stop probability by the starting biochemical "
                "property class. This shows which category is most likely to "
                "terminate early under each model.",
                bg="#FDEDEC")
            _nv_stop_prop_cmp = self._make_norm_toggle(parent, lambda: _render_stop_prop_cmp())
            stop_prop_u = property_stop_counter(stop_u)
            stop_prop_p = property_stop_counter(stop_p)
            def _draw_stop_prop_cmp(cv):
                draw_comparison_bar_chart(
                    cv, stop_prop_u, stop_prop_p,
                    label_a="User", label_b="Preset",
                    color_a=USER_COLOR, color_b=PRESET_COLOR,
                    title="Stop probability by starting property — User vs Preset",
                    top_n=len(PROPERTY_GROUPS),
                    normalize=_nv_stop_prop_cmp.get())
            _c_stop_prop_cmp = self._scroll_chart(parent, _draw_stop_prop_cmp,
                                                  height=300, min_w=1000, min_h=420)
            def _render_stop_prop_cmp(ev=None):
                _draw_stop_prop_cmp(_c_stop_prop_cmp)

        # ── Same-category retention overlay ──
        tk.Label(parent, text="Same-category retention — User (solid) vs Preset (dashed):",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(2,2))
        def _render_cat(cv):
            self._draw_dual_retention(
                cv, N,
                {cat_names[k]: [_self(pgc_u,k,g) for g in range(N)] for k in cat_keys},
                {cat_names[k]: [_self(pgc_p,k,g) for g in range(N)] for k in cat_keys},
                {cat_names[k]: cat_colraw[k] for k in cat_keys},
                "Same-category retention — User vs Preset")
        self._scroll_chart(parent, _render_cat,
                           height=320, min_w=1000, min_h=460)

        # ── Same-AA retention overlay (selectable AA) ──
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))
        tk.Label(parent, text="Same-amino-acid retention — pick an AA:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,2))
        self._legend(parent,
            "Self-retention of one amino acid over generations: solid = User, "
            "dashed = Preset. Shows which model better preserves this AA.",
            bg="#E8EEF8")
        row = tk.Frame(parent, bg=BG_PANEL); row.pack(anchor="w", padx=8, pady=(0,2))
        tk.Label(row, text="Amino acid:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        aa_var = tk.StringVar(value=ALL_AAS[0])
        aa_menu = ttk.Combobox(row, textvariable=aa_var, state="readonly",
                               values=ALL_AAS, font=("Helvetica",10), width=8)
        aa_menu.pack(side="left", padx=(6,0))
        def _render_aa(cv):
            aa = aa_var.get()
            col = AA_COLOR_MAP.get(aa, "#444")
            self._draw_dual_retention(
                cv, N,
                {aa: [_self(pga_u, aa, g) for g in range(N)]},
                {aa: [_self(pga_p, aa, g) for g in range(N)]},
                {aa: col},
                f"{aa} self-retention — User vs Preset")
        c_aa = self._scroll_chart(parent, _render_aa,
                                  height=300, min_w=1000, min_h=420)
        aa_menu.bind("<<ComboboxSelected>>", lambda e: _render_aa(c_aa))

        # ── Category spotlight comparison ──────────────────────────────────
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))
        tk.Label(parent, text="Category spotlight — User vs Preset:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,2))
        self._legend(parent,
            "For each AA in the selected starting category, stacked bars show what "
            "fraction of its mass ended in each destination category. Left = User, "
            "Right = Preset. Bars sorted by User self-retention.",
            bg="#E8EEF8")

        cmp_e_ctrl = tk.Frame(parent, bg=BG_PANEL)
        cmp_e_ctrl.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(cmp_e_ctrl, text="Starting category:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        cmp_e_cat_var = tk.StringVar(value=cat_names[cat_keys[0]])
        cmp_e_cat_menu = ttk.Combobox(cmp_e_ctrl, textvariable=cmp_e_cat_var,
                                       state="readonly",
                                       values=[cat_names[k] for k in cat_keys],
                                       font=("Helvetica",10), width=22)
        cmp_e_cat_menu.pack(side="left", padx=(6,12))
        tk.Label(cmp_e_ctrl, text="Generation:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        cmp_e_gen_var = tk.IntVar(value=N)
        cmp_e_gen_spin = tk.Spinbox(cmp_e_ctrl, from_=1, to=max(N,1),
                                     textvariable=cmp_e_gen_var,
                                     width=5, font=("Courier",11))
        cmp_e_gen_spin.pack(side="left", padx=(4,0))

        cmp_e_panes = tk.Frame(parent, bg=BG_PANEL)
        cmp_e_panes.pack(fill="both", expand=True, padx=4, pady=(0,4))

        cmp_e_lp = tk.Frame(cmp_e_panes, bg=BG_PANEL, relief="solid", bd=2)
        cmp_e_lp.pack(side="left", fill="both", expand=True, padx=(0,3))
        tk.Label(cmp_e_lp, text="  [User]", font=("Helvetica",9,"bold"),
                 bg=lighten_hex(USER_COLOR,0.75), fg=USER_COLOR, anchor="w"
                 ).pack(fill="x", ipady=3)

        cmp_e_rp = tk.Frame(cmp_e_panes, bg=BG_PANEL, relief="solid", bd=2)
        cmp_e_rp.pack(side="left", fill="both", expand=True, padx=(3,0))
        tk.Label(cmp_e_rp, text="  [Preset]", font=("Helvetica",9,"bold"),
                 bg=lighten_hex(PRESET_COLOR,0.75), fg=PRESET_COLOR, anchor="w"
                 ).pack(fill="x", ipady=3)

        def _draw_cmp_e_side(cv, pga_data, label):
            cv.delete("all")
            W = cv.winfo_width(); H = cv.winfo_height()
            if W < 50 or H < 50 or N < 1: return
            disp = cmp_e_cat_var.get()
            sk = next((k for k in cat_keys if cat_names[k] == disp), cat_keys[0])
            gen = min(cmp_e_gen_var.get()-1, N-1)
            aas_in_cat = [aa for aa in ALL_AAS if get_primary_group(aa) == sk]
            if not aas_in_cat:
                cv.create_text(W//2, H//2, text="No AAs in this category",
                               fill="#aaa", font=("Helvetica",11)); return
            aa_cat_data = {}
            for aa in aas_in_cat:
                dist = pga_data[gen].get(aa, {}) if gen < N else {}
                by_cat = {k: 0.0 for k in cat_keys}
                for da, w in dist.items():
                    dk = get_primary_group(da)
                    if dk in by_cat: by_cat[dk] += w
                aa_cat_data[aa] = by_cat
            aas_sorted = sorted(aas_in_cat,
                key=lambda a: -(aa_cat_data[a].get(sk,0)/(sum(aa_cat_data[a].values()) or 1)))
            pad_l=70; pad_r=90; pad_t=32; pad_b=10
            chart_w = W-pad_l-pad_r; n = len(aas_sorted)
            bar_h = max(14, min(28, (H-pad_t-pad_b)//max(n,1)-4))
            gap = max(2, (H-pad_t-pad_b-n*bar_h)//max(n+1,1))
            _chart_title(cv, W, 14, f"{label}: {disp} gen {gen+1}",
                         font=("Helvetica",9,"bold"))
            for i, aa in enumerate(aas_sorted):
                by_cat = aa_cat_data[aa]; total = sum(by_cat.values()) or 1
                y = pad_t + i*(bar_h+gap)
                cv.create_text(pad_l-3, y+bar_h//2,
                               text=_fit_text(aa, pad_l-8, 9, True),
                               anchor="e", font=("Courier",9), fill="#333")
                x_cur = pad_l
                for cat_k in cat_keys:
                    frac = by_cat.get(cat_k, 0)/total
                    if frac <= 0: continue
                    bw = max(1, int(frac*chart_w))
                    col = cat_colraw[cat_k]
                    cv.create_rectangle(x_cur, y, x_cur+bw, y+bar_h,
                                        fill=col, outline="white", width=1)
                    if bw > 24:
                        cv.create_text(x_cur+bw//2, y+bar_h//2,
                                       text=f"{frac*100:.0f}%", anchor="center",
                                       font=("Helvetica",7), fill="white")
                    x_cur += bw
                sp = by_cat.get(sk, 0)/total
                cv.create_text(pad_l+chart_w+4, y+bar_h//2,
                               text=_fit_text(f"{sp*100:.0f}%", pad_r-8, 8),
                               anchor="w", font=("Helvetica",8), fill="#444")
            cv.create_line(pad_l, pad_t, pad_l, H-pad_b, fill="#ccc")
            lx = W-pad_r+5
            for li, k in enumerate(cat_keys):
                col = cat_colraw[k]; ly = pad_t + li*14
                cv.create_rectangle(lx, ly, lx+8, ly+8, fill=col, outline="")
                cv.create_text(lx+10, ly, text=_fit_text(cat_names[k], pad_r-22, 7), anchor="nw",
                               font=("Helvetica",7), fill="#333")

        c_cmp_e_u = self._scroll_chart(cmp_e_lp,
            lambda cv: _draw_cmp_e_side(cv, pga_u, "User"),
            height=240, min_w=560, min_h=360)
        c_cmp_e_p = self._scroll_chart(cmp_e_rp,
            lambda cv: _draw_cmp_e_side(cv, pga_p, "Preset"),
            height=240, min_w=560, min_h=360)

        def _refresh_cmp_e(ev=None):
            _draw_cmp_e_side(c_cmp_e_u, pga_u, "User")
            _draw_cmp_e_side(c_cmp_e_p, pga_p, "Preset")

        cmp_e_cat_menu.bind("<<ComboboxSelected>>", lambda e: _refresh_cmp_e())
        cmp_e_gen_spin.config(command=_refresh_cmp_e)
        cmp_e_gen_spin.bind("<Return>", _refresh_cmp_e)
        self.after(140, _refresh_cmp_e)

        # ── AA spotlight comparison ─────────────────────────────────────────
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))
        tk.Label(parent, text="AA spotlight — category destination: User vs Preset:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,2))
        self._legend(parent,
            "For a selected amino acid, shows how its category distribution evolves "
            "across all generations: solid lines = User, dashed = Preset. "
            "Each colour = one destination category.",
            bg="#E8EEF8")

        cmp_f_row = tk.Frame(parent, bg=BG_PANEL)
        cmp_f_row.pack(anchor="w", padx=8, pady=(0,4))
        tk.Label(cmp_f_row, text="Amino acid:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(side="left")
        cmp_f_aa_var = tk.StringVar(value=ALL_AAS[0])
        cmp_f_aa_menu = ttk.Combobox(cmp_f_row, textvariable=cmp_f_aa_var,
                                      state="readonly", values=ALL_AAS,
                                      font=("Helvetica",10), width=8)
        cmp_f_aa_menu.pack(side="left", padx=(6,0))
        cmp_f_conv_lbl = tk.Label(cmp_f_row, text="", bg=BG_PANEL,
                                  font=("Helvetica",8,"bold"), fg="#555")
        cmp_f_conv_lbl.pack(side="left", padx=(12,0))

        def _aa_cat_dist_cmp(aa, pga_data, gen):
            dist = pga_data[gen].get(aa, {}) if 0 <= gen < N else {}
            by_cat = {k: 0.0 for k in cat_keys}
            for da, w in dist.items():
                dk = get_primary_group(da)
                if dk in by_cat: by_cat[dk] += w
            return by_cat

        def _render_cmp_f(cv):
            aa = cmp_f_aa_var.get()
            series_u = {}; series_p = {}
            col_map_named = {cat_names[k]: cat_colraw[k] for k in cat_keys}
            col_map_named[stop_line_label] = "#C0392B"
            for k in cat_keys:
                name = cat_names[k]
                vu = []; vp = []
                for gen in range(N):
                    bu = _aa_cat_dist_cmp(aa, pga_u, gen)
                    bp = _aa_cat_dist_cmp(aa, pga_p, gen)
                    su = _cum_stop_cmp(pstop_aa_u, aa, gen)
                    sp = _cum_stop_cmp(pstop_aa_p, aa, gen)
                    tu = sum(bu.values()) + su or 1
                    tp = sum(bp.values()) + sp or 1
                    vu.append(bu[k]/tu); vp.append(bp[k]/tp)
                series_u[name] = vu; series_p[name] = vp
            series_u[stop_line_label] = []
            series_p[stop_line_label] = []
            for gen in range(N):
                bu = _aa_cat_dist_cmp(aa, pga_u, gen)
                bp = _aa_cat_dist_cmp(aa, pga_p, gen)
                su = _cum_stop_cmp(pstop_aa_u, aa, gen)
                sp = _cum_stop_cmp(pstop_aa_p, aa, gen)
                series_u[stop_line_label].append(su / ((sum(bu.values()) + su) or 1))
                series_p[stop_line_label].append(sp / ((sum(bp.values()) + sp) or 1))
            cmp_f_conv_lbl.config(
                text=f"User {convergence_text(series_u)} | Preset {convergence_text(series_p)}")
            self._draw_dual_retention(cv, N, series_u, series_p, col_map_named,
                f"{aa} — category/stop distribution — User (solid) vs Preset (dashed)")

        c_cmp_f = self._scroll_chart(parent, _render_cmp_f,
                                     height=320, min_w=1000, min_h=460)
        cmp_f_aa_menu.bind("<<ComboboxSelected>>", lambda e: _render_cmp_f(c_cmp_f))
        self.after(150, lambda: _render_cmp_f(c_cmp_f))

    def _draw_dual_retention(self, canvas, N, series_u, series_p, color_map, title):
        """Overlay two sets of retention lines: solid (User) vs dashed (Preset)."""
        canvas.delete("all")
        W = canvas.winfo_width(); H = canvas.winfo_height()
        if W < 60 or H < 60 or N < 1: return
        legend_px = max((_text_px(lbl, 8) for lbl in series_u), default=90)
        pad_l=54; pad_r=int(min(210, max(150, legend_px+38))); pad_t=34; pad_b=40
        if W - pad_l - pad_r < 140:
            pad_r = max(105, W//5)
        plot_w = max(30, W-pad_l-pad_r); plot_h = H-pad_t-pad_b
        all_vals = [v for s in (series_u, series_p) for vals in s.values() for v in vals]
        max_y = (max(all_vals) if all_vals else 1) or 1
        max_y = max_y*1.1

        _chart_title(canvas, W, 14, title)
        canvas.create_line(pad_l, pad_t, pad_l, pad_t+plot_h, fill="#ccc")
        canvas.create_line(pad_l, pad_t+plot_h, pad_l+plot_w, pad_t+plot_h, fill="#ccc")
        for frac in [0,0.25,0.5,0.75,1.0]:
            yy = pad_t+plot_h-frac*plot_h
            canvas.create_line(pad_l-3, yy, pad_l, yy, fill="#bbb")
            canvas.create_text(pad_l-5, yy, text=f"{frac*max_y:.2f}",
                               anchor="e", font=("Helvetica",7), fill="#999")
            if 0 < frac < 1:
                canvas.create_line(pad_l, yy, pad_l+plot_w, yy, fill="#f3f3f3")
        n_ticks = min(N,8)
        for t in range(n_ticks):
            g = int(t*(N-1)/max(n_ticks-1,1)) if N>1 else 0
            xx = pad_l+(g/(N-1))*plot_w if N>1 else pad_l
            canvas.create_line(xx, pad_t+plot_h, xx, pad_t+plot_h+3, fill="#bbb")
            canvas.create_text(xx, pad_t+plot_h+5, text=str(g+1),
                               anchor="n", font=("Helvetica",7), fill="#999")
        def _x(g): return pad_l+(g/(N-1))*plot_w if N>1 else pad_l
        def _plot(series, dash):
            for lbl, vals in series.items():
                col = color_map.get(lbl, "#888")
                pts = []
                for g in range(N):
                    pts.extend([_x(g), pad_t+plot_h-(vals[g]/max_y)*plot_h])
                if len(pts) >= 4:
                    canvas.create_line(*pts, fill=col, width=2, smooth=True,
                                       **({"dash":dash} if dash else {}))
        _plot(series_u, None)        # User solid
        _plot(series_p, (5,3))       # Preset dashed
        # Legend
        lx = W-pad_r+8
        canvas.create_text(lx, pad_t-4, text=_fit_text("User = solid", pad_r-12, 8), anchor="nw",
                           font=("Helvetica",8,"bold"), fill="#333")
        canvas.create_text(lx, pad_t+9, text=_fit_text("Preset = dashed", pad_r-12, 8), anchor="nw",
                           font=("Helvetica",8,"bold"), fill="#333")
        ranked = sorted(series_u.items(), key=lambda kv: -kv[1][-1])
        for i,(lbl,vals) in enumerate(ranked[:12]):
            col = color_map.get(lbl, "#888")
            ly = pad_t+26+i*15
            canvas.create_line(lx, ly+5, lx+14, ly+5, fill=col, width=3)
            canvas.create_text(lx+18, ly+5, text=_fit_text(lbl, pad_r-30, 8), anchor="w",
                               font=("Helvetica",8), fill="#333")
        canvas.create_text(pad_l+plot_w//2, H-10, text="Generation",
                           font=("Helvetica",8), fill="#888", anchor="center")


    # ─────────────────────────────────────────────────────────────────────
    # Compare: Summary Table tab
    # ─────────────────────────────────────────────────────────────────────

    def _populate_compare_summary(self, parent, enc_u, fin_u, stop_u,
                                  enc_p, fin_p, stop_p, _legend_fn, n_gen):
        """
        One row per amino acid with side-by-side User/Preset metrics:
          encountered prob, final prob, stop prob (by start AA), and the
          User-Preset deltas. Plus an overall stats strip and a small
          'biggest movers' highlight. Fully sortable.
        """
        self._header(parent, "⚖  Summary table — User vs Preset (all amino acids)")
        _legend_fn(parent,
            "Every AA with both models side by side. Enc = encountered prob "
            "(all gens), Fin = final prob (gen N), Stop = prob of stops from "
            "this AA's codons. Δ columns = User − Preset. Click any header to sort.",
            bg="#E8EEF8")

        # Normalised helpers
        teu = sum(enc_u.values()) or 1; tep = sum(enc_p.values()) or 1
        tfu = sum(fin_u.values()) or 1; tfp = sum(fin_p.values()) or 1
        su  = stop_u["by_start_aa"];     sp  = stop_p["by_start_aa"]
        tsu = sum(su.values()) or 1;     tsp = sum(sp.values()) or 1

        # ── Overall stats strip ──
        strip = tk.Frame(parent, bg="#E6F1FB", relief="solid", bd=1)
        strip.pack(fill="x", padx=6, pady=(4,6))
        total_start = self._params["start_copies"] * len(VALID_CODONS)
        items = [
            ("Generations", str(n_gen)),
            ("User stop %",   f"{100*sum(stop_u['by_stop_codon'].values())/total_start:.2f}%"),
            ("Preset stop %", f"{100*sum(stop_p['by_stop_codon'].values())/total_start:.2f}%"),
            ("User uniq AAs",   str(len(enc_u))),
            ("Preset uniq AAs", str(len(enc_p))),
        ]
        for i,(l,v) in enumerate(items):
            tk.Label(strip,text=l,bg="#E6F1FB",font=("Helvetica",8,"bold"),fg="#0C447C"
                     ).grid(row=0,column=i*2,padx=(12,2),pady=5)
            tk.Label(strip,text=v,bg="#dce8f8",font=("Courier",9,"bold"),fg="#0C447C",
                     relief="solid",bd=1,padx=6).grid(row=0,column=i*2+1,padx=(0,8),pady=5)

        # ── Legend for row colours ──
        leg = tk.Frame(parent, bg=BG_PANEL); leg.pack(fill="x", padx=8, pady=(0,4))
        for col,label in [("#D6EAF8","User favoured (final Δ > 0)"),
                          ("#E8DAEF","Preset favoured (final Δ < 0)"),
                          ("#F8F8F8","≈ equal")]:
            tk.Label(leg,text="   ",bg=col,relief="solid",bd=1).pack(side="left",padx=(0,2))
            tk.Label(leg,text=label+"    ",bg=BG_PANEL,font=("Helvetica",8),fg="#555"
                     ).pack(side="left")

        # ── Table ──
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill="both", expand=True, padx=6, pady=4)
        vsb = tk.Scrollbar(outer); vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(outer, orient="horizontal"); hsb.pack(side="bottom", fill="x")
        cols = ["aa","full","ncod",
                "enc_u","enc_p","enc_d",
                "fin_u","fin_p","fin_d",
                "stop_u","stop_p","stop_d"]
        tv = ttk.Treeview(outer, columns=cols, show="headings",
                          yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=tv.yview); hsb.config(command=tv.xview)
        tv.pack(fill="both", expand=True)
        tv.tag_configure("user_fav",   background="#D6EAF8")
        tv.tag_configure("preset_fav", background="#E8DAEF")
        tv.tag_configure("neutral",    background="#F8F8F8")
        heads = [
            ("aa","AA",55),("full","Full name",140),("ncod","# cod",55),
            ("enc_u","Enc U",80),("enc_p","Enc P",80),("enc_d","Enc Δ",80),
            ("fin_u","Fin U",80),("fin_p","Fin P",80),("fin_d","Fin Δ",80),
            ("stop_u","Stop U",80),("stop_p","Stop P",80),("stop_d","Stop Δ",80),
        ]
        for cid,head,w in heads:
            tv.heading(cid, text=head, command=lambda c=cid: self._sort_table(tv,c,False))
            tv.column(cid, width=w, anchor="center" if cid not in ("full",) else "w")

        all_aa = sorted(set(list(enc_u)+list(enc_p)+list(fin_u)+list(fin_p)),
                        key=lambda a: -(fin_u.get(a,0)/tfu + fin_p.get(a,0)/tfp))
        for aa in all_aa:
            eu, ep = enc_u.get(aa,0)/teu, enc_p.get(aa,0)/tep
            fu, fp = fin_u.get(aa,0)/tfu, fin_p.get(aa,0)/tfp
            stu, stp = su.get(aa,0)/tsu, sp.get(aa,0)/tsp
            fd = fu - fp
            tag = "user_fav" if fd > 0.001 else ("preset_fav" if fd < -0.001 else "neutral")
            tv.insert("","end", values=[
                aa, AA_FULL.get(aa,aa), CODON_COUNT_MAP.get(aa,"?"),
                f"{eu:.4f}", f"{ep:.4f}", f"{eu-ep:+.4f}",
                f"{fu:.4f}", f"{fp:.4f}", f"{fd:+.4f}",
                f"{stu:.4f}", f"{stp:.4f}", f"{stu-stp:+.4f}",
            ], tags=(tag,))


    # ─────────────────────────────────────────────────────────────────────
    # Compare: Per Generation tab
    # ─────────────────────────────────────────────────────────────────────

    def _populate_compare_pergen(self, parent, per_gen_aa_u, per_gen_aa_p,
                                 _legend_fn, n_gen):
        """
        Side-by-side per-generation explorer: one generation spinner drives
        both User and Preset panels simultaneously, so the same generation is
        compared. Each side shows the AA distribution and the category
        (property) analysis for that generation.
        """
        self._header(parent, "⚖  Per-generation comparison — User vs Preset")
        _legend_fn(parent,
            "One generation selector drives both panels. "
            "Left = User (blue header), Right = Preset (purple header). "
            "Each panel shows AA distribution and category analysis for that generation.",
            bg="#E8EEF8")

        # Shared controls
        ctrl = tk.Frame(parent, bg=BG_PANEL)
        ctrl.pack(anchor="w", padx=8, pady=(2,4))
        tk.Label(ctrl, text="Generation: ", bg=BG_PANEL,
                 font=("Helvetica",10,"bold")).pack(side="left")
        gen_sel = tk.IntVar(value=1)
        spin = tk.Spinbox(ctrl, from_=1, to=n_gen, textvariable=gen_sel,
                          width=6, font=("Courier",11))
        spin.pack(side="left")
        tk.Label(ctrl, text="  (use ← → arrow keys to step)", bg=BG_PANEL,
                 font=("Helvetica",8), fg="#888").pack(side="left")

        norm_var, deg_var = self._make_filter_toolbar(parent, lambda: _render())

        # Two side-by-side panels
        panes = tk.Frame(parent, bg=BG_PANEL)
        panes.pack(fill="both", expand=True, padx=4, pady=(0,6))

        # ── User panel ──
        up = tk.Frame(panes, bg=BG_PANEL, relief="solid", bd=2)
        up.pack(side="left", fill="both", expand=True, padx=(0,3))
        tk.Label(up, text="  [User]", font=("Helvetica",10,"bold"),
                 bg=lighten_hex(USER_COLOR, 0.75), fg=USER_COLOR,
                 anchor="w").pack(fill="x", ipady=4)
        tk.Label(up, text="AA distribution:", font=("Helvetica",8,"bold"),
                 bg=BG_PANEL, fg="#333").pack(anchor="w", padx=4, pady=(2,0))
        c_aa_u = self._scroll_chart(up, lambda cv: _render(), height=380,
                                    min_w=420, min_h=480)
        tk.Label(up, text="Category analysis:", font=("Helvetica",8,"bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(anchor="w", padx=4, pady=(2,0))
        c_cat_u = self._scroll_chart(up, lambda cv: _render(), height=360,
                                     min_w=420, min_h=520)

        # ── Preset panel ──
        pp = tk.Frame(panes, bg=BG_PANEL, relief="solid", bd=2)
        pp.pack(side="left", fill="both", expand=True, padx=(3,0))
        tk.Label(pp, text="  [Preset]", font=("Helvetica",10,"bold"),
                 bg=lighten_hex(PRESET_COLOR, 0.75), fg=PRESET_COLOR,
                 anchor="w").pack(fill="x", ipady=4)
        tk.Label(pp, text="AA distribution:", font=("Helvetica",8,"bold"),
                 bg=BG_PANEL, fg="#333").pack(anchor="w", padx=4, pady=(2,0))
        c_aa_p = self._scroll_chart(pp, lambda cv: _render(), height=380,
                                    min_w=420, min_h=480)
        tk.Label(pp, text="Category analysis:", font=("Helvetica",8,"bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(anchor="w", padx=4, pady=(2,0))
        c_cat_p = self._scroll_chart(pp, lambda cv: _render(), height=360,
                                     min_w=420, min_h=520)

        def _draw_side(c_aa, c_cat, per_gen_aa, g, badge):
            if not (0 <= g < len(per_gen_aa)):
                return
            gen_counter = per_gen_aa[g]
            fset = self._get_filter_set(deg_var)
            draw_bar_chart(c_aa, gen_counter, f"AAs gen {g+1} {badge}",
                           color_map=AA_COLOR_MAP, top_n=21,
                           normalize=norm_var.get(), filter_aa_set=fset)
            sel_aas = [aa for aa in ALL_AAS if (fset is None or aa in fset)]
            g_order = list(PROPERTY_GROUPS.keys())
            g_names = {k: v[0] for k, v in PROPERTY_GROUPS.items()}
            g_cols  = {k: v[1] for k, v in PROPERTY_GROUPS.items()}
            g_bgs   = PROPERTY_GROUP_BG
            by_group = {grp: collections.Counter() for grp in g_order}
            for aa in sel_aas:
                grp = get_primary_group(aa)
                if grp in by_group:
                    by_group[grp][aa] = gen_counter.get(aa, 0)
            self._draw_grouped_bars(c_cat, by_group, g_order, g_names,
                                    g_cols, g_bgs, f"Categories gen {g+1}",
                                    codon_counter=None, normalize=norm_var.get())

        def _render(ev=None):
            g = gen_sel.get() - 1
            _draw_side(c_aa_u, c_cat_u, per_gen_aa_u, g, "[User]")
            _draw_side(c_aa_p, c_cat_p, per_gen_aa_p, g, "[Preset]")

        spin.config(command=_render); spin.bind("<Return>", _render)
        self.bind("<Right>", lambda e: (gen_sel.set(min(n_gen, gen_sel.get()+1)), _render()))
        self.bind("<Left>",  lambda e: (gen_sel.set(max(1, gen_sel.get()-1)), _render()))
        self.after(100, _render)


    # ─────────────────────────────────────────────────────────────────────

    def _populate_compare_deg(self, parent, fin_aa_u, fin_aa_p, _legend_fn, n_gen):
        """Standalone tab: codon degeneracy comparison — User vs Preset."""
        self._header(parent, "⚖  Codon Degeneracy — User vs Preset")
        _legend_fn(parent,
            "Amino acids grouped by how many synonymous codons encode them. "
            "AAs with 6 codons (Leu, Arg, Ser) are reachable via more paths, "
            "so they tend to accumulate more probability.", bg="#E8EEF8")

        def _deg_totals(fin_aa):
            tot = collections.Counter()
            for aa, w in fin_aa.items():
                n = get_codon_count(aa)
                tot[f"{n} codon{'s' if n>1 else ''}"] += w
            return tot

        deg_u = _deg_totals(fin_aa_u)
        deg_p = _deg_totals(fin_aa_p)

        # ── Summary bar chart: group totals ──────────────────────────────
        tk.Label(parent, text="Summary — final probability by degeneracy group:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(4,2))

        _nv_deg = tk.BooleanVar(value=False)

        def _rdr_summary_cv(c_sum):
            draw_comparison_bar_chart(c_sum, deg_u, deg_p,
                label_a="User", label_b="Preset",
                color_a=USER_COLOR, color_b=PRESET_COLOR,
                title=f"Final probability by codon degeneracy (gen {n_gen})",
                top_n=6, normalize=_nv_deg.get())
        def _rdr_summary(ev=None): _rdr_summary_cv(_c_sum)

        _nv_deg = self._make_norm_toggle(parent, _rdr_summary)

        def _build_deg_po(frm):
            po_nv = tk.BooleanVar(value=False)
            def _po_draw(cv_local):
                draw_comparison_bar_chart(cv_local, deg_u, deg_p,
                    label_a="User", label_b="Preset",
                    color_a=USER_COLOR, color_b=PRESET_COLOR,
                    title="Final probability by codon degeneracy",
                    top_n=6, normalize=po_nv.get())
            def _po_render(ev=None):
                _po_draw(cv_po)
            po_nv = self._make_norm_toggle(frm, _po_render)
            cv_po = self._scroll_chart(frm, _po_draw, height=420,
                                       min_w=720, min_h=460)
        self._popout_btn(parent, "Codon Degeneracy Summary", _build_deg_po, h=480)

        _c_sum = self._scroll_chart(parent, _rdr_summary_cv, height=260,
                                    min_w=620, min_h=280)

        # ── Per-group breakdown with LabelFrames ─────────────────────────
        tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(8,4))
        tk.Label(parent, text="Per-amino-acid breakdown within each degeneracy group:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=8, pady=(0,4))
        _legend_fn(parent,
            "Each LabelFrame = one degeneracy class. Paired bars per AA: "
            "top = User (blue), bottom = Preset (purple). "
            "Members listed in the frame title.", bg="#EEF4FF")

        for n_cod in sorted(CODON_COUNT_GROUPS.keys()):
            aas_in_grp = CODON_COUNT_GROUPS[n_cod]
            sub_u = collections.Counter({aa: fin_aa_u.get(aa,0) for aa in aas_in_grp})
            sub_p = collections.Counter({aa: fin_aa_p.get(aa,0) for aa in aas_in_grp})
            col  = CODON_COUNT_COLORS.get(n_cod, "#888")
            members = ", ".join(f"{aa} ({AA_FULL.get(aa, aa)})" for aa in aas_in_grp)
            lbl_text = f"{n_cod} codon{'s' if n_cod>1 else ''}  —  {members}"
            n_aa = len(aas_in_grp)
            chart_h = max(120, n_aa * 36 + 60)  # scale height to number of AAs

            gf = tk.LabelFrame(parent, text=lbl_text, bg=BG_PANEL,
                               font=("Helvetica",9,"bold"), fg=col,
                               relief="solid", bd=2)
            gf.pack(fill="both", expand=True, padx=8, pady=(0,8))

            # Stats strip inside each group
            tu = sum(sub_u.values()); tp = sum(sub_p.values())
            tot_u_all = sum(fin_aa_u.values()) or 1
            tot_p_all = sum(fin_aa_p.values()) or 1
            stats_bar = tk.Frame(gf, bg=lighten_hex(col, 0.80))
            stats_bar.pack(fill="x", padx=4, pady=(4,2))
            tk.Label(stats_bar,
                     text=(f"Group total — User: {tu/tot_u_all:.3f} ({100*tu/tot_u_all:.1f}%)  "
                           f"│  Preset: {tp/tot_p_all:.3f} ({100*tp/tot_p_all:.1f}%)  "
                           f"│  Δ = {(tu/tot_u_all - tp/tot_p_all):+.4f}"),
                     bg=lighten_hex(col, 0.80), fg="#333",
                     font=("Helvetica", 8, "bold")).pack(side="left", padx=8, pady=3)

            _su = sub_u; _sp = sub_p
            def _rdr_g_cv(cc, cu=_su, cp=_sp, pc=col, nc=n_cod):
                draw_comparison_bar_chart(cc, cu, cp,
                    label_a="User", label_b="Preset",
                    color_a=USER_COLOR, color_b=pc,
                    title=f"{nc} codon{'s' if nc>1 else ''} — final probability",
                    top_n=len(cu)+len(cp), normalize=_nv_deg.get())
            self._scroll_chart(gf, _rdr_g_cv, height=chart_h,
                               min_w=520, min_h=chart_h)

    # ─────────────────────────────────────────────────────────────────────
    # Compare: Start → End Map tab
    # ─────────────────────────────────────────────────────────────────────

    def _populate_compare_codon_map(self, parent, s2f_u, s2f_p, _legend_fn, n_gen):
        """Standalone tab: start→end codon comparison — User vs Preset."""
        self._header(parent, "⚖  Start → End Codon Map — User vs Preset")
        _legend_fn(parent,
            "Select any start codon to compare its final AA distribution and "
            "reachable final codons between User and Preset.", bg="#E8EEF8")

        # ── Per-codon selector ────────────────────────────────────────────
        tk.Label(parent,
                 text="Per-starting-codon comparison — select a codon:",
                 font=("Helvetica",10,"bold"), bg=BG_PANEL, fg=ACCENT
                 ).pack(anchor="w", padx=10, pady=(4,2))
        _legend_fn(parent,
            "Paired bars show the final AA distribution from the selected start codon "
            "under User (blue, top bar) and Preset (purple, bottom bar). "
            "Table lists every reachable final codon with both probabilities and their difference.",
            bg="#E8EEF8")

        detail_row = tk.Frame(parent, bg=BG_PANEL)
        detail_row.pack(fill="both", expand=True, padx=6, pady=(0,8))

        # ── Left: listbox ─────────────────────────────────────────────────
        lb_frm = tk.Frame(detail_row, bg=BG_PANEL, width=148)
        lb_frm.pack(side="left", fill="y"); lb_frm.pack_propagate(False)

        tk.Label(lb_frm, text="Start codon", bg=BG_PANEL,
                 font=("Helvetica",9,"bold"), fg="#333").pack(anchor="w", padx=4, pady=(2,1))

        lb_vsb = tk.Scrollbar(lb_frm); lb_vsb.pack(side="right", fill="y")
        lb = tk.Listbox(lb_frm, yscrollcommand=lb_vsb.set, font=("Courier",10),
                        selectmode="single", bg="white",
                        selectbackground=ACCENT, selectforeground="white",
                        relief="solid", bd=1)
        lb.pack(fill="both", expand=True, padx=(4,0))
        lb_vsb.config(command=lb.yview)
        for c in VALID_CODONS:
            aa = CODON_TABLE.get(c, "?")
            lb.insert("end", f"{c}  {aa}")

        # ── Right: chart + info + table ───────────────────────────────────
        rf = tk.Frame(detail_row, bg=BG_PANEL)
        rf.pack(side="left", fill="both", expand=True, padx=(8,0))

        info_lbl = tk.Label(rf, text="Select a starting codon from the list on the left.",
                            bg="#F0F4FA", font=("Helvetica",9), fg="#555",
                            anchor="w", relief="solid", bd=1, padx=6, pady=4)
        info_lbl.pack(fill="x", padx=0, pady=(0,4))

        # Norm toggle
        _nv_det = tk.BooleanVar(value=False)
        nbar = tk.Frame(rf, bg="#F5F5F0", relief="solid", bd=1)
        nbar.pack(fill="x", pady=(0,4))
        tk.Label(nbar, text="Display:", bg="#F5F5F0",
                 font=("Helvetica",8,"bold")).pack(side="left", padx=(8,4))
        tk.Radiobutton(nbar, text="Probability (0–1)", variable=_nv_det, value=False,
                       bg="#F5F5F0", font=("Helvetica",8),
                       command=lambda: _on_select() if lb.curselection() else None
                       ).pack(side="left")
        tk.Radiobutton(nbar, text="Percentage (%)", variable=_nv_det, value=True,
                       bg="#F5F5F0", font=("Helvetica",8),
                       command=lambda: _on_select() if lb.curselection() else None
                       ).pack(side="left")

        # Chart — comparison bar (final AAs)
        tk.Label(rf, text="Final amino acid distribution:",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg="#333"
                 ).pack(anchor="w", padx=2, pady=(2,1))
        c_det = self._scroll_chart(rf,
            lambda cv: _on_select() if lb.curselection() else None,
            height=300, min_w=720, min_h=560)

        # Table — final codon level
        tk.Label(rf, text="All reachable final codons — User vs Preset  (sortable):",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg="#333"
                 ).pack(anchor="w", padx=2, pady=(4,1))
        tbl_frm = tk.Frame(rf, bg=BG_PANEL, height=180)
        tbl_frm.pack(fill="x", pady=(0,4)); tbl_frm.pack_propagate(False)
        vsb_t = tk.Scrollbar(tbl_frm); vsb_t.pack(side="right", fill="y")
        tv = ttk.Treeview(tbl_frm,
             columns=["rank","codon","aa","n_cod","user_p","preset_p","diff","favors"],
             show="headings", height=7, yscrollcommand=vsb_t.set)
        vsb_t.config(command=tv.yview); tv.pack(fill="both", expand=True)
        tv.tag_configure("user_hi",   background="#D6EAF8", foreground="#0C447C")
        tv.tag_configure("preset_hi", background="#E8DAEF", foreground="#6C3483")
        tv.tag_configure("neutral",   background="#F8F8F8")
        for cid, head, w in [
            ("rank",     "#",              35),
            ("codon",    "Final codon",    90),
            ("aa",       "AA",             60),
            ("n_cod",    "# codons",       70),
            ("user_p",   "User prob.",    100),
            ("preset_p", "Preset prob.",  100),
            ("diff",     "Diff (U–P)",     90),
            ("favors",   "Favors",         70),
        ]:
            tv.heading(cid, text=head,
                       command=lambda c=cid: self._sort_table(tv, c, False))
            tv.column(cid, width=w, anchor="center")

        def _on_select(ev=None):
            sel = lb.curselection()
            if not sel: return
            sc  = VALID_CODONS[sel[0]]
            saa = CODON_TABLE.get(sc, "?")
            fu  = s2f_u.get(sc, collections.Counter())
            fp  = s2f_p.get(sc, collections.Counter())
            tu  = sum(fu.values()) or 1
            tp  = sum(fp.values()) or 1

            info_lbl.config(
                text=(f"  Start: {sc}  ({AA_FULL.get(saa, saa)})  "
                      f"│  User surviving prob: {tu:.4f}  "
                      f"│  Preset surviving prob: {tp:.4f}"))

            # AA-level bar chart
            aau = collections.Counter()
            aap = collections.Counter()
            for fc, w in fu.items(): aau[CODON_TABLE.get(fc,"?")] += w
            for fc, w in fp.items(): aap[CODON_TABLE.get(fc,"?")] += w
            draw_comparison_bar_chart(c_det, aau, aap,
                label_a="User", label_b="Preset",
                color_a=USER_COLOR, color_b=PRESET_COLOR,
                title=f"{sc} ({saa}) → final AAs — User vs Preset",
                top_n=21, normalize=_nv_det.get())

            # Codon-level table
            for item in tv.get_children(): tv.delete(item)
            all_fc = sorted(set(list(fu.keys()) + list(fp.keys())))
            rows = [(fc, fu.get(fc,0)/tu, fp.get(fc,0)/tp) for fc in all_fc]
            rows.sort(key=lambda x: -(x[1]+x[2]))
            for rank, (fc, pu, pp) in enumerate(rows, 1):
                diff = pu - pp
                faa  = CODON_TABLE.get(fc, "?")
                favors = "User" if diff > 5e-4 else ("Preset" if diff < -5e-4 else "Equal")
                tag = ("user_hi" if diff > 5e-4
                       else "preset_hi" if diff < -5e-4
                       else "neutral")
                tv.insert("", "end", values=[
                    rank, fc, faa,
                    CODON_COUNT_MAP.get(faa, "?"),
                    f"{pu:.5f}", f"{pp:.5f}",
                    f"{diff:+.5f}", favors,
                ], tags=(tag,))

        lb.bind("<<ListboxSelect>>", _on_select)
        lb.selection_set(0)
        self.after(220, _on_select)



    def _build_start_end_tab(self, parent, start_to_fin, samp_start_to_fin=None):
        outer = tk.Frame(parent, bg=BG_PANEL)
        outer.pack(fill="both", expand=True)
        paned = tk.PanedWindow(outer, orient="horizontal", bg=BG_PANEL, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=4, pady=4)

        lf = tk.Frame(paned, bg=BG_PANEL, width=140)
        paned.add(lf, minsize=120)
        tk.Label(lf, text="Start codon", bg=BG_PANEL,
                 font=("Helvetica",9,"bold")).pack(anchor="w", padx=4)
        sb = tk.Scrollbar(lf); sb.pack(side="right", fill="y")
        lb = tk.Listbox(lf, yscrollcommand=sb.set, font=("Courier",10),
                        selectmode="single", bg="white",
                        selectbackground=ACCENT, selectforeground="white",
                        relief="solid", bd=1)
        lb.pack(fill="both", expand=True, padx=(4,0))
        sb.config(command=lb.yview)
        for c in VALID_CODONS:
            lb.insert("end", f"{c}  {CODON_TABLE.get(c,'?')}")

        rf = tk.Frame(paned, bg=BG_PANEL)
        paned.add(rf, minsize=400)
        self._se_info = tk.Label(rf, text="Select a starting codon on the left.",
                                  bg=BG_PANEL, font=("Helvetica",9), fg="#888")
        self._se_info.pack(anchor="w", padx=8, pady=(4,1))

        _nv_se = tk.BooleanVar(value=False)
        se_nb = tk.Frame(rf, bg="#F5F5F0", relief="solid", bd=1)
        se_nb.pack(fill="x", padx=4, pady=(0,2))
        tk.Label(se_nb, text="Display:", bg="#F5F5F0",
                 font=("Helvetica",8,"bold")).pack(side="left", padx=(8,4))
        tk.Radiobutton(se_nb, text="Probability (0–1)", variable=_nv_se, value=False,
                       bg="#F5F5F0", font=("Helvetica",8),
                       command=lambda: on_select(None) if lb.curselection() else None
                       ).pack(side="left")
        tk.Radiobutton(se_nb, text="Percentage (%)", variable=_nv_se, value=True,
                       bg="#F5F5F0", font=("Helvetica",8),
                       command=lambda: on_select(None) if lb.curselection() else None
                       ).pack(side="left")

        charts_row = tk.Frame(rf, bg=BG_PANEL)
        charts_row.pack(fill="both", expand=True)
        rc_frm = tk.Frame(charts_row, bg=BG_PANEL, relief="solid", bd=1)
        rc_frm.pack(side="left", fill="both", expand=True, padx=(4,4), pady=4)
        tk.Label(rc_frm, text="Actual sampled counts",
                 font=("Helvetica",9,"bold"), bg="#EAF3DE", fg="#3B6D11",
                 anchor="center").pack(fill="x")
        c_samp = self._scroll_chart(rc_frm,
            lambda cv: on_select() if lb.curselection() else None,
            height=440, min_w=680, min_h=520)

        tk.Label(rf, text="Individual copy outcomes",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg="#333"
                 ).pack(anchor="w", padx=8, pady=(4,1))
        tbl_frm = tk.Frame(rf, bg=BG_PANEL, height=120)
        tbl_frm.pack(fill="x", padx=4, pady=(0,4)); tbl_frm.pack_propagate(False)
        vsb2 = tk.Scrollbar(tbl_frm); vsb2.pack(side="right", fill="y")
        tv = ttk.Treeview(tbl_frm,
             columns=["copy","start","saa","final","faa","stopped","gen"],
             show="headings", height=5, yscrollcommand=vsb2.set)
        vsb2.config(command=tv.yview)
        tv.pack(fill="both", expand=True)
        tv.tag_configure("stop",    background="#FDEDEC", foreground="#A32D2D")
        tv.tag_configure("survive", background="#D5F5E3", foreground="#1A6B3A")
        tv.tag_configure("alt",     background="#FAFAFA")
        for cid,head,w in [("copy","Copy #",55),("start","Start codon",90),
                            ("saa","Start AA",80),("final","Final codon",90),
                            ("faa","Final AA",80),("stopped","Hit stop?",70),
                            ("gen","Stop gen",70)]:
            tv.heading(cid,text=head); tv.column(cid,width=w,anchor="center")

        _all_records = []

        def on_select(ev=None):
            sel = lb.curselection()
            if not sel: return
            sc  = VALID_CODONS[sel[0]]
            saa = CODON_TABLE.get(sc,"?")
            fin = start_to_fin.get(sc, collections.Counter())
            aa_dist = collections.Counter()
            for fc,w in fin.items(): aa_dist[CODON_TABLE.get(fc,"?")] += w
            prob_tot = sum(aa_dist.values()) or 1
            samp_dist = collections.Counter()
            if samp_start_to_fin:
                for fc,cnt in samp_start_to_fin.get(sc,{}).items():
                    samp_dist[CODON_TABLE.get(fc,"?")] += cnt
            n_stop = sum(1 for r in _all_records if r["start"]==sc and r["hit_stop"])
            n_tot  = sum(1 for r in _all_records if r["start"]==sc)
            self._se_info.config(
                text=(f"Start: {sc} ({saa})  | Theory surviving: {prob_tot:.3f}  "
                      f"| Sampled: {sum(samp_dist.values())} survived, "
                      f"{n_stop} stop of {n_tot} total"))
            draw_bar_chart(c_samp, samp_dist, f"Sampled: {sc}→final AA",
                           color_map=AA_COLOR_MAP, top_n=21, normalize=_nv_se.get())
            for item in tv.get_children(): tv.delete(item)
            for i,r in enumerate([r for r in _all_records if r["start"]==sc]):
                tag = "stop" if r["hit_stop"] else ("alt" if i%2 else "survive")
                tv.insert("","end", values=[i+1,r["start"],r["start_aa"],
                    r["final"],r["final_aa"],
                    "YES" if r["hit_stop"] else "no",
                    str(r["stop_gen"]) if r["hit_stop"] else "—"], tags=(tag,))

        lb.bind("<<ListboxSelect>>", on_select)
        lb.selection_set(0); self.after(120, lambda: on_select())
        return _all_records

    # ─────────────────────────────────────────────────────────────────────
    # Categories tab
    # ─────────────────────────────────────────────────────────────────────

    def _build_categories_tab(self, parent, enc_aa, fin_aa, enc_codon, fin_codon, n_gen):
        filter_outer = tk.LabelFrame(parent, text="Filters",
                                     bg=BG_PANEL, font=("Helvetica",9,"bold"), fg="#333")
        filter_outer.pack(fill="x", padx=8, pady=(6,4))

        prop_row = tk.Frame(filter_outer, bg=BG_PANEL)
        prop_row.pack(fill="x", padx=6, pady=(4,2))
        tk.Label(prop_row, text="Property:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold"), width=12, anchor="w").pack(side="left")
        self._cat_prop = tk.StringVar(value="all")
        for lbl,val,bg,fg in [("All","all",BG_PANEL,"#333"),
            ("Hydrophobic","hydrophobic",PROPERTY_GROUP_BG["hydrophobic"],PROPERTY_GROUPS["hydrophobic"][1]),
            ("Polar uncharged","polar_uncharged",PROPERTY_GROUP_BG["polar_uncharged"],PROPERTY_GROUPS["polar_uncharged"][1]),
            ("Pos. charged","pos_charged",PROPERTY_GROUP_BG["pos_charged"],PROPERTY_GROUPS["pos_charged"][1]),
            ("Neg. charged","neg_charged",PROPERTY_GROUP_BG["neg_charged"],PROPERTY_GROUPS["neg_charged"][1]),
            ("Special","special",PROPERTY_GROUP_BG["special"],PROPERTY_GROUPS["special"][1])]:
            tk.Radiobutton(prop_row, text=lbl, variable=self._cat_prop, value=val,
                           bg=bg, fg=fg,
                           selectcolor=lighten_hex(fg,0.6) if val!="all" else "#e0e8f8",
                           font=("Helvetica",9,"bold" if val!="all" else "normal"),
                           indicatoron=False, relief="solid", bd=1,
                           padx=7, pady=3, cursor="hand2",
                           command=lambda: self._refresh_categories(enc_aa,fin_aa,n_gen)
                           ).pack(side="left", padx=2)

        cnt_row = tk.Frame(filter_outer, bg=BG_PANEL)
        cnt_row.pack(fill="x", padx=6, pady=(2,6))
        tk.Label(cnt_row, text="# codons:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold"), width=12, anchor="w").pack(side="left")
        self._cat_cnt = tk.StringVar(value="all")
        for lbl,val,bg,fg in [("All","all",BG_PANEL,"#333"),
            ("1  (Met,Trp)","1",CODON_COUNT_BG[1],CODON_COUNT_COLORS[1]),
            ("2","2",CODON_COUNT_BG[2],CODON_COUNT_COLORS[2]),
            ("3  (Ile)","3",CODON_COUNT_BG[3],CODON_COUNT_COLORS[3]),
            ("4","4",CODON_COUNT_BG[4],CODON_COUNT_COLORS[4]),
            ("6  (Leu,Arg,Ser)","6",CODON_COUNT_BG[6],CODON_COUNT_COLORS[6])]:
            tk.Radiobutton(cnt_row, text=lbl, variable=self._cat_cnt, value=val,
                           bg=bg, fg=fg,
                           selectcolor=lighten_hex(fg,0.6) if val!="all" else "#e0e8f8",
                           font=("Helvetica",9,"bold" if val!="all" else "normal"),
                           indicatoron=False, relief="solid", bd=1,
                           padx=7, pady=3, cursor="hand2",
                           command=lambda: self._refresh_categories(enc_aa,fin_aa,n_gen)
                           ).pack(side="left", padx=2)

        sec_row = tk.Frame(filter_outer, bg=BG_PANEL)
        sec_row.pack(fill="x", padx=6, pady=(0,4))
        tk.Label(sec_row, text="Also limit:", bg=BG_PANEL,
                 font=("Helvetica",8), width=12, anchor="w").pack(side="left")
        self._show_aromatic = tk.BooleanVar(value=False)
        self._show_small    = tk.BooleanVar(value=False)
        tk.Checkbutton(sec_row, text="Aromatic only (Phe,Trp,Tyr,His)",
                       variable=self._show_aromatic, bg=BG_PANEL, font=("Helvetica",8),
                       command=lambda: self._refresh_categories(enc_aa,fin_aa,n_gen)
                       ).pack(side="left", padx=(0,12))
        tk.Checkbutton(sec_row, text="Small only (Ala,Gly,Ser)",
                       variable=self._show_small, bg=BG_PANEL, font=("Helvetica",8),
                       command=lambda: self._refresh_categories(enc_aa,fin_aa,n_gen)
                       ).pack(side="left")

        norm_row = tk.Frame(filter_outer, bg=BG_PANEL)
        norm_row.pack(fill="x", padx=6, pady=(0,6))
        tk.Label(norm_row, text="Display:", bg=BG_PANEL,
                 font=("Helvetica",9,"bold"), width=12, anchor="w").pack(side="left")
        self._cat_normalize = tk.BooleanVar(value=False)
        tk.Radiobutton(norm_row, text="Probability (0–1)", variable=self._cat_normalize,
                       value=False, bg=BG_PANEL, font=("Helvetica",9),
                       command=lambda: self._refresh_categories(enc_aa,fin_aa,n_gen)
                       ).pack(side="left")
        tk.Radiobutton(norm_row, text="Percentage (%)", variable=self._cat_normalize,
                       value=True, bg=BG_PANEL, font=("Helvetica",9),
                       command=lambda: self._refresh_categories(enc_aa,fin_aa,n_gen)
                       ).pack(side="left", padx=(0,16))

        self._cat_summary_lbl = tk.Label(parent, text="", bg=BG_PANEL,
                                          font=("Helvetica",8,"italic"), fg="#555")
        self._cat_summary_lbl.pack(anchor="w", padx=10, pady=(0,2))

        chart_outer = tk.Frame(parent, bg=BG_PANEL)
        chart_outer.pack(fill="both", expand=True, padx=4, pady=(0,2))
        lff = tk.Frame(chart_outer, bg=BG_PANEL, relief="solid", bd=1)
        lff.pack(side="left", fill="both", expand=True, padx=(0,3))
        tk.Label(lff, text="Encountered probability", font=("Helvetica",9,"bold"),
                 bg="#E6F1FB", fg=ACCENT, anchor="center").pack(fill="x")
        self._cat_canvas_enc = self._scroll_chart(lff,
            lambda cv: self._refresh_categories(enc_aa,fin_aa,n_gen),
            height=420, min_w=560, min_h=700)
        rff = tk.Frame(chart_outer, bg=BG_PANEL, relief="solid", bd=1)
        rff.pack(side="left", fill="both", expand=True, padx=(3,0))
        tk.Label(rff, text=f"Final probability (gen {n_gen})", font=("Helvetica",9,"bold"),
                 bg="#EAF3DE", fg="#3B6D11", anchor="center").pack(fill="x")
        self._cat_canvas_fin = self._scroll_chart(rff,
            lambda cv: self._refresh_categories(enc_aa,fin_aa,n_gen),
            height=420, min_w=560, min_h=700)

        tk.Label(parent, text="Category comparison table",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg="#333"
                 ).pack(anchor="w", padx=8, pady=(4,1))
        tbl_outer = tk.Frame(parent, bg=BG_PANEL, height=160)
        tbl_outer.pack(fill="x", padx=6, pady=(0,6)); tbl_outer.pack_propagate(False)
        vsb = tk.Scrollbar(tbl_outer); vsb.pack(side="right", fill="y")
        self._cat_tv = ttk.Treeview(tbl_outer,
            columns=["cat","members","enc_w","enc_pct","fin_w","fin_pct","ratio"],
            show="headings", height=5, yscrollcommand=vsb.set)
        vsb.config(command=self._cat_tv.yview); self._cat_tv.pack(fill="both", expand=True)
        for cid,head,w in [("cat","Category",160),("members","AAs in selection",230),
                            ("enc_w","Enc. prob.",95),("enc_pct","Enc. %",65),
                            ("fin_w","Final prob.",95),("fin_pct","Final %",65),
                            ("ratio","Final/Enc",90)]:
            self._cat_tv.heading(cid, text=head,
                command=lambda c=cid: self._sort_table(self._cat_tv,c,False))
            self._cat_tv.column(cid, width=w, anchor="w" if w>120 else "center")

        self._cat_enc_codon = enc_codon
        self._cat_fin_codon = fin_codon

        self.after(120, lambda: self._refresh_categories(enc_aa,fin_aa,n_gen))

    def _refresh_categories(self, enc_aa, fin_aa, n_gen):
        prop_sel = self._cat_prop.get()
        cnt_sel  = self._cat_cnt.get()
        only_ar  = self._show_aromatic.get()
        only_sm  = self._show_small.get()

        def passes(aa):
            if prop_sel!="all" and get_primary_group(aa)!=prop_sel: return False
            if cnt_sel!="all"  and get_codon_count(aa)!=int(cnt_sel): return False
            if only_ar and aa not in AA_AROMATIC: return False
            if only_sm and aa not in AA_SMALL:    return False
            return True

        selected = [aa for aa in ALL_AAS if passes(aa)]
        active = []
        if prop_sel!="all": active.append(PROPERTY_GROUPS[prop_sel][0])
        if cnt_sel!="all":  active.append(f"{cnt_sel}-codon AAs")
        if only_ar:  active.append("aromatic")
        if only_sm:  active.append("small")
        if active:
            self._cat_summary_lbl.config(
                text=f"Filters: {' + '.join(active)} → {', '.join(selected) or 'none'}")
        else:
            self._cat_summary_lbl.config(
                text=f"No filter — all {len(selected)} amino acids")

        if prop_sel!="all" and cnt_sel=="all":
            g_order = sorted(CODON_COUNT_GROUPS.keys())
            g_names = {n:f"{n} codon{'s' if n>1 else ''}" for n in g_order}
            g_cols  = CODON_COUNT_COLORS; g_bgs = CODON_COUNT_BG
            enc_bg  = {n: collections.Counter() for n in g_order}
            fin_bg  = {n: collections.Counter() for n in g_order}
            for aa in selected:
                n = get_codon_count(aa)
                enc_bg[n][aa] = enc_aa.get(aa,0); fin_bg[n][aa] = fin_aa.get(aa,0)
        elif cnt_sel!="all" and prop_sel=="all":
            g_order = list(PROPERTY_GROUPS.keys())
            g_names = {k:v[0] for k,v in PROPERTY_GROUPS.items()}
            g_cols  = {k:v[1] for k,v in PROPERTY_GROUPS.items()}
            g_bgs   = PROPERTY_GROUP_BG
            enc_bg  = {g: collections.Counter() for g in g_order}
            fin_bg  = {g: collections.Counter() for g in g_order}
            for aa in selected:
                pg = get_primary_group(aa)
                enc_bg[pg][aa] = enc_aa.get(aa,0); fin_bg[pg][aa] = fin_aa.get(aa,0)
        elif prop_sel!="all" and cnt_sel!="all":
            col   = PROPERTY_GROUPS[prop_sel][1]; bg2 = PROPERTY_GROUP_BG[prop_sel]
            lbl   = f"{PROPERTY_GROUPS[prop_sel][0]} · {cnt_sel}-codon"
            g_order=[lbl]; g_names={lbl:lbl}; g_cols={lbl:col}; g_bgs={lbl:bg2}
            enc_bg = {lbl: collections.Counter()}; fin_bg = {lbl: collections.Counter()}
            for aa in selected:
                enc_bg[lbl][aa]=enc_aa.get(aa,0); fin_bg[lbl][aa]=fin_aa.get(aa,0)
        else:
            g_order = list(PROPERTY_GROUPS.keys())
            g_names = {k:v[0] for k,v in PROPERTY_GROUPS.items()}
            g_cols  = {k:v[1] for k,v in PROPERTY_GROUPS.items()}
            g_bgs   = PROPERTY_GROUP_BG
            enc_bg  = {g: collections.Counter() for g in g_order}
            fin_bg  = {g: collections.Counter() for g in g_order}
            for aa in selected:
                pg = get_primary_group(aa)
                enc_bg[pg][aa]=enc_aa.get(aa,0); fin_bg[pg][aa]=fin_aa.get(aa,0)

        show_codons = (cnt_sel!="all")
        enc_cod_d   = getattr(self,"_cat_enc_codon",None)
        fin_cod_d   = getattr(self,"_cat_fin_codon",None)
        norm_v      = getattr(self,"_cat_normalize",None)
        nv          = norm_v.get() if norm_v else False

        self._draw_grouped_bars(self._cat_canvas_enc, enc_bg, g_order, g_names,
                                g_cols, g_bgs, "Encountered probability",
                                codon_counter=enc_cod_d if show_codons else None,
                                normalize=nv)
        self._draw_grouped_bars(self._cat_canvas_fin, fin_bg, g_order, g_names,
                                g_cols, g_bgs, f"Final probability (gen {n_gen})",
                                codon_counter=fin_cod_d if show_codons else None,
                                normalize=nv)

        for row in self._cat_tv.get_children(): self._cat_tv.delete(row)
        total_enc = sum(enc_aa.get(aa,0) for aa in selected) or 1
        total_fin = sum(fin_aa.get(aa,0) for aa in selected) or 1
        for gkey in PROPERTY_GROUPS:
            self._cat_tv.tag_configure(f"prop_{gkey}",
                background=PROPERTY_GROUP_BG.get(gkey,"#fff"))
        for n in CODON_COUNT_GROUPS:
            self._cat_tv.tag_configure(f"cnt_{n}",
                background=CODON_COUNT_BG.get(n,"#fff"))
        self._cat_tv.tag_configure("single", background="#EEF4FF")
        for g in g_order:
            ew = sum(enc_bg[g].values()); fw = sum(fin_bg[g].values())
            ratio = fw/ew if ew > 0 else 0
            members = ", ".join(sorted(enc_bg[g].keys()|fin_bg[g].keys()))
            tag = f"cnt_{g}" if isinstance(g,int) else \
                  (f"prop_{g}" if isinstance(g,str) and g in PROPERTY_GROUPS else "single")
            self._cat_tv.insert("","end", values=[
                g_names[g], members or "—",
                f"{ew/total_enc:.4f}", f"{100*ew/total_enc:.1f}%",
                f"{fw/total_fin:.4f}", f"{100*fw/total_fin:.1f}%",
                f"{ratio:.3f}"], tags=(tag,))

    def _draw_grouped_bars(self, canvas, data_by_group, group_order,
                           group_names, group_colors, group_bgs, title,
                           codon_counter=None, normalize=False):
        canvas.delete("all")
        W = canvas.winfo_width(); H = canvas.winfo_height()
        if W < 50 or H < 50: return

        items = []
        for g in group_order:
            gt = sum(data_by_group[g].values())
            items.append((g, group_names.get(g,str(g)), gt, 0))
            for aa in sorted(data_by_group[g].keys()):
                items.append((g, aa, data_by_group[g][aa], 1))
                if codon_counter is not None:
                    for codon in sorted(c for c,a in CODON_TABLE.items()
                                        if a==aa and c not in STOP_CODONS):
                        items.append((g, codon, codon_counter.get(codon,0), 2))
        if not items:
            canvas.create_text(W//2,H//2,text="No data",fill="#aaa",
                               font=("Helvetica",11)); return

        label_px = max((_text_px(label, 8, level > 0) + {0:0,1:16,2:32}[level]
                        for _, label, _, level in items), default=120)
        pad_l=int(min(245, max(130, label_px+14)))
        pad_r=96
        if W - pad_l - pad_r < 120:
            pad_l = min(pad_l, max(80, W//3))
            pad_r = min(pad_r, max(58, W//8))
        n = len(items); pad_t=28; pad_b=16
        avail = H-pad_t-pad_b
        unit_h = max(8, min(20, avail//max(n,1)-2))
        bh = {0:unit_h, 1:max(8,unit_h-3), 2:max(6,unit_h-5)}
        gap = min(3, max(1, (avail-sum(bh[it[3]] for it in items))//max(n+1,1)))
        chart_w = max(20, W-pad_l-pad_r)
        chart_right = pad_l + chart_w
        grand_total = sum(v for _,_,v,lv in items if lv==0) or 1
        all_probs = [v/grand_total for _,_,v,_ in items if v>0]
        max_v = max(all_probs) if all_probs else 1
        indent = {0:0, 1:16, 2:32}
        badge = "  [% of total]" if normalize else "  [probability 0–1]"
        _chart_title(canvas, W, 14, title+badge, font=("Helvetica",10,"bold"))
        y = pad_t
        for g,label,val,level in items:
            prob = val/grand_total; col=group_colors.get(g,"#888")
            bg2  = group_bgs.get(g,"#f9f9f9"); h=bh[level]; ind=indent[level]
            canvas.create_rectangle(0,y-1,W,y+h+1,fill=bg2,outline="")
            bw = max(2, int(prob/max_v*chart_w)) if prob>0 else 0
            x0 = pad_l+ind
            fill_col = col if level==0 else \
                       (lighten_hex(col,0.35) if level==1 else lighten_hex(col,0.60))
            canvas.create_rectangle(x0,y,x0+bw,y+h,fill=fill_col,outline="")
            if level==0:
                canvas.create_text(pad_l+ind-4,y+h//2,
                                   text=_fit_text(label, pad_l+ind-8, 8),
                                   anchor="e",font=("Helvetica",8,"bold"),fill="#222")
            elif level==1:
                hint = f" ({get_codon_count(label)})" if codon_counter else ""
                canvas.create_text(pad_l+ind-3,y+h//2,
                                   text=_fit_text(label+hint, pad_l+ind-7, 8, True),
                                   anchor="e",font=("Courier",8),fill="#444")
            else:
                canvas.create_text(pad_l+ind-3,y+h//2,
                                   text=_fit_text(label, pad_l+ind-7, 8, True),
                                   anchor="e",font=("Courier",8,"bold"),fill="#555")
            if prob>0:
                val_str = f"{prob*100:.1f}%" if normalize else f"{prob:.4f}"
                fnt = ("Helvetica",8,"bold") if level==0 else ("Helvetica",7)
                _safe_value_label(canvas, x0+bw, y+h//2, val_str,
                                  "#555", x0, chart_right, bw, font=fnt)
            else:
                if level>0:
                    canvas.create_text(x0+3,y+h//2,text="—",
                                       anchor="w",font=("Helvetica",7),fill="#aaa")
            y += h+gap
        canvas.create_line(pad_l,pad_t,pad_l,y,fill="#ccc",width=1)

    # ─────────────────────────────────────────────────────────────────────
    # Sampled tab
    # ─────────────────────────────────────────────────────────────────────

    def _build_sampled_tab(self, parent, records, samp_fin_codon, samp_fin_aa,
                           samp_start_to_fin, n_gen):
        n_total=len(records); n_stopped=sum(1 for r in records if r["hit_stop"])
        n_survived=n_total-n_stopped
        strip = tk.Frame(parent, bg="#EAF3DE", relief="solid", bd=1)
        strip.pack(fill="x", padx=6, pady=(4,6))
        for i,(l,v) in enumerate([("Total copies",str(n_total)),
                                   ("Survived",str(n_survived)),
                                   ("Hit stop",str(n_stopped)),
                                   ("Stop rate",f"{100*n_stopped/max(n_total,1):.1f}%")]):
            tk.Label(strip,text=l,bg="#EAF3DE",font=("Helvetica",8,"bold"),fg="#1A6B3A"
                     ).grid(row=0,column=i*2,padx=(14,2),pady=5)
            tk.Label(strip,text=v,bg="#c8e6c9",font=("Courier",10,"bold"),fg="#1A6B3A",
                     relief="solid",bd=1,padx=6).grid(row=0,column=i*2+1,padx=(0,12),pady=5)
        tk.Label(parent,text="Final amino acid distribution — sampled counts",
                 font=("Helvetica",10,"bold"),bg=BG_PANEL,fg="#3B6D11"
                 ).pack(anchor="w",padx=8,pady=(0,2))
        def _redraw(): draw_fn_aa(); draw_fn_cod()
        _nv = self._make_norm_toggle(parent, _redraw)
        chart_row=tk.Frame(parent,bg=BG_PANEL); chart_row.pack(fill="both",expand=True,padx=4)
        lf=tk.Frame(chart_row,bg=BG_PANEL,relief="solid",bd=1)
        lf.pack(side="left",fill="both",expand=True,padx=(0,3))
        tk.Label(lf,text="Final AAs (sampled)",font=("Helvetica",9,"bold"),
                 bg="#EAF3DE",fg="#3B6D11",anchor="center").pack(fill="x")
        def _draw_fn_aa_cv(c_aa):
            draw_bar_chart(c_aa,samp_fin_aa,"Sampled final AAs",
                color_map=AA_COLOR_MAP,top_n=21,normalize=_nv.get())
        _c_s_aa = self._scroll_chart(lf, _draw_fn_aa_cv, height=440, min_w=520, min_h=520)
        def draw_fn_aa(ev=None): _draw_fn_aa_cv(_c_s_aa)
        rf=tk.Frame(chart_row,bg=BG_PANEL,relief="solid",bd=1)
        rf.pack(side="left",fill="both",expand=True,padx=(3,0))
        tk.Label(rf,text="Final codons (sampled)",font=("Helvetica",9,"bold"),
                 bg="#EAF3DE",fg="#3B6D11",anchor="center").pack(fill="x")
        def _draw_fn_cod_cv(c_cod):
            draw_codon_bar_chart(c_cod,samp_fin_codon,"Sampled final codons",
                top_n=30,normalize=_nv.get())
        _c_s_cod = self._scroll_chart(rf, _draw_fn_cod_cv, height=440, min_w=520, min_h=640)
        def draw_fn_cod(ev=None): _draw_fn_cod_cv(_c_s_cod)
        tk.Label(parent,text="All copy outcomes  (green=survived, red=hit stop)",
                 font=("Helvetica",9,"bold"),bg=BG_PANEL,fg="#333"
                 ).pack(anchor="w",padx=8,pady=(6,1))
        tbl=tk.Frame(parent,bg=BG_PANEL); tbl.pack(fill="both",expand=True,padx=6,pady=(0,6))
        vsb=tk.Scrollbar(tbl); vsb.pack(side="right",fill="y")
        hsb=tk.Scrollbar(tbl,orient="horizontal"); hsb.pack(side="bottom",fill="x")
        cols=["idx","start","saa","final","faa","stopped","stop_gen"]
        tv=ttk.Treeview(tbl,columns=cols,show="headings",
                        yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        vsb.config(command=tv.yview); hsb.config(command=tv.xview)
        tv.pack(fill="both",expand=True)
        tv.tag_configure("stop",background="#FDEDEC",foreground="#A32D2D")
        tv.tag_configure("survive",background="#D5F5E3",foreground="#1A6B3A")
        tv.tag_configure("alt",background="#F8F8F8")
        for cid,head,w in [("idx","#",45),("start","Start codon",90),
                            ("saa","Start AA",80),("final","Final codon",90),
                            ("faa","Final AA",80),("stopped","Hit stop?",70),
                            ("stop_gen","Stop gen",70)]:
            tv.heading(cid,text=head); tv.column(cid,width=w,anchor="center")
        for i,r in enumerate(records):
            tag="stop" if r["hit_stop"] else ("alt" if i%2 else "survive")
            tv.insert("","end",values=[i+1,r["start"],r["start_aa"],
                r["final"],r["final_aa"],
                "YES" if r["hit_stop"] else "no",
                str(r["stop_gen"]) if r["hit_stop"] else "—"],tags=(tag,))

    # ─────────────────────────────────────────────────────────────────────
    # Per-codon stop analysis tab
    # ─────────────────────────────────────────────────────────────────────

    def _build_per_codon_stop_tab(self, parent, stop_data, n_gen):
        """
        Lets the user pick any starting codon and see:
          - Total stop probability emitted from that codon across all generations
          - Bar chart: which stop codon (TAA / TAG / TGA) was hit and how much
          - Bar chart: which specific mutation (pre-stop codon → stop) was the path
          - Sorted detail table: every (pre-codon, stop_codon) pair with probability
        """
        STOP_COLORS = {"TAA": "#E74C3C", "TAG": "#8E44AD", "TGA": "#E67E22"}

        # ── Selector row ──────────────────────────────────────────────────
        sel_row = tk.Frame(parent, bg=BG_PANEL)
        sel_row.pack(fill="x", padx=8, pady=(4,6))

        tk.Label(sel_row, text="Starting codon:", bg=BG_PANEL,
                 font=("Helvetica",10,"bold"), fg="#333").pack(side="left")

        codon_var = tk.StringVar(value=VALID_CODONS[0])
        codon_menu = ttk.Combobox(sel_row, textvariable=codon_var,
                                  values=VALID_CODONS, state="readonly",
                                  font=("Courier",11), width=8)
        codon_menu.pack(side="left", padx=(8,4))

        aa_lbl = tk.Label(sel_row, text="", bg=BG_PANEL,
                          font=("Helvetica",10,"bold"), fg=ACCENT)
        aa_lbl.pack(side="left", padx=(0,12))

        info_lbl = tk.Label(sel_row, text="", bg="#F0F6FF",
                            font=("Helvetica",9), fg="#333",
                            relief="solid", bd=1, padx=8, pady=3)
        info_lbl.pack(side="left", fill="x", expand=True)

        # ── Charts row ────────────────────────────────────────────────────
        charts_top = tk.Frame(parent, bg=BG_PANEL)
        charts_top.pack(fill="both", expand=True, padx=6, pady=(0,4))

        # Left: which stop codon was hit
        lf = tk.Frame(charts_top, bg=BG_PANEL, relief="solid", bd=1)
        lf.pack(side="left", fill="both", expand=True, padx=(0,4))
        tk.Label(lf, text="Which stop codon was reached",
                 font=("Helvetica",9,"bold"), bg="#FDEDEC", fg="#A32D2D",
                 anchor="center").pack(fill="x", ipady=3)
        self._legend(lf, "TAA = ochre · TAG = purple · TGA = orange. "
                     "Bar = probability flowing into that stop codon from this start.",
                     bg="#FEF5F5")
        c_which = self._scroll_chart(lf, lambda cv: _refresh(),
                                     height=200, min_w=420, min_h=240)

        # Right: which pre-mutation codon caused the stop
        rf = tk.Frame(charts_top, bg=BG_PANEL, relief="solid", bd=1)
        rf.pack(side="left", fill="both", expand=True, padx=(4,0))
        tk.Label(rf, text="Which codon mutated into a stop",
                 font=("Helvetica",9,"bold"), bg="#FEF9E7", fg="#7D6608",
                 anchor="center").pack(fill="x", ipady=3)
        self._legend(rf, "The codon that was 'live' just before the stop mutation. "
                     "Coloured by its own amino acid.",
                     bg="#FEFDF5")
        c_pre = self._scroll_chart(rf, lambda cv: _refresh(),
                                   height=200, min_w=560, min_h=420)

        # ── Detail table ──────────────────────────────────────────────────
        tk.Label(parent, text="Detailed stop paths from this start codon  (sortable):",
                 font=("Helvetica",9,"bold"), bg=BG_PANEL, fg="#333"
                 ).pack(anchor="w", padx=8, pady=(6,1))
        self._legend(parent,
            "Each row = one unique (pre-stop codon → stop codon) path. "
            "Probability = total weight from this start that followed this exact path. "
            "Row colour: red=TAA, purple=TAG, orange=TGA.",
            bg="#FEF5F5")

        tbl_outer = tk.Frame(parent, bg=BG_PANEL)
        tbl_outer.pack(fill="both", expand=True, padx=6, pady=(0,8))
        vsb = tk.Scrollbar(tbl_outer); vsb.pack(side="right", fill="y")
        cols = ["pre_c","pre_aa","stop_c","prob","prob_pct_start","prob_pct_total"]
        tv   = ttk.Treeview(tbl_outer, columns=cols, show="headings",
                            yscrollcommand=vsb.set)
        vsb.config(command=tv.yview); tv.pack(fill="both", expand=True)
        tv.tag_configure("TAA", background="#FADBD8", foreground="#922B21")
        tv.tag_configure("TAG", background="#E8DAEF", foreground="#6C3483")
        tv.tag_configure("TGA", background="#FAE5D3", foreground="#784212")
        tv.tag_configure("alt", background="#FAFAFA")
        for cid, head, w in [
            ("pre_c",           "Pre-stop codon",  110),
            ("pre_aa",          "Pre-stop AA",      90),
            ("stop_c",          "Stop codon hit",  110),
            ("prob",            "Probability",      110),
            ("prob_pct_start",  "% of this start",  110),
            ("prob_pct_total",  "% of all stops",   110),
        ]:
            tv.heading(cid, text=head,
                       command=lambda c=cid: self._sort_table(tv, c, False))
            tv.column(cid, width=w, anchor="center")

        # Pre-compute per-start-codon stop data from detail list
        # stop_data["detail"] = list of (start_c, start_aa, pre_c, pre_aa, stop_c, prob)
        total_all_stops = stop_data["total_prob"] or 1

        def _refresh(ev=None):
            sc  = codon_var.get()
            saa = CODON_TABLE.get(sc, "?")
            aa_lbl.config(text=f"({AA_FULL.get(saa, saa)})")

            # Filter detail for this start codon
            rows_raw = [(pre_c, pre_aa, stop_c, p)
                        for (start_c, start_aa, pre_c, pre_aa, stop_c, p)
                        in stop_data["detail"]
                        if start_c == sc]

            # Aggregate (pre_c, stop_c) pairs
            agg = collections.defaultdict(float)
            pre_aa_map = {}
            for pre_c, pre_aa, stop_c, p in rows_raw:
                agg[(pre_c, stop_c)] += p
                pre_aa_map[pre_c] = pre_aa

            total_from_start = sum(agg.values())
            stop_rate = 100 * total_from_start / total_all_stops

            info_lbl.config(
                text=(f"  Total stop probability from {sc}: {total_from_start:.4f}  "
                      f"│  {stop_rate:.2f}% of all stops in the simulation"))

            # Which stop codon chart
            by_stop = collections.Counter()
            for (pre_c, stop_c), p in agg.items():
                by_stop[stop_c] += p
            draw_bar_chart(c_which, by_stop,
                           f"Stop codons hit from {sc}",
                           color_map=STOP_COLORS, top_n=3, normalize=False)

            # Pre-stop codon chart
            by_pre = collections.Counter()
            for (pre_c, stop_c), p in agg.items():
                by_pre[pre_c] += p
            pre_cmap = {c: AA_COLOR_MAP.get(CODON_TABLE.get(c, "?"), "#888")
                        for c in by_pre}
            draw_bar_chart(c_pre, by_pre,
                           f"Pre-stop codons from {sc}",
                           color_map=pre_cmap, top_n=20, normalize=False)

            # Detail table
            for item in tv.get_children(): tv.delete(item)
            sorted_rows = sorted(agg.items(), key=lambda x: -x[1])
            for (pre_c, stop_c), p in sorted_rows:
                paa = pre_aa_map.get(pre_c, CODON_TABLE.get(pre_c, "?"))
                pct_start = (100 * p / total_from_start) if total_from_start > 0 else 0
                pct_total = 100 * p / total_all_stops
                tag = stop_c if stop_c in ("TAA","TAG","TGA") else "alt"
                tv.insert("", "end", values=[
                    pre_c, paa, stop_c,
                    f"{p:.5f}",
                    f"{pct_start:.2f}%",
                    f"{pct_total:.3f}%",
                ], tags=(tag,))

        codon_menu.bind("<<ComboboxSelected>>", _refresh)
        self.after(150, _refresh)

    # ─────────────────────────────────────────────────────────────────────
    # Stop codons tab
    # ─────────────────────────────────────────────────────────────────────

    def _build_stops_tab(self, parent, stop_data, stats, n_gen, per_gen_aa=None):
        total_start = stats.get("total_start_copies", stats["n_starts"])
        total_stop  = stop_data["total_prob"]
        stop_rate   = 100*total_stop/max(total_start,1)
        strip = tk.Frame(parent, bg="#FDEDEC", relief="solid", bd=1)
        strip.pack(fill="x", padx=6, pady=(4,6))
        for i,(l,v) in enumerate([
            ("Total start prob.", f"{total_start:.0f}"),
            ("Total stop prob.",  f"{total_stop:.3f}"),
            ("Overall stop rate", f"{stop_rate:.2f}%"),
            ("Stop codons hit",
             ", ".join(f"{c}:{v:.2f}" for c,v in sorted(stop_data["by_stop_codon"].items())))]):
            tk.Label(strip,text=l,bg="#FDEDEC",font=("Helvetica",8,"bold"),fg="#A32D2D"
                     ).grid(row=0,column=i*2,padx=(12,2),pady=5)
            tk.Label(strip,text=v,bg="#f5c6c6",font=("Courier",9,"bold"),fg="#A32D2D",
                     relief="solid",bd=1,padx=6).grid(row=0,column=i*2+1,padx=(0,10),pady=5)

        # ── Survival curve across generations ──
        if per_gen_aa:
            tk.Label(parent, text="Survival curve — how the population is depleted by stops:",
                     font=("Helvetica",9,"bold"), bg=BG_PANEL, fg="#A32D2D"
                     ).pack(anchor="w", padx=8, pady=(2,1))
            self._legend(parent,
                "Blue = surviving probability (% of starting pool that has NOT hit a "
                "stop codon by this generation). Orange dashed = number of distinct AAs "
                "still present. Red line marks the half-life (gen where survival drops below 50%).",
                bg="#FDEDEC")
            surv_w = [sum(per_gen_aa[gg].values()) for gg in range(len(per_gen_aa))]
            n_aas  = [sum(1 for v in per_gen_aa[gg].values() if v > 0)
                      for gg in range(len(per_gen_aa))]
            def _draw_surv_cv(c_surv):
                draw_survival_curve(c_surv, surv_w, n_aas,
                                    "Survival across generations",
                                    start_total=total_start, n_gen=len(per_gen_aa))
            self._scroll_chart(parent, _draw_surv_cv, height=320,
                               min_w=760, min_h=320)
            tk.Frame(parent, bg="#ccc", height=2).pack(fill="x", padx=8, pady=(2,4))

        def _redraw_stops(): draw_saa(); draw_prop(); draw_sc(); draw_pre()
        _nv_s = self._make_norm_toggle(parent, _redraw_stops)

        top_row=tk.Frame(parent,bg=BG_PANEL); top_row.pack(fill="both",expand=True,padx=4,pady=(0,2))
        lf=tk.Frame(top_row,bg=BG_PANEL,relief="solid",bd=1)
        lf.pack(side="left",fill="both",expand=True,padx=(0,3))
        tk.Label(lf,text="Stop prob. by starting AA",font=("Helvetica",9,"bold"),
                 bg="#FDEDEC",fg="#A32D2D",anchor="center").pack(fill="x")
        def _draw_saa_cv(c_aa):
            draw_bar_chart(c_aa,stop_data["by_start_aa"],"Stop prob. by start AA",
                color_map={aa:"#C0392B" for aa in stop_data["by_start_aa"]},
                top_n=21,normalize=_nv_s.get())
        _c_saa = self._scroll_chart(lf, _draw_saa_cv, height=420, min_w=520, min_h=520)
        def draw_saa(ev=None): _draw_saa_cv(_c_saa)

        pf=tk.Frame(top_row,bg=BG_PANEL,relief="solid",bd=1)
        pf.pack(side="left",fill="both",expand=True,padx=(3,3))
        tk.Label(pf,text="Stop prob. by starting property",font=("Helvetica",9,"bold"),
                 bg="#FDEDEC",fg="#A32D2D",anchor="center").pack(fill="x")
        stop_prop = property_stop_counter(stop_data)
        def _draw_prop_cv(c_prop):
            draw_bar_chart(c_prop, stop_prop, "Stop prob. by start property",
                color_map=property_color_map_by_name(),
                top_n=len(PROPERTY_GROUPS), normalize=_nv_s.get())
        _c_prop_stop = self._scroll_chart(pf, _draw_prop_cv, height=420,
                                          min_w=420, min_h=360)
        def draw_prop(ev=None): _draw_prop_cv(_c_prop_stop)

        rf=tk.Frame(top_row,bg=BG_PANEL,relief="solid",bd=1); rf.config(width=240)
        rf.pack(side="left",fill="both",padx=(3,0)); rf.pack_propagate(False)
        tk.Label(rf,text="Which stop codon",font=("Helvetica",9,"bold"),
                 bg="#FDEDEC",fg="#A32D2D",anchor="center").pack(fill="x")
        stop_cmap={"TAA":"#E74C3C","TAG":"#8E44AD","TGA":"#E67E22"}
        def _draw_sc_cv(c_sc):
            draw_bar_chart(c_sc,stop_data["by_stop_codon"],"Stop codon distribution",
                color_map=stop_cmap,top_n=3,normalize=_nv_s.get())
        _c_sc = self._scroll_chart(rf, _draw_sc_cv, height=420, min_w=220, min_h=300)
        def draw_sc(ev=None): _draw_sc_cv(_c_sc)

        mid=tk.Frame(parent,bg=BG_PANEL,relief="solid",bd=1)
        mid.pack(fill="both",expand=True,padx=4,pady=(2,2))
        tk.Label(mid,text="Pre-stop codons",font=("Helvetica",9,"bold"),
                 bg="#FEF9E7",fg="#7D6608",anchor="center").pack(fill="x")
        pre_cmap={c:AA_COLOR_MAP.get(CODON_TABLE.get(c,"?"),"#888") for c in stop_data["by_pre_codon"]}
        def _draw_pre_cv(c_pre):
            draw_bar_chart(c_pre,stop_data["by_pre_codon"],"Pre-stop codons (top 25)",
                color_map=pre_cmap,top_n=25,normalize=_nv_s.get())
        _c_pre = self._scroll_chart(mid, _draw_pre_cv, height=420, min_w=560, min_h=640)
        def draw_pre(ev=None): _draw_pre_cv(_c_pre)

        tk.Label(parent,text="Detailed stop events",font=("Helvetica",9,"bold"),
                 bg=BG_PANEL,fg="#333").pack(anchor="w",padx=8,pady=(4,1))
        tbl=tk.Frame(parent,bg=BG_PANEL); tbl.pack(fill="both",expand=True,padx=6,pady=(2,6))
        vsb=tk.Scrollbar(tbl); vsb.pack(side="right",fill="y")
        hsb=tk.Scrollbar(tbl,orient="horizontal"); hsb.pack(side="bottom",fill="x")
        cols=["start_c","start_aa","pre_c","pre_aa","stop_c","prob","prob_pct"]
        tv=ttk.Treeview(tbl,columns=cols,show="headings",
                        yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        vsb.config(command=tv.yview); hsb.config(command=tv.xview); tv.pack(fill="both",expand=True)
        tv.tag_configure("TAA",background="#FADBD8",foreground="#922B21")
        tv.tag_configure("TAG",background="#E8DAEF",foreground="#6C3483")
        tv.tag_configure("TGA",background="#FAE5D3",foreground="#784212")
        tv.tag_configure("alt",background="#FAFAFA")
        for cid,head,w in [("start_c","Start codon",90),("start_aa","Start AA",80),
                            ("pre_c","Pre-stop codon",90),("pre_aa","Pre-stop AA",80),
                            ("stop_c","Stop codon",90),("prob","Probability",90),
                            ("prob_pct","% of total stop",95)]:
            tv.heading(cid,text=head,command=lambda c=cid: self._sort_table(tv,c,False))
            tv.column(cid,width=w,anchor="center")
        agg=collections.defaultdict(float)
        for sc,sa,pc,pa,stop,p in stop_data["detail"]:
            agg[(sc,sa,pc,pa,stop)] += p
        total_p = stop_data["total_prob"] or 1
        for i,((sc,sa,pc,pa,stop),p) in enumerate(sorted(agg.items(),key=lambda x:-x[1])):
            tag=stop if stop in ("TAA","TAG","TGA") else "alt"
            tv.insert("","end",values=[sc,sa,pc,pa,stop,f"{p:.4f}",f"{100*p/total_p:.2f}%"],tags=(tag,))

    # ─────────────────────────────────────────────────────────────────────
    # Summary table
    # ─────────────────────────────────────────────────────────────────────

    def _build_summary_table(self, parent, enc_aa, enc_aa_cnt, fin_aa, stats, n_gen):
        total_copies = int(stats.get("total_start_copies", stats["n_starts"]))
        strip=tk.Frame(parent,bg="#E6F1FB",relief="solid",bd=1)
        strip.pack(fill="x",padx=6,pady=(6,4))
        for i,(l,v) in enumerate([("Unique starts",str(stats["n_starts"])),
                                   ("Total copies",str(total_copies)),
                                   ("Generations",str(n_gen)),
                                   ("Unique AAs",str(stats["unique_aas_seen"])),
                                   ("Unique codons",str(stats["unique_codons_seen"]))]):
            tk.Label(strip,text=l,bg="#E6F1FB",font=("Helvetica",8,"bold"),fg="#0C447C"
                     ).grid(row=0,column=i*2,padx=(14,2),pady=6)
            tk.Label(strip,text=v,bg="#dce8f8",font=("Courier",10,"bold"),fg="#0C447C",
                     relief="solid",bd=1,padx=6).grid(row=0,column=i*2+1,padx=(0,10),pady=6)
        tk.Label(parent,text="Amino acid distribution — encountered vs final",
                 font=("Helvetica",10,"bold"),bg=BG_PANEL,fg=ACCENT
                 ).pack(anchor="w",padx=8,pady=(4,2))

        # ── Biggest movers callout (transient vs attractor) ──
        teu = sum(enc_aa.values()) or 1
        tfu = sum(fin_aa.values()) or 1
        movers = sorted(
            ((aa, fin_aa.get(aa,0)/tfu - enc_aa.get(aa,0)/teu) for aa in ALL_AAS),
            key=lambda kv: kv[1])
        gainers = [m for m in reversed(movers) if m[1] > 1e-9][:3]   # attractors
        losers  = [m for m in movers if m[1] < -1e-9][:3]            # transients
        mv = tk.Frame(parent, bg="#EEF4FF", relief="solid", bd=1)
        mv.pack(fill="x", padx=6, pady=(0,4))
        def _fmt(lst):
            return ", ".join(f"{aa} ({d:+.3f})" for aa, d in lst) or "none"
        tk.Label(mv, text="▲ Attractors (final ≫ encountered): " + _fmt(gainers),
                 bg="#EEF4FF", fg="#1A6B3A", font=("Helvetica",8,"bold"),
                 anchor="w").pack(fill="x", padx=8, pady=(3,0))
        tk.Label(mv, text="▼ Transients (encountered ≫ final): " + _fmt(losers),
                 bg="#EEF4FF", fg="#A32D2D", font=("Helvetica",8,"bold"),
                 anchor="w").pack(fill="x", padx=8, pady=(0,3))

        leg=tk.Frame(parent,bg=BG_PANEL); leg.pack(fill="x",padx=8,pady=(0,4))
        for bg_col,label in [("#D6EAF8","Top 25% enc. prob."),
                              ("#D5F5E3","Top 25% final prob."),
                              ("#FEF9E7","Top 25% visit count"),
                              ("#FDEDEC","Top final% but not top enc%")]:
            tk.Label(leg,text="   ",bg=bg_col,relief="solid",bd=1).pack(side="left",padx=(0,2))
            tk.Label(leg,text=label+"   ",bg=BG_PANEL,font=("Helvetica",8),fg="#555"
                     ).pack(side="left")
        outer=tk.Frame(parent,bg=BG_PANEL); outer.pack(fill="both",expand=True,padx=6,pady=4)
        vsb=tk.Scrollbar(outer); vsb.pack(side="right",fill="y")
        hsb=tk.Scrollbar(outer,orient="horizontal"); hsb.pack(side="bottom",fill="x")
        cols=["aa","full","enc_w","enc_pct","enc_n","enc_npct","fin_w","fin_pct"]
        tv=ttk.Treeview(outer,columns=cols,show="headings",
                        yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        vsb.config(command=tv.yview); hsb.config(command=tv.xview); tv.pack(fill="both",expand=True)
        tv.tag_configure("top_enc",  background="#D6EAF8",font=("Helvetica",9,"bold"))
        tv.tag_configure("top_fin",  background="#D5F5E3",font=("Helvetica",9,"bold"))
        tv.tag_configure("top_cnt",  background="#FEF9E7")
        tv.tag_configure("top_fin2", background="#FDEDEC")
        tv.tag_configure("odd",      background="#FAFAFA")
        tv.tag_configure("even",     background="#FFFFFF")
        for cid,head,w,anchor in [("aa","AA",58,"center"),("full","Full name",155,"w"),
                                   ("enc_w","Enc. prob. ▼",110,"center"),("enc_pct","Enc. %",80,"center"),
                                   ("enc_n","Enc. count",90,"center"),("enc_npct","Enc. cnt %",80,"center"),
                                   ("fin_w","Final prob.",110,"center"),("fin_pct","Final %",80,"center")]:
            tv.heading(cid,text=head,command=lambda c=cid: self._sort_table(tv,c,False))
            tv.column(cid,width=w,anchor=anchor,minwidth=50)
        tew=sum(enc_aa.values()) or 1; tec=sum(enc_aa_cnt.values()) or 1
        tfw=sum(fin_aa.values()) or 1
        sorted_aas=sorted(enc_aa,key=lambda a:-enc_aa[a])
        n25=max(1,len(sorted_aas)//4)
        top25_enc=set(sorted_aas[:n25])
        top25_fin=set(sorted(fin_aa,key=lambda a:-fin_aa[a])[:n25])
        top25_cnt=set(sorted(enc_aa_cnt,key=lambda a:-enc_aa_cnt[a])[:n25])
        for ri,aa in enumerate(sorted_aas):
            ew=enc_aa[aa]; ec=enc_aa_cnt[aa]; fw=fin_aa.get(aa,0)
            vals=[aa,AA_FULL.get(aa,aa),f"{ew/tew:.4f}",f"{100*ew/tew:.1f}%",
                  str(ec),f"{100*ec/tec:.1f}%",f"{fw/tfw:.4f}",f"{100*fw/tfw:.1f}%"]
            if aa in top25_enc: tag="top_enc"
            elif aa in top25_fin and aa not in top25_enc: tag="top_fin2"
            elif aa in top25_fin: tag="top_fin"
            elif aa in top25_cnt: tag="top_cnt"
            else: tag="odd" if ri%2 else "even"
            tv.insert("","end",values=vals,tags=(tag,))

    # ─────────────────────────────────────────────────────────────────────
    # Export (stub — PDF for user results)
    # ─────────────────────────────────────────────────────────────────────

    def _export(self):
        messagebox.showinfo("Export",
            "PDF export is available for the active mode.\n"
            "This feature exports the User probability results.\n"
            "(Full PDF export code carried over from v2 — attach reportlab.)")

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = MutationExplorerApp()
    app.mainloop()
