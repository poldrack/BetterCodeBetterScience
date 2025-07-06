# pytest tests for textmining functions
# assumes that coding_for_science has been installed as a module
# should install as editable with pip install -e .

import pytest
import requests
from BetterCodeBetterScience.textmining.textmining import (
    get_PubmedIDs_for_query,
    parse_year_from_Pubmed_record,
    get_record_from_PubmedID,
)

# fixtures

@pytest.fixture(scope="session")
def ids():
    query = "friston-k AND 'free energy'"
    ids = get_PubmedIDs_for_query(query)
    return ids

# # integration tests

# def test_get_num_records_per_year_for_query():
#     query = "friston-k AND 'free energy'"
#     records_by_year_df = get_num_records_per_year_for_query(query)
#     assert records_by_year_df is not None
#     assert records_by_year_df.shape[0] > 0

# unit tests

def test_get_PubmedIDs_for_query_check_valid(ids):
    assert isinstance(ids, list)
    assert len(ids) > 0


def test_get_PubmedIDs_for_query_check_empty():
    query = "friston-k AND 'fizzbuzz'"
    ids = get_PubmedIDs_for_query(query)
    assert len(ids) == 0


def test_get_PubmedIDs_for_query_check_badurl():
    query = "friston-k AND 'free energy'"
    # bad url
    esearch_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.f'
    
    # make sure that the function raises an exception
    with pytest.raises(Exception):
        ids = get_PubmedIDs_for_query(query, esearch_url=esearch_url)
    

# adapted from the pytest documentation
# https://docs.pytest.org/en/6.2.x/monkeypatch.html
class MockPubmedResponse:
    status_code = 200
    @staticmethod
    def json():
        return {
            'header': {'type': 'esearch', 'version': '0.3'},
            'esearchresult': {
                'count': '2',
                'retmax': '20',
                'retstart': '0',
                'idlist': ['39312494', '39089179']
            }
        }


@pytest.fixture
def ids_mocked(monkeypatch):

    def mock_get(*args, **kwargs):
        return MockPubmedResponse()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)

    query = "friston-k AND 'free energy'"
    ids = get_PubmedIDs_for_query(query)
    return ids


def test_get_PubmedIDs_for_query_check_valid_mocked(ids_mocked):
    assert isinstance(ids_mocked, list)
    assert len(ids_mocked) == 2


# better implementation of the mock suggested by Gemini 2.5 Pro
@pytest.fixture
def mock_pubmed_api(monkeypatch):

    class MockPubmedResponse:
        status_code = 200
        def json(self):
            return {
                'header': {'type': 'esearch', 'version': '0.3'},
                'esearchresult': {
                    'count': '2',
                    'retmax': '20',
                    'retstart': '0',
                    'idlist': ['39312494', '39089179']
                }
            }

    def mock_get(*args, **kwargs):
        return MockPubmedResponse()

    # Apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)


# The test requests the setup, then performs the action and assertion.
def test_get_PubmedIDs_for_query_check_valid_mocked(mock_pubmed_api):
    # Action: Call the function under test
    query = "friston-k AND 'free energy'"
    ids = get_PubmedIDs_for_query(query)

    # Assertion: Check the result
    assert isinstance(ids, list)
    assert len(ids) == 2


@pytest.fixture(scope="session")
def valid_pmid():
    return "39312494"


@pytest.fixture(scope="session")
def pmid_record(valid_pmid):
    record = get_record_from_PubmedID(valid_pmid)
    return record


def test_get_record_from_valid_PubmedID(pmid_record, valid_pmid):
    assert pmid_record is not None
    assert isinstance(pmid_record, dict)
    assert pmid_record['uid'] == valid_pmid


def test_get_record_from_invalid_PubmedID():
    pmid = "10000000000"
    with pytest.raises(Exception):
        record = get_record_from_PubmedID(pmid)



def test_parse_year_from_Pubmed_record():
    record = {
        "pubdate": "2021 Jan 1"
    }
    year = parse_year_from_Pubmed_record(record)
    assert year == 2021


def test_parse_year_from_Pubmed_record_empty():
    record = {
        "pubdate": ""
    }
    year = parse_year_from_Pubmed_record(record)
    assert year is None

def test_parse_year_from_Pubmed_record_valid():
    record = {
        "pubdate": "2022 12 05"
    }
    year = parse_year_from_Pubmed_record(record)
    assert year == 2022


# # parameterized tests - specific pubmed records across decades
# testdata = [
#     ('17773841', 1944),
#     ('13148370', 1954),
#     ('14208567', 1964),
#     ('4621244', 1974),
#     ('6728178', 1984),
#     ('10467601', 1994),
#     ('15050513', 2004)
# ]


# @pytest.mark.parametrize("pmid, year_true", testdata)
# def test_parse_year_from_pmid_parametric(pmid, year_true):
#     record = get_record_from_PubmedID(pmid)
#     year_result = parse_year_from_Pubmed_record(record)
#     assert year_result == year_true
