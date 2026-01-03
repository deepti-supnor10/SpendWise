import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import pickle

def train_spend_model():
    # 1. Dataset Generation (Synthesizing 3 years of data)
    np.random.seed(42)
    months = np.arange(1, 37)
    
    # Logic: Base (1200) + Trend (Month * 10) + Seasonal (Dec/July spikes) + Noise
    base = 1200
    seasonal = np.array([600 if m % 12 == 0 or m % 12 == 7 else 0 for m in months])
    noise = np.random.normal(0, 150, 36)
    total_spent = base + (months * 12) + seasonal + noise

    df = pd.DataFrame({
        'month_index': months,
        'prev_month_spend': np.roll(total_spent, 1),
        'target_spend': total_spent
    })
    df.iloc[0, 1] = 1200 # Fill first row

    # 2. Pipeline Creation (Scaling + Modeling)
    X = df[['month_index', 'prev_month_spend']]
    y = df['target_spend']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scikit-learn Pipeline
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('rf', RandomForestRegressor(n_estimators=200, random_state=42))
    ])

    # 3. Training
    pipeline.fit(X_train, y_train)
    
    # 4. Save model
    with open('spend_model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    
    print(f"Model Trained. Accuracy Score: {pipeline.score(X_test, y_test):.2f}")

if __name__ == "__main__":
    train_spend_model()
