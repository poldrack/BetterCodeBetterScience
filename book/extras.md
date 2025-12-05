## for Intro

- discuss Naur, "Programming as theory building"

## for essentials

- discuss databases - e.g., sqlite example


## from AI-assisted coding chapter

## github spec kit

## More on MCP?

## AI-human pair programming

We often view AI coding agents as autonomous 

## Leveraging LLM coding for reproducibility

LLM-based chatbots can be very useful for solving many problems beyond coding.  For example, we recently worked on a paper with more than 100 authors, and needed to harmonize the affiliation listings across authors.  This would have been immensely tedious for a human, but working with an LLM we were able to solve the problem with only a few manual changes needed.  Other examples where we have used LLMs in the research process include data reformatting and summarization of text for meta-analyses.  However, as noted above, the use of chatbots in scientific research is challenging from the standpoint of reproducibility, since it is generally impossible to guarantee the ability to reproduce an LLM output; even if the random seed is fixed, the commercial models change regularly, without the ability to go back to a specific model version.  

The ability to LLMs to write code to solve problems provides a solution to the reproducibility challenge: instead of simply using a chatbot to solve a problem, ask the chatbot to generate code to solve the problem, which makes the result testable and reproducible.  This is also a way to solve problems with information that you don't want to submit to the LLM for privacy reasons.

For example, ...

# Project structure


## Python modules

While Python has native access to a small number of functions, much of the functionality of Python comes from *modules*, which provide access to objects defined in separate files that can be imported into a Python session.  All Python users will be familiar with importing functions from standard libraries (such as `os` or `math`) or external packages (such as `numpy` or `pytorch`). It's also possible to create one's own modules simply by putting functions into a file.

Let's say that we have a set of functions that do specific operations on text, saved to a file called `textfuncs.py` in our working directory:

```
def reverse(text):
    return text[::-1]

def capitalize(text):
    return text.capitalize()

def lowercase(text):
    return text.lower()
```

If we wish to use those functions within another script ('mytext.py'), we can simply import the module and then run them:

```
import textfuncs

def main():
    mytext = "Hello World"
    print(mytext)
    print(textfuncs.reverse(mytext))
    print(textfuncs.capitalize(mytext))
    print(textfuncs.lowercase(mytext))

if __name__ == "__main__":
    main()
```

Giving the results:

```
❯ python mytext.py
Hello World
dlroW olleH
Hello world
hello world
```

```{admonition} Antipattern
It's not uncommon to see Python programmers use *wildcard imports*, such as `from mytext import *`.  This practice is an antipattern and should be avoided, because it can make it very difficult to debug problems with imported functions, particularly if there is a wildcard import from more than one module.  It can also result in collisions if two modules have a function with the same name, and can prevent linters from properly analyzing the code.  It's better practice to explicitly import all objects from a module, or to use fully specified paths within the module.

R users might notice that this antipattern is built into the way that library functions are usually imported in R: In general, when one imports a library the functions are made available directly in the global namespace.  For example, if we load the `dplyr` library we will see several errors regarding objects being masked:

````
> library(dplyr)

Attaching package: ‘dplyr’

The following objects are masked from ‘package:stats’:

    filter, lag

The following objects are masked from ‘package:base’:

    intersect, setdiff, setequal, union
````

This means that if we call `filter()` it will now refer to `dplyr::filter()` rather than the default reference to `stats::filter()`.  This can cause major problems when one adds library imports during the development process, since those later additions can mask functions that had worked without disambiguation before.  For this reason, when coding in R it's always good to use the full disambiguated function call for any functions with generic names like "select" or "filter".

```

### Creating a Python module using uv




### Practical principles for scientific data management

This chapter will lay out a set of approaches for effective data management, which are built around a set of principles that I think are useful and practical for researchers:

- Original data should be immutable (read-only)
- Original data should be backed up on a separate system
- Data access should operate according to the principle of least privilege
- All data processing operations should be reproducible
    - Thus, manual operations should be minimized and extensively documented
- File/folder names should be machine-readable
- Open and non-proprietary file formats should be used whenever possible
- The provenance of any file should be findable
- All data should be documented so that the user can determine the identity of any variable in the dataset
- Changes to the data should be tracked
    - Either via VCS or some other strategy
- When working with secondary data, always know your rights and responsibilities
- Understand the data storage/retention/deletion requirements for your data



##### Timeseries databases

Timeseries data represent repeated measurements over time, and are ubiquitous in science, from 
Timeseries data have several features that can be leveraged to optimized storage and querying:

- They are naturally ordered in time
- Operations mostly involve appending new data, rather than modifying older data
- Queries are usual defined by specific ranges of time, rather than random queries

Timeseries databases like InfluxDB are optimized to represent and query timeseries data.  By taking advantage of the unique structure of timeseries data, they can query these data much more efficiently than other databases that are not optimized. 




#### Column-family databases

A column-family database is built to effectively store and retrieve very large datasets where there are many columns for each row, and where the columns may be grouped together into *families*.  These databases are purpose-built for the processing of large datasets that may be distributed across multiple computers. An important difference from a standard data frame representation is that each row doesn't have to have any entry for every column, which allows much more efficient storage and retrieval of sparse data.  They are also very efficient for tasks that involve a large number of database writes, such as high-throughput data collection devices.  Well-known column-family databases include Apache Cassandra, Apache HBase, and Google Bigtable.

- Cassandra example



As an example, let's upload the demographic data from the Eisenberg et al. (2019) into a SQL database using SQLite, which is a very lightweight database package, and perform some example queries. We can create the database and load the data using the following code:

```python
demographics_df = pd.read_csv("https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/demographics.csv", index_col=0)
# recode sex based on data dictionary: {1: 'F', 0: 'M'}
demographics_df['Sex'] = demographics_df['Sex'].map({1: 'F', 0: 'M'})

# Create an SQLite database 
database_name = 'demographics.db'
with sqlite3.connect(database_name) as conn:
    # Load the DataFrame into the SQLite database
    demographics_df.to_sql('demographics', conn, 
                        if_exists='replace', index=False)

    # Verify the table was created
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables in database:", cursor.fetchall())
```
```bash
Tables in database: [('demographics',)]
```

We can see that the demographics table was created in the database; a production-level SQL server such as MySQL or MariaDB would store this information in a separate location, possibly on a different machine where the server runs, whereas SQLite stores it in a local file.  Now let's say that we wanted to count how many records there are for each sex.  We do this by creating a SQL query that computes the count of the variable separately for each group. Here we use the pandas `read_sql_query` function, which is a handy function to convert the output of an SQL database query into a Pandas data frame:

```python
SELECT Sex, COUNT(*) as count 
FROM demographics 
GROUP BY Sex
ORDER BY count DESC
"""
with sqlite3.connect(database_name) as conn:
    result_df = pd.read_sql_query(query, conn)
print("Count by sex:")
print(result_df)
```
```bash
Count by sex:
  Sex  count
0   F    262
1   M    260
```

We can also create a query to further summarize data, in this case computing the mean height for each sex:

```python
query = """
SELECT Sex, 
       ROUND(AVG(HeightInches), 2) as avg_height
FROM demographics 
GROUP BY Sex
"""
with sqlite3.connect(database_name) as conn:
    result_df = pd.read_sql_query(query, conn)
    
print("Height statistics by sex:")
print(result_df)
```
```bash
Height statistics by sex:
  Sex  avg_height
0   F       64.48
1   M       70.01
```

This example highlights the fluidity with which one can move between data frames and relational databases, since they fundamentally have the same underlying structure.

### Pymongo example


One of the most popular document stores is [MongoDB](https://www.mongodb.com/). The MongoDB software can be installed locally on one's own computer, but for this example I will take advantage of the free *Atlas* hosting service that MongoDB offers.  After logging into [MongoDB](https://www.mongodb.com/) (which I did using my Github credentials), I was asked to select the kind of cluster that I wanted to create, for which I chose the *Free* tier, and I named it "testcluster".  The site then provides information on how to connect, along with a username and password, which I saved to my `.env` file as `MONGO_USERNAME` and `MONGO_PASSWORD`.  After creating the database user, the database is now running, and the site provides us with a full code snippet showing how to connect to the database within Python:

```python
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import dotenv
import os

dotenv.load_dotenv()
assert 'MONGO_USERNAME' in os.environ and 'MONGO_PASSWORD' in os.environ, 'MongoDB username and password should be set in .env'

uri = f"mongodb+srv://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@testcluster.n3ilcua.mongodb.net/?appName=testcluster"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
```
```bash
Pinged your deployment. You successfully connected to MongoDB!
```

Now we can create a new database table. In this example we will store bibliographic data obtained from the PubMed database for a particular search query, using a set of functions defined the `pubmed` module.

```python
import pubmed

results = pubmed.get_processed_query_results('"fMRI"', retmax=10000, verbose=True)
print(f'found {len(results)} results')
```
```bash
searching for "fMRI"
found 9999 matches
found 9941 results
```

The results are returned as a dictionary that is keyed by the DOI for the publication and includes a set of elements representing the various parts of the PubMed record, as in this example record:

```python
{'DOI': '10.1093/cercor/bhaf238',
 'Abstract': 'The SPM software package played a major role in the establishment of open source software practices within the field of neuroimaging. I outline its role in my career development and the impact it has had within our field.',
 'PMC': None,
 'PMID': 40928748,
 'type': 'journal-article',
 'journal': 'Cereb Cortex',
 'year': 2025,
 'volume': '35',
 'title': 'SPM as a cornerstone of an open source software ecosystem for neuroimaging.',
 'page': None,
 'authors': 'Poldrack RA'}
```

The Python interface to MongoDB take dictionaries as input, so we can convert the dictionary into a list of separate dictionaries for each publication and then add these to the collection:

```python
from pymongo import UpdateOne

# In MongoDB, databases and collections are created lazily (when first document is inserted)
db = client['research_database']
publications_collection = db['publications'] 

# Clear existing data in the collection (optional, for clean start)
publications_collection.delete_many({})

# Convert results dictionary to list of documents
documents = [document for document in results.values()]

# Insert all documents into the collection
# Create a unique index on PMID to prevent duplicates
publications_collection.create_index("PMID", unique=True)

if documents:
    # Use bulk_write with upsert operations to update existing or insert new documents
    operations = [
        UpdateOne(
            {"PMID": doc["PMID"]},  # Filter by PMID
            {"$set": doc},  # Update the document
            upsert=True  # Insert if it doesn't exist
        )
        for doc in documents
    ]
    
    result = publications_collection.bulk_write(operations)
    print(f"Successfully upserted {result.upserted_count} new publications")
    print(f"Modified {result.modified_count} existing publications")
    print(f"Total operations: {len(operations)}")
else:
    print("No documents to insert")

# Verify insertion by counting documents
count = publications_collection.count_documents({})
print(f"Total publications in collection: {count}")
```
```bash
Successfully upserted 9941 new publications
Modified 0 existing publications
Total operations: 9941
Total publications in collection: 9941
```

Now that the documents are in the database, we can search for documents that match a specific query.  For example, let's say that we want to find all papers that include the term "Memory" (in a case-insensitive manner) in the title:

```python
query = {"title": {"$regex": "Memory", "$options": "i"}}  # Case-insensitive search for "Memory"
memory_pubs = list(publications_collection.find(query))
print(f"Found {len(memory_pubs)} publications containing {query['title']['$regex']} in the title")
```
```bash
Found 422 publications containing Memory in the title
```

One very nice feature of the document store is that not all records have to have the same keys; this provides a great deal of flexibility at data ingestion.  However, too much heterogeneity between documents can make the database hard to work with.  One benefit of homogeneity in the document structure is that it allows indexing, which can greatly increase the speed of queries in large document stores.  For example, if we know that we will often want to search by the `year` field, then we can add an index for this field:

*MORE HERE*
