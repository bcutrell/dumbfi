"""Plotly Dash dashboard for portfolio holdings visualization."""

from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.io as pio

from dumbfi.dashboard.data import (
    DailySnapshot,
    build_snapshots,
    TARGET_WEIGHTS,
)

# --- NES / retro theme constants ---

NES_BG = "#212529"
NES_PAPER = "#212529"
NES_GRID = "#3a3a4a"
NES_TEXT = "#e0e0e0"
NES_FONT = "'Press Start 2P', monospace"
NES_GREEN = "#92cc41"
NES_BLUE = "#209cee"
NES_RED = "#e76e55"
NES_YELLOW = "#f7d51d"

# Register a custom Plotly template matching NES.css dark style
_nes_template = go.layout.Template()
_nes_template.layout = go.Layout(
    paper_bgcolor=NES_PAPER,
    plot_bgcolor=NES_BG,
    font=dict(family=NES_FONT, size=10, color=NES_TEXT),
    title=dict(font=dict(size=12)),
    xaxis=dict(
        showgrid=False,
        color=NES_TEXT,
        linecolor=NES_GRID,
        tickfont=dict(size=8),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=NES_GRID,
        gridwidth=1,
        color=NES_TEXT,
        linecolor=NES_GRID,
        tickfont=dict(size=8),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=8),
    ),
    bargap=0.05,
)
pio.templates["nes"] = _nes_template


# --- Color helpers ---

# NES-palette hues per ticker. Gain/loss encoded as lightness/saturation.
TICKER_HUE: dict[str, int] = {
    "AAPL": 220,
    "XOM": 15,
    "YUM": 160,
    "IBM": 270,
}


def ticker_gain_color(ticker: str, gain_pct: float) -> str:
    """Map ticker identity + gain/loss to a single color.

    Hue identifies the ticker. Gains push toward saturated/dark,
    losses toward desaturated/light, neutral sits in the middle.
    """
    hue = TICKER_HUE.get(ticker, 0)
    t = min(abs(gain_pct) / 30, 1.0)
    if gain_pct >= 0:
        sat = int(40 + t * 50)   # 40% -> 90%
        lit = int(55 - t * 20)   # 55% -> 35%
    else:
        sat = int(40 - t * 20)   # 40% -> 20%
        lit = int(55 + t * 25)   # 55% -> 80%
    return f"hsl({hue},{sat}%,{lit}%)"


# --- Chart builders ---


def _build_ticker_chart(snapshots: list[DailySnapshot], show_targets: bool) -> go.Figure:
    """Stacked bar chart with one trace per ticker."""
    dates = [s.date for s in snapshots]
    fig = go.Figure()

    tickers = list(TARGET_WEIGHTS.keys())
    for ticker in tickers:
        weights = [s.weights.get(ticker, 0) * 100 for s in snapshots]
        gains = []
        for s in snapshots:
            ticker_lots = [l for l in s.lots if l.ticker == ticker]
            if ticker_lots:
                total_val = sum(l.value for l in ticker_lots)
                avg_gain = sum(l.gain_pct * l.value for l in ticker_lots) / total_val if total_val else 0
                gains.append(avg_gain)
            else:
                gains.append(0)

        colors = [ticker_gain_color(ticker, g) for g in gains]
        fig.add_trace(go.Bar(
            name=ticker,
            x=dates,
            y=weights,
            marker_color=colors,
            hovertemplate=f"{ticker}<br>Weight: %{{y:.1f}}%<br>Avg Gain: %{{customdata:.1f}}%<extra></extra>",
            customdata=gains,
        ))

    fig.update_layout(barmode="stack", **_chart_layout("PORTFOLIO ALLOCATION (%)"))

    if show_targets:
        _add_target_lines(fig, tickers)

    return fig


def _build_lot_chart(snapshots: list[DailySnapshot], show_targets: bool) -> go.Figure:
    """Stacked bar chart with one trace per tax lot."""
    dates = [s.date for s in snapshots]
    fig = go.Figure()

    if not snapshots:
        return fig
    lot_keys = [(l.ticker, l.lot_index) for l in snapshots[0].lots]

    for ticker, lot_idx in lot_keys:
        weights = []
        gains = []
        for s in snapshots:
            lot = next((l for l in s.lots if l.ticker == ticker and l.lot_index == lot_idx), None)
            weights.append(lot.weight * 100 if lot else 0)
            gains.append(lot.gain_pct if lot else 0)

        colors = [ticker_gain_color(ticker, g) for g in gains]
        fig.add_trace(go.Bar(
            name=f"{ticker} L{lot_idx}",
            x=dates,
            y=weights,
            marker_color=colors,
            hovertemplate=(
                f"{ticker} Lot {lot_idx}<br>"
                "Weight: %{y:.1f}%<br>"
                "Gain: %{customdata:.1f}%<extra></extra>"
            ),
            customdata=gains,
        ))

    fig.update_layout(barmode="stack", **_chart_layout("ALLOCATION BY LOT (%)"))

    if show_targets:
        _add_target_lines(fig, list(TARGET_WEIGHTS.keys()))

    return fig


def _add_target_lines(fig: go.Figure, tickers: list[str]) -> None:
    """Add dashed horizontal lines at cumulative target weights."""
    cumulative = 0.0
    for ticker in tickers:
        cumulative += TARGET_WEIGHTS[ticker] * 100
        fig.add_hline(
            y=cumulative,
            line_dash="dash",
            line_color=NES_GREEN,
            opacity=0.6,
            annotation_text=f"{ticker} target",
            annotation_position="top left",
            annotation_font_color=NES_GREEN,
            annotation_font_size=8,
        )


def _build_return_chart(snapshots: list[DailySnapshot]) -> go.Figure:
    """Cumulative return line chart."""
    if not snapshots:
        return go.Figure()

    dates = [s.date for s in snapshots]
    base_value = snapshots[0].total_value
    returns = [(s.total_value / base_value - 1) * 100 for s in snapshots]

    fig = go.Figure(go.Scatter(
        x=dates,
        y=returns,
        mode="lines",
        line=dict(color=NES_GREEN, width=2, shape="hv"),
        hovertemplate="Date: %{x}<br>Return: %{y:.2f}%<extra></extra>",
    ))
    fig.update_layout(**_chart_layout("CUMULATIVE RETURN (%)"), height=250)
    return fig


def _chart_layout(title: str) -> dict:
    """Shared layout settings using NES template."""
    return dict(
        title=title,
        template="nes",
        margin=dict(l=50, r=30, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )


# --- App factory ---

# NES.css CDN + Press Start 2P font
_EXTERNAL_CSS = [
    "https://unpkg.com/nes.css@2.3.0/css/nes.min.css",
    "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap",
]


def create_app(csv_path: str | None = None) -> Dash:
    """Build and return the Dash application."""
    snapshots, holdings = build_snapshots(csv_path)

    app = Dash(__name__, external_stylesheets=_EXTERNAL_CSS)

    app.index_string = """<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>DumbFi Dashboard</title>
{%css%}
<style>
    body {
        background-color: #212529;
        color: #e0e0e0;
        font-family: 'Press Start 2P', monospace;
        image-rendering: pixelated;
    }
    .nes-container { margin-bottom: 16px; }
    .nes-container.is-dark { background-color: #212529; }
    /* style Dash checklist labels */
    #controls label {
        font-family: 'Press Start 2P', monospace;
        font-size: 11px;
        cursor: pointer;
    }
    #controls input[type="checkbox"] { display: none; }
    .nes-text.is-primary { color: #209cee; }
    .nes-text.is-success { color: #92cc41; }
    .nes-text.is-warning { color: #f7d51d; }
    .nes-text.is-error   { color: #e76e55; }
</style>
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>"""

    app.layout = html.Div(
        style={"padding": "24px", "maxWidth": "1600px", "margin": "0 auto"},
        children=[
            # Title container
            html.Div(
                className="nes-container is-dark with-title",
                children=[
                    html.P("PLAYER 1", className="title"),
                    html.H1(
                        "DumbFi Dashboard",
                        style={"fontSize": "18px", "marginBottom": "4px"},
                    ),
                    html.P(
                        "Tax-lot level holdings visualization",
                        style={"fontSize": "10px", "color": "#888"},
                    ),
                ],
            ),

            # Controls container
            html.Div(
                className="nes-container is-dark",
                children=[
                    html.Span(
                        "SELECT ",
                        style={"fontSize": "10px", "marginRight": "12px", "color": NES_YELLOW},
                    ),
                    dcc.Checklist(
                        id="controls",
                        options=[
                            {"label": " Show Lots", "value": "lots"},
                            {"label": " Target Weights", "value": "targets"},
                        ],
                        value=[],
                        inline=True,
                        style={"display": "inline-block"},
                        inputStyle={"marginRight": "6px"},
                        labelStyle={"marginRight": "24px"},
                    ),
                ],
                style={"marginBottom": "16px", "padding": "12px 16px"},
            ),

            # Main chart container
            html.Div(
                className="nes-container is-dark",
                children=[dcc.Graph(id="main-chart", config={"displayModeBar": True})],
                style={"padding": "8px"},
            ),

            # Return chart container
            html.Div(
                className="nes-container is-dark",
                children=[dcc.Graph(id="return-chart", figure=_build_return_chart(snapshots), config={"displayModeBar": True})],
                style={"padding": "8px"},
            ),
        ],
    )

    @app.callback(
        Output("main-chart", "figure"),
        Input("controls", "value"),
    )
    def update_main_chart(controls: list[str]) -> go.Figure:
        show_lots = "lots" in controls
        show_targets = "targets" in controls
        if show_lots:
            return _build_lot_chart(snapshots, show_targets)
        return _build_ticker_chart(snapshots, show_targets)

    return app


def main() -> None:
    """Entry point for dumbfi-dashboard command."""
    app = create_app()
    app.run(debug=True, port=8050)


if __name__ == "__main__":
    main()
