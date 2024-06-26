from pathlib import Path
from pandas import read_csv

import plotly.express as px
from sklearn.decomposition import PCA


def pca_3d_px(
    df,
    target=None,
    n_components=3,
    dpi=300,
    width=800,
    height=800,
    alpha=1,
    title=None,
    legend_orientation="v",
):
    # Setting n_components to 3 if None or less than 3
    if n_components is None or n_components < 3:
        n_components = 3

    # Extracting features and target
    if target is None:
        features = df.iloc[:, :-1]
        y = df.iloc[:, -1]
    else:
        features = df.drop(columns=[target])
        y = df[target]

    # Applying PCA
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(features)

    # Creating the scatter plot
    fig = px.scatter_3d(
        components,
        x=0,
        y=1,
        z=2,
        color=y.astype(str),  # Convert to string to ensure discrete colors
        title=title,
        labels={"0": "PC 1", "1": "PC 2", "2": "PC 3"},
    )

    # Customizing the layout
    fig.update_layout(
        width=width,
        height=height,
        title={
            "text": title,
            "x": 0.5,  # Centered title
            "y": 0.95,  # Adjust the y-coordinate as needed
            "xanchor": "center",
            "yanchor": "top",
        },
    )

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
        fig.update_layout(legend_title_text="")  # Remove legend title

    fig.update_traces(marker=dict(opacity=alpha))

    return fig.to_html(
        include_plotlyjs=False, full_html=False, default_height=f"{height}px"
    )


def main(
    data: Path,
    target: str,
    n_components: int,
    dpi: int,
    width: int,
    height: int,
    alpha: int
    title: str,
    legend_orientation: str,
    diagonal_visible: bool,
):
    df = read_csv(data)
    fig = pca_3d_px(
        df=df,
        target=target
        n_components=n_components,
        dpi=dpi,
        width=width,
        height=height,
        alpha=alpha
        title=title,
        legend_orientation=legend_orientation,
        diagonal_visible=diagonal_visible,
    )
    return fig.to_html(
        include_plotlyjs=False, full_html=False, default_height=f"{height}px"
    )
