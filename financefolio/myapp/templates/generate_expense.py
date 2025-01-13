import pandas as pd
import random
import datetime

# Categories and description for sample data
categories = ['Transportation', 'Groceries', 'Dining', 'Entertainment', 'Utilities']

# Generate random data
data = []
for i in range(50):  # Generate 50 sample entries
    date = datetime.date.today() - datetime.timedelta(days=random.randint(0, 365))
    category = random.choice(categories)
    amount = round(random.uniform(5, 100), 2)  # Random amount between 5 and 100
    description = f"Sample expense for {category}"
    
    data.append([date, category, amount, description])

# Create a DataFrame
df = pd.DataFrame(data, columns=['date', 'category', 'amount', 'description'])

# Save to CSV
df.to_csv('expenses.csv', index=False)

print("CSV file generated successfully!")
