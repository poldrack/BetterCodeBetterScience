"""Functions to work with pubmed data

This module provides functions to work with pubmed data, including querying
pubmed for articles and parsing the results.

The module contains the following functions:

- `get_processed_query_results`: Query pubmed for articles and return a dictionary of processed results.
- `run_pubmed_query`: Query pubmed for articles and return the raw pubmed records.
- `parse_pubmed_query_result`: Parse the pubmed records into a dictionary.
- `get_pubmed_journal_name`: Get the journal name from a pubmed record.
- `get_pubmed_title`: Get the title from a pubmed record.
- `get_pubmed_pmid`: Get the PMID from a pubmed record.
- `get_pubmed_doi`: Get the DOI from a pubmed record.
- `get_pubmed_pmcid`: Get the PMCID from a pubmed record.
- `get_pubmed_year`: Get the year from a pubmed record.
- `get_pubmed_volume`: Get the volume from a pubmed record.
- `get_pubmed_pages`: Get the pages from a pubmed record.
- `get_pubmed_authors`: Get the authors from a pubmed record.
- `get_pubmed_abstract`: Get the abstract from a pubmed record.
- `parse_pubmed_record`: Parse a pubmed record into a dictionary.
"""

from Bio import Entrez
import dotenv
import os
from typing import Optional


def get_email_from_dotenv() -> str:
    email = os.getenv("ENTREZ_EMAIL")
    if email is None:
        dotenv.load_dotenv()
        email = os.getenv("ENTREZ_EMAIL")
    if email is None:
        raise ValueError(
            "ENTREZ_EMAIL is not set in env - set in .env file or set as environment variable"
        )
    return email


def get_processed_query_results(
    query: str, email: Optional[str] = None, retmax: int = 1000, verbose: bool = False
) -> dict:
    """
    Get processed query results for a pubmed query

    Args:
        query (str): the query to search for
        email (str): the email to use for the Entrez service
        retmax (int): the maximum number of results to return
        verbose (bool): whether to print verbose output

    Returns:
        dict: a dictionary of processed query results
    """
    if email is None:
        email = get_email_from_dotenv()

    pubmed_records = run_pubmed_query(query, email, retmax, verbose)
    return parse_pubmed_query_result(pubmed_records)


def run_pubmed_query(
    query: str, email: str, retmax: int = 1000, verbose: bool = False
) -> dict:
    """
    Run a pubmed query and return the raw pubmed records

    Args:
        query (str): the query to search for
        email (str): the email to use for the Entrez service
        retmax (int): the maximum number of results to return
        verbose (bool): whether to print verbose output

    Returns:
        dict: a dictionary of pubmed records
    """
    Entrez.email = email
    if verbose:
        print(f"using {email} for Entrez service")
        print("searching for", query)
    handle = Entrez.esearch(db="pubmed", retmax=retmax, term=query)
    record = Entrez.read(handle)
    handle.close()
    pmids = [int(i) for i in record["IdList"]]
    if verbose:
        print("found %d matches" % len(pmids))

    # load full records
    handle = Entrez.efetch(
        db="pubmed",
        id=",".join(["%d" % i for i in pmids]),
        retmax=retmax,
        retmode="xml",
    )
    return Entrez.read(handle)


def parse_pubmed_query_result(pubmed_records: dict) -> dict:
    """
    Parse the pubmed records into a dictionary

    Args:
        pubmed_records (dict): the pubmed records to parse

    Returns:
        dict: a dictionary of parsed pubmed records
    """
    pubs = {}
    for i in pubmed_records["PubmedArticle"]:
        parsed_record = parse_pubmed_record(i)
        pubs[parsed_record["DOI"]] = parsed_record
    return pubs


def get_pubmed_journal_name(record: dict) -> str:
    """
    Get the journal name from a pubmed record

    Args:
        record (dict): the pubmed record to parse

    Returns:
        str: the journal name
    """
    return record["MedlineCitation"]["Article"]["Journal"]["ISOAbbreviation"]


def get_pubmed_title(record: dict) -> str:
    """
    Get the title from a pubmed record

    Args:
        record (dict): the pubmed record to parse

    Returns:
        str: the title
    """
    return record["MedlineCitation"]["Article"]["ArticleTitle"]


def get_pubmed_pmid(record: dict) -> int:
    """
    Get the PMID from a pubmed record

    Args:
        record (dict): the pubmed record to parse

    Returns:
        int: the PMID
    """
    return int(record["MedlineCitation"]["PMID"])


def get_pubmed_doi(record: dict) -> str:
    """
    Get the DOI from a pubmed record

    Args:
        record (dict): the pubmed record to parse

    Returns:
        str: the DOI
    """
    doi = None
    for j in record["PubmedData"]["ArticleIdList"]:
        if j.attributes["IdType"] == "doi":
            doi = str(j).lower().replace("http://dx.doi.org/", "")
    return doi


def get_pubmed_pmcid(record: dict) -> str:
    """
    Get the PMCID from a pubmed record

    Args:
        record (dict): the pubmed record to parse

    Returns:
        str: the PMCID
    """
    pmc = None
    for j in record["PubmedData"]["ArticleIdList"]:
        if j.attributes["IdType"] == "pmc":
            pmc = str(j)
    return pmc


def get_pubmed_year(record: dict) -> int:
    """
    Get the year from a pubmed record

    Args:
        record (dict): the pubmed record to parse

    Returns:
        int: the year
    """
    year = None
    if (
        "Year"
        in record["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"]
    ):
        year = int(
            record["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"][
                "Year"
            ]
        )
    elif (
        "MedlineDate"
        in record["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"]
    ):
        year = int(
            record["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"][
                "MedlineDate"
            ].split(" ")[0]
        )
    return year


def get_pubmed_volume(record: dict) -> str:
    """
    Get the volume from a pubmed record

    Args:
        record (dict): the pubmed record to parse

    Returns:
        str: the volume
    """
    volume = None
    if "Volume" in record["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]:
        volume = record["MedlineCitation"]["Article"]["Journal"]["JournalIssue"][
            "Volume"
        ]
    return volume


def get_pubmed_pages(record: dict) -> str:
    """
    Get the pages from a pubmed record

    Args:
        record (dict): the pubmed record to parse

    Returns:
        str: the pages
    """
    pages = None
    if "Pagination" in record["MedlineCitation"]["Article"]:
        pages = record["MedlineCitation"]["Article"]["Pagination"]["MedlinePgn"]
    return pages


def get_pubmed_authors(record: dict) -> str:
    """
    Get the authors from a pubmed record

    Args:
        record (dict): the pubmed record to parse

    Returns:
        str: the authors
    """
    authors = None
    if "AuthorList" in record["MedlineCitation"]["Article"]:
        authorlist = [
            " ".join([author["LastName"], author["Initials"]])
            for author in record["MedlineCitation"]["Article"]["AuthorList"]
            if "LastName" in author and "Initials" in author
        ]

        authors = ", ".join(authorlist)
    return authors


def get_pubmed_abstract(record: dict) -> str:
    """
    Get the abstract from a pubmed record

    Args:
        record (dict): the pubmed record to parse

    Returns:
        str: the abstract
    """
    abstract = None
    if "Abstract" in record["MedlineCitation"]["Article"]:
        if "AbstractText" in record["MedlineCitation"]["Article"]["Abstract"]:
            abstract = " ".join(
                record["MedlineCitation"]["Article"]["Abstract"]["AbstractText"]
            )
    return abstract


def parse_pubmed_record(record: dict) -> dict:
    """
    Parse a pubmed record into a dictionary

    Args:
        record (dict): the pubmed record to parse

    Returns:
        dict: a dictionary of parsed pubmed record
    """
    return {
        "DOI": get_pubmed_doi(record),
        "Abstract": get_pubmed_abstract(record),
        "PMC": get_pubmed_pmcid(record),
        "PMID": get_pubmed_pmid(record),
        "type": "journal-article",
        "journal": get_pubmed_journal_name(record),
        "year": get_pubmed_year(record),
        "volume": get_pubmed_volume(record),
        "title": get_pubmed_title(record),
        "page": get_pubmed_pages(record),
        "authors": get_pubmed_authors(record),
    }
