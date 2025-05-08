import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Month name to number mapping
month_map = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
}

# Load Section 1 outputs
try:
    df_base = pd.read_csv("ResearchOutputs_Group4.csv")
except FileNotFoundError:
    print("Error: ResearchOutputs_Group4.csv not found. Using dummy data.")
    df_base = pd.DataFrame({
        'ProjectID': ['5', '18', '57'],
        'ProjectStartYear': [2001, 2006, 2001],
        'ProjectEndYear': [2004, '2006', 2001],
        'OutputYear': [2004, 2008, 2002],
        'OutputMonth': ['May', 'February', np.nan],
        'OutputTitle': ['Entry, Expansion, and Intensity', 'Wage and Productivity', 'Home Bias']
    })

try:
    df_enriched = pd.read_csv("Group4_Enriched.csv")
except FileNotFoundError:
    print("Error: Group4_Enriched.csv not found. Using dummy data.")
    df_enriched = pd.DataFrame({
        'ProjectID': ['5', '18', '57'],
        'ProjectStartYear': [2001, 2006, 2001],
        'ProjectEndYear': [2004, '2006', 2001],
        'OutputYear': [2004, 2008, 2002],
        'OutputMonth': ['May', 'February', np.nan],
        'OutputTitle': ['Entry, Expansion, and Intensity', 'Wage and Productivity', 'Home Bias']
    })

# Load 2024 ResearchOutput.xlsx
try:
    df_2024 = pd.read_excel("2024 ResearchOutput.xlsx")
except FileNotFoundError:
    print("Warning: 2024 ResearchOutput.xlsx not found. Using dummy data.")
    df_2024 = pd.DataFrame({
        'ProjectID': ['5', '18', '57'],
        'ProjectStartYear': [2001, 2006, 2001],
        'ProjectEndYear': [2004, '2006', 2001],
        'OutputYear': [2004, 2008, 2002],
        'OutputMonth': ['May', 'February', np.nan],
        'OutputTitle': ['Entry, Expansion, and Intensity', 'Wage and Productivity', 'Home Bias']
    })

# Merge datasets
df = pd.concat([df_base, df_enriched, df_2024], ignore_index=True)
df = df.drop_duplicates(subset=['ProjectID', 'OutputTitle']).reset_index(drop=True)

# Select features and target
features = ['ProjectStartYear', 'ProjectEndYear', 'OutputMonth']
target = 'OutputYear'

# Check if required columns exist
missing_cols = [col for col in features + [target] if col not in df.columns]
if missing_cols:
    print(f"Error: Missing columns {missing_cols}. Using dummy data for missing columns.")
    for col in missing_cols:
        df[col] = np.nan

# Convert month names to numbers
if 'OutputMonth' in df.columns:
    df['OutputMonth'] = df['OutputMonth'].str.lower().map(month_map).fillna(df['OutputMonth'])
    # Handle any non-mapped values (e.g., already numeric or invalid strings)
    df['OutputMonth'] = pd.to_numeric(df['OutputMonth'], errors='coerce')

# Handle missing values and data types
df['ProjectStartYear'] = pd.to_numeric(df['ProjectStartYear'], errors='coerce')
df['ProjectEndYear'] = pd.to_numeric(df['ProjectEndYear'], errors='coerce')
df['OutputMonth'] = df['OutputMonth'].fillna(df['OutputMonth'].median())
df = df[features + [target]].dropna()

# Prepare X (features) and y (target)
X = df[features]
y = df[target]

# Initialize and train the model
model = LinearRegression()
model.fit(X, y)

# Predict and evaluate
y_pred = model.predict(X)
mse = mean_squared_error(y, y_pred)
print(f"Mean Squared Error: {mse:.2f}")

# Visualize actual vs predicted
plt.figure(figsize=(8, 6))
plt.scatter(y, y_pred, alpha=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
plt.xlabel("Actual OutputYear")
plt.ylabel("Predicted OutputYear")
plt.title("Linear Regression: Actual vs Predicted OutputYear")
plt.tight_layout()
plt.show()

# Save results
results = df.copy()
results['Predicted_OutputYear'] = y_pred
results.to_csv("Regression_Results.csv", index=False)
print("Regression results saved to Regression_Results.csv")