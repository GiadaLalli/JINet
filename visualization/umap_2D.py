import pandas as pd
import plotly
import plotly.express as px
#from sklearn.manifold import UMAP
from umap import UMAP

def UMAP_2d_px(df, target=None, n_components=2, dpi=300, width=1100, height=600, alpha=1.0, title="UMAP 2D Scatter Plot", legend_orientation="h"):
    # Extracting features and target
    if target is None:
        features = df.iloc[:, :-1]
        y = df.iloc[:, -1]
    else:
        features = df.drop(columns=[target])
        y = df[target]

    # Applying UMAP with specified number of components
    umap_2d = UMAP(n_components=n_components, init='random', n_neighbors=5, min_dist=0.3, random_state=None)
    proj_2d = umap_2d.fit_transform(features)

    # Creating the 2D scatter plot with generically the last column as label
    fig_2d = px.scatter(
        proj_2d, x=0, y=1,
        color=y.astype(str),  # Convert y to string for discrete values
        labels={'color': y.name},
        color_continuous_scale='cool',
        opacity=alpha
    )

    # Customizing the layout
    fig_2d.update_layout(
        title={
            'text': title,
            'x': 0.5,  # Centered title
            'y': 0.95,  # Adjust the y-coordinate as needed
            'xanchor': 'center',
            'yanchor': 'top',
        },
        xaxis_title="Component 1",  # Updated x-axis label
        yaxis_title="Component 2",  # Updated y-axis label
        width=width,
        height=height,
        legend_title_text='',  # Remove legend title
    )

    # Update legend orientation
    if legend_orientation == "h":
        fig_2d.update_layout(
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",
                y=-0.1,
                xanchor="right",
                x=1
            )
        )
    elif legend_orientation == "v":
        fig_2d.update_layout(
            legend_title_text=''  # Remove legend title
        )

    # Show the 2D plot
    fig_2d.show()

# Example usage
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
df = pd.read_csv(url, names=['sepal length','sepal width','petal length','petal width','target'])

UMAP_2d_px(df, n_components=2, dpi=350, width=1100, height=800, alpha=0.8, title="UMAP 2D Scatter Plot Example", legend_orientation="h")