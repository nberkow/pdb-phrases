

class WordTree:

    def __init__(self):

        self.tree = {}
        self.chains = []

    def add_word(self, word):

        current_sub_dict = self.tree
        for letter in word + "$":
            if not letter in current_sub_dict:
                current_sub_dict[letter] = {}
            current_sub_dict = current_sub_dict[letter]

    def find_word_chain(self, target_text, start, current_chain):
        current_subtree = self.tree
        current_word = ""
        i = 0

        traversal_complete = False

        while (start + i) < len(target_text) and not traversal_complete:

            # dollar sign marks the end of complete words
            if "$" in current_subtree:
                self.find_word_chain(target_text, start + i, current_chain + [current_word])

            # traverse the tree one letter at a time using the input string
            letter = target_text[start + i]
            if letter in current_subtree:
                current_word += letter
                current_subtree = current_subtree[letter]

            else:
                traversal_complete = True

            i += 1

            self.chains.append(current_chain)


    def build_from_file(self, file):

        with open(file) as words_file:

            for word in words_file:
                self.add_word(word.rstrip())

    def reset(self):
        self.chains = []

    def get_best_chains(self, min_chain_len, min_avg_word):

        filtered_chains = []
        
        for chain in self.chains:            
            if len(chain) >= min_chain_len: 
                wordlen_sum = 0.
                for word in chain:
                    wordlen_sum += len(word)
                if (wordlen_sum/len(chain)) >= min_avg_word:
                    filtered_chains.append(chain)
        return(filtered_chains)
                



if __name__ == "__main__":
    wt = WordTree()

    # IANDLAD
    test = "GTTQCTACRTMIANDLADTMTCHFTQ"

    wt.build_from_file("Taylor/bracelets.txt")
    for i in range(len(test)):
        wt.find_word_chain(test, i, [])

    #print(wt.chains)
