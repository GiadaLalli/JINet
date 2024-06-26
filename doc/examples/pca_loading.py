import plotly.express as px
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np


def pca_with_loadings_px(
    df,
    target=None,
    n_components=2,
    dpi=300,
    width=800,
    height=800,
    alpha=1,
    title=None,
    legend_orientation="v",
):
    # Setting n_components to 2 if None or less than 2
    if n_components is None or n_components < 2:
        n_components = 2

    if target is None:
        X = df.iloc[:, :-1]
        features = list(X.columns)
        y = df.iloc[:, -1]
    else:
        X = df.drop(columns=[target])
        features = list(X.columns)

    # Applying PCA
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(X)

    # Calculating loadings
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

    # Creating scatter plot
    fig = px.scatter(components, x=0, y=1, color=df[target] if target else y)

    # Adding annotations for loadings
    for i, feature in enumerate(features):
        fig.add_annotation(
            ax=0,
            ay=0,
            axref="x",
            ayref="y",
            x=loadings[i, 0],
            y=loadings[i, 1],
            showarrow=True,
            arrowsize=2,
            arrowhead=2,
            xanchor="right",
            yanchor="top",
        )
        fig.add_annotation(
            x=loadings[i, 0],
            y=loadings[i, 1],
            ax=0,
            ay=0,
            xanchor="center",
            yanchor="bottom",
            text=feature,
            yshift=5,
        )

    # Customizing layout
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

    # Update trace opacity
    fig.update_traces(marker=dict(opacity=alpha))

    fig.to_html(include_plotlyjs=False, full_html=False, default_height=f"{height}px")


def main(
    data_path,
    target,
    n_components,
    dpi,
    width,
    height,
    alpha,
    title,
    legend_orientation,
) -> str:
    df = pd.read_csv(data_path)
    return pca_with_loadings_px(
        df,
        target=None,
        n_components=2,
        dpi=300,
        width=800,
        height=800,
        alpha=1,
        title=None,
        legend_orientation="v",
    )

    return fig.to_html(
        include_plotlyjs=False, full_html=False, default_height=f"{height}px"
    )
