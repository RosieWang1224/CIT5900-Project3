import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
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

# Select numerical features
features = ['ProjectStartYear', 'ProjectEndYear', 'OutputYear', 'OutputMonth']

# Check if required columns exist
missing_cols = [col for col in features if col not in df.columns]
if missing_cols:
    print(f"Error: Missing columns {missing_cols}. Using dummy data for missing columns.")
    for col in missing_cols:
        df[col] = np.nan

# Convert month names to numbers
if 'OutputMonth' in df.columns:
    df['OutputMonth'] = df['OutputMonth'].str.lower().map(month_map).fillna(df['OutputMonth'])
    df['OutputMonth'] = pd.to_numeric(df['OutputMonth'], errors='coerce')

# Handle missing values and data types
df['ProjectStartYear'] = pd.to_numeric(df['ProjectStartYear'], errors='coerce')
df['ProjectEndYear'] = pd.to_numeric(df['ProjectEndYear'], errors='coerce')
df['OutputMonth'] = df['OutputMonth'].fillna(df['OutputMonth'].median())
df = df[features].dropna()

# Standardize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# Apply PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Explained variance
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")

# Visualize PCA results
plt.figure(figsize=(8, 6))
plt.scatter(X_pca[:, 0], X_pca[:, 1], alpha=0.5)
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.title("PCA of Research Outputs")
plt.tight_layout()
plt.show()

# Save PCA results
pca_df = pd.DataFrame(X_pca, columns=['PC1', 'PC2'])
pca_df.to_csv("PCA_Results.csv", index=False)
print("PCA results saved to PCA_Results.csv")