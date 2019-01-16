# import the Gujarati wordnet module
import wnguj as wn

# setup
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

# Smilarity measures

# path similarity
print(wn.similarity_path(wn.synsets('મહિલા')[0], wn.synsets('ઇલા')[1]))

# leacock chodorow similarity
print(wn.similarity_lch(wn.synsets('મહિલા')[0], wn.synsets('ઇલા')[1]))

# wu palmer similarity measure
print(wn.similarity_wup(wn.synsets('મહિલા')[0], wn.synsets('ઇલા')[1]))
