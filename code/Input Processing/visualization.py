
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import textwrap

sns.set_style("whitegrid")


def visualize_csv(file_path):
    """
    Load a CSV of research outputs and produce in order:
      1. Top 10 RDCs by number of research outputs
      2. Publications per year (Year vs. count)
      3. Top 10 most prolific authors
      4. Distribution of Output Types
      5. Cleaned boxplot of Output Pages by Output Type
      6. Top projects by number of publications
    """
    df = pd.read_csv(file_path)

    top_10_rdcs(df)
    publications_per_year(df)
    top_10_authors(df)
    distribution_of_output_types(df)
    top_projects_by_publications(df)


def top_10_rdcs(df):
    """
    1. Top 10 RDCs by number of research outputs.
    """
    rdc_counts = (
        df.groupby("ProjectRDC")
          .size()
          .sort_values(ascending=False)
          .head(10)
          .sort_values()
    )
    plt.figure(figsize=(10, 6))
    sns.barplot(
        x=rdc_counts.values,
        y=rdc_counts.index,
        palette="Blues_d",
        edgecolor=".3"
    )
    plt.title("Top 10 RDCs by Number of Research Outputs", fontsize=16)
    plt.xlabel("Number of Outputs", fontsize=12)
    plt.ylabel("RDC", fontsize=12)
    plt.tight_layout()
    plt.show()


def publications_per_year(df):
    """
    2. Publications per year (line chart).
    """
    df_year = df.copy()
    df_year["OutputYear"] = pd.to_numeric(df_year["OutputYear"], errors="coerce")
    df_year = df_year.dropna(subset=["OutputYear"])
    df_year["OutputYear"] = df_year["OutputYear"].astype(int)
    counts = df_year.groupby("OutputYear").size()

    plt.figure(figsize=(10, 6))
    sns.lineplot(
        x=counts.index,
        y=counts.values,
        marker="o",
        color="tab:green",
        linewidth=2
    )
    plt.title("Publications per Year", fontsize=16)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Number of Publications", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def top_10_authors(df):
    """
    3. Top 10 most prolific authors.
    """
    def extract_authors(cit):
        if not isinstance(cit, str):
            return []
        m = re.match(r'^(.*?)\s+\(\d{4}|n\.d\.\)', cit)
        if not m:
            return []
        return [a.strip() for a in m.group(1).split(" & ") if a.strip()]

    def flip_name(name):
        parts = name.split(", ")
        return f"{parts[1]} {parts[0]}" if len(parts) == 2 else name

    df2 = df.copy()
    df2["Authors"] = df2["OutputBiblio"].apply(extract_authors)
    authors = df2["Authors"].explode().dropna().map(flip_name)
    ac = authors.value_counts().head(10).sort_values()

    plt.figure(figsize=(10, 6))
    sns.barplot(
        x=ac.values,
        y=ac.index,
        palette="magma",
        edgecolor=".3"
    )
    plt.title("Top 10 Most Prolific Authors", fontsize=16)
    plt.xlabel("Number of Publications", fontsize=12)
    plt.ylabel("")
    plt.tight_layout()
    plt.show()


def distribution_of_output_types(df):
    """
    4. Distribution of Output Types (bar chart).
    """
    counts = df["OutputType"].value_counts()
    plt.figure(figsize=(8, 5))
    sns.barplot(
        x=counts.index,
        y=counts.values,
        palette="pastel",
        edgecolor=".3"
    )
    plt.title("Distribution of Output Types", fontsize=16)
    plt.xlabel("Output Type", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def top_projects_by_publications(df, top_n=10, min_pubs=1, wrap_width=40, annotate=True):
    """
    6. Top projects by publication count.
    """
    pc = (
        df.groupby("ProjectTitle")
          .size()
          .rename("PublicationCount")
          .reset_index()
    )
    filt = pc[pc["PublicationCount"] >= min_pubs]
    tp = filt.sort_values("PublicationCount", ascending=False).head(top_n).copy()
    tp["WrappedTitle"] = tp["ProjectTitle"].apply(
        lambda t: "\n".join(textwrap.wrap(t, wrap_width))
    )

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=tp,
        y="WrappedTitle",
        x="PublicationCount",
        palette="rocket",
        edgecolor=".3"
    )

    if annotate:
        mx = tp["PublicationCount"].max()
        for bar in ax.patches:
            w = bar.get_width()
            ax.text(
                w + mx * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{int(w)}",
                va="center"
            )

    ax.set_title(f"Top {len(tp)} Projects by Publications", fontsize=16)
    ax.set_xlabel("Number of Publications", fontsize=12)
    ax.set_ylabel("")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    visualize_csv("ResearchOutputs_Group4.csv")
