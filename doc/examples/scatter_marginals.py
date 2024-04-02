"""Create the scatter plot with marginal plots using Plotly Express."""

from pathlib import Path

from pandas import read_csv
import plotly.express as px


def scatter_marginals_px(
    df,
    x,
    y,
    target,
    marginal_y="violin",
    marginal_x="box",
    trendline="ols",
    template="simple_white",
    dpi=300,
    height=600,
    width=800,
    title=None,
    legend_orientation="v",
):
    """Create the scatter plot with marginal plots using Plotly Express."""
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=target,
        marginal_y=marginal_y,
        marginal_x=marginal_x,
        trendline=trendline,
        template=template,
    )

    # Set the title if provided
    if title:
        fig.update_layout(
            title=title,
            title_x=0.5,  # Center the title
            title_font=dict(size=20, color="black", family="Arial"),
        )

    # Update the figure layout to adjust DPI and figsize
    fig.update_layout(
        autosize=False,
        width=width,
        height=height,
    )

    # Update the legend orientation
    if legend_orientation == "h":
        fig.update_layout(
            legend_title_text="",  # Remove legend title
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",
                y=-0.1,
                xanchor="right",
                x=1,
            ),
        )
    elif legend_orientation == "v":
        fig.update_layout(legend_title_text="")

    return fig


def main(
    data: Path,
    x: str,
    y: str,
    target: str,
    dpi: int,
    height: int,
    width: int,
    title: str,
    legend_orientation: str,
):
    df = read_csv(data)
    fig = scatter_marginals_px(
        df,
        x,
        y,
        target,
        dpi=dpi,
        height=height,
        width=width,
        title=title,
        legend_orientation=legend_orientation,
    )
    return fig.to_html(
        include_plotlyjs=False, full_html=False, default_height=f"{height}px"
    )
