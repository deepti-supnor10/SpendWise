from sklearn.linear_model import LinearRegression
from data_utils import load_clean_data

def predict_next_expense():
    df = load_clean_data()

    if len(df) < 5:
        return "Not enough clean data for prediction"

    # Create time index
    df["day_index"] = range(1, len(df) + 1)

    X = df[["day_index"]]
    y = df["amount"]

    model = LinearRegression()
    model.fit(X, y)

    next_day = [[df["day_index"].max() + 1]]
    prediction = model.predict(next_day)

    return round(float(prediction[0]), 2)
