import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import matplotlib.pyplot as plt

# Download NLTK data (run once in Colab)
nltk.download('punkt')
nltk.download('punkt_tab')  # Explicitly download punkt_tab for tokenization
nltk.download('stopwords')

# Load Section 1 outputs
try:
    df_base = pd.read_csv("ResearchOutputs_Group4.csv")
except FileNotFoundError:
    print("Error: ResearchOutputs_Group4.csv not found. Using dummy data.")
    df_base = pd.DataFrame({
        'ProjectID': ['5', '18', '57'],
        'OutputTitle': [
            'Entry, Expansion, and Intensity in the U.S. Export Boom',
            'Wage and Productivity Stability in U.S. Manufacturing Plants',
            'Explaining Home Bias in Consumption'
        ]
    })

try:
    df_enriched = pd.read_csv("Group4_Enriched.csv")
except FileNotFoundError:
    print("Error: Group4_Enriched.csv not found. Using dummy data.")
    df_enriched = pd.DataFrame({
        'ProjectID': ['5', '18', '57'],
        'OutputTitle': [
            'Entry, Expansion, and Intensity in the U.S. Export Boom',
            'Wage and Productivity Stability in U.S. Manufacturing Plants',
            'Explaining Home Bias in Consumption'
        ]
    })

# Load 2024 ResearchOutput.xlsx
try:
    df_2024 = pd.read_excel("2024 ResearchOutput.xlsx")
except FileNotFoundError:
    print("Warning: 2024 ResearchOutput.xlsx not found. Using dummy data.")
    df_2024 = pd.DataFrame({
        'ProjectID': ['5', '18', '57'],
        'OutputTitle': [
            'Entry, Expansion, and Intensity in the U.S. Export Boom',
            'Wage and Productivity Stability in U.S. Manufacturing Plants',
            'Explaining Home Bias in Consumption'
        ]
    })

# Merge datasets
df = pd.concat([df_base, df_enriched, df_2024], ignore_index=True)
df = df.drop_duplicates(subset=['ProjectID', 'OutputTitle']).reset_index(drop=True)

# Check if OutputTitle exists
if 'OutputTitle' not in df.columns:
    print("Error: OutputTitle column missing. Using dummy titles.")
    df['OutputTitle'] = ['Sample Title'] * len(df)

# Text processing
stop_words = set(stopwords.words('english'))
words = []

for title in df['OutputTitle'].dropna():
    tokens = word_tokenize(str(title).lower())
    # Remove stopwords and non-alphabetic tokens
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    words.extend(tokens)

# Count word frequencies
word_counts = Counter(words)
top_words = word_counts.most_common(10)

# Visualize top words
words, counts = zip(*top_words) if top_words else (['No words'], [0])
plt.figure(figsize=(10, 6))
plt.bar(words, counts)
plt.xlabel("Words")
plt.ylabel("Frequency")
plt.title("Top 10 Words in Output Titles")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Save text analysis results
text_df = pd.DataFrame(top_words, columns=['Word', 'Count']) if top_words else pd.DataFrame({'Word': ['No words'], 'Count': [0]})
text_df.to_csv("Text_Processing_Results.csv", index=False)
print("Text processing results saved to Text_Processing_Results.csv")