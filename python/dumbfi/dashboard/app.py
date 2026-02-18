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
            customdata=gains,
            hoverinfo="none",
        ))

    fig.update_layout(barmode="stack", **_chart_layout("PORTFOLIO ALLOCATION (%)", dates))

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
            marker_line_color=NES_BG,
            marker_line_width=1,
            customdata=gains,
            hoverinfo="none",
        ))

    fig.update_layout(barmode="stack", **_chart_layout("ALLOCATION BY LOT (%)", dates))

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
        hoverinfo="none",
    ))
    layout = _chart_layout("CUMULATIVE RETURN (%)", dates)
    layout["height"] = 280
    fig.update_layout(**layout)
    return fig


def _quarter_ticks(dates: list[str]) -> tuple[list[str], list[str]]:
    """Compute tick positions and labels for quarter boundaries."""
    tickvals: list[str] = []
    ticktext: list[str] = []
    seen: set[tuple[int, int]] = set()
    for d in dates:
        year = int(d[:4])
        month = int(d[5:7])
        q = (month - 1) // 3 + 1
        key = (year, q)
        if key not in seen:
            seen.add(key)
            tickvals.append(d)
            ticktext.append(f"{year} Q{q}")
    return tickvals, ticktext


def _chart_layout(title: str, dates: list[str] | None = None) -> dict:
    """Shared layout settings using NES template."""
    xaxis = dict(type="category", ticklabelstandoff=12)
    if dates:
        tickvals, ticktext = _quarter_ticks(dates)
        xaxis.update(tickvals=tickvals, ticktext=ticktext)
    return dict(
        title=title,
        template="nes",
        margin=dict(l=50, r=30, t=60, b=60),
        showlegend=False,
        hovermode="x",
        xaxis=xaxis,
        height=600,
    )


# --- App factory ---

# NES.css CDN + Press Start 2P font
_EXTERNAL_CSS = [
    "https://unpkg.com/nes.css@2.3.0/css/nes.min.css",
    "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap",
]


def _info_cell(label: str, value_id: str, color: str | None = None) -> html.Div:
    """One cell in the hover info bar. Colored label for ticker cells."""
    label_color = color if color else "#888"
    return html.Div([
        html.Div(label, style={"fontSize": "8px", "color": label_color, "marginBottom": "2px"}),
        html.Span(id=value_id, children="--", style={"fontSize": "11px"}),
    ], style={"flex": "1 1 auto", "minWidth": "120px"})


def _legend_bar() -> html.Div:
    """NES-styled legend bar with colored blocks per ticker + target weight."""
    items = []
    for ticker, target in TARGET_WEIGHTS.items():
        color = ticker_gain_color(ticker, 0)
        items.append(html.Div([
            html.Span(style={
                "display": "inline-block",
                "width": "20px",
                "height": "20px",
                "backgroundColor": color,
                "marginRight": "8px",
                "verticalAlign": "middle",
                "border": "3px solid #e0e0e0",
                "imageRendering": "pixelated",
            }),
            html.Span(f"{ticker}", style={
                "fontSize": "11px",
                "color": color,
                "marginRight": "4px",
                "verticalAlign": "middle",
            }),
            html.Span(f"{target * 100:.0f}%", style={
                "fontSize": "9px",
                "color": "#888",
                "verticalAlign": "middle",
            }),
        ], style={"display": "inline-block", "marginRight": "32px"})
        )
    return html.Div(
        className="nes-container is-dark",
        children=items,
        style={"marginBottom": "8px", "padding": "10px 16px"},
    )


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
    .nes-container.is-dark { background-color: #212529; }
    #controls label {
        font-family: 'Press Start 2P', monospace;
        font-size: 11px;
        cursor: pointer;
    }
    #controls input[type="checkbox"] { display: none; }
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
            # Controls
            html.Div(
                className="nes-container is-dark with-title",
                children=[
                    html.P("dumbfi", className="title"),
                    html.Span("SELECT ", style={"fontSize": "10px", "marginRight": "12px", "color": NES_YELLOW}),
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
                style={"marginBottom": "8px", "padding": "12px 16px"},
            ),

            # Legend bar
            _legend_bar(),

            # Hover info bar (external tooltip)
            html.Div(
                className="nes-container is-dark",
                children=[html.Div(
                    children=[
                        _info_cell("DATE", "info-date"),
                        _info_cell("VALUE", "info-value"),
                        _info_cell("AAPL", "info-AAPL", ticker_gain_color("AAPL", 0)),
                        _info_cell("XOM", "info-XOM", ticker_gain_color("XOM", 0)),
                        _info_cell("YUM", "info-YUM", ticker_gain_color("YUM", 0)),
                        _info_cell("IBM", "info-IBM", ticker_gain_color("IBM", 0)),
                        _info_cell("RETURN", "info-return"),
                    ],
                    style={"display": "flex", "flexWrap": "wrap", "gap": "8px"},
                )],
                style={"marginBottom": "8px", "padding": "10px 16px"},
            ),

            # Main chart
            html.Div(
                className="nes-container is-dark",
                children=[dcc.Graph(
                    id="main-chart",
                    config={"displayModeBar": True, "displaylogo": False},
                )],
                style={"padding": "4px", "marginBottom": "8px"},
            ),

            # Return chart
            html.Div(
                className="nes-container is-dark",
                children=[dcc.Graph(
                    id="return-chart",
                    figure=_build_return_chart(snapshots),
                    config={"displayModeBar": True, "displaylogo": False},
                )],
                style={"padding": "4px"},
            ),
        ],
    )

    # --- Callbacks ---

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

    @app.callback(
        Output("info-date", "children"),
        Output("info-value", "children"),
        Output("info-AAPL", "children"),
        Output("info-XOM", "children"),
        Output("info-YUM", "children"),
        Output("info-IBM", "children"),
        Output("info-return", "children"),
        Input("main-chart", "hoverData"),
    )
    def update_info_bar(hover_data: dict | None) -> tuple:
        if hover_data is None:
            return ("--",) * 7

        date_str = hover_data["points"][0]["x"]
        snap = next((s for s in snapshots if s.date == date_str), None)
        if snap is None:
            return ("--",) * 7

        base_value = snapshots[0].total_value
        ret_pct = (snap.total_value / base_value - 1) * 100

        ticker_strs = []
        for ticker in ["AAPL", "XOM", "YUM", "IBM"]:
            w = snap.weights.get(ticker, 0) * 100
            d = snap.drift.get(ticker, 0) * 100
            ticker_lots = [l for l in snap.lots if l.ticker == ticker]
            if ticker_lots:
                total_val = sum(l.value for l in ticker_lots)
                avg_gain = sum(l.gain_pct * l.value for l in ticker_lots) / total_val if total_val else 0
            else:
                avg_gain = 0
            sign = "+" if avg_gain >= 0 else ""
            ticker_strs.append(f"{w:.1f}% ({sign}{avg_gain:.1f}%)")

        return (
            date_str,
            f"${snap.total_value:,.0f}",
            ticker_strs[0],
            ticker_strs[1],
            ticker_strs[2],
            ticker_strs[3],
            f"{ret_pct:+.2f}%",
        )

    return app


def main() -> None:
    """Entry point for dumbfi-dashboard command."""
    app = create_app()
    app.run(debug=True, port=8050)


if __name__ == "__main__":
    main()
