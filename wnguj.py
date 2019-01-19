import pickle
import csv
import sys
import math
from pathlib import Path



def setup():
    # from Guj 'word' :[synset_ids] dictionary dump
# from gujarati_words table we create dictionary where in key is word and value is list of synset_ids it belongs to
# Eg: {
#   'મહાદેવ':[5,2061],
#    ...
# }
    words = {}
    with open('gujarati_words.csv', encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:

                line_count += 1
            else:
                line_count += 1
                s = str(row[0])
                s = s.strip()

                if s in words:
                    words[s].append(int(row[1]))
                else:
                    words[s] = []
                    words[s].append(int(row[1]))

    # serializing the words dictionary
    filename = 'words_synid_mapping_dump'
    outfile = open(filename, 'wb')
    pickle.dump(words, outfile)
    outfile.close()

    reader = open('tbl_all_gujarati_synset_data.csv', encoding='utf8')
    line = (reader.readline())
    mapping = {}
    while line:
        offset = reader.tell()
        line = reader.readline()
        syn_id = line.split(',')[0]
        if syn_id != '':
            mapping[int(syn_id)]=offset
        


    # dump mapping
    filename = 'synid_fileoffset_mapping_dump'
    outfile = open(filename, 'wb')
    pickle.dump(mapping, outfile)
    outfile.close()


class IndoWordNetError(Exception):
    '''An exception class for wordnet-related errors.'''

class Lemma:
    def __init__(self, synset, name):
        self._synset = synset
        self._name = name
        self._lang = 'hindi'

    def __repr__(self):
        return 'Lemma(\'{}.{}.{}.{}\')'.format(self._synset.head_word(), self._synset.pos(), self._synset.synset_id(), self._name)

    def name(self):
        return self._name

    def synset(self):
        return self._synset

    def lang(self):
        return self._lang


class Synset:

    def __init__(self, synset_id, head_word, lemma_names, pos, gloss, examples):
        self._synset_id = synset_id
        self._head_word = head_word
        self._lemma_names = lemma_names
        self._pos = pos
        self._gloss = gloss
        self._examples = examples

    def __repr__(self):
        return 'Synset(\'{}.{}.{}\')'.format(self._head_word, self._pos, self._synset_id)

    def synset_id(self):
        return self._synset_id

    def head_word(self):
        return self._head_word

    def lemma_names(self):
        return self._lemma_names

    def lemmas(self):
        return [Lemma(self, lemma)for lemma in self._lemma_names]

    def pos(self):
        return self._pos

    def gloss(self):
        return self._gloss

    def examples(self):
        return self._examples

    def _relations(self, relation):
        synset_id_list = []
        with open('relations/tbl_{}_{}.csv'.format(self._pos.lower(), relation),encoding='utf8') as reader:
            csv_reader = csv.reader(reader, delimiter=',')
            next(csv_reader)
            for line in csv_reader:
                x = int(line[0].strip())
                if self._synset_id == x:
                    synset_id_list.append(int(line[1]))

        # load synset offset mapping
        synset_filename = 'synid_fileoffset_mapping_dump'
        infile = open(synset_filename, 'rb')
        synset_offset_mapping = pickle.load(infile)
        infile.close()

        # find all synsets
        all_synsets = []
        with open('tbl_all_gujarati_synset_data.csv', encoding='utf8') as reader:
            for i in synset_id_list:
                offset = synset_offset_mapping[i]
                reader.seek(offset)
                csv_reader = csv.reader(reader)
                syn_data = next(csv_reader)
                syn_id = int(syn_data[0])
                syn_pos = syn_data[-1]
                syn_lemmas = syn_data[2].split(',')
                syn_headword = syn_lemmas[0]
                syn_definition = syn_data[3].split(';')[0]
                syn_examples = syn_data[3].split(';')[-1]
                all_synsets.append(
                    Synset(syn_id, syn_headword, syn_lemmas, syn_pos, syn_definition, syn_examples))
        return all_synsets


    def hypernymy(self, lvl=None):

        if self._pos in ['ADJECTIVE', 'ADVERB']:

            raise IndoWordNetError('This synset relation is not valid for adjectives and adverbs.')
        if lvl is not None:
            all_synsets = [[self]]
            for i in range(lvl):
                lvl_synsets = []
                for x in all_synsets[i]:
                    for y in x.hypernymy():
                        lvl_synsets.append(y)
                all_synsets.append(lvl_synsets)
            return all_synsets  
        else:
            return self._relations('hypernymy')

    def hyponymy(self):
        if self._pos in ['ADJECTIVE', 'ADVERB','VERB']:
            raise IndoWordNetError(
                'This synset relation is not valid for adjectives,noun and adverbs.')
        return self._relations('hyponymy')


    def entailment(self):

        if self._pos in ['ADJECTIVE', 'ADVERB','NOUN']:
            raise IndoWordNetError(
                'This synset relation is not valid for adjectives,noun and adverbs.')
        return self._relations('entailment')

    def troponymy(self):

        if self._pos in ['ADJECTIVE', 'ADVERB','NOUN']:
            raise IndoWordNetError(
                'This synset relation is not valid for adjectives,noun and adverbs.')
        return self._relations('troponymy')


    def antonymy(self):
        
        cat =['action','personality','amount','place','colour','quality','direction','size','gender','state','manner','time']
        synset_id_list = set()
        for c in cat:
            with open('relations/tbl_{}_anto_{}.csv'.format(self._pos.lower(), c),encoding='utf8') as reader:
                
                csv_reader = csv.reader(reader, delimiter=',')
                next(csv_reader)
                for line in csv_reader:
                    x = int(line[0].strip())
                    if self._synset_id == x:
                        synset_id_list.add(int(line[2]))
            
        # load synset offset mapping
        synset_filename = 'synid_fileoffset_mapping_dump'
        infile = open(synset_filename, 'rb')
        synset_offset_mapping = pickle.load(infile)
        infile.close()

        # find all synsets
        all_synsets = []
        with open('tbl_all_gujarati_synset_data.csv', encoding='utf8') as reader:
            for i in synset_id_list:
                offset = synset_offset_mapping[i]
                reader.seek(offset)
                csv_reader = csv.reader(reader)
                syn_data = next(csv_reader)
                syn_id = int(syn_data[0])
                syn_pos = syn_data[-1]
                syn_lemmas = syn_data[2].split(',')
                syn_headword = syn_lemmas[0]
                syn_definition = syn_data[3].split(';')[0]
                syn_examples = syn_data[3].split(';')[-1]
                all_synsets.append(
                    Synset(syn_id, syn_headword, syn_lemmas, syn_pos, syn_definition, syn_examples))
        return all_synsets
    
    def meronymy(self):
        
        if self._pos in ['ADJECTIVE', 'ADVERB','VERB']:
            raise IndoWordNetError(
                'This synset relation is not valid for adjectives,verbs and adverbs.')
        
        cat =['component_object','feature_activity','member_collection','phase_state','place_area','portion_mass','position_area','resource_process','stuff_object']
        synset_id_list = set()
        for c in cat:
            with open('relations/tbl_{}_mero_{}.csv'.format(self._pos.lower(), c),encoding='utf-8') as reader:
                
                csv_reader = csv.reader(reader, delimiter=',')
                next(csv_reader)
                for line in csv_reader:
                    x = int(line[0].strip())
                    if self._synset_id == x:
                        synset_id_list.add(int(line[1]))
            
        # load synset offset mapping
        synset_filename = 'synid_fileoffset_mapping_dump'
        infile = open(synset_filename, 'rb')
        synset_offset_mapping = pickle.load(infile)
        infile.close()

        # find all synsets
        all_synsets = []
        with open('tbl_all_gujarati_synset_data.csv', encoding='utf8') as reader:
            for i in synset_id_list:
                offset = synset_offset_mapping[i]
                reader.seek(offset)
                csv_reader = csv.reader(reader)
                syn_data = next(csv_reader)
                syn_id = int(syn_data[0])
                syn_pos = syn_data[-1]
                syn_lemmas = syn_data[2].split(',')
                syn_headword = syn_lemmas[0]
                syn_definition = syn_data[3].split(';')[0]
                syn_examples = syn_data[3].split(';')[-1]
                all_synsets.append(
                    Synset(syn_id, syn_headword, syn_lemmas, syn_pos, syn_definition, syn_examples))
        return all_synsets

    def holonymy(self):
        
        if self._pos in ['ADJECTIVE', 'ADVERB','VERB']:
            raise IndoWordNetError(
                'This synset relation is not valid for adjectives,verbs and adverbs.')
        
        cat =['component_object','feature_activity','member_collection','phase_state','place_area','portion_mass','position_area','resource_process','stuff_object']
        synset_id_list = set()
        for c in cat:
            with open('relations/tbl_{}_holo_{}.csv'.format(self._pos.lower(), c),encoding='utf-8') as reader:
                
                csv_reader = csv.reader(reader, delimiter=',')
                next(csv_reader)
                for line in csv_reader:
                    x = int(line[0].strip())
                    if self._synset_id == x:
                        synset_id_list.add(int(line[1]))
            
        # load synset offset mapping
        synset_filename = 'synid_fileoffset_mapping_dump'
        infile = open(synset_filename, 'rb')
        synset_offset_mapping = pickle.load(infile)
        infile.close()

        # find all synsets
        all_synsets = []
        with open('tbl_all_gujarati_synset_data.csv', encoding='utf8') as reader:
            for i in synset_id_list:
                offset = synset_offset_mapping[i]
                reader.seek(offset)
                csv_reader = csv.reader(reader)
                syn_data = next(csv_reader)
                syn_id = int(syn_data[0])
                syn_pos = syn_data[-1]
                syn_lemmas = syn_data[2].split(',')
                syn_headword = syn_lemmas[0]
                syn_definition = syn_data[3].split(';')[0]
                syn_examples = syn_data[3].split(';')[-1]
                all_synsets.append(
                    Synset(syn_id, syn_headword, syn_lemmas, syn_pos, syn_definition, syn_examples))
        return all_synsets



def synsets(lemma, pos=None):
    # load words_synset mapping
    words_filename = 'words_synid_mapping_dump'
    infile = open(words_filename, 'rb')
    words_synset_mapping = pickle.load(infile)
    infile.close()

    # load synset offset mapping
    synset_filename = 'synid_fileoffset_mapping_dump'
    infile = open(synset_filename, 'rb')
    synset_offset_mapping = pickle.load(infile)
    infile.close()
    

    # find all synsets
    all_synsets = []
    with open('tbl_all_gujarati_synset_data.csv', encoding='utf8') as reader:
        for i in words_synset_mapping[lemma]:
            offset = synset_offset_mapping[i]
            reader.seek(offset)
            csv_reader = csv.reader(reader)
            syn_data = next(csv_reader)
            syn_id = int(syn_data[0])
            syn_pos = syn_data[-1]
            syn_lemmas = syn_data[2].split(',')
            syn_headword = syn_lemmas[0]
            syn_definition = syn_data[3].split(';')[0]
            syn_examples = syn_data[3].split(';')[-1]
            all_synsets.append(
                Synset(syn_id, syn_headword, syn_lemmas, syn_pos, syn_definition, syn_examples))
    return all_synsets



def synset(word):
    synset_id = int(word.split('.')[2])
    # load synset offset mapping
    synset_filename = 'synid_fileoffset_mapping_dump'
    infile = open(synset_filename, 'rb')
    synset_offset_mapping = pickle.load(infile)
    infile.close()
        
    # find synset
    if synset_id in synset_offset_mapping:
        with open('tbl_all_gujarati_synset_data.csv', encoding='utf8') as reader:
            offset = synset_offset_mapping[synset_id]
            reader.seek(offset)
            csv_reader = csv.reader(reader)
            syn_data = next(csv_reader)
            syn_id = int(syn_data[0])
            syn_pos = syn_data[-1]
            syn_lemmas = syn_data[2].split(',')
            syn_headword = syn_lemmas[0]
            syn_definition = syn_data[3].split(';')[0]
            syn_examples = syn_data[3].split(';')[1].strip('\\').split('/')
            
            return Synset(syn_id, syn_headword, syn_lemmas, syn_pos, syn_definition, syn_examples)
def similarity_path(sense1, sense2):
    ancestors1 = {sense1.synset_id(): 1}
    ancestors2 = {sense2.synset_id(): 1}

    queue1 = [sense1]
    queue2 = [sense2]
    
    if sense1.pos() == sense2.pos() and sense1.pos() == 'NOUN':
        while queue1:
            x = queue1.pop()
            for parent in x.hypernymy():
                queue1.append(parent)
                if parent.synset_id() not in ancestors1:
                    ancestors1[parent.synset_id()] = ancestors1[x.synset_id()] + 1
                else:
                    ancestors1[parent.synset_id()] = min(
                        ancestors1[parent.synset_id()], ancestors1[x.synset_id()] + 1)

        while queue2:
            x = queue2.pop()
            for parent in x.hypernymy():
                queue2.append(parent)
                if parent.synset_id() not in ancestors2:
                    ancestors2[parent.synset_id()] = ancestors2[x.synset_id()] + 1
                else:
                    ancestors2[parent.synset_id()] = min(
                        ancestors2[parent.synset_id()], ancestors2[x.synset_id()] + 1)

        min_dist = sys.maxsize
        for item in ancestors1.keys():
            if item in ancestors2:
                min_dist = min(ancestors1[item]+ancestors2[item], min_dist)

        return 1.0/(min_dist-1)
    
    elif sense1.pos() == sense2.pos() and sense1.pos() == 'VERB':
        
        dummy_root =Synset(0, None, None, None, None, None)
        ancestors1[dummy_root.synset_id()] = sys.maxsize
        ancestors2[dummy_root.synset_id()] = sys.maxsize
        
        while queue1:
            x = queue1.pop()
            if not x.hypernymy():
                ancestors1[dummy_root.synset_id()] = min(ancestors1[x.synset_id()] + 1,ancestors1[dummy_root.synset_id()])
            else:
                for parent in x.hypernymy():
                    queue1.append(parent)
                    if parent.synset_id() not in ancestors1:
                        ancestors1[parent.synset_id()] = ancestors1[x.synset_id()] + 1
                    else:
                        ancestors1[parent.synset_id()] = min(
                            ancestors1[parent.synset_id()], ancestors1[x.synset_id()] + 1)

        while queue2:
            x = queue2.pop()
            if not x.hypernymy():
                ancestors2[dummy_root.synset_id()] = min(ancestors2[x.synset_id()] + 1,ancestors2[dummy_root.synset_id()])
            else:
                for parent in x.hypernymy():
                    queue2.append(parent)
                    if parent.synset_id() not in ancestors2:
                        ancestors2[parent.synset_id()] = ancestors2[x.synset_id()] + 1
                    else:
                        ancestors2[parent.synset_id()] = min(
                            ancestors2[parent.synset_id()], ancestors2[x.synset_id()] + 1)

        min_dist = sys.maxsize
        for item in ancestors1.keys():
            if item in ancestors2:
                min_dist = min(ancestors1[item]+ancestors2[item], min_dist)

        return 1.0/(min_dist-1)

def similarity_wup(sense1, sense2):
    ancestors1 = {sense1.synset_id(): 1}
    ancestors2 = {sense2.synset_id(): 1}

    queue1 = [sense1]
    queue2 = [sense2]
    
    if sense1.pos() == sense2.pos() and sense1.pos() == 'NOUN':
        root = 73
        while queue1:
            x = queue1.pop()
            for parent in x.hypernymy():
                queue1.append(parent)
                if parent.synset_id() not in ancestors1:
                    ancestors1[parent.synset_id()] = ancestors1[x.synset_id()] + 1
                else:
                    ancestors1[parent.synset_id()] = min(
                        ancestors1[parent.synset_id()], ancestors1[x.synset_id()] + 1)

        while queue2:
            x = queue2.pop()
            for parent in x.hypernymy():
                queue2.append(parent)
                if parent.synset_id() not in ancestors2:
                    ancestors2[parent.synset_id()] = ancestors2[x.synset_id()] + 1
                else:
                    ancestors2[parent.synset_id()] = min(
                        ancestors2[parent.synset_id()], ancestors2[x.synset_id()] + 1)

        min_dist = sys.maxsize
        lcs = None
        for item in ancestors1.keys():
            if item in ancestors2:
                if (ancestors1[item]+ancestors2[item]) < min_dist:
                    lcs = item
                    min_dist = (ancestors1[item]+ancestors2[item])

        return (2.0*(ancestors1[root]-ancestors1[lcs])/(ancestors1[root] + ancestors2[root]))
    
    elif sense1.pos() == sense2.pos() and sense1.pos() == 'VERB':
        
        dummy_root =Synset(0, None, None, None, None, None)
        ancestors1[dummy_root.synset_id()] = sys.maxsize
        ancestors2[dummy_root.synset_id()] = sys.maxsize
        
        while queue1:
            x = queue1.pop()
            if not x.hypernymy():
                ancestors1[dummy_root.synset_id()] = min(ancestors1[x.synset_id()] + 1,ancestors1[dummy_root.synset_id()])
            else:
                for parent in x.hypernymy():
                    queue1.append(parent)
                    if parent.synset_id() not in ancestors1:
                        ancestors1[parent.synset_id()] = ancestors1[x.synset_id()] + 1
                    else:
                        ancestors1[parent.synset_id()] = min(
                            ancestors1[parent.synset_id()], ancestors1[x.synset_id()] + 1)
 
        while queue2:
            x = queue2.pop()
            if not x.hypernymy():
                ancestors2[dummy_root.synset_id()] = min(ancestors2[x.synset_id()] + 1,ancestors2[dummy_root.synset_id()])
            else:
                for parent in x.hypernymy():
                    queue2.append(parent)
                    if parent.synset_id() not in ancestors2:
                        ancestors2[parent.synset_id()] = ancestors2[x.synset_id()] + 1
                    else:
                        ancestors2[parent.synset_id()] = min(
                            ancestors2[parent.synset_id()], ancestors2[x.synset_id()] + 1)

        min_dist = sys.maxsize
        root = dummy_root.synset_id()
        lcs = None
        for item in ancestors1.keys():
            if item in ancestors2:
                if (ancestors1[item]+ancestors2[item]) < min_dist:
                    lcs = item
                    min_dist = (ancestors1[item]+ancestors2[item])
       
        
        return (2.0*(ancestors1[root]-ancestors1[lcs])/(ancestors1[root] + ancestors2[root]))


def similarity_lch(sense1, sense2):
    ancestors1 = {sense1.synset_id(): 1}
    ancestors2 = {sense2.synset_id(): 1}

    queue1 = [sense1]
    queue2 = [sense2]
    
    if sense1.pos() == sense2.pos() and sense1.pos() == 'NOUN':
        root = 73
        while queue1:
            x = queue1.pop()
            for parent in x.hypernymy():
                queue1.append(parent)
                if parent.synset_id() not in ancestors1:
                    ancestors1[parent.synset_id()] = ancestors1[x.synset_id()] + 1
                else:
                    ancestors1[parent.synset_id()] = min(
                        ancestors1[parent.synset_id()], ancestors1[x.synset_id()] + 1)

        while queue2:
            x = queue2.pop()
            for parent in x.hypernymy():
                queue2.append(parent)
                if parent.synset_id() not in ancestors2:
                    ancestors2[parent.synset_id()] = ancestors2[x.synset_id()] + 1
                else:
                    ancestors2[parent.synset_id()] = min(
                        ancestors2[parent.synset_id()], ancestors2[x.synset_id()] + 1)

        min_dist = sys.maxsize
        for item in ancestors1.keys():
            if item in ancestors2:
                min_dist = min(ancestors1[item]+ancestors2[item], min_dist)

        return -1.0 * math.log10((min_dist-1)/(2 * max(ancestors1[root],ancestors2[root])))