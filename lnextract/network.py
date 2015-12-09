# stdlib
import csv
import json
from itertools import combinations, chain
flatten = chain.from_iterable # alias
from collections import Counter
import operator

# external
import pandas
from nltk.corpus import sentiwordnet

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
        vertex_attr = ['Label', 'Gender']
        self.vertex_df = pandas.DataFrame(index=xrange(len(char_data)), columns=vertex_attr)
        self.vertex_df['Label'] = [char['names'][0]['n'] if char['names'] else 'UNK' for char in char_data]
        if gender:
            self.vertex_df['Gender'] = [
                self.__get_gender(tokens_df[tokens_df['characterId'] == char_id]['lemma']) 
                for char_id in self.vertex_df.index]

        # Create edges w/ attributes
        edge_attr = ['Source', 'Target', 'Weight']
        if sentiment:
            edge_attr += ['Pos', 'Neg', 'Obj']
        interactions = {}
        # Get character groups for each sentence or paragraph
        for sentenceID, group in tokens_df[tokens_df['characterId'] != -1].groupby(strategy)['characterId'].unique().iteritems():
            if len(group) > 1:
                if sentiment:
                    score = self.__get_sentiment(tokens_df[tokens_df[strategy] == sentenceID]['lemma'])
                else:
                    score = []
                # form an edge out of all unique pairs of the group
                for edge in combinations(group, 2):
                    interactions[edge] = map(operator.add, interactions.get(edge, [0]*(1+len(score))),[1] + score)
        self.edge_df = pandas.DataFrame(([k[0], k[1]] + v for k,v in interactions.viewitems()), columns=edge_attr)

    ########################
    #### HELPER METHODS ####
    ########################

    def __get_sentiment(self, lemmas):
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
        ''' Get an igraph.Graph object for graph theoretical social network analysis.

            :returns: a weighted igraph.Graph object
        '''
        import igraph
        graph = igraph.Graph()
        graph.add_vertices(self.vertex_df.index.values)
        graph.add_edges(zip(self.edge_df['Source'], self.edge_df['Target']))
        graph.es['weight'] = self.edge_df['Weight']
        return graph


    def to_csv(self, vertex_file, edge_file):
        ''' Write the vertex attribute and edge attribute DataFrames to CSV files.

            :param vertex_file: File for vertex csv.
            :param edge_file: file for file csv.
        '''
        self.vertex_df.to_csv(path_or_buf=vertex_file, encoding='utf-8')
        self.edge_df.to_csv(path_or_buf=edge_file, encoding='utf-8')