
from flask import Blueprint
import random
import time
from datetime import datetime
import string
from experiment_parameters import stopwords, optimized

import json
import numpy as np
from scipy.sparse import csr_matrix

#import pkg_resources
#from symspellpy import SymSpell

"""

#random_walker = Blueprint('random_walker', __name__)


@random_walker.route('/randomwalker')
def show():
	print('in here')
	w = WeightedRandomWalker()
	print(w.start_word)
	return w.start_word
    # stuff


#spellcheck --- hope we don't need it

n = datetime.now()

sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_dictionary_en_82_765.txt"
)


bigram_path = pkg_resources.resource_filename(
    "symspellpy", "frequency_bigramdictionary_en_243_342.txt"
)

# term_index is the column of the term and count_index is the
# column of the term frequency
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)

# lookup suggestions for multi-word input strings (supports compound
# splitting & merging)
input_term = (
    "make a chandleier with earings"
    "bake brwad in an oven"
)
# max edit distance per lookup (per single word, not per whole input string)
suggestions = sym_spell.lookup_compound(input_term, max_edit_distance=2)
# display suggestion term, edit distance, and term frequency
for suggestion in suggestions:
    print(suggestion)

print(datetime.now() - n)

"""


class WordRecommender:
 
    def __init__(self, previous_phrases, directed_towards_previous_ideas = True, start_word = 'brick'):
        self.start_word = start_word
        current_time = datetime.now()
        self.towards_prev = directed_towards_previous_ideas
        #print('load matrix', datetime.now() - current_time)
        #self.matrix = self.load_sparse_csr('sparse_distances_matrix')
        self.matrix = np.load('sparse_distances_matrix.npz')
        #print('load matrix end', datetime.now() - current_time)
        self.name_dict = self.load_dict('name_dict.json')
        self.prev = self.get_prev(previous_phrases)
        self.num_word = dict((v, k) for k, v in self.name_dict.items())
        #print('end initiate', datetime.now() - current_time)
 

    def load_dict(self, filename):
      with open(filename) as f:
        name_dict = json.loads(f.read())
      return name_dict


    def load_sparse_csr(self, filename):
      # here we need to add .npz extension manually
      loader = np.load(filename + '.npz')
      return csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape'])

    """ 
    #old one worked on crazy sparse array
    def get_all_at_distance(self, index, distance, matrix):
      #get all at row
      distances = np.where(matrix.getrow(index).toarray()[0] == distance)[0]
      #get all at column
      return np.append(np.where(matrix.getcol(index).toarray().T[0] == distance)[0], distances)
    """

    def get_all_at_distance(self, index, distance, matrix):
      name = 'arr_' + str(index)
      return np.where(matrix[name] == distance)[0]


    def remove_stopwords(self, phrase):
      phrase_without_stopwords = []
      for p in phrase.split(' '):
        if p not in stopwords:
          phrase_without_stopwords.append(p)

      return phrase_without_stopwords


    def get_prev(self, previous_phrases):
      pr = []
      for p in previous_phrases:
        #p = p.lower().translate(str.maketrans('', '', string.punctuation))
        p = ' '.join(p.split("'")).lower().translate(str.maketrans("", '', string.punctuation))
        pro = self.remove_stopwords(p)
        for i in pro:
          if i in self.name_dict.keys():
            pr.append(i)
      return pr


    def get_words_optimized(self, distance, num_words):
      words_at_distance = self.get_all_at_distance(self.name_dict[self.start_word], distance, self.matrix)
      #remove all stopwords

      words_to_recommend = self.get_min_max_for_distances_from_rows(distance, self.matrix, words_at_distance)
      words_to_recommend.sort(key = lambda x: x[1])

      if not self.towards_prev:
        words_to_recommend.reverse()

      words = []
      for word in words_to_recommend:
        w_i = self.num_word[word[0]]
        if w_i not in self.prev and w_i not in stopwords:
          words.append(word)
      if len(words) > num_words:
        words = words[:num_words]

      if len(words) < num_words:
        print('not enough words')
        #if it didn't work: get a random word and add 99 to distace
        for word in range(num_words):
          word = random.choice(list(self.name_dict.keys()))
          words.append((word, 99))

      return [(self.num_word[x[0]], x[1]) for x in words]



    #start here new
    #current trial now 27/07
    def get_words(self, distance, num_words):
      if optimized == 'optimized':
        return self.get_words_optimized(distance, num_words)
      else:
        return self.get_words_walking(distance, num_words)



    #use this instead of dense whatever thing to quickly get average distance for lots of words at a time :) 
    #I guess will need to do this once for every node in all_nodes or for every node in prev words. can just see which is shorter and use that..
    def get_min_max_for_distances_from_rows(self, index, matrix, words_at_distance):
      #for each node in distances check average distance to nodes in prev) 

      #if no previous words get random words
      if len(self.prev) < 1:
        words = []
        for word in words_at_distance:
          words.append((word, 1000))
        return words

      #else get real recommendations
      prev_word_list = []
      for word in self.prev:
        prev_word_list.append(self.name_dict[word])

      words = []
      if len(prev_word_list) > len(words_at_distance):
        for word in words_at_distance:
          name = 'arr_' + str(word)
          row = matrix[name]
          distance = row[prev_word_list].mean()
          words.append((word, distance))
        return words

      else:
        all_distances = []
        for prev in prev_word_list:
          name = 'arr_' + str(prev)
          row = matrix[name]
          distances = row[words_at_distance]
          all_distances.append(distances)
        distances = np.asarray(all_distances).T.mean(axis=1)
        return list(zip(words_at_distance, distances))

    def get_words_walking(self, distance, num_words):
      words = []
      for w in range(num_words):
        new_word = self.get_word_walk(distance)
        new_word = (self.num_word[new_word[0]], new_word[1])
        if new_word in words:
          for i in range(20):
            new_word = self.get_word_walk(distance)
            if new_word not in words:
              new_word = (self.num_word[new_word[0]], new_word[1])
              break
        words.append(new_word)
      return words

    #kind of broken
    def get_word_walk(self, distance):
      #get all rows of prev words
      #if no previous words get random words
      if len(self.prev) < 1:
        return (random.choice(self.name_dict.keys()), 1000)
      #else get real recommendations
      prev_word_list = []
      prev_matrix = []
      for word in self.prev:
        word_index = self.name_dict[word]
        word_index_name = 'arr_' + str(word_index)
        prev_word_list.append(word_index)
        prev_matrix.append(self.matrix[word_index_name])
      #for each step in range(distance). start at start
      cur_word = (self.name_dict[self.start_word], 0)
      for i in range(distance):
        try:
          cur_word = self.get_next_step(cur_word[0], prev_matrix)
        except:
          return cur_word
      return cur_word


    def get_next_step(self, cur_word, prev_matrix):
      name = 'arr_' + str(cur_word)
      neighbors = np.where(self.matrix[name] == 1)[0]
      #get mean of prev_matrix at position neighbors for each neighbor
      prev_matrix = np.asarray(prev_matrix)
      distances = list(zip(neighbors, np.mean(prev_matrix, axis=0)[neighbors]))

      distances.sort(key = lambda x: x[1])
      if not self.towards_prev:
        distances.reverse()

      pick_first = 0.7
      for d in distances:
        if self.num_word[d[0]] not in self.prev:
          if random.random() < pick_first:
            return d
      #if still no return
      for d in distances:
        if self.num_word[d[0]] not in self.prev:
          return d


"""
obj = ['broom', 'belt', 'bucket', 'shoe', 'towel', 'knife', 'clock', 'comb', 'pillow', 'pencil', 'brick', 'paperclip', 'candle', 'purse', 'sock']
obj = ['candle', 'towel', 'shoe', 'broom', 'knife', 'clock', 'pencil', 'lamp']
phrases = ['lift weights at gym', 'build a pizza oven', 'build a wall']
#phrases = ['paper']
optimized = 'optimized'
distance = 5
num_words = 2

for o in obj:
  print(o)
  now = datetime.now()
  w = WordRecommender(previous_phrases = phrases, directed_towards_previous_ideas = True, start_word = obj)
  for i in range(3):
    #print(i, len(w.get_all_at_distance(w.name_dict[o], i, w.matrix)), [w.num_word[x] for x in w.get_all_at_distance(w.name_dict[o], i, w.matrix)])
    print(i, len(w.get_all_at_distance(w.name_dict[o], i, w.matrix)))


now = datetime.now()
w = WordRecommender(previous_phrases = phrases, directed_towards_previous_ideas = False, start_word = obj)
cur_word = w.get_words(distance, num_words)
print('away', cur_word, datetime.now() - now)



optimized = 'walk'
print('optimized walk')
start_vector = w.matrix[w.name_dict[obj]]
distance = 10
num_words = 2
now = datetime.now()
w = WordRecommender(previous_phrases = phrases, directed_towards_previous_ideas = True, start_word = obj)
cur_word = w.get_words(distance, num_words)

for j in cur_words:
  print('distance' , w.matrix[w.name_dict[j[0]]
print('towards', cur_word, datetime.now() - now)

now = datetime.now()
w = WordRecommender(previous_phrases = phrases, directed_towards_previous_ideas = False, start_word = obj)
cur_word = w.get_words(distance, num_words)
print('away', cur_word, datetime.now() - now)



#test it

obj = 'paperclip'
phrases = ['lift weights at gym', 'build a pizza oven', 'connect paper']
num_words = 2
now = datetime.now()
w = WordRecommender(previous_phrases = phrases, directed_towards_previous_ideas = False, start_word = obj)

print('word recommender:', datetime.now() - now, w.prev, w)

#todo: add distance and direction seperately to database
prompts = w.get_words(3, num_words)
print(prompts)
print('after get wrods;', datetime.now() - now)

#filename = 'sparse_distances_matrix_new'
#np.savez(filename, data = w.matrix.data, indices= w.matrix.indices, indptr = w.matrix.indptr, shape=w.matrix.shape, compressed=True)



for r_i in range(1,5): 
  print(r_i)
  def run_walk():
    return w.get_words(r_i, num_words), datetime.now() - n

  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = False, start_word = obj)
  distance_to_prev = 0
  word, time = run_walk()
  #distance = nx.shortest_path(w.G, word, obj)
  print('away, optimized', word, time)


  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = True, start_word = obj)
  distance_to_prev = 0
  word, time = run_walk()
  #distance = nx.shortest_path(w.G, word, obj)
  print('towards, optimized', word, time)

"""
        


