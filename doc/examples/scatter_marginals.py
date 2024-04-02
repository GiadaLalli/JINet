import pandas as pd
import plotly
import plotly.express as px

def scatter_marginals_px(df, x, y, target, marginal_y="violin", marginal_x="box", trendline="ols", template="simple_white", 
                                dpi=300, height=600, width=800, title=None, legend_orientation="v"):
    # Create the scatter plot with marginal plots using Plotly Express
    fig = px.scatter(df, x=x, y=y, color=target, marginal_y=marginal_y, marginal_x=marginal_x, trendline=trendline, template=template)

    # Set the title if provided
    if title:
        fig.update_layout(
            title=title, 
            title_x=0.5,  # Center the title
            title_font=dict(size=20, color="black", family="Arial")
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
            legend_title_text='',  # Remove legend title
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",
                y=-0.1,
                xanchor="right",
                x=1
            )
        )
    elif legend_orientation == "v":
        fig.update_layout(
            legend_title_text='')

    # Show the figure
    fig.show()

# Example usage:
#url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
#df = pd.read_csv(url, names=['sepal length','sepal width','petal length','petal width','target'])
scatter_marginals_px(df, "sepal width", "sepal length", "target", dpi=300, height=1000, width=1100, 
                     title="Scatter Plot with Marginals on Iris Data", legend_orientation="h")
