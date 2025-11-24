# functions used in database examples notebook

import requests
import dotenv
from database import (
    setup_mongo_collection,
    get_chromadb_collection,
    get_neo4j_session
)
from tqdm import tqdm
import pandas as pd
import os
from pathlib import Path
import ols_client
from requests.exceptions import HTTPError
from gprofiler import GProfiler
from pubmed import (
    run_pubmed_search,
    fetch_pubmed_records,
    parse_pubmed_query_result
)
import pymongo
from pymongo import UpdateOne
import hashlib
import json
import numpy as np

dotenv.load_dotenv()


def compute_phenotype_similarities():
    with get_neo4j_session() as session:
        try:
            session.run("CALL gds.graph.drop('phenotype-pathway-graph') YIELD graphName")
        except: # noqa: E722
            pass  # graph did not exist

        session.run("""
            CALL gds.graph.project(
            'phenotype-pathway-graph',
            ['Phenotype', 'Pathway'],
            {
                MAPPED_TO: {
                orientation: 'UNDIRECTED'
                }
            }) """
        )

        # drop nodes with degree less than make similarity estimate more reliable
        results = session.run("""
            CALL gds.nodeSimilarity.stream('phenotype-pathway-graph')
            YIELD node1, node2, similarity
            WITH node1, node2, similarity
            MATCH (p1:Phenotype), (p2:Phenotype)
            WHERE id(p1) = node1 AND id(p2) = node2
                AND COUNT { (p1)-[:MAPPED_TO]->(:Pathway) } > 1
                AND COUNT { (p2)-[:MAPPED_TO]->(:Pathway) } > 1
            RETURN p1.id AS phenotype1, p2.id AS phenotype2, similarity
            ORDER BY similarity DESC
        """)

        return pd.DataFrame([{
            'phenotype1': record['phenotype1'],
            'phenotype2': record['phenotype2'],
            'similarity': record['similarity']
        } for record in results])


def compute_text_similarities(similarity_result_df):
    pmids_by_trait_collection = setup_mongo_collection('pmids_by_trait',  
        clear_existing=False)

    results = []
    for idx in similarity_result_df.index:
        pmids = []
        num_pmids = []

        for phenotype in [similarity_result_df.loc[idx, 'phenotype1'],
                        similarity_result_df.loc[idx, 'phenotype2']]:

            doc = pmids_by_trait_collection.find_one({'trait_uri': phenotype})
            if doc and 'pmids' in doc:
                pmids.append([str(i) for i in doc['pmids']])
                num_pmids.append(len(doc['pmids']))
            else:
                num_pmids.append(0)
        if len(pmids) == 2 and len(pmids[0]) > 0 and len(pmids[1]) > 0:
            tsim = vectorized_pairwise_similarity(pmids[0], pmids[1])
        else:
            tsim = None
        result = {
            'phenotype1': similarity_result_df.loc[idx, 'phenotype1'],
            'phenotype2': similarity_result_df.loc[idx, 'phenotype2'],
            'pathway_similarity': similarity_result_df.loc[idx, 'similarity'],
            'text_similarity': tsim,
            'num_pmids_phenotype1': num_pmids[0],
            'num_pmids_phenotype2': num_pmids[1],
        }
        results.append(result)

    return pd.DataFrame(results)


def build_neo4j_graph():

    geneset_annotations_by_trait = setup_mongo_collection(
        collection_name='geneset_annotations_by_trait')

    with get_neo4j_session() as session:
        # Clear existing data if needed
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create constraints for performance
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Phenotype) REQUIRE p.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (g:Gene) REQUIRE g.id IS UNIQUE")
        
        # add all pathways as nodes
        pathway_collection = setup_mongo_collection('pathways',  
            clear_existing=False)
        pathways = list(pathway_collection.find())
        for pathway in pathways:
            session.run("""
                MERGE (pw:Pathway {id: $pathway_id})
                SET pw.name = $name,
                    pw.source = $source,
                    pw.description = $description
            """, pathway_id=pathway['pathway_id'],
                 name=pathway.get('name', ''),
                 source=pathway.get('source', ''),
                 description=pathway.get('description', ''))
        
        # load all annotation data from MongoDB
        phenotypes = geneset_annotations_by_trait.find()
        
        for phenotype in phenotypes:
            phenotype_id = phenotype['mapped_trait_uri']
            pathways = [i['native'] for i in phenotype.get('functional_annotation', [])]
            if len(pathways) == 0:
                continue
            # Batch create nodes and relationships
            session.run("""
                MERGE (p:Phenotype {id: $phenotype_id})
                SET p.name = $name
                WITH p
                UNWIND $pathways AS pathway
                MERGE (g:Pathway {id: pathway})
                MERGE (p)-[:MAPPED_TO]->(g)
            """, phenotype_id=str(phenotype_id), 
                 name=phenotype.get('trait_name', ''),
                 pathways=pathways)

    # print total number of pathways and phenotypes in the database
    with get_neo4j_session() as session:
        result = session.run("MATCH (p:Phenotype) RETURN count(p) AS phenotype_count")
        phenotype_count = result.single()['phenotype_count']
        result = session.run("MATCH (pw:Pathway) RETURN count(pw) AS pathway_count")
        pathway_count = result.single()['pathway_count']
        print(f"Total Phenotypes in DB: {phenotype_count}")
        print(f"Total Pathways in DB: {pathway_count}")


def vectorized_pairwise_similarity(set_a_ids, set_b_ids):
    """Vectorized computation of pairwise similarities"""
    collection = get_chromadb_collection()

    results_a = collection.get(ids=set_a_ids, include=['embeddings'])
    results_b = collection.get(ids=set_b_ids, include=['embeddings'])
    
    embeddings_a = np.array(results_a['embeddings'])
    embeddings_b = np.array(results_b['embeddings'])
    
    # Normalize embeddings
    embeddings_a = embeddings_a / np.linalg.norm(embeddings_a, axis=1, keepdims=True)
    embeddings_b = embeddings_b / np.linalg.norm(embeddings_b, axis=1, keepdims=True)
    
    # Compute similarity matrix
    similarity_matrix = embeddings_a @ embeddings_b.T
    
    return similarity_matrix.mean()


def add_pubmed_abstracts_to_chromadb():
    pubmed_collection = setup_mongo_collection('pubmed_abstracts',  
        clear_existing=False)
    pubmed_collection.create_index([('PMID', pymongo.ASCENDING)], unique=True)

    collection = get_chromadb_collection()
    # get ids (pmid) and documents (title + abstract) from pubmed_collection
    ids = []
    documents = []
    for entry in pubmed_collection.find({}):
        full_text = entry.get('title', '') + ' ' + entry.get('abstract', '')
        documents.append(full_text)
        ids.append(str(entry['PMID']))

    # exclude ids that are already in the chromadb collection
    existing_ids = set(collection.get(ids=[]).ids)
    ids_to_add = []
    documents_to_add = []
    for i, id_ in enumerate(ids):
        if id_ not in existing_ids:
            ids_to_add.append(id_)
            documents_to_add.append(documents[i])

    # add in batches of 5000
    batch_size = 5000
    for i in range(0, len(ids_to_add), batch_size):
        batch_ids = ids_to_add[i:i + batch_size]
        batch_documents = documents_to_add[i:i + batch_size]
        collection.add(
            ids=batch_ids,
            documents=batch_documents
        )
        print(f"Added {len(batch_ids)} documents to chromadb collection")


def create_gene_info_collection(gene_symbol):
    # get information about each gene 
    geneset_collection = setup_mongo_collection('geneset_annotations_by_trait',  
        clear_existing=False)
    gene_collection = setup_mongo_collection('gene_info',  
        clear_existing=False)
    geneset_docs = geneset_collection.find({})
    unique_genes = set()
    for doc in geneset_docs:
        genes = doc.get('gene_sets', [])
        unique_genes.update(genes)

    print(f"Unique genes to annotate: {len(unique_genes)}")

    # Now fetch gene info from Ensembl REST API
    for gene in tqdm(unique_genes):
        # check if already in db
        existing = gene_collection.find_one({'gene_symbol': gene})
        if existing:
            continue
        res = get_gene_info(gene)
        # save to mongo gene_info collection
        gene_collection.update_one(
            {'gene_symbol': gene},
            {'$set': res},
            upsert=True
        )


def get_pathway_info_by_trait():
    # get information about each gene 
    geneset_collection = setup_mongo_collection('geneset_annotations_by_trait',  
        clear_existing=False)
    pathway_collection = setup_mongo_collection('pathways',  
        clear_existing=False)

    # loop through traits and add pathway information to the database
    traits = [i for i in geneset_collection.find() 
        if 'functional_annotation' in i and len(i['functional_annotation']) > 0]

    for trait in tqdm(traits):
        annotations = trait['functional_annotation']
        for pathway in annotations:
            # change key for clarity
            pathway['pathway_id'] = pathway.pop('native')

            pathway_collection.update_one(
                {'pathway_id': pathway['pathway_id']},
                {'$set': {'name': pathway.get('name', ''),
                        'source': pathway.get('source', ''),
                        'description': pathway.get('description', '')}},
                upsert=True
            )


def get_gene_info(ensembl_id):
    url = f"https://rest.ensembl.org/lookup/id/{ensembl_id}"
    headers = {"Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()
    return None


def fetch_and_store_pubmed_abstracts(batch_size=500, collection_name='pubmed_abstracts'):
    # loop through in batches of batch_size, fetch the records using fetch_pubmed_records, 
    # parse them using parse_pubmed_query_result, and store them in a new mongodb collection
    pubmed_collection = setup_mongo_collection(collection_name,  
        clear_existing=False)
    pubmed_collection.create_index([('PMID', pymongo.ASCENDING)], unique=True)

    # remove any PMIDs already in the pubmed_collection
    existing_pmids = set()
    for entry in pubmed_collection.find({}, {'PMID': 1}):
        existing_pmids.add(entry['PMID'])

    pmids_to_fetch = [pmid for pmid in get_unique_pmids_from_trait_collection() 
                    if pmid not in existing_pmids]

    if len(pmids_to_fetch) == 0:
        print("All PMIDs are already fetched. Skipping.")
    else:
        print(f"Fetching {len(pmids_to_fetch)} PMIDs...")


    for i in tqdm(range(0, len(pmids_to_fetch), batch_size), desc="Fetching PubMed abstracts"):
        batch = pmids_to_fetch[i:i + batch_size]
        pubmed_records = fetch_pubmed_records(batch, retmax=batch_size)
        parsed_records = parse_pubmed_query_result(pubmed_records)
        if not parsed_records:
            print(f"No new records to insert for batch {i // batch_size + 1}.")
            continue
        pubmed_collection.insert_many(parsed_records.values())
        #print(f"Inserted {len(parsed_records)} abstracts")


def get_pmids_for_traits(n_abstracts_per_trait=100, collection_name='pmids_by_trait',
    verbose=False):
    # loop through entires in synonyms_dict and for each synonym, run a pubmed search and store the results in mongodb - combine all synonyms for each DOID into a single query

    pmid_collection = setup_mongo_collection(collection_name)
    _ = pmid_collection.create_index([('trait_uri', pymongo.ASCENDING)], unique=True)
    

    # get all entries from the trait_info_by_trait collection and pull out the label and synonyms to use as pubmed search terms
    trait_info_collection = setup_mongo_collection('trait_info_by_trait')
    db_result = list(trait_info_collection.find({}))


    for result in tqdm(db_result,  desc="Searching PubMed"):
        # split the result into its components in a single line
        trait_uri = result['trait_uri']
        lbl = result['trait_info']['label']
        synonyms = result['trait_info'].get('synonyms', [])
        # create a pubmed query using the label and synonyms
        query_terms = [lbl] + synonyms
        query = ' OR '.join([f'"{term}"' for term in query_terms])

        # see whether this trait_uri is already in the mongodb collection
        existing_entry = pmid_collection.find_one({'trait_uri': trait_uri})
        # check if existing entry is not None and skip if pmid entry is not empty
        if existing_entry is not None and existing_entry.get('pmids') and len(existing_entry.get('pmids')) > 0:
            if verbose:
                print(f"PMIDs already exist for {lbl}, skipping...")
            continue
        # run pubmed search - retry up to 3 times if it fails
        for attempt in range(3):
            try:
                pmids = run_pubmed_search(query,        
                    retmax=n_abstracts_per_trait)
                break
            except: # noqa: E722
                if attempt < 2:
                    print(f"PubMed search failed for {trait_uri} (attempt {attempt + 1}/3). Retrying...")
                else:
                    print(f"PubMed search failed for {trait_uri} after 3 attempts. Skipping.")
                    pmids = []
        pmids = run_pubmed_search(query, retmax=n_abstracts_per_trait)
        pmid_collection.update_one(
            {'trait_uri': trait_uri},
            {'$set': {
                'label': lbl,
                'pmids': pmids,
                'search_query': query
            }},
            upsert=True
        )


def get_unique_pmids_from_trait_collection():
    pmids_to_fetch = []
    pmid_collection = setup_mongo_collection('pmids_by_trait')
    for entry in pmid_collection.find({}, {'pmids': 1}):
        pmids = entry.get('pmids', [])
        pmids_to_fetch.extend(pmids)
    return list(set(pmids_to_fetch))  # unique PMIDs


def annotate_geneset_annotations_by_trait(collection_name='geneset_annotations_by_trait'):
    # loop over all entries in the geneset_annotations_by_trait collection 
    # and do functional annotation of the gene sets

    geneset_annotations_by_trait = setup_mongo_collection(
        collection_name)
        
    gp = GProfiler(return_dataframe=True)

    # use a list here so that we can use tqdm to show progress
    # skip any entries that already have functional_annotation
    annotations = [i for i in geneset_annotations_by_trait.find({}) 
                    if 'functional_annotation' not in i]

    for entry in tqdm(annotations):
        mapped_trait_uri = entry['mapped_trait_uri']
        gene_sets = entry['gene_sets']
        if len(gene_sets) == 0:
            continue
        # do functional annotation
        try:
            annotation_results = gp.profile(
                organism='hsapiens',
                query=gene_sets,
                sources=['GO:BP', 'GO:MF', 'GO:CC', 'KEGG', 'REAC']
            )
        except Exception as e:
            # bare except to avoid breaking the loop
            print(f'Error annotating {mapped_trait_uri}: {e}')
            continue

        # convert the dataframe to a dictionary
        annotation_results_dict = annotation_results.to_dict(orient='records')
        # update the entry in the mongo collection with the annotation results
        geneset_annotations_by_trait.update_one(
            {'mapped_trait_uri': str(mapped_trait_uri)},
            {'$set': {
                'functional_annotation': annotation_results_dict
            }}
        )
    # drop members of geneset_annotations_by_trait with empty functional annotation
    geneset_annotations_by_trait.delete_many({'functional_annotation': {'$in': [None, [], {}]}})
    
    print(f'Remaining entries with functional annotation: {geneset_annotations_by_trait.count_documents({})}')


def get_trait_info_from_ols(collection_name='trait_info_by_trait',
    client_url='http://www.ebi.ac.uk/ols'):
    # use EBI OLS API to get trait information for all traits
    trait_info_by_trait = setup_mongo_collection(
        collection_name='trait_info_by_trait')

    trait_info_by_trait.create_index('trait_uri', unique=True)

    geneset_annotations_by_trait = setup_mongo_collection(
        collection_name='geneset_annotations_by_trait')

    # get all unique trait URIs that are not already in the trait_info_by_trait collection
    unique_trait_uris = [
        i.lstrip() 
        for i in geneset_annotations_by_trait.distinct('mapped_trait_uri')
        if trait_info_by_trait.count_documents({'trait_uri': i.lstrip()}) == 0 
    ]
    print(f'Found {len(unique_trait_uris)} un-annotated trait URIs.')

    client = ols_client.Client(client_url)

    for trait_uri in tqdm(unique_trait_uris):
        trait_id = trait_uri.split('/')[-1]
        trait_uri = str(trait_uri)
        # skip if already in the collection
        if trait_info_by_trait.count_documents({'trait_uri': trait_uri}) > 0:
            continue
        try:
            term_data = get_info_from_ols(trait_id, client)
        except HTTPError:
            print(f'HTTPError for {trait_uri}')
            continue
        if term_data is None:
            print(f'No data returned for {trait_uri}')
            continue
        trait_info_by_trait.update_one(
            {'trait_uri': str(trait_uri)},
            {'$set': {
                'trait_uri': str(trait_uri),
                'trait_info': term_data
            }},
            upsert=True
        )


def import_geneset_annotations_by_trait(gwas_data_melted,       
    collection_name='geneset_annotations_by_trait'):

    geneset_annotations_by_trait = setup_mongo_collection(
        collection_name)

    geneset_annotations_by_trait.create_index('mapped_trait_uri', unique=True)

    # first get a mapping from MAPPED_TRAIT_URI to TRAIT_NAME
    trait_name_mapping = gwas_data_melted.set_index('MAPPED_TRAIT_URI')['MAPPED_TRAIT'].to_dict()

    # loop through each unique MAPPED_TRAIT_URI in gwas_data data frame add all of its gene sets to the mongo collection - don't do the annotation yet
    # lstrip each gene id of any leading or trailing whitespace
    for mapped_trait_uri in tqdm(gwas_data_melted['MAPPED_TRAIT_URI'].unique()):
        gene_sets = gwas_data_melted[
            gwas_data_melted['MAPPED_TRAIT_URI'] == mapped_trait_uri]['GENE_ID'].unique().tolist()
        gene_sets = [gene.strip() for gene in gene_sets]
        geneset_annotations_by_trait.update_one(
            {'mapped_trait_uri': str(mapped_trait_uri)},
            {'$set': {
                'mapped_trait_uri': str(mapped_trait_uri),
                'gene_sets': gene_sets,
                'trait_name': trait_name_mapping.get(mapped_trait_uri, '')
            }},
            upsert=True
        )


def get_exploded_gwas_data(datafile=None):
    if datafile is None:
        datadir = Path(os.getenv('DATA_DIR', '../../data'))
        datafile = datadir / 'gwas' / 'gwas-catalog-download-associations-alt-full.tsv'

    gwas_data = pd.read_csv(datafile, sep='\t', low_memory=False)

    # do some cleaning of the data
    # drop rows where 'REPORTED GENE(S)' is None
    gwas_data = gwas_data[gwas_data['REPORTED GENE(S)'].notna()]
    # the column SNP_GENE_IDS maps to multiple genes, explode the column to have one gene per row
    gwas_data_melted = gwas_data.assign(
        SNP_GENE_ID = gwas_data['SNP_GENE_IDS'].str.split(',')
    ).explode('SNP_GENE_ID')
    # the MAPPED_TRAIT_URI column also has some entries with multiple values, explode those too
    gwas_data_melted = gwas_data_melted.assign(
        MAPPED_TRAIT_URI = gwas_data_melted['MAPPED_TRAIT_URI'].str.split(',')
    ).explode('MAPPED_TRAIT_URI')
    gwas_data_melted = gwas_data_melted.reset_index(drop=True)
    gwas_data_melted = gwas_data_melted.rename(columns={'SNP_GENE_ID': 'GENE_ID'})
    gwas_data_melted = gwas_data_melted.drop(columns=['SNP_GENE_IDS'])
    gwas_data_melted = gwas_data_melted[gwas_data_melted['GENE_ID'].notna()]
    gwas_data_melted.shape

    print(f'found data for {gwas_data_melted["PUBMEDID"].nunique()} unique PUBMEDIDs')
    return gwas_data_melted


def load_disease_ontology(url=None):
    if url is None:
        url = "https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/refs/heads/main/src/ontology/doid-base.json"

    response = requests.get(url)
    if response.status_code == 200:
        # load json from url into a Python dictionary
        return response.json()
    else:
        raise ValueError(f"Failed to load JSON: {response.status_code}")

def process_disease_ontology(data):
    # remove obsolete nodes, which have 'obsolete' in their 'lbl' field
    total_nodes = len(data['graphs'][0]['nodes'])

    data['graphs'][0]['nodes'] = [node for node in data['graphs'][0]['nodes']
        if 'lbl' in node and 'obsolete' not in node['lbl']]

    print(f"Removed {total_nodes - len(data['graphs'][0]['nodes'])} obsolete nodes")

    # move contents of 'meta' into root of data

    
    for node in data['graphs'][0]['nodes']:
        if 'meta' in node:
            for key, value in node['meta'].items():
                node[key] = value
            del node['meta']
        synonyms = []
        for syn in node.get('synonyms', []):
            if 'val' in syn:
                synonyms.append(syn['val'])
        node['synonyms'] = synonyms
        if 'definition' in node and isinstance(node['definition'], dict):
            node['definition'] = node['definition'].get('val', '')
        node['text'] = node.get('lbl', '') + ' ' + node.get('definition', '') + ' ' + ' '.join([i for i in node.get('synonyms', [])])
        query_terms = []
        for syn in node.get('synonyms', []) + [node.get('lbl', '')]:
            query_terms.append(f'"{syn}"')

        node['query'] = " OR ".join(query_terms)


    node_classes = [node for node in data['graphs'][0]['nodes'] if 'type' in node and node['type'] == 'CLASS']

    for node in node_classes:
        del node['type']
        
    node_properties = [node for node in data['graphs'][0]['nodes'] if 'type' in node and node['type'] == 'PROPERTY']

    edges = data['graphs'][0]['edges']

    print(f"""
    Total nodes:    {len(data['graphs'][0]['nodes'])}
        Classes:    {len(node_classes)}
        Properties: {len(node_properties)}
    Total edges:    {len(edges)}
    """)
    return node_classes, node_properties, edges


def get_info_from_ols(trait_id, ols_client):
    ontology, id = trait_id.split('_')
    response = ols_client.get_term(ontology=ontology, iri=f'{trait_id}')
    if '_embedded' in response and 'terms' in response['_embedded']:
        term_data = response['_embedded']['terms'][0]
        return term_data
    else:
        return None



def extract_owl_mappings(owl_path):
    import xml.etree.ElementTree as ET
    def local(tag):
        return tag.split('}')[-1]
    def normalize_id(s):
        if s is None:
            return None
        if ':' in s:
            return s
        if '_' in s:
            return s.replace('_', ':', 1)
        return s

    tree = ET.parse(str(owl_path))
    root = tree.getroot()
    mappings = {}  # oboInOwl:id -> target id (normalized)
    for cls in root.iter():
        if local(cls.tag) != 'Class':
            continue
        # get oboInOwl:id child text (may appear with different prefix)
        obo_id = None
        for ch in cls:
            if local(ch.tag) in ('id', 'ID') and ch.text:
                # common oboInOwl:id tag
                obo_id = ch.text.strip()
                break
        if not obo_id:
            # fallback: try rdfs:label or the class IRI local name
            label = None
            for ch in cls:
                if local(ch.tag) == 'label' and ch.text:
                    label = ch.text.strip()
                    break
            if label:
                obo_id = label

        # find restrictions under subClassOf
        for sub in cls:
            if local(sub.tag) != 'subClassOf':
                continue
            # direct Restriction child
            for restr in sub:
                if local(restr.tag) != 'Restriction':
                    continue
                prop_uri = None
                val_uri = None
                for rch in restr:
                    if local(rch.tag) == 'onProperty':
                        # this was written by claude - not sure why it's necessary
                        prop_uri = rch.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource') or rch.attrib.get('resource') # noqa: F841
                    elif local(rch.tag) == 'someValuesFrom':
                        val_uri = rch.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource') or rch.attrib.get('resource')
                if obo_id and val_uri:
                    target = val_uri.split('/')[-1]
                    mappings[obo_id.replace('MIM', 'OMIM')] = normalize_id(target)
    return mappings

## Disease ontology parsing functions

def get_rel_type_from_edge(rel_type):
    # first filter for bespoke case from infectious disease ontology
    bespoke_replacements = {
        "IDO_0000664": "has_material_basis_in",
        "RO_0002452": "has_symptom",
        "has_origin": "has_origin"
    }
    for key, value in bespoke_replacements.items():
        if key in rel_type:
            return value

    # load json and extract label
    short_form = rel_type.split('/')[-1]

    url = f'https://www.ebi.ac.uk/ols4/api/ontologies/ro/properties/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F{short_form}'    
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()  # This loads the JSON data into a Python dictionary
            if 'label' in data:
                return data['label'].replace(' ', '_')
    except Exception:
        pass
    print('defaulting to RELATED_TO for', rel_type)
    return 'RELATED_TO'


def get_relation_dict(edges):
    edge_types = set([edge.get('pred') for edge in edges])

    relation_dict = {}

    # create a dict mapping edge types to relation labels
    # so that we don't have to do a web request for each edge
    for edge_type in edge_types:
        if 'http' in edge_type:
            relation_dict[edge_type] = get_rel_type_from_edge(edge_type)
        else:
            relation_dict[edge_type] = edge_type
    return relation_dict


# add labels to edge records
def add_relation_labels_to_edges(edges):
    relation_dict = get_relation_dict(edges)
    for i, edge in enumerate(edges):
        pred = edge.get('pred')
        if pred in relation_dict:
            edges[i]['relation_label'] = relation_dict[pred].upper()
        else:
            print('defaulting to RELATED_TO for', pred)
            edges[i]['relation_label'] = 'RELATED_TO'

        doc_id = hashlib.md5(json.dumps(edges[i], sort_keys=True).encode()).hexdigest()
        edges[i]['id'] = doc_id
    assert len(set([edge['id'] for edge in edges])) == len(edges), "Edge IDs are not unique"
    return edges


def create_collection_from_documents(collection, documents, unique_index_col, drop_existing=True):
    # Clear existing data in the collection (optional, for clean start)
    if drop_existing:
        collection.drop()

    # convert documents to list if it's a dict
    if isinstance(documents, dict):
        documents = [doc for doc in documents.values()]

    # Create a unique index on the specified column to prevent duplicates
    collection.create_index(unique_index_col, unique=True)

    if documents:
        # Use bulk_write with upsert operations to update existing or insert new documents
        
        operations = [
            UpdateOne(
                {unique_index_col: doc[unique_index_col]},  # Filter by unique index column
                {"$set": doc},  # Update the document
                upsert=True  # Insert if it doesn't exist
            )
            for doc in documents
        ]

        result = collection.bulk_write(operations)
        print(f"Successfully upserted {result.upserted_count} new documents")
        print(f"Modified {result.modified_count} existing documents")
        print(f"Total operations: {len(operations)}")
    else:
        print("No documents to insert")




# Updated code for Neo4j driver (version 5.x or later)
# Using MERGE for Upsert functionality with batching for performance

def upsert_nodes_batch(tx, nodes_batch):
    """Upsert multiple nodes in a single transaction"""
    query = """
    UNWIND $nodes AS node
    MERGE (n:CLASS {id: node.id})
    SET n += node.properties
    """
    tx.run(query, nodes=nodes_batch)

def upsert_relationships_batch(tx, relationships_batch):
    """Upsert multiple relationships in a single transaction"""
    query = """
    UNWIND $rels AS rel
    MATCH (a {id: rel.sub_id}), (b {id: rel.obj_id})
    MERGE (a)-[r:RELATION {rel_type: rel.rel_type}]->(b)
    """
    tx.run(query, rels=relationships_batch)

def filter_properties(props):
    """Filter properties to only include Neo4j-compatible types"""
    filtered = {}
    for k, v in props.items():
        if isinstance(v, (str, int, float, bool)):
            filtered[k] = v
        elif isinstance(v, list) and all(isinstance(item, (str, int, float, bool)) for item in v):
            filtered[k] = v
    return filtered


    