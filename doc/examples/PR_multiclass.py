import plotly.graph_objects as go
import pandas as pd
from sklearn.metrics import precision_recall_curve, average_precision_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB


def PR_multiclass_px(
    df, target=None, model_type="LogisticRegression", width=900, height=700
):
    # Extract features and target
    if target is None:
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
    else:
        X = df.drop(columns=[target])
        y = df[target]

    # Instantiate the selected classifier
    if model_type == "LogisticRegression":
        model = LogisticRegression(max_iter=200)
    elif model_type == "RandomForestClassifier":
        model = RandomForestClassifier()
    elif model_type == "GradientBoostingClassifier":
        model = GradientBoostingClassifier()
    elif model_type == "SVC":
        model = SVC(probability=True)
    elif model_type == "KNeighborsClassifier":
        model = KNeighborsClassifier()
    elif model_type == "GaussianNB":
        model = GaussianNB()
    else:
        raise ValueError(
            "Invalid model_type. Please choose from 'LogisticRegression', 'RandomForestClassifier', 'GradientBoostingClassifier', 'SVC', 'KNeighborsClassifier', or 'GaussianNB'."
        )

    # Fit the model
    model.fit(X, y)
    y_scores = model.predict_proba(X)

    # One hot encode the labels in order to plot them
    y_onehot = pd.get_dummies(y, columns=model.classes_)

    # Create an empty figure, and iteratively add new lines
    # every time we compute a new class
    fig = go.Figure()
    fig.add_shape(type="line", line=dict(dash="dash"), x0=0, x1=1, y0=1, y1=0)

    for i in range(y_scores.shape[1]):
        y_true = y_onehot.iloc[:, i]
        y_score = y_scores[:, i]

        precision, recall, _ = precision_recall_curve(y_true, y_score)
        auc_score = average_precision_score(y_true, y_score)

        name = f"{y_onehot.columns[i]} (AP={auc_score:.2f})"
        fig.add_trace(go.Scatter(x=recall, y=precision, name=name, mode="lines"))

    fig.update_layout(
        xaxis_title="Recall",
        yaxis_title="Precision",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        xaxis=dict(constrain="domain"),
        width=width,
        height=height,
    )
    return fig.to_html(
        include_plotlyjs=False, full_html=False, default_height=f"{height}px"
    )


def main(data_path, target, model_type, width, height) -> str:
    df = pd.read_csv(data_path)
    return PR_multiclass_px(df, target, model_type, width, height)
