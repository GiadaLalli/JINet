from pandas import read_csv

import plotly.express as px
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve, auc


def PR_binary_px(df, target=None, width=700, height=500):
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
    y_score = model.predict_proba(X)[:, 1]

    # Calculate precision-recall curve
    precision, recall, thresholds = precision_recall_curve(y, y_score)
    auc_score = auc(recall, precision)

    # Plot precision-recall curve
    fig = px.area(
        x=recall,
        y=precision,
        title=f"Precision-Recall Curve (AUC={auc_score:.4f})",
        labels=dict(x="Recall", y="Precision"),
        width=width,
        height=height,
    )
    fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=1, y1=0)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_xaxes(constrain="domain")

    return fig.to_html(
        include_plotlyjs=False, full_html=False, default_height=f"{height}px"
    )


def main(data_path, target, width, height) -> str:
    df = read_csv(data_path)
    return PR_binary_px(df, target, width, height)
