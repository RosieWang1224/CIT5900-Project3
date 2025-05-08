def filter_csv(enriched_file, output_file):
    import pandas as pd
    from build_metadata import build_project_metadata_dict

    # Load enriched file
    enriched_df = pd.read_csv(enriched_file, converters={"Authors": eval})

    # Load project metadata
    project_metadata_dict = build_project_metadata_dict("ProjectsAllMetadata.xlsx")

    # Normalize full PI names
    def normalize_name(name):
        return " ".join(name.strip().lower().split())

    # Extract first initial and last name
    def extract_initial_and_last(name):
        """
        Extract first initial and last name
        """
        if not isinstance(name, str) or not name.strip():
            return None, None
        parts = name.replace(".", "").strip().split()
        if len(parts) == 1:
            return None, parts[0].lower()
        return parts[0][0].lower(), parts[-1].lower()

    def extract_keywords(text):
        """
        Extract keywords from a block of text (e.g., abstract or title)
        """
        if not isinstance(text, str):
            return set()

        common_words = {
            "a", "an", "the", "and", "or", "in", "on", "of", "for", "with",
            "to", "by", "their", "it", "its", "this", "that", "as", "from",
            "is", "are", "was", "were", "be"
        }

        words = text.lower().split()
        words = [word.strip(",!?():;.\"'") for word in words]
        keywords = {word for word in words if word not in common_words and len(word) > 2}

        return keywords

    def match_output_to_project(output_title, candidate_projects):
        """
        Given an output title and a dict of candidate project metadata, return
        the best-matching (projid, metadata) tuple based on keyword overlap.
        """
        title_keywords = extract_keywords(output_title)

        best_match = None
        max_overlap = -1

        for projid, metadata in candidate_projects.items():
            abstract = metadata.get("Abstract", "")
            abstract_keywords = extract_keywords(abstract)
            overlap = len(title_keywords & abstract_keywords)

            if overlap > max_overlap:
                best_match = (projid, metadata)
                max_overlap = overlap

        return best_match

    # Match authors to PIs and merge info
    filtered_rows = []
    for _, row in enriched_df.iterrows():
        authors = row.get("Authors", [])
        matched_pi_name = None
        matched_projects = {}

        # Step 1: Match an author to a PI
        for author in authors:
            a_init, a_last = extract_initial_and_last(author)
            for pi_norm, meta in project_metadata_dict.items():
                pi_name = meta.get("ProjectPI", "")
                pi_init, pi_last = extract_initial_and_last(pi_name)
                if a_last == pi_last and (a_init == pi_init or not a_init or not pi_init):
                    matched_pi_name = pi_name
                    # Collect all projects by this PI
                    matched_projects = {
                        projid: m for projid, m in project_metadata_dict.items()
                        if normalize_name(m.get("ProjectPI", "")) == normalize_name(pi_name)
                    }
                    break
            if matched_pi_name:
                break

        # Step 2: If a PI is matched, now choose the best matching project
        if matched_projects:
            best_match = match_output_to_project(row.get("OutputTitle", ""), matched_projects)
            if best_match:
                projid, meta = best_match
                enriched_row = {
                    "ProjID": projid,
                    "ProjectStatus": meta.get("ProjectStatus", ""),
                    "ProjectTitle": meta.get("ProjectTitle", ""),
                    "ProjectRDC": meta.get("ProjectRDC", ""),
                    "ProjectYearStarted": int(meta["ProjectYearStarted"]) if pd.notna(meta.get("ProjectYearStarted")) else pd.NA,
                    "ProjectYearEnded": int(meta["ProjectYearEnded"]) if pd.notna(meta.get("ProjectYearEnded")) else pd.NA,
                    "ProjectPI": meta.get("ProjectPI", "")
                }
                # Combine with row (excluding Authors)
                enriched_row.update(row.drop(labels=["Authors"]).to_dict())
                filtered_rows.append(enriched_row)

    # Sort by ProjID and write to CSV
    final_df = pd.DataFrame(filtered_rows)
    final_df = final_df.sort_values(by="ProjID", key=lambda col: pd.to_numeric(col, errors='coerce'))
    final_df.to_csv(output_file, index=False)