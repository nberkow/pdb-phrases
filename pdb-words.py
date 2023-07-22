import requests
import asyncio
import aiohttp

import backoff
from WordTree import WordTree

import sys
import logging

async def return_emptystring(e):
    return ""


@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException,
                      max_tries=3
                      )
def query_pdb(pdb_id, logger):

    """
    Query PDB with a generated ID and index. The entry may not exist.

    - return the amino acid sequence on success
    - fails if the query raises an exception
    """

    i = 1
    template = "https://data.rcsb.org/rest/v1/core/polymer_entity/{}/{}"
    q = template.format(pdb_id, i)

    logger.info(f"trying: {pdb_id}")
    response = requests.get(q)
    logger.info(response.status_code)
    
    sequence = response.json()["entity_poly"]["pdbx_seq_one_letter_code"]
    return((pdb_id, sequence))

async def fetch_data(endpoint, logger):
    try:
        seq = query_pdb(endpoint, logger)
        return(seq)
    except:
        logger.error(f"Exception caught for {endpoint}")
        return "" 
    
def find_words(aa_seq, word_tree, pdb_id):
    for i in range(len(aa_seq)):
        word_tree.find_word_chain(aa_seq, i, [])

    chains = word_tree.get_best_chains(3, 2.25)
    if len(chains) > 0:
        with open(f"chains/{pdb_id}.txt", 'w') as chains_file:
            for c in chains:
                printable_chain = " ".join(c)
                print(f"{pdb_id}\t{printable_chain}", file=chains_file)
    word_tree.reset() 

def get_fetch_tasks(logger):

    
    id_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVXYZ"
    #id_characters = "4HB" # this subset has hits
    tasks = []

    for char1 in id_characters:
        for char2 in id_characters:
            for char3 in id_characters: 
                for char4 in id_characters:
                    pdb_id = char1 + char2 + char3 + char4
                    tasks.append(fetch_data(pdb_id, logger))
    return(tasks)
         
async def process_data(data, word_tree):

    if len(data) == 2:
        pdb_id, seq = data

        #print(pdb_id)
        #print(seq)

        if len(seq) > 0:
            find_words(seq, word_tree, pdb_id)

async def main():

    logging.basicConfig(filename="pdb.log",
        format='%(asctime)s %(message)s',
        filemode='w')
    logger = logging.getLogger()

    # build a word search tree
    word_list_file = sys.argv[1]
    word_tree = WordTree()
    word_tree.build_from_file(word_list_file)

    # get fetch_data function calls for each pdb ID
    tasks = get_fetch_tasks(logger)
    logger.info(f"{len(tasks)} queries to run")

    responses = await asyncio.gather(*tasks)
    for response in responses:
        await process_data(response, word_tree)

if __name__ == "__main__":
    asyncio.run(main())

    #find_words(aa_seq, word_tree, pdb_id)

