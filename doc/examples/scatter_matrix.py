from pathlib import Path

from pandas import read_csv
import plotly.express as px


def scatter_matrix_px(
    df,
    target=None,
    dpi=300,
    height=600,
    width=800,
    title=None,
    legend_orientation="v",
    diagonal_visible=True,
):
    # Extracting features and target
    if target is None:
        features = df.iloc[:, :-1]
        y = df.iloc[:, -1]
    else:
        features = df.drop(columns=[target])
        y = df[target]

    # Creating the scatter matrix plot
    fig = px.scatter_matrix(df, dimensions=features, color=y.name)

    # Customizing the layout
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,  # Centered title
            "y": 0.95,  # Adjust the y-coordinate as needed
            "xanchor": "center",
            "yanchor": "top",
        },
        width=width,
        height=height,
    )
    fig.update_traces(diagonal_visible=diagonal_visible)

    # Update legend orientation
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
    target: str,
    dpi: int,
    width: int,
    height: int,
    title: str,
    legend_orientation: str,
    diagonal_visible: bool,
):
    df = read_csv(data)
    fig = scatter_matrix_px(
        df=df,
        target=target,
        dpi=dpi,
        height=height,
        width=width,
        title=title,
        legend_orientation=legend_orientation,
        diagonal_visible=diagonal_visible,
    )
    return fig.to_html(
        include_plotlyjs=False, full_html=False, default_height=f"{height}px"
    )
