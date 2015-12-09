# stdlib
import csv
import json
from itertools import combinations, chain
flatten = chain.from_iterable # alias
from collections import defaultdict
import operator

# external
import pandas

class CharacterNetwork:

    SENTENCE = 'sentenceID'
    PARAGRAPH = 'paragraphId'
    M = -1
    F = 1
    WORD_GENDERS = {
        'Mr.' : M,
        'he' : M,
        'his' : M,
        'him' : M,
        'himself' : M,

        'Ms.' : F,
        'Mrs.' : F,
        'she' : F,
        'her' : F,
        'hers' : F,
        'herself' : F,
    }

    def __init__(self, tokens_file, book_file, strategy='sentenceID', gender=True, sentiment=True):
        ''' Creates an undirected, weighted graph of characters (vertices) and interactions (edges).

            :param tokens_file: The bookNLP output token file.
            :param book_file: The bookNLP output JSON .book file.
            :param strategy: Grouping strategy for determining interactions. 
                Also effects context window for sentiment analysis.
                Supports CharacterNetwork.SENTENCE and CharacterNetwork.PARAGRAPH.
            :param gender: Assign a gender to the characters.
            :param sentiments: Assign a sentiment to the interactions.
        '''
        ### LOAD FILES ###
        # BookNLP output tokens csv into a Pandas DataFrame
        tokens_df = pandas.read_csv(filepath_or_buffer=tokens_file, sep='\t', 
            engine='c', quoting=csv.QUOTE_NONE)

        # BookNLP .book file into a dictionary
        char_data = json.load(book_file)['characters']
        ###################

        # Create vertices w/ attributes
        vertex_attr = ['label']
        if gender:
            vertex_attr += ['gender']
        self.vertex_df = pandas.DataFrame(index=xrange(len(char_data)), columns=vertex_attr)
        self.vertex_df['label'] = [char['names'][0]['n'] if char['names'] else 'UNK' for char in char_data]
        if gender:
            self.vertex_df['gender'] = [
                self.__get_gender(tokens_df[tokens_df['characterId'] == char_id]['lemma']) 
                for char_id in self.vertex_df.index]

        # Create edges w/ attributes
        edge_attr = ['weight']
        if sentiment:
            from nltk.corpus import sentiwordnet
            edge_attr += ['avg_pos', 'avg_neg', 'avg_obj']

        edge_dict = defaultdict(lambda:[0]*len(edge_attr))
        # Get character groups for each sentence or paragraph
        for sentenceID, group in tokens_df[tokens_df['characterId'] != -1].groupby(strategy)['characterId'].unique().iteritems():
            if len(group) > 1:
                if sentiment:
                    score = self.__get_sentiment(tokens_df[tokens_df[strategy] == sentenceID]['lemma'], sentiwordnet)
                else:
                    score = []
                # form an edge out of all unique pairs of the group
                for edge in combinations(group, 2):
                    edge_dict[edge] = map(operator.add, edge_dict[edge], [1] + score)
       
        if sentiment:
             # average pos,neg,obj scores by weight
            edge_dict = {k:v[:1] + map(lambda x:float(x)/v[0], v[1:]) for k,v in edge_dict.iteritems()}

        self.edge_df = pandas.DataFrame.from_dict(edge_dict, orient='index')
        self.edge_df.columns = edge_attr

    ########################
    #### HELPER METHODS ####
    ########################

    def __get_sentiment(self, lemmas, sentiwordnet):
        ''' Assign a gender to a given character.
        
            :param lemmas: list of lemmas to use for assigning sentiment.

            :returns: score list: [pos, neg, obj]
        '''
        score = [0,0,0]
        for lemma in lemmas:
            senti_synsets = sentiwordnet.senti_synsets(lemma.decode('ascii','ignore'))
            if senti_synsets:
                score = map(operator.add, score, 
                    [senti_synsets[0].pos_score(),
                    senti_synsets[0].neg_score(),
                    senti_synsets[0].obj_score()])
        return score


    def __get_gender(self, lemmas):
        ''' Assign a gender to a given character.

            :param lemmas: list of words to use for assigning gender.

            :returns: 'Male', 'Female', or 'UNK'
        '''
        score = sum(CharacterNetwork.WORD_GENDERS.get(lemma, 0) for lemma in lemmas)
        if score < 0: return 'Male'
        elif score > 0: return 'Female'
        else: return 'UNK'


    #####################
    #### API METHODS ####
    #####################

    def get_vertices(self):
        ''' :returns: a copy of the vertex DataFrame '''
        return self.vertex_df.copy()


    def get_edges(self):
        ''' :returns: a copy of the edge DataFrame '''
        return self.edge_df.copy()


    def get_igraph(self):
        ''' Get an igraph.Graph object for all graph theoretical needs.

            :returns: a igraph.Graph object
        '''
        import igraph

        graph = igraph.Graph()

        graph.add_vertices(self.vertex_df.index.values)
        for attribute in self.vertex_df:
            graph.vs[attribute] = self.vertex_df[attribute]

        graph.add_edges(self.edge_df.index.values)
        for attribute in self.edge_df:
            graph.es[attribute] = self.edge_df[attribute]

        return graph