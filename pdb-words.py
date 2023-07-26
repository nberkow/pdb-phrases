import requests
import asyncio

import backoff
from WordTree import WordTree

import sys
import logging
import math
from optparse import OptionParser

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
    logger.info(f"found sequence of length: {len(sequence)}")
    return((pdb_id, sequence))

async def fetch_and_process(pdb_id, word_tree, out_path, min_words, min_avg_wordlen, logger):
    try:
        pdb_id, seq = query_pdb(pdb_id, logger)
        
    except Exception as e:
        logger.error(f"Exception caught for {pdb_id}")
        logger.error(str(e))
        return "" 
    
    process_data((pdb_id, seq), word_tree, out_path, min_words, min_avg_wordlen, logger)
    
def find_words(aa_seq, word_tree, pdb_id, out_path, min_words, min_avg_wordlen, logger):

    logger.info(f"finding word chains for {pdb_id}")
    word_tree.reset() 
    for i in range(len(aa_seq)):
        word_tree.find_word_chain(aa_seq, i, [])

    chains = word_tree.get_best_chains(min_words, min_avg_wordlen)
    logger.info(f"found {len(chains)} for {pdb_id}")

    if len(chains) > 0:
        with open(f"{out_path}/{pdb_id}.txt", 'w') as chains_file:
            for c in chains:
                printable_chain = " ".join(c)
                print(f"{pdb_id}\t{printable_chain}", file=chains_file)
    

def get_fetch_tasks(test, word_tree, out_path, min_words, min_avg_wordlen, skip_ids, logger):

    if test:
        id_characters = "4HB" # this subset has hits
    else:
        id_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVXYZ"
    
    tasks = []

    for char1 in id_characters[1:]:
        for char2 in id_characters:
            for char3 in id_characters: 
                for char4 in id_characters:
                    pdb_id = char1 + char2 + char3 + char4
                    if not pdb_id in skip_ids:
                        tasks.append(fetch_and_process(pdb_id, word_tree, out_path, min_words, min_avg_wordlen, logger))
    return(tasks)
         
def process_data(data, word_tree, out_path, min_words, min_avg_wordlen, logger):

    logger.info(f"processing data")
    if len(data) == 2:
        pdb_id, seq = data
        
        if len(seq) > 0:
            find_words(seq, word_tree, pdb_id, out_path, min_words, min_avg_wordlen, logger)
        else:
            logger.error(f"empty sequence for {pdb_id}")

    else:
        logger.info(f"empty data: {data}")

async def main():

    # args
    parser = OptionParser()
    parser.add_option("-m", "--min-words", dest="min_words", default=1)
    parser.add_option("-M", "--min-avg-wordlen", dest="min_avg_wordlen", default=1)
    parser.add_option("-s", "--skip-list", dest="skip_list", default = "")
    parser.add_option("-t", "--test", dest="test_ids_given", default="0")

    (options, args) = parser.parse_args()
    word_list_file = args[0]
    out_path = args[1]
    
    min_words = int(options.min_words)
    min_avg_wordlen = float(options.min_avg_wordlen)

    skip_ids = set()
    if options.skip_list != "":
        with open(options.skip_list, 'r') as skip_file:
            for sid in skip_file:
                skip_ids.add(sid.rstrip())
    print(skip_ids)

    # build a word search tree
    word_tree = WordTree()
    word_tree.build_from_file(word_list_file)

    # set up logging
    logging.basicConfig(filename=f"{out_path}.log",
        format='%(asctime)s %(message)s',
        filemode='w')
    logger = logging.getLogger()
    logger.setLevel("INFO")

    # get fetch_data function calls for each pdb ID
    use_test_ids = False
    if int(options.test_ids_given) > 0:
        use_test_ids = True

    tasks = get_fetch_tasks(use_test_ids, word_tree, out_path, min_words, min_avg_wordlen, skip_ids, logger)
    logger.info(f"{len(tasks)} queries to run")
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())



