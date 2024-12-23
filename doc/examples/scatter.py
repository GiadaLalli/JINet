from pathlib import Path

import pandas as pd
import plotly
import plotly.express as px


def scatter_px(
    df, x, y, target, dpi=300, height=600, width=800, title=None, legend_orientation="v"
):

    if x is None:
        x = df.columns[0]  # First column of the DataFrame
    if y is None:
        y = df.columns[1]  # Second column of the DataFrame
    # Create the scatter plot using Plotly Express
    fig = px.scatter(df, x=x, y=y, color=target)

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

    # Show the figure
    return fig


# Example usage:
# url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
# df = pd.read_csv(url, names=['sepal length','sepal width','petal length','petal width','target'])
# scatter_px(df, "sepal width", "sepal length", "target", dpi=450, height=1000, width=1100,
#             title="Scatter Plot on Iris data", legend_orientation="h")


def main(data: Path, x: str, y: str, target: str, height: int, width: int, title: str) -> str:
    df = pd.read_csv(data)
    fig = scatter_px(
        df,
        x,
        y,
        target,
        dpi=450,
        height=height,
        width=width,
        title=title,
        legend_orientation="h",
    )
    return fig.to_html(include_plotlyjs=False, full_html=False, default_height=f"{height}px")

if __name__ == "__main__":
    import sys
    df = pd.read_csv(sys.argv[1])
    fig = scatter_px(df, x=sys.argv[2], y=sys.argv[3], target=sys.argv[4])
    fig.write_image("scatter_plot.png")
