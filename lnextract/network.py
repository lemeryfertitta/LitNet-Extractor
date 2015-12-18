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
    VERTEX_ATTR = ['label', 'count', 'gender']

    def __init__(self, tokens_file, char_file, strategy='sentenceID', sentiment=False):
        ''' Creates an undirected, weighted graph of characters (vertices) and interactions (edges).

            :param tokens_file: The bookNLP output token CSV file.
            :param book_file: The bookNLP output character JSON file.
            :param strategy: Grouping strategy for determining interactions (and sentiments). 
                Supports CharacterNetwork.SENTENCE and CharacterNetwork.PARAGRAPH.
            :param sentiments: Assign a sentiment to the interactions.
        '''
        ### LOAD FILES ###
        # BookNLP tokens CSV into a Pandas DataFrame
        tokens_df = pandas.read_csv(filepath_or_buffer=tokens_file, sep='\t', 
            engine='c', quoting=csv.QUOTE_NONE)

        # BookNLP character JSON into a dictionary
        char_data = json.load(char_file)['characters']
        ###################

        # Create vertices w/ attributes
        self.vertex_df = pandas.DataFrame(
            data=[self.__get_char_attr(char) for char in char_data],
            index=xrange(len(char_data)),
            columns=CharacterNetwork.VERTEX_ATTR)

        # Create edges w/ attributes
        edge_attr = ['weight']
        if sentiment:
            from nltk.corpus import sentiwordnet
            edge_attr += ['avg_pos', 'avg_neg', 'avg_obj']

        edge_dict = defaultdict(lambda:[0]*len(edge_attr))
        # Get character groups for each sentence or paragraph
        for context_id, group in tokens_df[tokens_df['characterId'] != -1].groupby(strategy)['characterId'].unique().iteritems():
            if len(group) > 1:
                if sentiment:
                    score = self.__get_sentiment(tokens_df[tokens_df[strategy] == context_id]['lemma'], sentiwordnet)
                else:
                    score = []
                # form an edge out of all unique pairs of the group
                for edge in combinations(group, 2):
                    # undirected, so we don't want parallel edges.
                    edge = tuple(sorted(edge))
                    edge_dict[edge] = map(operator.add, edge_dict[edge], [1] + score)
       
        if sentiment:
             # average pos,neg,obj scores by weight
            edge_dict = {k:v[:1] + map(lambda x:float(x)/v[0], v[1:]) for k,v in edge_dict.iteritems()}

        self.edge_df = pandas.DataFrame.from_dict(edge_dict, orient='index')
        self.edge_df.columns = edge_attr
        if sentiment:
            self.edge_df['pos-neg'] = self.edge_df['avg_pos'] - self.edge_df['avg_neg']

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

    def __get_char_attr(self, char_dict):
        name_list = char_dict['names']
        label = name_list[0]['n'].encode('utf-8') if name_list else 'UNK'
        gender_int = char_dict['g']
        gender = 'female' if (gender_int == 1) else 'male' if (gender_int == 2) else 'UNK'
        count = char_dict['NNPcount']
        return (label, count, gender)

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

        graph.add_vertices(len(self.vertex_df))
        for attribute in self.vertex_df:
            graph.vs[attribute] = self.vertex_df[attribute]

        graph.add_edges(self.edge_df.index.values)
        for attribute in self.edge_df:
            graph.es[attribute] = self.edge_df[attribute]

        return graph