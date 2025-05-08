def enrich_csv(df, output_file):
    import pandas as pd
    import re
    import time
    import requests
    import xml.etree.ElementTree as ET

    # Fixes the spacing of the titles in the file
    df["title"] = df["title"].astype(str).str.replace('\n', ' ').str.replace('\r', ' ').str.replace(r'\s+', ' ', regex=True).str.strip()

    # Prepare containers for metadata
    output_years, output_months = [], []
    output_venues, output_volumes = [], []
    output_numbers, output_pages = [], []
    output_biblios, output_authors = [], []
    output_titles = []

    def normalize_title(title):
        """
        Normalizes the title for search to ensure matches are found
        """
        title = str(title).lower()
        title = re.sub(r"[’‘“”]", "'", title)  # Normalize quotes
        title = re.sub(r"[^\w\s]", "", title)  # Remove punctuation
        title = re.sub(r"\s+", " ", title)     # Remove extra whitespace
        return title.strip()

    def normalize_doi(doi):
        """
        Normalizes the doi by returning just the identifying section
        """
        if isinstance(doi, str):
            return doi.replace("https://doi.org/", "").strip()
        return doi

    def search_openalex(norm_title):
        """
        Searches OpenAlex for the first result when a title is searched
            Falls back on CrossRef DOI search if the journal is missing from OpenAlex
            """
        try:
            query = "+".join(norm_title.split())
            r = requests.get(f"https://api.openalex.org/works?search={query}&per-page=1")
            if r.status_code == 200:
                results = r.json().get("results", [])
                if results:
                    data = results[0]

                    doi = data.get("doi")
                    if not doi or not isinstance(doi, str) or not doi.startswith("https://doi.org/"):
                        doi = pd.NA

                    host_venue = data.get("host_venue", {})
                    journal = host_venue.get("display_name")

                    # Fallback to CrossRef if journal is missing and DOI is usable
                    if (journal is None or pd.isna(journal)) and isinstance(doi, str):
                        fallback = search_crossref_doi(doi)
                        if fallback:
                            _, _, _, fallback_journal, *_ = fallback
                            journal = fallback_journal

                    title = data.get("title", "").strip()
                    authors = [a.get("author", {}).get("display_name", "") for a in data.get("authorships", [])]
                    year = data.get("publication_year", pd.NA)
                    month = int(data.get("publication_date", "0000-00-00")[5:7]) if data.get("publication_date") else pd.NA
                    volume = data.get("biblio", {}).get("volume", pd.NA)
                    issue = data.get("biblio", {}).get("issue", pd.NA)
                    pages = data.get("biblio", {}).get("first_page", pd.NA)

                    return title, authors, year, month, journal, volume, issue, pages, doi, "OpenAlex"
        except Exception as e:
            print(f"OpenAlex title search failed for '{norm_title}': {e}")

    def search_crossref_doi(doi):
        """
        Searches CrossRef using DOI as a fallback for OpenAlex Title Search
        """
        doi = normalize_doi(doi)
        try:
            r = requests.get(f"https://api.crossref.org/works/{doi}")
            if r.status_code == 200:
                data = r.json().get("message", {})
                title_api = data.get("title", [""])[0].strip() if "title" in data else ""
                authors = []
                for a in data.get("author", []):
                    if isinstance(a, dict):
                        name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                        if name: authors.append(name)
                journal = data.get("container-title", [pd.NA])[0] if data.get("container-title") else pd.NA
                return title_api, authors, None, None, journal, None, None, None, doi, "CrossRef"
        except Exception as e:
            print(f"CrossRef DOI lookup failed for {doi}: {e}")

        return None

    def search_crossref(norm_title):
        """
        Searches CrossRef for the first result when a title is searched
        """
        try:
            query = "+".join(norm_title.split())
            r = requests.get(f"https://api.crossref.org/works?query.title={query}&rows=1")
            if r.status_code == 200:
                items = r.json()["message"].get("items", [])
                if items:
                    data = items[0]
                    title_api = data.get("title", [""])[0].strip() if "title" in data else ""
                    authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in data.get("author", [])]
                    year = data.get("issued", {}).get("date-parts", [[pd.NA]])[0][0]
                    month = data.get("issued", {}).get("date-parts", [[pd.NA, pd.NA]])[0][1] if len(data.get("issued", {}).get("date-parts", [[pd.NA]])[0]) > 1 else pd.NA
                    journal = data.get("container-title", [pd.NA])[0]
                    volume = data.get("volume", pd.NA)
                    issue = data.get("issue", pd.NA)
                    pages = data.get("page", pd.NA)
                    doi = data.get("DOI", pd.NA)
                    return title_api, authors, year, month, journal, volume, issue, pages, doi, "CrossRef"
        except Exception as e:
            print(f"CrossRef title search failed for '{norm_title}': {e}")

    def search_arxiv(norm_title):
        """
        Searches arXiv for the first result when a title is searched
        """
        try:
            query = "+".join(norm_title.split())
            r = requests.get(f"https://export.arxiv.org/api/query?search_query=ti:{query}&max_results=1")
            if r.status_code == 200:
                root = ET.fromstring(r.text)
                entries = root.findall("{http://www.w3.org/2005/Atom}entry")
                if entries:
                    entry = entries[0]
                    title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
                    title_api = title_elem.text.strip() if title_elem is not None else ""
                    authors = [
                        a.find("{http://www.w3.org/2005/Atom}name").text
                        for a in entry.findall("{http://www.w3.org/2005/Atom}author")
                    ]
                    published = entry.find("{http://www.w3.org/2005/Atom}published")
                    year = int(published.text[:4]) if published is not None else pd.NA
                    month = int(published.text[5:7]) if published is not None else pd.NA
                    doi_elem = entry.find("{http://arxiv.org/schemas/atom}doi")
                    doi = doi_elem.text if doi_elem is not None else pd.NA
                    return title_api, authors, year, month, "arXiv", pd.NA, pd.NA, pd.NA, doi, "arxiv"
        except Exception as e:
            print(f"arXiv fallback failed for '{norm_title}': {e}")

    def sequential_api_search(doi, norm_title):
        """
        Enacts a pipeline in which, for each title, OpenAlex (and CrossRef DOI) is searched
            followed by CrossRef title search
            and finally arXiv title search
            """
        result = search_openalex(norm_title)
        if result:
            return result

        result = search_crossref(norm_title)
        if result:
            return result

        result = search_arxiv(norm_title)
        if result:
            return result

        return None

    def get_metadata(title, doi=None):
        """
        Enriches the data by searching the 3 APIs: OpenAlex, CrossRef, and arXiv
        """
        norm_title = normalize_title(title)
        result = sequential_api_search(doi, norm_title)
        if result:
            title_api, authors, year, month, journal, volume, issue, pages, doi, source = result
        else:
            title_api, authors, year, month, journal, volume, issue, pages, doi, source = "", [], pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA
        return title_api, authors, year, month, journal, volume, issue, pages, doi, source

    def format_apa_authors(authors):
        """
        Creates a formatted list of author names to fit APA format: Last Name, First Initial
        """
        def format_one(name):
            """
            Formats each individual name in APA format
            """
            parts = name.strip().split()
            if len(parts) == 1:
                return parts[0]
            last = parts[-1]
            initials = [p[0] + "." for p in parts[:-1] if p]
            return f"{last}, {' '.join(initials)}"

        formatted = [format_one(name) for name in authors if name]
        if len(formatted) == 0:
            return ""
        elif len(formatted) == 1:
            return formatted[0]
        elif len(formatted) == 2:
            return f"{formatted[0]} & {formatted[1]}"
        else:
            return ", ".join(formatted[:-1]) + ", & " + formatted[-1]

    def make_apa_citation(authors, year, title, journal, volume, issue, pages, doi, source):
        """
        Makes APA citations from components extracted
        """
        authors_str = format_apa_authors(authors)
        year_str = str(year) if pd.notna(year) else "n.d."

        if isinstance(source, str) and source.lower() == "arxiv" and isinstance(doi, str) and "arxiv" in doi.lower():
            arxiv_id = doi.split("/")[-1]
            citation = f"{authors_str} ({year_str}). \"{title}\" (arXiv:{arxiv_id}). *arXiv*."
        elif isinstance(source, str) and "ssrn" in str(doi).lower():
            citation = f"{authors_str} ({year_str}). \"{title}\". *SSRN Working Paper Series*."
        elif isinstance(source, str) and "nber" in str(doi).lower():
            citation = f"{authors_str} ({year_str}). \"{title}\". *NBER Working Paper Series*."
        else:
            citation = f"{authors_str} ({year_str}). \"{title}\""
            if pd.notna(journal):
                citation += f". *{journal}*"
            if pd.notna(volume):
                citation += f", {volume}"
            if pd.notna(issue):
                citation += f"({issue})"
            if pd.notna(pages):
                citation += f", {pages}"
            citation += "."

        if isinstance(doi, str) and "doi.org" in doi:
            citation += f" {doi.strip()}"
        elif isinstance(doi, str) and doi.startswith("10."):
            citation += f" https://doi.org/{doi.strip()}"

        return citation

    # Matches month numbers to names
    month_lookup = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    def month_number_to_name(month):
        """
        Changes month numbers to names
        """
        try:
            if pd.isna(month):
                return pd.NA
            return month_lookup.get(int(month), pd.NA)
        except:
            return pd.NA

    """Iterates through each title and adds the metadata to lists"""
    for idx, row in df.iterrows():
        title = row.get("title")
        doi = row.get("doi")
        print(f"Searching ({idx + 1} of {len(df)}): {title}")

        title_api, authors, year, month, journal, volume, issue, pages, doi, source = get_metadata(title, doi)
        time.sleep(0.5)

        citation = make_apa_citation(authors, year, title_api, journal, volume, issue, pages, doi, source)
        year_str = str(year) if pd.notna(year) else "n.d."

        output_titles.append(title_api)
        output_biblios.append(citation)
        output_authors.append(authors)
        output_years.append(year_str)
        output_months.append(month_number_to_name(month))
        output_venues.append(journal)
        output_volumes.append(volume)
        output_numbers.append(issue)
        output_pages.append(pages)

    def infer_output_type(row):
        """
        Uses OutputBiblio and OutputVenue to determine the OutputType
        """
        citation = str(row.get("OutputBiblio", "")).lower()
        venue = str(row.get("OutputVenue", "")).lower()

        type_keywords = {
            "WP": ["arxiv", "ssrn", "nber", "mimeo", "working paper", "white paper", "technical report", "preprint", "discussion paper"],
            "JA": ["journal", "review", "letters", "transactions", "proceedings", "bulletin", "chaos", "fractals", "economic", "science", "statistics"],
            "MI": ["media", "interview", "press release", "news"],
            "BC": ["book chapter", "in ", "edited volume"],
            "BK": ["book", "monograph"],
            "RE": ["report", "census report", "annual report"],
            "TN": ["technical note"],
            "DI": ["dissertation", "thesis"],
            "SW": ["software", "codebase", "repository", "github"],
            "MT": ["multimedia", "video", "podcast"],
            "DS": ["dataset", "data release"],
            "BG": ["blog", "opinion", "column", "newsletter"]
        }

        if "*" in citation and re.search(r"\d{4}\)\. \"(.*?)\"\.* \*.*?\*", citation):
            return "JA"

        for type_code, keywords in type_keywords.items():
            if any(keyword in citation or keyword in venue for keyword in keywords):
                return type_code

        return "WP"  # assume WP if uncertain

    def infer_output_status(row):
        """
        Uses OutputVenue, OutputType, and OutputBiblio to determine OutputStatus
        """
        output_type = row.get("OutputType", "")
        venue = str(row.get("OutputVenue", "")).lower()
        citation = str(row.get("OutputBiblio", "")).lower()

        if venue.strip() == "":
            return "UP"

        wp_keywords = ["working paper", "white paper", "technical report", "arxiv", "ssrn", "nber", "mimeo", "preprint", "discussion paper", "conference"]
        if any(word in citation for word in wp_keywords):
            return "UP"

        journal_keywords = ["journal", "review", "letters", "transactions", "proceedings", "bulletin", "matematika", "economic", "statistics"]
        if output_type == "JA" and any(j in venue for j in journal_keywords):
            return "PB"

        if output_type == "WP":
            return "UP"

        return "PB"

    """Adds all of the information to an enriched DataFrame"""
    enriched_df = pd.DataFrame()
    enriched_df["OutputTitle"] = output_titles
    enriched_df["Authors"] = output_authors
    enriched_df["OutputBiblio"] = output_biblios
    enriched_df["OutputVenue"] = output_venues
    enriched_df["OutputType"] = enriched_df.apply(infer_output_type, axis=1)
    enriched_df["OutputStatus"] = enriched_df.apply(infer_output_status, axis=1)
    enriched_df["OutputYear"] = output_years
    enriched_df["OutputMonth"] = output_months
    enriched_df["OutputVolume"] = output_volumes
    enriched_df["OutputNumber"] = output_numbers
    enriched_df["OutputPages"] = output_pages

    # Creates a CSV file from the enriched DataFrame
    enriched_df.to_csv(output_file, index=False)

    return enriched_df