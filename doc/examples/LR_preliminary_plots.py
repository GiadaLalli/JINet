import plotly.express as px
from pandas import DataFrame, read_csv
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve


def LR_px(df, target=None, width=800, height=800):
    # Extract features and target
    if target is None:
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values
    else:
        X = df.drop(columns=[target]).values
        y = df[target].values

    # Check if the target column contains only 0s and 1s
    if not set(y).issubset({0, 1}):
        raise ValueError("The target column must contain only 0s and 1s.")

    # Fit logistic regression model
    model = LogisticRegression()
    model.fit(X, y)

    # Predict probabilities
    y_score = model.predict_proba(X)[:, 1]

    # Calculate ROC curve
    fpr, tpr, thresholds = roc_curve(y, y_score)

    # Plot histogram of scores compared to true labels
    fig_hist = px.histogram(
        x=y_score, color=y, nbins=50, labels=dict(color="True Labels", x="Score")
    )
    fig_hist.show()

    # Evaluate model performance at various thresholds
    df = DataFrame(
        {"False Positive Rate": fpr, "True Positive Rate": tpr}, index=thresholds
    )
    df.index.name = "Thresholds"
    df.columns.name = "Rate"

    fig_thresh = px.line(
        df, title="TPR and FPR at every threshold", width=width, height=height
    )

    fig_thresh.update_yaxes(scaleanchor="x", scaleratio=1)
    fig_thresh.update_xaxes(range=[0, 1], constrain="domain")

    return fig_thresh.to_html(
        include_plotlyjs=False, full_html=False, default_height=f"{height}px"
    )


def main(data_path, target, width, height) -> str:
    df = read_csv(data_path)
    return LR_px(df, target, width, height)
