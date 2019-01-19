# import the Gujarati wordnet module
import wnguj as wn

# setup (run once only)
# wn.setup()

# Get all synsets for a given word
print(wn.synsets('ઇલા'))

# get particular synset
ss = wn.synset('ઇલા.NOUN.33884')
print(ss)

# print part of speach
print(ss.pos())

# print all lemmas in synset
print(ss.lemma_names())

# print glossary of synset
print(ss.gloss())

# print examples of synset
print(ss.examples())

# print hypernyms of synset
print(ss.hypernymy())

# print hypernyms of synset by level
print(ss.hypernymy(3))

#print hyponyms
print(wn.synsets('લગ્ન')[1].hyponymy())

#print antonyms of synset
print(wn.synset('મહિલા.NOUN.2954').antonymy())

#print meronym of synset
print(wn.synset('શિવાલય.NOUN.5').meronymy())

#print entailment
print(wn.synset('વિલાપ_કરવો.VERB.240').entailment())

#print troponym
print(wn.synset('હસવું.VERB.4679').troponymy())

#print holonyms
print(wn.synset('મહિલા.NOUN.2954').holonymy())

# Smilarity measures

# path similarity
print(wn.similarity_path(wn.synsets('મહિલા')[0], wn.synsets('ઇલા')[1]))

# leacock chodorow similarity
print(wn.similarity_lch(wn.synsets('મહિલા')[0], wn.synsets('ઇલા')[1]))

# wu palmer similarity measure
print(wn.similarity_wup(wn.synsets('મહિલા')[0], wn.synsets('ઇલા')[1]))
