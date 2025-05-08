def build_project_metadata_dict(file):
    """
    Builds a dictionary from the All Metadata sheet with ProjID as keys.
    Each value is a dictionary of project metadata fields.
    """
    import pandas as pd

    # Loads the project metadata file
    projects_df = pd.read_excel(file, sheet_name="All Metadata")

    # Instatiates a dictionary
    project_metadata_dict = {}

    # Iterates through each row in projects_df and extracts the Proj ID as the key and the project info as a dictionary of values
    for _, row in projects_df.iterrows():
        proj_id = f"{int(row['Proj ID']):04d}" if pd.notna(row['Proj ID']) else None
        if proj_id:
            project_metadata_dict[proj_id] = {
                "ProjectStatus": row.get("Status", pd.NA),
                "ProjectTitle": row.get("Title", pd.NA),
                "ProjectRDC": row.get("RDC", pd.NA),
                "ProjectYearStarted": row.get("Start Year", pd.NA),
                "ProjectYearEnded": row.get("End Year", pd.NA),
                "ProjectPI": row.get("PI", pd.NA),
                "Abstract": row.get("Abstract", pd.NA)
            }
    return project_metadata_dict