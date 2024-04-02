import pandas as pd
import plotly
import plotly.express as px
from sklearn.decomposition import PCA

def pca_2d_px(df, target=None, n_components=3, dpi=300, width=800, height=800, alpha=1, title=None, legend_orientation="v", diagonal_visible=True):
    # Setting n_components to 2 if None or less than 2
    if n_components is None or n_components < 2:
        n_components = 2

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

    # Creating labels for the principal components
    labels = {
        str(i): f"PC {i+1} ({var:.1f}%)"
        for i, var in enumerate(pca.explained_variance_ratio_ * 100)
    }

    # Creating the scatter matrix plot
    fig = px.scatter_matrix(
        components,
        labels=labels,
        dimensions=range(n_components),
        color=y.astype(str),  # Convert to string to ensure discrete colors
        title=title
    )
    
    # Customizing the layout
    fig.update_layout(
        width=width,
        height=height,
        title={
            'text': title,
            'x': 0.5,  # Centered title
            'y': 0.95,  # Adjust the y-coordinate as needed
            'xanchor': 'center',
            'yanchor': 'top',
        }
    )
    
    # Update traces to show/hide diagonal elements
    fig.update_traces(diagonal_visible=diagonal_visible)

    # Remove color scale
    fig.update_layout(coloraxis_showscale=False)

    # Update legend orientation
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
            legend_title_text=''  # Remove legend title
        )

    fig.update_traces(marker=dict(opacity=alpha))

    # Show the plot
    fig.show()

#url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
#df = pd.read_csv(url, names=['sepal length','sepal width','petal length','petal width','target'])

pca_2d_px(df, n_components=4, dpi=400, width=1000, height=1000, title="2D PCA Plot", legend_orientation="h", diagonal_visible=True)