# text mining example for testing chapter
# We wish to perform a search of the pubmed database for a given query
# and return the results for that query over years

# Problem decomposition:
# 1. Create a function that will search pubmed for a given query and return a list of pubmed IDs
# 2. Create a function that will retrieve the record for a given pubmed ID
# 3. Create a function that will parse a record to extract the year
# 4. Create a function that will summarize the number of records per year
# 5. Create a main function that will take in a query and return a data frame
# with the number of records per year for the query
#
# Notes:
# - We will use the requests module to interact with the pubmed rest api
# - use restructured text for the docstrings
# - use type hints for the function signatures

# import the necessary modules
import requests

# define the eutils base URL globally for the module
# - not best practice but probably ok here
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


# create a function that will search the database for a given query and return a list of pubmed IDs
# the follow code was written by Copilot
def get_PubmedIDs_for_query(
    query: str, retmax: int = None, esearch_url: str = None
) -> list:
    """
    Search database for a given query and return a list of IDs.
    :param query: str, the query to search for
    :param retmax: int, the maximum number of results to return
    :base_url: str, the base url for the pubmed search
    :return: list, a list of pubmed IDs
    """
    # define the base url for the pubmed search
    if esearch_url is None:
        esearch_url = f"{BASE_URL}/esearch.fcgi"

    params = format_pubmed_query_params(query, retmax=retmax)

    response = requests.get(esearch_url, params=params)

    return get_idlist_from_response(response)


def format_pubmed_query_params(query: str, retmax: int = 10000) -> str:
    """
    Format a query for use with the pubmed api.
    :param query: str, the query to format
    :return: dict, the formatted query dict
    """

    # define the parameters for the search
    return {"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax}


def get_idlist_from_response(response: requests.Response) -> list:
    if response.status_code == 200:
        # extract the pubmed IDs from the response
        ids = response.json()["esearchresult"]["idlist"]
        return ids
    else:
        raise ValueError("Bad request")


# given a pubmed ID, retrieve the record using the pubmed api via requests
def get_record_from_PubmedID(pmid: str, esummary_url: str = None) -> dict:
    """
    Retrieve the record for a given pubmed ID.
    :param pmid: str, the pubmed ID to retrieve
    :return: dict, the record for the pubmed ID
    """

    if esummary_url is None:
        esummary_url = f"{BASE_URL}/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"

    response = requests.get(esummary_url)

    result_json = response.json()

    if (
        response.status_code != 200
        or "result" not in result_json
        or pmid not in result_json["result"]
        or "error" in result_json["result"][pmid]
    ):
        raise ValueError("Bad request")

    return result_json["result"][pmid]


def parse_year_from_Pubmed_record(pubmed_record: dict) -> int:
    """
    Parse the year from a pubmed record.
    :param pubmed_record: dict, the pubmed record to parse
    :return: int, the year of the record
    """
    pubdate = pubmed_record.get("pubdate", "")
    if pubdate:
        year = int(pubdate.split()[0])
    else:
        print("problem:", pubmed_record)
    year = int(pubdate.split()[0]) if pubdate else None
    return year
