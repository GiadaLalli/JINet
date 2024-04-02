import pandas as pd
import plotly
import plotly.express as px

def scatter_matrix_px(df, target=None, dpi=300, height=600, width=800, title=None, legend_orientation="v", diagonal_visible=True):
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
            'text': title,
            'x': 0.5,  # Centered title
            'y': 0.95,  # Adjust the y-coordinate as needed
            'xanchor': 'center',
            'yanchor': 'top',
        },
        width=width,
        height=height,
    )
    fig.update_traces(diagonal_visible=diagonal_visible)

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
            legend_title_text=''
        )

    # Show the plot
    fig.show()


# Example usage
#url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
#df = pd.read_csv(url, names=['sepal length','sepal width','petal length','petal width','target'])

scatter_matrix_px(df, "target", dpi=350, height=800, width=1000, 
                  title="Scatter Matrix Plot Example", legend_orientation="h", diagonal_visible=False)