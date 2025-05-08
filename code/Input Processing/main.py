import pandas as pd
from enrich_all_csv_files import enrich_csv
from build_metadata import build_project_metadata_dict
from filter_all_csv_files import filter_csv
from visualizations import visualize_csv

def load_and_normalize_title(filepath):
    df = pd.read_csv(filepath)
    for col in ["title", "Title", "OutputTitle"]:
        if col in df.columns:
            df["title"] = df[col]
            df["normalized_title"] = df[col].astype(str).str.lower().str.strip()
            return df
    raise ValueError(f"No title column found in {filepath}")

# List of files
files = [f"group{i}.csv" for i in range(1, 9)]

# Load and normalize "title" in files
all_dfs = [load_and_normalize_title(file) for file in files]

# Concatenate and remove duplicates
combined_df = pd.concat(all_dfs, ignore_index=True)
deduped_df = combined_df.drop_duplicates(subset="normalized_title").reset_index(drop=True)
deduped_df["title"] = deduped_df["normalized_title"]

enrich_csv(deduped_df, "Group4_Enriched.csv")
filter_csv("Group4_Enriched.csv", "ResearchOutputs_Group4.csv")
visualize_csv("ResearchOutputs_Group4.csv")