import pandas as pd
from sklearn.datasets import load_iris, load_wine


def get_iris() -> pd.DataFrame:
    data = load_iris()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df["species"] = pd.Categorical.from_codes(data.target, data.target_names)
    return df


def get_wine() -> pd.DataFrame:
    data = load_wine()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df["wine_class"] = pd.Categorical.from_codes(data.target, data.target_names)
    return df


BUILTIN_DATASETS = {
    "iris": get_iris,
    "wine": get_wine,
}
