from pathlib import Path

from pandas import read_csv
import plotly.express as px
from sklearn.manifold import TSNE


def tsne_2d_px(
    df,
    target=None,
    dpi=300,
    width=800,
    height=800,
    alpha=1,
    title=None,
    legend_orientation="v",
):
    # Extracting features and target
    if target is None:
        features = df.iloc[:, :-1]
        y = df.iloc[:, -1]
    else:
        features = df.drop(columns=[target])
        y = df[target]

    # Applying t-SNE
    tsne = TSNE(n_components=2, random_state=0)
    projections = tsne.fit_transform(features)

    # Map discrete values in 'y' to colors
    if y.dtype != "object":
        color_map = {val: f"color{i}" for i, val in enumerate(sorted(y.unique()))}
        y = y.astype(str)
    else:
        color_map = None

    # Creating the scatter plot
    fig = px.scatter(
        projections,
        x=0,
        y=1,
        color=y,  # Convert y to string for discrete values
        color_discrete_map=color_map,  # Map discrete values to colors
        labels={"color": "Class"},  # Legend label
    )

    # Customizing the layout
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,  # Centered title
            "y": 1,  # Adjust the y-coordinate as needed
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title="Component 1",  # Updated x-axis label
        yaxis_title="Component 2",  # Updated y-axis label
        width=width,
        height=height,
        legend_title_text="",  # Remove legend title
    )

    # Update legend orientation
    if legend_orientation == "h":
        fig.update_layout(
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",
                y=-0.1,
                xanchor="right",
                x=1,
            )
        )
    elif legend_orientation == "v":
        fig.update_layout(legend_title_text="")  # Remove legend title

    fig.update_traces(marker=dict(opacity=alpha))

    return fig


# Example usage
# url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
# df = pd.read_csv(url, names=['sepal length','sepal width','petal length','petal width','target'])

tsne_2d_px(
    df,
    "target",
    dpi=350,
    width=1100,
    height=800,
    alpha=0.5,
    title="2D t-SNE plot on Iris Data",
    legend_orientation="h",
)


def main(
    data: Path,
    target: str,
    dpi: int,
    width: int,
    height: int,
    alpha: float,
    title: str,
    legend_oriantation: str,
):
    df = read_csv(data)
    fig = tsne_2d_px(
        df=df,
        target=target,
        dpi=dpi,
        width=width,
        height=height,
        alpha=alpha,
        title=title,
        legend_orientation=legend_oriantation,
    )
    return fig.to_html(
        include_plotlyjs=False, full_html=False, default_height=f"{height}px"
    )
