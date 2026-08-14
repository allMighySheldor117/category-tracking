"""
Streamlit web app for the UI-independent scientific engine.

Run:
    streamlit run category_tracking_web.py
"""

from __future__ import annotations

import random
import time
from typing import Iterable, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from engine import category_analysis as _analysis
from engine import summaries as _summaries
from engine.exact_tracking import run_simulation as _engine_run_simulation
from engine.genetic_code import (
    CODON_TABLE,
    PROPERTY_LABELS,
    VALID_CODONS,
    get_primary_group_name,
)
from engine.models import ExactSimulationResult, SampledSimulationResult
from engine.mutation_matrix import (
    PRESET_AC,
    PRESET_AG,
    PRESET_AT,
    build_substitution_matrix,
)
from engine.sampled_tracking import run_experiment as _engine_run_experiment


TRAIT_NAMES = list(PROPERTY_LABELS.values())
APP_BG = "#F8FAFC"
PANEL_BG = "#FFFFFF"
SIDEBAR_BG = "#EEF2F7"
INK = "#111827"
MUTED = "#4B5563"
RULE = "#CBD5E1"
ACCENT_COLOR = "#0F766E"
PRESET_COLOR = "#6D28D9"
STOP_COLOR = "#B91C1C"
CAT_COLORS = {
    "Hydrophobic": "#B45309",
    "Polar uncharged": "#2563EB",
    "Positively charged": "#047857",
    "Negatively charged": "#BE123C",
    "Special (Cys/Gly/Pro)": "#7C3AED",
}


STYLE_HTML = f"""
    <style>
    :root {{
        --paper: {APP_BG};
        --panel: {PANEL_BG};
        --ink: {INK};
        --muted: {MUTED};
        --accent: {ACCENT_COLOR};
        --rail: {SIDEBAR_BG};
        --rule: {RULE};
    }}
    .stApp {{
        background: var(--paper);
        color: var(--ink);
    }}
    [data-testid="stSidebar"] {{
        background: var(--rail);
        border-right: 1px solid var(--rule);
    }}
    h1, h2, h3 {{
        letter-spacing: 0;
        text-wrap: balance;
        scroll-margin-top: 5rem;
        color: var(--ink);
    }}
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] {{
        overflow-wrap: anywhere;
    }}
    [data-testid="stMetricValue"] {{
        white-space: normal;
        line-height: 1.15;
        font-size: 1rem !important;
        font-weight: 650 !important;
        letter-spacing: 0;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: .76rem !important;
    }}
    a.skip-link {{
        position: fixed;
        left: .75rem;
        top: -5rem;
        padding: .45rem .65rem;
        background: var(--accent);
        color: white;
        border-radius: 4px;
        z-index: 1000;
    }}
    a.skip-link:focus-visible {{
        top: 1.25rem;
        outline: 3px solid #F59E0B;
        outline-offset: 2px;
    }}
    .stApp a, .stApp button, .stApp input, .stApp [role="button"] {{
        touch-action: manipulation;
    }}
    .stApp *:focus-visible {{
        outline: 3px solid #F59E0B;
        outline-offset: 2px;
    }}
    .lab-title {{
        display: flex;
        align-items: center;
        gap: .75rem;
        margin-bottom: .15rem;
    }}
    .codon-chip {{
        display: inline-block;
        min-width: 2.2rem;
        text-align: center;
        padding: .25rem .45rem;
        margin-right: .25rem;
        color: white;
        font-family: Consolas, monospace;
        font-weight: 700;
        border-radius: 4px;
    }}
    .small-note {{
        color: var(--muted);
        font-size: .85rem;
        overflow-wrap: anywhere;
    }}
    .phase7-product-hero {{
        display: grid;
        grid-template-columns: repeat(3, minmax(8rem, 1fr));
        gap: .75rem;
        align-items: stretch;
        margin: .75rem 0 1rem 0;
    }}
    .phase7-product-hero > div,
    .phase7-sidebar-guide,
    .phase7-result-context,
    .phase7-chart-shell,
    .phase7-table-context,
    .phase8-guided-intro,
    .phase8-sidebar-mode-guide,
    .phase8-result-interpretation {{
        border: 1px solid var(--rule);
        border-radius: 12px;
        background: rgba(255, 255, 255, .84);
        box-shadow: 0 10px 28px rgba(15, 23, 42, .055);
    }}
    .phase7-product-hero > div {{
        padding: .85rem .95rem;
    }}
    .phase7-product-hero strong {{
        display: block;
        color: var(--ink);
        font-size: .94rem;
        line-height: 1.15;
    }}
    .phase7-product-hero span {{
        display: block;
        color: var(--muted);
        font-size: .78rem;
        line-height: 1.35;
        margin-top: .25rem;
    }}
    .phase7-product-hero .phase7-kicker {{
        color: var(--accent);
        font-size: .72rem;
        font-weight: 750;
        letter-spacing: .06em;
        text-transform: uppercase;
    }}
    .phase7-product-hero .phase7-summary {{
        background:
            linear-gradient(135deg, rgba(15, 118, 110, .12), rgba(109, 40, 217, .10)),
            var(--panel);
    }}
    @media (max-width: 900px) {{
        .phase7-product-hero {{
            grid-template-columns: 1fr;
        }}
    }}
    code {{
        color: var(--ink);
        background: #E5E7EB;
        font-variant-numeric: tabular-nums;
        white-space: normal;
    }}
    div[data-testid="stMetric"] {{
        background: var(--panel);
        border: 1px solid var(--rule);
        border-radius: 8px;
        padding: .45rem .6rem;
        min-height: 72px;
    }}
    div[data-testid="stStatusWidget"] > div {{
        display: none !important;
    }}
    div[data-testid="stStatusWidget"] {{
        min-width: 142px;
    }}
    div[data-testid="stStatusWidget"]::before {{
        content: "";
        display: inline-block;
        width: 18px;
        height: 18px;
        margin-right: 7px;
        vertical-align: -4px;
        border-radius: 50%;
        background:
            linear-gradient(90deg, transparent 42%, var(--accent) 42% 58%, transparent 58%),
            radial-gradient(circle at 50% 18%, #2563EB 0 3px, transparent 4px),
            radial-gradient(circle at 50% 50%, #7C3AED 0 3px, transparent 4px),
            radial-gradient(circle at 50% 82%, #0F766E 0 3px, transparent 4px);
        animation: dna-toolbar-spin 1.1s linear infinite;
    }}
    div[data-testid="stStatusWidget"]::after {{
        content: "Mutating DNA";
        color: var(--ink);
        font-size: .78rem;
        font-weight: 650;
        letter-spacing: 0;
    }}
    .dna-loader {{
        display: flex;
        align-items: center;
        gap: .85rem;
        width: fit-content;
        max-width: 100%;
        margin: .45rem 0 1rem 0;
        padding: .7rem .9rem;
        border: 1px solid var(--rule);
        border-radius: 8px;
        background: var(--panel);
        color: var(--ink);
        box-shadow: 0 8px 20px rgba(15, 23, 42, .06);
    }}
    .dna-helix {{
        position: relative;
        width: 62px;
        height: 62px;
        flex: 0 0 62px;
    }}
    .dna-helix::before,
    .dna-helix::after {{
        content: "";
        position: absolute;
        top: 4px;
        width: 16px;
        height: 54px;
        border: 3px solid var(--accent);
        border-top-color: transparent;
        border-bottom-color: transparent;
        border-radius: 999px;
        animation: dna-wobble 1.25s ease-in-out infinite;
    }}
    .dna-helix::before {{
        left: 14px;
        transform: skewY(-22deg);
    }}
    .dna-helix::after {{
        right: 14px;
        border-color: #2563EB;
        border-top-color: transparent;
        border-bottom-color: transparent;
        transform: skewY(22deg);
        animation-delay: -.62s;
    }}
    .dna-rung {{
        position: absolute;
        left: 18px;
        width: 26px;
        height: 3px;
        border-radius: 999px;
        background: #7C3AED;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, .10);
        animation: dna-rung-pulse 1.25s ease-in-out infinite;
    }}
    .dna-rung:nth-child(1) {{ top: 13px; transform: rotate(20deg); }}
    .dna-rung:nth-child(2) {{ top: 29px; transform: rotate(-20deg); animation-delay: -.35s; }}
    .dna-rung:nth-child(3) {{ top: 45px; transform: rotate(20deg); animation-delay: -.7s; }}
    .dna-loader strong {{
        display: block;
        font-size: .92rem;
        line-height: 1.15;
    }}
    .dna-loader small {{
        color: var(--muted);
    }}
    @keyframes dna-toolbar-spin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    @keyframes dna-wobble {{
        0%, 100% {{ opacity: .75; }}
        50% {{ opacity: 1; }}
    }}
    @keyframes dna-rung-pulse {{
        0%, 100% {{ opacity: .55; }}
        50% {{ opacity: 1; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
        .dna-helix::before,
        .dna-helix::after,
        .dna-rung,
        div[data-testid="stStatusWidget"]::before {{ animation: none; }}
    }}
    </style>
    <a class="skip-link" href="#main-results">Skip to main content</a>
    """


def configure_page():
    st.set_page_config(
        page_title="Codon Category Tracking Lab",
        page_icon="AAA",
        layout="wide",
    )
    st.html(STYLE_HTML)


def render_product_hero() -> None:
    """Render visual hierarchy only; no scientific values are calculated here."""
    st.html(
        """
        <section class="phase7-product-hero" aria-label="Analysis workflow summary">
            <div class="phase7-summary">
                <strong>Configure</strong>
                <span>Mutation probabilities, sample size, seed, and view mode stay together.</span>
            </div>
            <div>
                <strong>Run</strong>
                <span>The app computes both user and preset paths for honest comparison.</span>
            </div>
            <div>
                <strong>Inspect</strong>
                <span>Fullscreen controls keep chart sections readable without changing the data.</span>
            </div>
        </section>
        """
    )


def parse_prob(value: str) -> float:
    """Parse the existing Streamlit probability input formats."""
    value = value.strip()
    try:
        if "/" in value:
            numerator, denominator = value.split("/", 1)
            return float(numerator.strip()) / float(denominator.strip())
        if value.endswith("%"):
            return float(value[:-1]) / 100.0
        return float(value)
    except Exception:
        raise ValueError(f"Cannot parse probability: '{value}'")


def probability_inputs(prefix: str, defaults: Tuple[str, str, str]) -> Tuple[float, float, float]:
    # phase8-error-guidance: keep probability errors concise and actionable.
    at_s = st.text_input(
        "A->T (= G<->C)",
        value=defaults[0],
        key=f"{prefix}_at",
        placeholder="e.g. 1/3…",
    )
    ag_s = st.text_input(
        "A->G (= T<->C)",
        value=defaults[1],
        key=f"{prefix}_ag",
        placeholder="e.g. 1/3…",
    )
    ac_s = st.text_input(
        "A->C (= T<->G)",
        value=defaults[2],
        key=f"{prefix}_ac",
        placeholder="e.g. 1/3…",
    )
    try:
        at, ag, ac = parse_prob(at_s), parse_prob(ag_s), parse_prob(ac_s)
    except ValueError as exc:
        st.error(
            f"{exc}. Use a decimal, percent, or fraction like 0.25, 25%, or 1/4.",
            icon=":material/error:",
        )
        st.stop()
    total = at + ag + ac
    if abs(total - 1.0) > 0.001:
        st.error(
            f"Set A->T, A->G, and A->C so they add to 1.0. Current sum is {total:.4f}.",
            icon=":material/error:",
        )
        st.stop()
    return at, ag, ac


@st.cache_data(show_spinner=False)
def run_cached(n_gen: int, copies: int, at: float, ag: float, ac: float, seed: int):
    start_weights = {codon: copies for codon in VALID_CODONS}
    matrix = build_substitution_matrix(at, ag, ac)
    sim = _engine_run_simulation(n_gen, matrix, start_weights)
    random.seed(seed)
    exp = _engine_run_experiment(n_gen, matrix, start_weights)
    return sim.to_legacy_tuple(), exp.to_legacy_tuple()


def codon_label(codon: str) -> str:
    aa = CODON_TABLE.get(codon, "Stop")
    return f"{codon} · {aa} · {get_primary_group_name(aa) if aa != 'Stop' else 'Stop'}"


def sampled_category_series(records: Iterable[dict], codon: str, n_gen: int) -> pd.DataFrame:
    return _analysis.sampled_category_series(records, codon, n_gen)


def exact_category_series(track_data: dict, codon: str, n_gen: int) -> pd.DataFrame:
    return _analysis.exact_category_series(track_data, codon, n_gen)


def sampled_all_category_series(records: Iterable[dict], n_gen: int) -> pd.DataFrame:
    return _analysis.sampled_all_category_series(records, n_gen)


def exact_all_category_series(track_data: dict, n_gen: int) -> pd.DataFrame:
    return _analysis.exact_all_category_series(track_data, n_gen)


def sampled_start_trait_survival_series(records: Iterable[dict], n_gen: int) -> pd.DataFrame:
    return _analysis.sampled_start_trait_survival_series(records, n_gen)


def exact_start_trait_survival_series(track_data: dict, n_gen: int) -> pd.DataFrame:
    return _analysis.exact_start_trait_survival_series(track_data, n_gen)


def sampled_start_trait_stop_percentage_series(records: Iterable[dict], n_gen: int) -> pd.DataFrame:
    return _analysis.sampled_start_trait_stop_percentage_series(records, n_gen)


def exact_start_trait_stop_percentage_series(track_data: dict, n_gen: int,
                                             copies_per_codon: float) -> pd.DataFrame:
    return _analysis.exact_start_trait_stop_percentage_series(
        track_data,
        n_gen,
        copies_per_codon,
    )


def codons_for_trait(trait: str) -> list[str]:
    return _analysis.codons_for_trait(trait)


def sampled_trait_codon_survival_series(records: Iterable[dict], trait: str,
                                        n_gen: int) -> pd.DataFrame:
    return _analysis.sampled_trait_codon_survival_series(records, trait, n_gen)


def exact_trait_codon_survival_series(track_data: dict, trait: str,
                                      n_gen: int) -> pd.DataFrame:
    return _analysis.exact_trait_codon_survival_series(track_data, trait, n_gen)


def sampled_trait_aa_survival_series(records: Iterable[dict], trait: str,
                                     n_gen: int) -> pd.DataFrame:
    return _analysis.sampled_trait_aa_survival_series(records, trait, n_gen)


def exact_trait_aa_survival_series(track_data: dict, trait: str,
                                   n_gen: int) -> pd.DataFrame:
    return _analysis.exact_trait_aa_survival_series(track_data, trait, n_gen)


def surviving_category_fraction_series(cat_df: pd.DataFrame) -> pd.DataFrame:
    return _analysis.surviving_category_fraction_series(cat_df)


def survival_balance_series(cat_df: pd.DataFrame, total_start_copies: float) -> pd.DataFrame:
    return _analysis.survival_balance_series(cat_df, total_start_copies)


def trait_codon_survival_summary(df: pd.DataFrame, copies_per_codon: float) -> pd.DataFrame:
    return _analysis.trait_codon_survival_summary(df, copies_per_codon)


def sampled_stop_series(records: Iterable[dict], codon: str, n_gen: int) -> pd.DataFrame:
    return _summaries.sampled_stop_series(records, codon, n_gen)


def exact_stop_series(track_data: dict, codon: str, n_gen: int) -> pd.DataFrame:
    return _summaries.exact_stop_series(track_data, codon, n_gen)


def no_more_change_from_df(
    df: pd.DataFrame,
    tolerance: float = 0.0,
    stable_status: str = "category counts stable",
) -> Tuple[str, str]:
    return _summaries.no_more_change_from_df(
        df,
        tolerance,
        stable_status,
    ).to_legacy_tuple()


def exact_no_more_change(track_data: dict, codon: str, n_gen: int,
                         basis: str = "Current computation",
                         alpha: float = 0.01) -> Tuple[str, str]:
    return _summaries.exact_no_more_change(
        track_data,
        codon,
        n_gen,
        basis,
        alpha,
    ).to_legacy_tuple()


def no_more_change_note(basis: str, alpha: float = 0.01) -> str:
    return _summaries.no_more_change_note(basis, alpha)


def category_chart(df: pd.DataFrame, title: str, marker_gen: str | None = None) -> go.Figure:
    fig = px.line(
        df,
        x="generation",
        y="value",
        color="category",
        color_discrete_map=CAT_COLORS,
        markers=True,
        title=title,
    )
    fig.update_layout(
        height=500,
        margin=dict(l=58, r=24, t=70, b=115),
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        font=dict(color=INK, size=13),
        title=dict(text=title, font=dict(size=16, color=INK), x=0.02, xanchor="left"),
        legend_title_text="Category",
        legend=dict(
            orientation="h",
            y=-0.26,
            x=0,
            xanchor="left",
            font=dict(size=12, color=INK),
        ),
        hovermode="x unified",
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_yaxes(
        title="Live category count" if df["value"].max() > 1 else "Exact live weight",
        gridcolor="#E5E7EB",
        zerolinecolor="#CBD5E1",
        automargin=True,
        rangemode="tozero",
    )
    fig.update_xaxes(
        title="Generation",
        dtick=max(1, int(df["generation"].max() / 10)),
        gridcolor="#F1F5F9",
        automargin=True,
    )
    if marker_gen and marker_gen.isdigit():
        fig.add_vline(
            x=int(marker_gen),
            line_width=2,
            line_dash="dash",
            line_color=ACCENT_COLOR,
            annotation_text="no more change",
            annotation_position="top left",
            annotation_font=dict(color=ACCENT_COLOR, size=12),
        )
    return fig


def surviving_fraction_chart(df: pd.DataFrame, title: str, marker_gen: str | None = None) -> go.Figure:
    fig = px.line(
        df,
        x="generation",
        y="value",
        color="category",
        color_discrete_map=CAT_COLORS,
        markers=True,
        title=title,
        hover_data={"surviving": ":.3f", "value": ":.3f"},
    )
    fig.update_layout(
        height=460,
        margin=dict(l=58, r=24, t=70, b=115),
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        font=dict(color=INK, size=13),
        title=dict(text=title, font=dict(size=16, color=INK), x=0.02, xanchor="left"),
        legend_title_text="Category",
        legend=dict(
            orientation="h",
            y=-0.27,
            x=0,
            xanchor="left",
            font=dict(size=12, color=INK),
        ),
        hovermode="x unified",
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_yaxes(
        title="Fraction in trait / surviving",
        tickformat=".0%",
        range=[0, 1],
        gridcolor="#E5E7EB",
        zerolinecolor="#CBD5E1",
        automargin=True,
    )
    fig.update_xaxes(
        title="Generation",
        dtick=max(1, int(df["generation"].max() / 10)),
        gridcolor="#F1F5F9",
        automargin=True,
    )
    if marker_gen and marker_gen.isdigit():
        fig.add_vline(
            x=int(marker_gen),
            line_width=2,
            line_dash="dash",
            line_color=ACCENT_COLOR,
            annotation_text="no more change",
            annotation_position="top left",
            annotation_font=dict(color=ACCENT_COLOR, size=12),
        )
    return fig


def stop_chart(df: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(
        x=df["generation"],
        y=df["new_stops"],
        name="new stops",
        marker_color=STOP_COLOR,
    )
    fig.add_trace(
        go.Scatter(
            x=df["generation"],
            y=df["cumulative_stops"],
            mode="lines+markers",
            name="cumulative stops",
            line=dict(color=PRESET_COLOR, width=3),
        )
    )
    fig.update_layout(
        height=340,
        margin=dict(l=58, r=24, t=58, b=90),
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        font=dict(color=INK, size=13),
        title=dict(text=title, font=dict(size=15, color=INK), x=0.02, xanchor="left"),
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0,
            xanchor="left",
            font=dict(size=12, color=INK),
        ),
        hovermode="x unified",
    )
    fig.update_xaxes(title="Generation", gridcolor="#F1F5F9", automargin=True)
    fig.update_yaxes(title="Copies / weight", gridcolor="#E5E7EB", automargin=True, rangemode="tozero")
    return fig


def survival_balance_chart(df: pd.DataFrame, title: str) -> go.Figure:
    fig = px.line(
        df,
        x="generation",
        y="value",
        color="state",
        color_discrete_map={"Surviving": ACCENT_COLOR, "Stopped": STOP_COLOR},
        markers=True,
        title=title,
    )
    fig.update_layout(
        height=340,
        margin=dict(l=58, r=24, t=58, b=88),
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        font=dict(color=INK, size=13),
        title=dict(text=title, font=dict(size=15, color=INK), x=0.02, xanchor="left"),
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0,
            xanchor="left",
            font=dict(size=12, color=INK),
        ),
        hovermode="x unified",
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_xaxes(title="Generation", gridcolor="#F1F5F9", automargin=True)
    fig.update_yaxes(title="Copies / weight", gridcolor="#E5E7EB", automargin=True, rangemode="tozero")
    return fig


def start_trait_survival_chart(df: pd.DataFrame, title: str) -> go.Figure:
    fig = px.line(
        df,
        x="generation",
        y="value",
        color="start_category",
        color_discrete_map=CAT_COLORS,
        markers=True,
        title=title,
    )
    fig.update_layout(
        height=420,
        margin=dict(l=58, r=24, t=64, b=112),
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        font=dict(color=INK, size=13),
        title=dict(text=title, font=dict(size=15, color=INK), x=0.02, xanchor="left"),
        legend_title_text="Starting trait",
        legend=dict(
            orientation="h",
            y=-0.27,
            x=0,
            xanchor="left",
            font=dict(size=12, color=INK),
        ),
        hovermode="x unified",
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_xaxes(title="Generation", gridcolor="#F1F5F9", automargin=True)
    fig.update_yaxes(
        title="Surviving copies / weight",
        gridcolor="#E5E7EB",
        automargin=True,
        rangemode="tozero",
    )
    return fig


def start_trait_stop_percentage_chart(df: pd.DataFrame, title: str) -> go.Figure:
    fig = px.line(
        df,
        x="generation",
        y="value",
        color="start_category",
        color_discrete_map=CAT_COLORS,
        markers=True,
        title=title,
        hover_data={
            "value": ":.2%",
            "stopped": ":,.2f",
            "total": ":,.2f",
            "start_category": True,
        },
    )
    fig.update_layout(
        height=420,
        margin=dict(l=58, r=24, t=64, b=112),
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        font=dict(color=INK, size=13),
        title=dict(text=title, font=dict(size=15, color=INK), x=0.02, xanchor="left"),
        legend_title_text="Starting trait",
        legend=dict(
            orientation="h",
            y=-0.27,
            x=0,
            xanchor="left",
            font=dict(size=12, color=INK),
        ),
        hovermode="x unified",
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_xaxes(title="Generation", gridcolor="#F1F5F9", automargin=True)
    fig.update_yaxes(
        title="Cumulative stop percentage",
        tickformat=".0%",
        gridcolor="#E5E7EB",
        automargin=True,
        rangemode="tozero",
    )
    return fig


def trait_codon_survival_chart(df: pd.DataFrame, trait: str, title: str) -> go.Figure:
    fig = px.line(
        df,
        x="generation",
        y="value",
        color="codon",
        markers=True,
        title=title,
        hover_data=["aa", "value"],
    )
    fig.update_layout(
        height=460,
        margin=dict(l=58, r=24, t=64, b=118),
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        font=dict(color=INK, size=13),
        title=dict(text=title, font=dict(size=15, color=INK), x=0.02, xanchor="left"),
        legend_title_text=f"{trait} codon",
        legend=dict(
            orientation="h",
            y=-0.28,
            x=0,
            xanchor="left",
            font=dict(size=12, color=INK),
        ),
        hovermode="x unified",
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
    fig.update_xaxes(title="Generation", gridcolor="#F1F5F9", automargin=True)
    fig.update_yaxes(
        title="Surviving copies / weight",
        gridcolor="#E5E7EB",
        automargin=True,
        rangemode="tozero",
    )
    return fig


def trait_aa_survival_chart(df: pd.DataFrame, trait: str, title: str) -> go.Figure:
    fig = px.line(
        df,
        x="generation",
        y="value",
        color="aa",
        markers=True,
        title=title,
    )
    fig.update_layout(
        height=420,
        margin=dict(l=58, r=24, t=64, b=108),
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        font=dict(color=INK, size=13),
        title=dict(text=title, font=dict(size=15, color=INK), x=0.02, xanchor="left"),
        legend_title_text=f"{trait} amino acid",
        legend=dict(
            orientation="h",
            y=-0.26,
            x=0,
            xanchor="left",
            font=dict(size=12, color=INK),
        ),
        hovermode="x unified",
    )
    fig.update_traces(line=dict(width=2.8), marker=dict(size=6))
    fig.update_xaxes(title="Generation", gridcolor="#F1F5F9", automargin=True)
    fig.update_yaxes(
        title="Surviving copies / weight",
        gridcolor="#E5E7EB",
        automargin=True,
        rangemode="tozero",
    )
    return fig


@st.dialog("Fullscreen section", width="large", icon=":material/fullscreen:")
def fullscreen_section(title: str, figures: list[tuple[str, go.Figure, str]]):
    st.subheader(title)
    st.caption("Press Esc or use the close button to return to the dashboard.")
    for chart_title, fig, key in figures:
        st.plotly_chart(fig, width="stretch", key=f"fullscreen_{key}")


@st.dialog("Two-codon comparison", width="large", icon=":material/fullscreen:")
def fullscreen_two_codon_comparison(codon_a: str, codon_b: str,
                                    sim: ExactSimulationResult,
                                    exp: SampledSimulationResult,
                                    n_gen: int, display_mode: str, no_more_basis: str,
                                    no_more_alpha: float):
    st.caption("Press Esc or use the close button to return to the dashboard.")
    left, right = st.columns(2)
    with left:
        render_codon_panel("Codon A", codon_a, sim, exp, n_gen, display_mode,
                           "fullscreen_codon_a", no_more_basis, no_more_alpha,
                           show_fullscreen=False)
    with right:
        render_codon_panel("Codon B", codon_b, sim, exp, n_gen, display_mode,
                           "fullscreen_codon_b", no_more_basis, no_more_alpha,
                           show_fullscreen=False)


def codon_to_codon_histogram(records: Iterable[dict], track_data: dict, codon: str,
                             generation: int, display_mode: str) -> go.Figure:
    if display_mode == "Sampled copies":
        df = _summaries.sampled_codon_outcome_table(records, codon, generation)
    else:
        df = _summaries.exact_codon_outcome_table(track_data, codon, generation)
    color_map = {**CAT_COLORS, "Stop": STOP_COLOR, "None": "#999999"}
    fig = px.bar(
        df,
        x="codon",
        y="value",
        color="category",
        color_discrete_map=color_map,
        hover_data=["amino_acid", "category", "value"],
        title=f"{codon}: codon outcomes at generation {generation}",
    )
    fig.update_layout(
        height=520,
        margin=dict(l=58, r=24, t=70, b=130),
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        font=dict(color=INK, size=13),
        title=dict(
            text=f"{codon}: codon outcomes at generation {generation}",
            font=dict(size=16, color=INK),
            x=0.02,
            xanchor="left",
        ),
        legend=dict(
            orientation="h",
            y=-0.28,
            x=0,
            xanchor="left",
            font=dict(size=12, color=INK),
        ),
    )
    fig.update_xaxes(title="Target codon", tickangle=-45, automargin=True)
    fig.update_yaxes(title="Copies / weight", gridcolor="#E5E7EB", automargin=True, rangemode="tozero")
    return fig


def all_codon_no_more_change(records: Iterable[dict], track_data: dict,
                             n_gen: int, display_mode: str,
                             no_more_basis: str = "Current computation",
                             no_more_alpha: float = 0.01) -> pd.DataFrame:
    return _summaries.all_codon_no_more_change(
        track_data,
        n_gen,
        no_more_basis,
        no_more_alpha,
    )


def no_more_change_chart(nm_df: pd.DataFrame) -> go.Figure | None:
    bar_df = nm_df[nm_df["no_more_change"].str.isnumeric()].copy()
    if bar_df.empty:
        return None
    bar_df["generation"] = bar_df["no_more_change"].astype(int)
    fig = px.bar(
        bar_df.sort_values("generation"),
        x="codon",
        y="generation",
        color="start_category",
        color_discrete_map=CAT_COLORS,
        hover_data=["aa", "status"],
        title="First generation where live category counts stop changing",
    )
    fig.update_layout(
        height=520,
        margin=dict(l=58, r=24, t=70, b=130),
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        font=dict(color=INK, size=13),
        title=dict(
            text="No more category change by starting codon",
            font=dict(size=16, color=INK),
            x=0.02,
            xanchor="left",
        ),
        legend=dict(
            orientation="h",
            y=-0.28,
            x=0,
            xanchor="left",
            font=dict(size=12, color=INK),
        ),
    )
    fig.update_xaxes(tickangle=-45, automargin=True)
    fig.update_yaxes(
        title="Generation",
        gridcolor="#E5E7EB",
        automargin=True,
        rangemode="tozero",
    )
    return fig


def render_no_more_change_panel(label: str, nm_df: pd.DataFrame,
                                panel_key: str) -> go.Figure | None:
    st.subheader(label)
    fig = no_more_change_chart(nm_df)
    if fig is not None:
        st.plotly_chart(
            fig,
            width="stretch",
            key=f"{panel_key}_no_more_change_chart",
        )
    st.dataframe(
        nm_df,
        width="stretch",
        hide_index=True,
        key=f"{panel_key}_no_more_change_table",
        column_config={
            "codon": st.column_config.TextColumn("Codon", pinned=True),
            "aa": st.column_config.TextColumn("AA"),
            "start_category": st.column_config.TextColumn("Start category"),
            "no_more_change": st.column_config.TextColumn("No more change"),
            "status": st.column_config.TextColumn("Status"),
        },
    )
    return fig


@st.dialog("No more category change", width="large", icon=":material/fullscreen:")
def fullscreen_no_more_change_comparison(user_sim: ExactSimulationResult,
                                         user_exp: SampledSimulationResult,
                                         preset_sim: ExactSimulationResult,
                                         preset_exp: SampledSimulationResult,
                                         n_gen: int, display_mode: str,
                                         no_more_basis: str,
                                         no_more_alpha: float):
    st.subheader("No more category change")
    st.caption("Press Esc or use the close button to return to the dashboard.")
    left, right = st.columns(2)
    with left:
        user_nm_df = all_codon_no_more_change(
            user_exp.records,
            user_sim.track_data,
            n_gen,
            display_mode,
            no_more_basis,
            no_more_alpha,
        )
        render_no_more_change_panel(
            "User probability",
            user_nm_df,
            "fullscreen_user",
        )
    with right:
        preset_nm_df = all_codon_no_more_change(
            preset_exp.records,
            preset_sim.track_data,
            n_gen,
            display_mode,
            no_more_basis,
            no_more_alpha,
        )
        render_no_more_change_panel(
            "Preset probability",
            preset_nm_df,
            "fullscreen_preset",
        )


def render_all_codon_population_panel(label: str, sim: ExactSimulationResult,
                                      exp: SampledSimulationResult,
                                      n_gen: int, display_mode: str,
                                      panel_key: str,
                                      show_fullscreen: bool = True):
    records = exp.records
    track_data = sim.track_data
    starting_metrics = _summaries.starting_population_metrics(sim, len(records))
    total_start_copies = starting_metrics.total_start_copies
    copies_per_codon = starting_metrics.copies_per_codon
    if display_mode == "Sampled copies":
        cat_df = sampled_all_category_series(records, n_gen)
        start_trait_df = sampled_start_trait_survival_series(records, n_gen)
        start_trait_stop_df = sampled_start_trait_stop_percentage_series(records, n_gen)
    else:
        cat_df = exact_all_category_series(track_data, n_gen)
        start_trait_df = exact_start_trait_survival_series(track_data, n_gen)
        start_trait_stop_df = exact_start_trait_stop_percentage_series(
            track_data,
            n_gen,
            copies_per_codon,
        )
    fraction_df = surviving_category_fraction_series(cat_df)
    survival_df = survival_balance_series(cat_df, total_start_copies)
    final_metrics = _summaries.final_population_metrics(
        cat_df,
        n_gen,
        total_start_copies,
    )
    final_live = final_metrics.final_live
    final_stopped = final_metrics.final_stopped
    stop_fraction = final_metrics.stop_fraction

    fraction_fig = surviving_fraction_chart(
        fraction_df,
        f"{label}: all-codon trait fraction among survivors",
    )
    survival_fig = survival_balance_chart(
        survival_df,
        f"{label}: total surviving vs stopped",
    )
    start_trait_fig = start_trait_survival_chart(
        start_trait_df,
        f"{label}: survival by starting trait",
    )
    start_trait_stop_fig = start_trait_stop_percentage_chart(
        start_trait_stop_df,
        f"{label}: stop percentage by starting trait",
    )

    with st.container(border=True):
        header, action = st.columns([0.78, 0.22], vertical_alignment="center")
        with header:
            st.subheader(label)
            st.caption("All starting codons pooled together with equal starting copies.")
        with action:
            if show_fullscreen:
                if st.button(
                    "Fullscreen",
                    icon=":material/fullscreen:",
                    key=f"{panel_key}_fullscreen",
                    width="stretch",
                ):
                    fullscreen_section(
                        f"{label}: all codons together",
                        [
                            ("Trait fraction among survivors", fraction_fig, f"{panel_key}_fraction"),
                            ("Survival by starting trait", start_trait_fig, f"{panel_key}_start_trait"),
                            (
                                "Stop percentage by starting trait",
                                start_trait_stop_fig,
                                f"{panel_key}_start_trait_stop",
                            ),
                            ("Surviving vs stopped", survival_fig, f"{panel_key}_survival"),
                        ],
                    )

        m1, m2, m3 = st.columns(3, vertical_alignment="top")
        with m1:
            st.metric("Starting population", f"{total_start_copies:,.0f}")
            st.caption("All valid starting codons combined.")
        with m2:
            st.metric("Final surviving", f"{final_live:,.2f}" if display_mode != "Sampled copies" else f"{final_live:,.0f}")
            st.caption(f"Generation {n_gen}.")
        with m3:
            st.metric("Final stopped", f"{stop_fraction:.1%}")
            st.caption(f"{final_stopped:,.2f} copies / weight stopped.")

        st.plotly_chart(
            fraction_fig,
            width="stretch",
            key=f"{panel_key}_all_fraction_chart",
        )
        st.plotly_chart(
            start_trait_fig,
            width="stretch",
            key=f"{panel_key}_start_trait_survival_chart",
        )
        st.plotly_chart(
            start_trait_stop_fig,
            width="stretch",
            key=f"{panel_key}_start_trait_stop_percentage_chart",
        )
        st.plotly_chart(
            survival_fig,
            width="stretch",
            key=f"{panel_key}_survival_chart",
        )


def render_trait_codon_survival_panel(label: str, sim: ExactSimulationResult,
                                      exp: SampledSimulationResult,
                                      n_gen: int, display_mode: str,
                                      panel_key: str, selected_trait: str,
                                      show_fullscreen: bool = True):
    records = exp.records
    track_data = sim.track_data
    copies_per_codon = _summaries.starting_population_metrics(
        sim,
        len(records),
    ).copies_per_codon
    if display_mode == "Sampled copies":
        trait_codon_df = sampled_trait_codon_survival_series(records, selected_trait, n_gen)
        trait_aa_df = sampled_trait_aa_survival_series(records, selected_trait, n_gen)
    else:
        trait_codon_df = exact_trait_codon_survival_series(track_data, selected_trait, n_gen)
        trait_aa_df = exact_trait_aa_survival_series(track_data, selected_trait, n_gen)
    summary_df = trait_codon_survival_summary(trait_codon_df, copies_per_codon)
    winner = summary_df.iloc[0] if not summary_df.empty else None
    trait_codon_fig = trait_codon_survival_chart(
        trait_codon_df,
        selected_trait,
        f"{label}: {selected_trait} codon survival",
    )
    trait_aa_fig = trait_aa_survival_chart(
        trait_aa_df,
        selected_trait,
        f"{label}: {selected_trait} amino-acid survival",
    )

    with st.container(border=True):
        header, action = st.columns([0.78, 0.22], vertical_alignment="center")
        with header:
            st.subheader(label)
            st.caption(f"One survival line for each starting codon in {selected_trait}.")
        with action:
            if show_fullscreen:
                if st.button(
                    "Fullscreen",
                    icon=":material/fullscreen:",
                    key=f"{panel_key}_fullscreen",
                    width="stretch",
                ):
                    fullscreen_section(
                        f"{label}: {selected_trait} codon survival",
                        [
                            (f"{selected_trait} codon survival", trait_codon_fig, f"{panel_key}_trait_codon"),
                            (
                                f"{selected_trait} amino-acid survival",
                                trait_aa_fig,
                                f"{panel_key}_trait_aa",
                            ),
                        ],
                    )
        if winner is not None:
            m1, m2, m3 = st.columns(3, vertical_alignment="top")
            with m1:
                st.metric("Most surviving", f"{winner['codon']} · {winner['aa']}")
                st.caption(f"Generation {n_gen}.")
            with m2:
                if display_mode == "Sampled copies":
                    st.metric("Surviving", f"{winner['final_surviving']:,.0f}")
                else:
                    st.metric("Surviving", f"{winner['final_surviving']:,.2f}")
                st.caption("Final surviving copies / weight.")
            with m3:
                st.metric("Stop percentage", f"{winner['stop_fraction']:.1%}")
                st.caption("Stopped from that starting codon.")
            st.dataframe(
                summary_df,
                width="stretch",
                hide_index=True,
                column_config={
                    "codon": st.column_config.TextColumn("Codon", pinned=True),
                    "aa": st.column_config.TextColumn("AA"),
                    "final_surviving": st.column_config.NumberColumn(
                        "Final surviving",
                        format="%.2f" if display_mode != "Sampled copies" else "%d",
                    ),
                    "stopped": st.column_config.NumberColumn(
                        "Stopped",
                        format="%.2f" if display_mode != "Sampled copies" else "%d",
                    ),
                    "stop_fraction": st.column_config.NumberColumn(
                        "Stop percentage",
                        format="percent",
                    ),
                },
            )
        st.plotly_chart(
            trait_codon_fig,
            width="stretch",
            key=f"{panel_key}_trait_codon_survival_chart",
        )
        st.plotly_chart(
            trait_aa_fig,
            width="stretch",
            key=f"{panel_key}_trait_aa_survival_chart",
        )


@st.dialog("All-codon population overview", width="large", icon=":material/fullscreen:")
def fullscreen_all_population_comparison(user_sim: ExactSimulationResult,
                                         user_exp: SampledSimulationResult,
                                         preset_sim: ExactSimulationResult,
                                         preset_exp: SampledSimulationResult,
                                         n_gen: int, display_mode: str):
    st.subheader("All-codon population overview")
    st.caption("Press Esc or use the close button to return to the dashboard.")
    left, right = st.columns(2)
    with left:
        render_all_codon_population_panel(
            "User probability",
            user_sim,
            user_exp,
            n_gen,
            display_mode,
            "fullscreen_all_codons_user",
            show_fullscreen=False,
        )
    with right:
        render_all_codon_population_panel(
            "Preset probability",
            preset_sim,
            preset_exp,
            n_gen,
            display_mode,
            "fullscreen_all_codons_preset",
            show_fullscreen=False,
        )


@st.dialog("Trait codon survival", width="large", icon=":material/fullscreen:")
def fullscreen_trait_survival_comparison(user_sim: ExactSimulationResult,
                                         user_exp: SampledSimulationResult,
                                         preset_sim: ExactSimulationResult,
                                         preset_exp: SampledSimulationResult,
                                         n_gen: int, display_mode: str,
                                         selected_trait: str):
    st.subheader("Trait codon survival")
    st.caption("Press Esc or use the close button to return to the dashboard.")
    left, right = st.columns(2)
    with left:
        render_trait_codon_survival_panel(
            "User probability",
            user_sim,
            user_exp,
            n_gen,
            display_mode,
            "fullscreen_trait_codons_user",
            selected_trait,
            show_fullscreen=False,
        )
    with right:
        render_trait_codon_survival_panel(
            "Preset probability",
            preset_sim,
            preset_exp,
            n_gen,
            display_mode,
            "fullscreen_trait_codons_preset",
            selected_trait,
            show_fullscreen=False,
        )


def render_codon_panel(label: str, codon: str, sim: ExactSimulationResult,
                       exp: SampledSimulationResult,
                       n_gen: int, display_mode: str, panel_key: str,
                       no_more_basis: str = "Current computation",
                       no_more_alpha: float = 0.01,
                       show_fullscreen: bool = True):
    records = exp.records
    track_data = sim.track_data
    if display_mode == "Sampled copies":
        cat_df = sampled_category_series(records, codon, n_gen)
        stop_df = sampled_stop_series(records, codon, n_gen)
    else:
        cat_df = exact_category_series(track_data, codon, n_gen)
        stop_df = exact_stop_series(track_data, codon, n_gen)
    stable_gen, stable_status = exact_no_more_change(
        track_data,
        codon,
        n_gen,
        no_more_basis,
        no_more_alpha,
    )
    aa = CODON_TABLE[codon]
    category = get_primary_group_name(aa)
    with st.container(border=True):
        header, action = st.columns([0.78, 0.22], vertical_alignment="center")
        with header:
            st.subheader(label)
        fraction_df = surviving_category_fraction_series(cat_df)
        cat_fig = category_chart(cat_df, f"{codon}: category counts", stable_gen)
        fraction_fig = surviving_fraction_chart(
            fraction_df,
            f"{codon}: trait fraction among surviving copies",
            stable_gen,
        )
        stop_fig = stop_chart(stop_df, f"{codon}: stop behavior")
        with action:
            if show_fullscreen:
                if st.button(
                    "Fullscreen",
                    icon=":material/fullscreen:",
                    key=f"{panel_key}_fullscreen",
                    width="stretch",
                ):
                    fullscreen_section(
                        f"{label} · {codon}",
                        [
                            (f"{codon}: category counts", cat_fig, f"{panel_key}_cat"),
                            (
                                f"{codon}: trait fraction among surviving copies",
                                fraction_fig,
                                f"{panel_key}_surviving_fraction",
                            ),
                            (f"{codon}: stop behavior", stop_fig, f"{panel_key}_stop"),
                        ],
                    )
        m1, m2, m3 = st.columns(3, vertical_alignment="top")
        with m1:
            st.metric("Starting codon", codon)
            st.caption(f"{aa} · {category}")
        with m2:
            st.metric("No more change", stable_gen)
            st.caption(no_more_change_note(no_more_basis, no_more_alpha))
        with m3:
            st.metric("Status", stable_status)
            st.caption(display_mode)
        st.plotly_chart(
            cat_fig,
            width="stretch",
            key=f"{panel_key}_category_chart",
        )
        st.plotly_chart(
            fraction_fig,
            width="stretch",
            key=f"{panel_key}_surviving_fraction_chart",
        )
        st.plotly_chart(
            stop_fig,
            width="stretch",
            key=f"{panel_key}_stop_chart",
        )


@st.dialog("Codon focus comparison", width="large", icon=":material/fullscreen:")
def fullscreen_codon_focus_comparison(selected_codon: str,
                                      user_sim: ExactSimulationResult,
                                      user_exp: SampledSimulationResult,
                                      preset_sim: ExactSimulationResult,
                                      preset_exp: SampledSimulationResult,
                                      n_gen: int, display_mode: str,
                                      no_more_basis: str,
                                      no_more_alpha: float):
    st.subheader("Codon focus comparison")
    st.caption("Press Esc or use the close button to return to the dashboard.")
    left, right = st.columns(2)
    with left:
        render_codon_panel(
            "User probability",
            selected_codon,
            user_sim,
            user_exp,
            n_gen,
            display_mode,
            "fullscreen_compare_user",
            no_more_basis,
            no_more_alpha,
            show_fullscreen=False,
        )
    with right:
        render_codon_panel(
            "Preset probability",
            selected_codon,
            preset_sim,
            preset_exp,
            n_gen,
            display_mode,
            "fullscreen_compare_preset",
            no_more_basis,
            no_more_alpha,
            show_fullscreen=False,
        )


def render_whole_population_view(view_mode: str, run_label: str,
                                 user_sim: ExactSimulationResult,
                                 user_exp: SampledSimulationResult,
                                 preset_sim: ExactSimulationResult,
                                 preset_exp: SampledSimulationResult,
                                 sim: ExactSimulationResult,
                                 exp: SampledSimulationResult,
                                 n_gen: int, display_mode: str):
    st.html('<span id="main-results"></span>')
    overview_header, overview_action = st.columns([0.78, 0.22], vertical_alignment="center")
    with overview_header:
        st.subheader("All-codon population overview")
        st.caption("Pooled view across every valid starting codon.")
    if view_mode == "Compare both":
        with overview_action:
            if st.button(
                "Fullscreen",
                icon=":material/fullscreen:",
                key="compare_all_population_fullscreen",
                width="stretch",
            ):
                fullscreen_all_population_comparison(
                    user_sim,
                    user_exp,
                    preset_sim,
                    preset_exp,
                    n_gen,
                    display_mode,
                )
        left, right = st.columns(2)
        with left:
            render_all_codon_population_panel(
                "User probability",
                user_sim,
                user_exp,
                n_gen,
                display_mode,
                "all_codons_user",
            )
        with right:
            render_all_codon_population_panel(
                "Preset probability",
                preset_sim,
                preset_exp,
                n_gen,
                display_mode,
                "all_codons_preset",
            )
    else:
        render_all_codon_population_panel(
            run_label,
            sim,
            exp,
            n_gen,
            display_mode,
            "all_codons_selected",
        )

    st.space("medium")
    trait_header, trait_action = st.columns([0.78, 0.22], vertical_alignment="center")
    with trait_header:
        st.subheader("Trait codon survival")
    selected_trait = st.selectbox(
        "Trait drilldown",
        TRAIT_NAMES,
        key="whole_population_trait",
        bind="query-params",
        help="Choose a starting trait to show one survival line per codon in that trait.",
    )
    if view_mode == "Compare both":
        with trait_action:
            if st.button(
                "Fullscreen",
                icon=":material/fullscreen:",
                key="compare_trait_survival_fullscreen",
                width="stretch",
            ):
                fullscreen_trait_survival_comparison(
                    user_sim,
                    user_exp,
                    preset_sim,
                    preset_exp,
                    n_gen,
                    display_mode,
                    selected_trait,
                )
        left, right = st.columns(2)
        with left:
            render_trait_codon_survival_panel(
                "User probability",
                user_sim,
                user_exp,
                n_gen,
                display_mode,
                "trait_codons_user",
                selected_trait,
            )
        with right:
            render_trait_codon_survival_panel(
                "Preset probability",
                preset_sim,
                preset_exp,
                n_gen,
                display_mode,
                "trait_codons_preset",
                selected_trait,
            )
    else:
        render_trait_codon_survival_panel(
            run_label,
            sim,
            exp,
            n_gen,
            display_mode,
            "trait_codons_selected",
            selected_trait,
        )


def render_codon_focus_view(view_mode: str, run_label: str, selected_codon: str,
                            compare_codon: str,
                            user_sim: ExactSimulationResult,
                            user_exp: SampledSimulationResult,
                            preset_sim: ExactSimulationResult,
                            preset_exp: SampledSimulationResult,
                            sim: ExactSimulationResult,
                            exp: SampledSimulationResult,
                            n_gen: int, display_mode: str, no_more_basis: str,
                            no_more_alpha: float, generation: int):
    if view_mode == "Compare both":
        st.html('<span id="main-results"></span>')
        compare_header, compare_action = st.columns([0.78, 0.22], vertical_alignment="center")
        with compare_header:
            st.subheader("Codon focus comparison")
        with compare_action:
            if st.button(
                "Fullscreen",
                icon=":material/fullscreen:",
                key="compare_codon_focus_fullscreen",
                width="stretch",
            ):
                fullscreen_codon_focus_comparison(
                    selected_codon,
                    user_sim,
                    user_exp,
                    preset_sim,
                    preset_exp,
                    n_gen,
                    display_mode,
                    no_more_basis,
                    no_more_alpha,
                )
        left, right = st.columns(2)
        with left:
            render_codon_panel("User probability", selected_codon, user_sim, user_exp,
                               n_gen, display_mode, "compare_user",
                               no_more_basis, no_more_alpha)
        with right:
            render_codon_panel("Preset probability", selected_codon, preset_sim, preset_exp,
                               n_gen, display_mode, "compare_preset",
                               no_more_basis, no_more_alpha)
    else:
        st.html('<span id="main-results"></span>')
        render_codon_panel(run_label, selected_codon, sim, exp, n_gen, display_mode,
                           "selected", no_more_basis, no_more_alpha)

        st.space("medium")
        comparison_header, comparison_action = st.columns([0.78, 0.22], vertical_alignment="center")
        with comparison_header:
            st.subheader("Two-codon comparison")
        with comparison_action:
            if st.button(
                "Fullscreen",
                icon=":material/fullscreen:",
                key="two_codon_comparison_fullscreen",
                width="stretch",
            ):
                fullscreen_two_codon_comparison(
                    selected_codon,
                    compare_codon,
                    sim,
                    exp,
                    n_gen,
                    display_mode,
                    no_more_basis,
                    no_more_alpha,
                )
        left, right = st.columns(2)
        with left:
            render_codon_panel("Codon A", selected_codon, sim, exp, n_gen,
                               display_mode, "codon_a", no_more_basis,
                               no_more_alpha)
        with right:
            render_codon_panel("Codon B", compare_codon, sim, exp, n_gen,
                               display_mode, "codon_b", no_more_basis,
                               no_more_alpha)

    st.space("medium")
    outcome_header, outcome_action = st.columns([0.78, 0.22], vertical_alignment="center")
    with outcome_header:
        st.subheader("Selected codon outcomes at one generation")
    source_sim = user_sim if view_mode != "Preset" else preset_sim
    source_exp = user_exp if view_mode != "Preset" else preset_exp
    outcome_fig = codon_to_codon_histogram(
        source_exp.records,
        source_sim.track_data,
        selected_codon,
        generation,
        display_mode,
    )
    with outcome_action:
        if st.button(
            "Fullscreen",
            icon=":material/fullscreen:",
            key="codon_outcomes_fullscreen",
            width="stretch",
        ):
            fullscreen_section(
                "Selected codon outcomes",
                [("Codon outcomes", outcome_fig, "codon_outcomes")],
            )
    st.plotly_chart(
        outcome_fig,
        width="stretch",
        key="codon_outcomes_chart",
    )

    st.space("medium")
    summary_header, summary_action = st.columns([0.78, 0.22], vertical_alignment="center")
    with summary_header:
        st.subheader("No more category change for all starting codons")

    if view_mode == "Compare both":
        with summary_action:
            if st.button(
                "Fullscreen",
                icon=":material/fullscreen:",
                key="compare_no_more_change_fullscreen",
                width="stretch",
            ):
                fullscreen_no_more_change_comparison(
                    user_sim,
                    user_exp,
                    preset_sim,
                    preset_exp,
                    n_gen,
                    display_mode,
                    no_more_basis,
                    no_more_alpha,
                )
        left, right = st.columns(2)
        with left:
            user_nm_df = all_codon_no_more_change(
                user_exp.records,
                user_sim.track_data,
                n_gen,
                display_mode,
                no_more_basis,
                no_more_alpha,
            )
            render_no_more_change_panel(
                "User probability",
                user_nm_df,
                "user",
            )
        with right:
            preset_nm_df = all_codon_no_more_change(
                preset_exp.records,
                preset_sim.track_data,
                n_gen,
                display_mode,
                no_more_basis,
                no_more_alpha,
            )
            render_no_more_change_panel(
                "Preset probability",
                preset_nm_df,
                "preset",
            )
    else:
        nm_df = all_codon_no_more_change(
            exp.records,
            sim.track_data,
            n_gen,
            display_mode,
            no_more_basis,
            no_more_alpha,
        )
        fig = no_more_change_chart(nm_df)
        if fig is not None:
            with summary_action:
                if st.button(
                    "Fullscreen",
                    icon=":material/fullscreen:",
                    key="no_more_change_fullscreen",
                    width="stretch",
                ):
                    fullscreen_section(
                        "No more category change",
                        [("No more category change", fig, "no_more_change")],
                    )
        render_no_more_change_panel(run_label, nm_df, "selected")


def main():
    configure_page()
    st.title("Codon Category Tracking Lab")
    st.caption(
        "Track exact starting codons through amino-acid property categories, "
        "with integer copy simulations and exact probability weights side by side when needed."
    )
    st.html(
        """
        <div style="margin:.8rem 0 1.1rem 0;">
            <span class="codon-chip" style="background:#B84242;">T</span>
            <span class="codon-chip" style="background:#146C72;">A</span>
            <span class="codon-chip" style="background:#7A4E8A;">C</span>
            <span class="codon-chip" style="background:#C88719;">G</span>
            <span class="small-note">exact codon copies -> category counts -> stop behavior</span>
        </div>
        """,
    )
    render_product_hero()
    st.caption(
        "Configure → Run → Inspect: set the sidebar once, then read each result section from top to bottom."
    )
    dashboard_view = st.segmented_control(
        "Workspace",
        ["Codon focus", "Whole population"],
        default="Codon focus",
        required=True,
        key="workspace",
        bind="query-params",
        width="stretch",
    )

    with st.sidebar:
        st.header("Simulation")
        st.caption("Configure once in the sidebar; the visible workspace updates together.")
        st.caption("Your probability and Preset use the same controls so Compare both stays honest.")
        n_gen = st.number_input("Generations", min_value=1, max_value=2000, value=20, step=1)
        copies = st.number_input(
            "Copies per codon",
            min_value=1,
            max_value=1_000_000,
            value=100,
            step=1,
        )
        seed = st.number_input("Sampling seed", min_value=0, max_value=999999, value=7, step=1)

        st.space("small")
        st.subheader("Your probability")
        user_probs = probability_inputs("user", ("1/3", "1/3", "1/3"))

        st.space("small")
        st.subheader("Preset probability")
        preset_probs = probability_inputs(
            "preset",
            (str(PRESET_AT), str(PRESET_AG), str(PRESET_AC)),
        )

        st.space("small")
        view_mode = st.segmented_control(
            "View",
            ["Your probability", "Preset", "Compare both"],
            default="Your probability",
            required=True,
            key="view",
            bind="query-params",
            width="stretch",
        )
        display_mode = st.segmented_control(
            "Data type",
            ["Sampled copies", "Exact probability"],
            default="Sampled copies",
            required=True,
            key="data_type",
            bind="query-params",
            width="stretch",
        )
        st.caption("Exact probability is deterministic; Sampled copies is the stochastic copy simulation.")
        no_more_basis = st.segmented_control(
            "No more change basis",
            ["Current computation", "Exact surviving trait fractions"],
            default="Current computation",
            required=True,
            key="no_more_basis",
            bind="query-params",
            width="stretch",
        )
        no_more_alpha = st.number_input(
            "Alpha for exact surviving fractions",
            min_value=0.0,
            max_value=1.0,
            value=0.01,
            step=0.001,
            format="%.4f",
            help=(
                "Used only when no more change basis is Exact surviving trait fractions. "
                "The stable state starts when every later trait fraction stays within alpha."
            ),
        )
        selected_codon = st.selectbox(
            "Selected codon",
            VALID_CODONS,
            format_func=codon_label,
            key="selected_codon",
            bind="query-params",
        )
        compare_codon = st.selectbox(
            "Compare with codon",
            VALID_CODONS,
            index=1,
            format_func=codon_label,
            key="compare_codon",
            bind="query-params",
        )
        generation = st.slider("Codon-outcome generation", 1, int(n_gen), min(5, int(n_gen)))

    loading_slot = st.empty()
    run_started_at = time.perf_counter()
    with loading_slot.container():
        st.html(
            """
            <div class="dna-loader phase8-run-guidance" role="status" aria-live="polite">
                <div class="dna-helix" aria-hidden="true">
                    <span class="dna-rung"></span>
                    <span class="dna-rung"></span>
                    <span class="dna-rung"></span>
                </div>
                <div>
                    <strong>Mutating codon populations</strong>
                    <small>Twisting through generations and category states.</small>
                </div>
            </div>
            """
        )
        user_sim_legacy, user_exp_legacy = run_cached(
            int(n_gen),
            int(copies),
            *user_probs,
            int(seed),
        )
        preset_sim_legacy, preset_exp_legacy = run_cached(
            int(n_gen),
            int(copies),
            *preset_probs,
            int(seed),
        )
    loading_slot.empty()
    run_elapsed = time.perf_counter() - run_started_at

    with st.sidebar:
        st.divider()
        st.caption(f"Analysis runtime: {run_elapsed:.2f} s")

    user_sim = ExactSimulationResult.from_legacy_tuple(user_sim_legacy)
    user_exp = SampledSimulationResult.from_legacy_tuple(user_exp_legacy)
    preset_sim = ExactSimulationResult.from_legacy_tuple(preset_sim_legacy)
    preset_exp = SampledSimulationResult.from_legacy_tuple(preset_exp_legacy)

    sim = user_sim if view_mode == "Your probability" else preset_sim
    exp = user_exp if view_mode == "Your probability" else preset_exp
    run_label = "User probability" if view_mode == "Your probability" else "Preset probability"

    st.caption("Charts and tables below preserve the accepted Phase 6 data display.")
    st.caption(
        "Use these results as a guided reading path: first the headline metrics, then the charts, then the tables."
    )

    if dashboard_view == "Whole population":
        render_whole_population_view(
            view_mode,
            run_label,
            user_sim,
            user_exp,
            preset_sim,
            preset_exp,
            sim,
            exp,
            int(n_gen),
            display_mode,
        )
    else:
        render_codon_focus_view(
            view_mode,
            run_label,
            selected_codon,
            compare_codon,
            user_sim,
            user_exp,
            preset_sim,
            preset_exp,
            sim,
            exp,
            int(n_gen),
            display_mode,
            no_more_basis,
            float(no_more_alpha),
            int(generation),
        )


if __name__ == "__main__":
    main()
