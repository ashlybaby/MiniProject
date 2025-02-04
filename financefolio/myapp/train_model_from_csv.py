import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import joblib

# Path to the CSV file
csv_file_path = 'expenses.csv'

def train_model_from_csv():
    # Load the data
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print("Error: The CSV file does not exist.")
        return

    # Ensure the necessary columns are present
    required_columns = {'category', 'amount', 'date'}
    if not required_columns.issubset(df.columns):
        print(f'Error: The CSV file must contain the following columns: {", ".join(required_columns)}.')
        return

    # Handle missing data (you can modify this depending on your preference)
    df = df.dropna(subset=['category', 'amount', 'date'])

    # Convert the date column to datetime format
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])  # Drop rows with invalid dates

    # Aggregate monthly expenses by category
    df['month'] = df['date'].dt.to_period('M')
    monthly_expenses_by_category = df.groupby(['month', 'category'])['amount'].sum().reset_index()
    monthly_expenses_by_category['month'] = monthly_expenses_by_category['month'].dt.to_timestamp()

    # Train models for each category
    models = {}
    for category, group in monthly_expenses_by_category.groupby('category'):
        try:
            # Use Exponential Smoothing (Holt-Winters) for forecasting
            model = ExponentialSmoothing(
                group['amount'],
                seasonal='add',
                seasonal_periods=12,
                trend='add'
            ).fit()
            models[category] = model
            print(f"Model trained for category: {category}")
        except Exception as e:
            print(f"Error training model for category {category}: {e}")

    # Save the trained models to a file
    joblib.dump(models, 'expense_prediction_models.pkl')
    print("Models saved successfully.")

# Run the training function
if __name__ == "__main__":
    train_model_from_csv()
