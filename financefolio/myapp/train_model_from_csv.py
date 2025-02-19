import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import joblib

csv_file_path = 'expenses.csv'

def train_model_from_csv():
    df = pd.read_csv(csv_file_path)

    df = df.dropna(subset=['category', 'amount', 'date'])
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df = df[df['amount'] > 0]

    df['month'] = df['date'].dt.to_period('M')
    monthly_expenses_by_category = df.groupby(['month', 'category'])['amount'].sum().reset_index()
    monthly_expenses_by_category['month'] = monthly_expenses_by_category['month'].dt.to_timestamp()

    models = {}
    for category, group in monthly_expenses_by_category.groupby('category'):
        group['amount'] = np.log1p(group['amount'] + 0.1)  # Improved stability

        model = ExponentialSmoothing(group['amount'], seasonal='add', seasonal_periods=12, trend='add').fit()
        models[category] = model

    joblib.dump(models, 'expense_prediction_models.pkl')

    for category, model in models.items():
        predictions = model.forecast(12)
        predictions = np.maximum(np.expm1(predictions), 0.5)  # Ensure positive predictions
        print(f"Predictions for category {category}: {predictions}")

if __name__ == "__main__":
    train_model_from_csv()
