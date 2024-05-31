from pandas import read_csv

import plotly.express as px
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc


def ROC_binary_px(df, target=None, width=800, height=800):
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

    # Create ROC Curve plot
    fig = px.area(
        x=fpr,
        y=tpr,
        title=f"ROC Curve (AUC={auc(fpr, tpr):.4f})",
        labels=dict(x="False Positive Rate", y="True Positive Rate"),
        width=width,
        height=height,
    )
    fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=0, y1=1)

    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_xaxes(constrain="domain")
    return fig.to_html(
        include_plotlyjs=False, full_html=False, default_height=f"{height}px"
    )


def main(data_path, target, width, height) -> str:
    df = read_csv(data_path)
    return ROC_binary_px(df, target, width, height)
