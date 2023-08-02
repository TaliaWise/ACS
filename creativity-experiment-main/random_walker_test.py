
from flask import Blueprint
import networkx as nx
import random
import time
from datetime import datetime
import string
from experiment_parameters import stopwords
import json

import multiprocessing
import time
import numpy as np
from scipy.sparse import csr_matrix

"""

#random_walker = Blueprint('random_walker', __name__)


@random_walker.route('/randomwalker')
def show():
	print('in here')
	w = WeightedRandomWalker()
	print(w.start_word)
	return w.start_word
    # stuff


"""



class WeightedRandomWalker:
 
    def __init__(self, previous_phrases, directed_towards_previous_ideas = True, start_word = 'brick', optimized = False, maximal = False):
        self.G = self.construct_graph()
        self.start_word = start_word
        self.cur_word = start_word
        self.word_list = []
        self.towards_prev = directed_towards_previous_ideas
        #print('previous phrases', previous_phrases)
        self.prev = self.get_prev(previous_phrases)
        #print('previous ideas in random walker: ', self.prev)
        self.optimized = optimized
        self.maximal = maximal
        self.matrix = self.load_sparse_csr('sparse_distances_matrix')
        self.name_dict = self.load_dict('name_dict.json')


    def get_all_at_distance(self, index, distance, matrix):
      #get all at row
      distances = np.where(matrix.getrow(index).toarray()[0] == distance)[0]
      #get all at column
      return np.append(np.where(matrix.getcol(index).toarray().T[0] == distance)[0], distances)


    def load_dict(self, filename):
      with open(filename) as f:
        name_dict = json.loads(f.read())
      return name_dict


    def load_sparse_csr(self, filename):
      # here we need to add .npz extension manually
      loader = np.load(filename + '.npz')
      return csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape'])


    def get_distance_from_dense(self, row, col, matrix):
      if row < col:
        value = matrix.getrow(row).todense()[0, col]
        if not value:
          return 5
        else:
          return value
      elif col < row:
        value = matrix.getrow(col).todense()[0, row]
        if not value:
          return 5
        else:
          return value
      elif row == col:
        return 0

 
    def construct_graph(self):
      G = nx.Graph()
      f = open("FreeAssociations.txt", "r")
      s = f.read()
      for line in s.split('\n'):
        a = line.split('\t')
        G.add_edge(a[0], a[1])
 
      #largest_cc:
      G = G.subgraph(max(nx.connected_components(G), key=len))
      return G


    def remove_stopwords(self, phrase):
      phrase_without_stopwords = []
      for p in phrase.split(' '):
        if p not in stopwords:
          phrase_without_stopwords.append(p)

      #print(phrase_without_stopwords)

      return phrase_without_stopwords


    def get_prev(self, previous_phrases):
      pr = []
      for p in previous_phrases:
        p = p.lower().translate(str.maketrans('', '', string.punctuation))
        pro = self.remove_stopwords(p)
        for i in pro:
          if i in self.G.nodes():
            pr.append(i)
      #print('previous words', pr)
      return pr
 
 
    def get_direction_weights(self):
      population = [n for n in self.G.neighbors(self.cur_word)]
      weights = []
      for n in population:
        path_len = 0
        for j in self.prev:
          path_len = path_len + len(bidirectional_shortest_path(self.G, n, j))
          #path_len = path_len + len(nx.shortest_path(self.G, n, j)) 
        path_len = path_len / max(1, len(self.prev))
        #if it's towards then weight = 1/path length so closer nodes will be max, if away then farther nodes will be max
        if self.towards_prev:
          weights.append(1/(path_len*path_len*path_len))
        else:
          weights.append(path_len*path_len*path_len)
      return population, weights


    def get_next_word(self):
      population, weights = self.get_direction_weights()
      new = random.choices(population = population, weights = weights, k = 1)
      while new[0] in self.word_list or new[0] in self.prev or new[0] == self.start_word:
        #if there is still a possible word option try again
        if False in [n in self.word_list for n in population]:
          population, weights = self.get_direction_weights()
          new = random.choices(population = population, weights = weights, k = 1)
        else:
          new[0] = self.word_list[-2]
          break
      self.cur_word = new[0]
      self.word_list.append(new[0])
 
    """
    def walk(self, num_steps):
      try:
        self.word_list = []
        for i in range(num_steps):
          self.get_next_word()
        return self.cur_word
      except:
        return 'no suggestions could be found'
    """

    def walk(self, num_steps):
      if self.optimized == True:
        #return self.get_min_max_words_optimized(num_steps)[0] #old 27/07
        return self.get_min_max_for_word_optimized_from_matrix_direct(num_steps)
      else:
        if self.maximal == False:
          time = datetime.now()
          try:
            self.word_list = []
            for i in range(num_steps):
              self.get_next_word()
              if (datetime.now() - time).total_seconds() > 2.5:
                raise Exception('time issue')
            return self.cur_word
          except Exception as e:
            return e

        elif self.maximal:
          try:
            self.word_list = []
            for i in range(num_steps):
              self.get_next_word_maximal()
            return self.cur_word
          except Exception as e:
            return 'no suggestions could be found, maximal'




    def get_next_word_maximal(self):
      population, weights = self.get_direction_weights()
      i = 0
      sorted_population = [x for _,x in sorted(zip(weights,population), reverse=True)]
      new = sorted_population[0]
      #print(population, weights)
      #print(sorted_population, new)

      while new in self.word_list or new in self.prev or new == self.start_word:
        if False in [n in self.word_list for n in population]:
          i = i + 1
          new = sorted_population[i]
        else:
          new = self.word_list[-2]
          break
      self.cur_word = new
      self.word_list.append(new)



    def get_min_max_words_optimized_old(self, distance):
      cur_time = datetime.now()
      num = nx.single_source_shortest_path_length(self.G, self.start_word, cutoff=distance)
      all_nodes_n = [x for x, y in num.items() if y == distance]
      all_nodes_distance = {}
      #print(distance, len(all_nodes_n))
      for node in all_nodes_n:
        distance = 0
        for word in self.prev:
          distance += nx.shortest_path_length(self.G, source=node, target=word)
        all_nodes_distance[node] = distance/len(self.prev)
      #print(datetime.now() - cur_time)

      if self.towards_prev == True:
        lst = sorted(all_nodes_distance.items(), key=lambda x: x[1], reverse=False)
        return [lst[0][0], lst[1][0]]
        #min(all_nodes_distance.items(), key = lambda k : k[1])
      else:
        lst = sorted(all_nodes_distance.items(), key=lambda x: x[1], reverse=True)
        #print(lst)
        return [lst[0][0], lst[1][0]]
        #max(all_nodes_distance.items(), key = lambda k : k[1])



    def get_min_max_words_optimized_works(self, distance):

      if distance == 5:
        all_nodes_n = self.get_all_at_distance(self.name_dict[self.start_word], 0, self.matrix)
        all_nodes_n = np.delete(all_nodes_n, np.where(all_nodes_n == self.name_dict[self.start_word]))
      else:
        all_nodes_n = self.get_all_at_distance(self.name_dict[self.start_word], distance, self.matrix)


      all_nodes_distance = {}
      #print(distance, len(all_nodes_n))
      now = datetime.now()
      print(all_nodes_n)
      for node in all_nodes_n:
        distance = 0
        for word in self.prev:
          #distance += nx.shortest_path_length(self.G, source=node, target=word)
          distance += self.get_distance_from_dense(self.name_dict[self.start_word], self.name_dict[word], self.matrix)
        all_nodes_distance[node] = distance/len(self.prev)
      #print(datetime.now() - cur_time)
      print(264, datetime.now()-now)

      if self.towards_prev == True:
        lst = sorted(all_nodes_distance.items(), key=lambda x: x[1], reverse=False)
        return [lst[0][0], lst[1][0]]
        #min(all_nodes_distance.items(), key = lambda k : k[1])
      else:
        lst = sorted(all_nodes_distance.items(), key=lambda x: x[1], reverse=True)
        #print(lst)
        return [lst[0][0], lst[1][0]]
        #max(all_nodes_distance.items(), key = lambda k : k[1])


    #current trial now 27/07
    def get_min_max_for_word_optimized_from_matrix_direct(self, distance):
      if distance == 5:
        words_at_distance = self.get_all_at_distance(self.name_dict[self.start_word], 0, self.matrix)
        words_at_distance = np.delete(words_at_distance, np.where(words_at_distance == self.name_dict[self.start_word]))
      else:
        words_at_distance = self.get_all_at_distance(self.name_dict[self.start_word], distance, self.matrix)

      words_to_recommend = self.get_min_max_for_distances_from_rows(distance, self.matrix, words_at_distance)
      words_to_recommend.sort(key = lambda x: x[1])

      if self.towards_prev:
        return words_to_recommend[0], words_to_recommend[1]
      else:
        return words_to_recommend[-1], words_to_recommend[-2]


    #use this instead of dense whatever thing to quickly get average distance for lots of words at a time :) 
    #I guess will need to do this once for every node in all_nodes or for every node in prev words. can just see which is shorter and use that..
    def get_min_max_for_distances_from_rows(self, index, matrix, words_at_distance):
      #for each node in distances check average distance to nodes in prev) 
      prev_word_list = []
      for word in self.prev:
        prev_word_list.append(self.name_dict[word])

      words = []

      if len(words_at_distance) < len(self.prev):
        for word in words_at_distance:
          row = matrix.getrow(word).toarray()[0]
          #print(row[word ]) #0 - is all zeros 
          col = matrix.getcol(word).toarray().T[0]
          #print('col', col[word]) # 0 + is all zeros
          together = np.append(col[:word], row[word:])
          distance = np.where(together[prev_word_list] == 0, 5, together[prev_word_list]).mean()
          words.append((word, distance))
        return words

      else:
        all_distances = []
        for prev in self.prev:
          prev = self.name_dict[prev]
          row = matrix.getrow(prev).toarray()[0]
          #print(row[word ]) #0 - is all zeros 
          col = matrix.getcol(prev).toarray().T[0]
          #print('col', col[word]) # 0 + is all zeros

          together = np.append(col[:prev], row[prev:])
          distances = np.where(together[words_at_distance] == 0, 5, together[words_at_distance])
          all_distances.append(distances)

        distances = np.asarray(all_distances).T.mean(axis=1)
        return list(zip(words_at_distance, distances))




    def get_min_max_words_optimized(self, distance):

      if distance == 5:
        print('BIG MISTAKE')
        #fix this if i need to
      else:
        all_nodes_n = self.get_all_at_distance(self.name_dict[self.start_word], distance, self.matrix)


      all_nodes_distance = {}
      #print(distance, len(all_nodes_n))
      now = datetime.now()

      print(all_nodes_n)
      for node in all_nodes_n:
        distance = 0
        for word in self.prev:
          #distance += nx.shortest_path_length(self.G, source=node, target=word)
          distance += self.get_distance_from_dense(self.name_dict[self.start_word], self.name_dict[word], self.matrix)
        all_nodes_distance[node] = distance/len(self.prev)
      #print(datetime.now() - cur_time)
      print(264, datetime.now()-now)

      if self.towards_prev == True:
        lst = sorted(all_nodes_distance.items(), key=lambda x: x[1], reverse=False)
        return [lst[0][0], lst[1][0]]
        #min(all_nodes_distance.items(), key = lambda k : k[1])
      else:
        lst = sorted(all_nodes_distance.items(), key=lambda x: x[1], reverse=True)
        #print(lst)
        return [lst[0][0], lst[1][0]]
        #max(all_nodes_distance.items(), key = lambda k : k[1])





def bidirectional_shortest_path(G, source, target):
    if source not in G or target not in G:
        msg = f"Either source {source} or target {target} is not in G"
        raise nx.NodeNotFound(msg)

    # call helper to do the real work
    results = _bidirectional_pred_succ(G, source, target)
    pred, succ, w = results

    # build path from pred+w+succ
    path = []
    # from source to w
    while w is not None:
        path.append(w)
        w = pred[w]
    path.reverse()
    # from w to target
    w = succ[path[-1]]
    while w is not None:
        path.append(w)
        w = succ[w]

    return path



def _bidirectional_pred_succ(G, source, target):
    time_start = datetime.now()
    """Bidirectional shortest path helper.

    Returns (pred, succ, w) where
    pred is a dictionary of predecessors from w to the source, and
    succ is a dictionary of successors from w to the target.
    """
    # does BFS from both source and target and meets in the middle
    if target == source:
        return ({target: None}, {source: None}, source)

    # handle either directed or undirected
    if G.is_directed():
        Gpred = G.pred
        Gsucc = G.succ
    else:
        Gpred = G.adj
        Gsucc = G.adj

    # predecesssor and successors in search
    pred = {source: None}
    succ = {target: None}

    # initialize fringes, start with forward
    forward_fringe = [source]
    reverse_fringe = [target]

    while (datetime.now() - time_start).total_seconds() < 2.5:
      while forward_fringe and reverse_fringe:
          if len(forward_fringe) <= len(reverse_fringe):
              this_level = forward_fringe
              forward_fringe = []
              for v in this_level:
                  for w in Gsucc[v]:
                      if w not in pred:
                          forward_fringe.append(w)
                          pred[w] = v
                      if w in succ:  # path found
                          return pred, succ, w
          else:
              this_level = reverse_fringe
              reverse_fringe = []
              for v in this_level:
                  for w in Gpred[v]:
                      if w not in succ:
                          succ[w] = v
                          reverse_fringe.append(w)
                      if w in pred:  # found path
                          return pred, succ, w

    raise nx.NetworkXNoPath(f"No path between {source} and {target}.")


obj = 'brick'
phrases = ['build a house', 'build a wall', 'lift weights at gym', 'build a pizza oven']
  

w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = True, start_word = obj, optimized = False, maximal = True)
  
print('______________________________________')


for r_i in range(1,5): 
  print(r_i)
  def run_walk():
    return w.walk(r_i), datetime.now() - n

  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = False, start_word = obj, optimized = True, maximal = False)
  distance_to_prev = 0
  word, time = run_walk()
  #distance = nx.shortest_path(w.G, word, obj)
  print('away, optimized', word, time)


  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = True, start_word = obj, optimized = True, maximal = False)
  distance_to_prev = 0
  word, time = run_walk()
  #distance = nx.shortest_path(w.G, word, obj)
  print('towards, optimized', word, time)

  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = True, start_word = obj, optimized = False, maximal = False)
  distance_to_prev = 0
  word, time = run_walk()
  distance = nx.shortest_path(w.G, word, obj)
  for i in w.prev:
    distance_to_prev = distance_to_prev + len(nx.shortest_path(w.G, i, word))
  print('towards, random', word, time, len(distance), distance_to_prev/len(w.prev))

  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = True, start_word = obj, optimized = False, maximal = True)
  distance_to_prev = 0
  word, time = run_walk()
  distance = nx.shortest_path(w.G, word, obj)
  for i in w.prev:
    distance_to_prev = distance_to_prev + len(nx.shortest_path(w.G, i, word))
  print('towards, max', word, time, len(distance), distance_to_prev/len(w.prev))



exit()
"""
nodes_to_do = list(w.G.nodes())
print(nodes_to_do)

nodes_left = [i for i in reversed(nodes_to_do)]

distance_dict = []

print(datetime.now())
now = datetime.now()
for node1 in nodes_to_do:
  for node2 in nodes_left:
#   if (node1, node2) not in distance_dict:
#      if (node2, node1) not in distance_dict:
    distance_dict.append(((node1, node2), len(bidirectional_shortest_path(w.G, node1, node2))))
  nodes_left = nodes_left[:-1]
  break

print(len(w.G.nodes), datetime.now(), datetime.now() - now)

distances = pd.DataFrame(distance_dict)
distances.to_csv('node_distances.csv')
"""


obj = 'brick'
phrases = ['build a house', 'build a wall', 'lift weights at gym', 'build a pizza oven']
  

def run_walk():
  return w.walk(5), datetime.now() - n

for r_i in range(1,8): 
  def run_walk():
    return w.walk(r_i), datetime.now() - n

  print(r_i, '___________________________________________')

  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = True, start_word = obj, optimized = False, maximal = True)
  distance_to_prev = 0
  word, time = run_walk()
  distance = nx.shortest_path(w.G, word, obj)
  for i in w.prev:
    distance_to_prev = distance_to_prev + len(nx.shortest_path(w.G, i, word))
  print('towards, max', word, time, len(distance), distance_to_prev/len(w.prev))


  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = False, start_word = obj, optimized = False, maximal = True)
  distance_to_prev = 0
  word, time = run_walk()
  distance = nx.shortest_path(w.G, word, obj)
  for i in w.prev:
    distance_to_prev = distance_to_prev + len(nx.shortest_path(w.G, i, word))
  print('away, max', word, time, len(distance), distance_to_prev/len(w.prev))


  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = True, start_word = obj, optimized = False, maximal = False)
  distance_to_prev = 0
  word, time = run_walk()
  distance = nx.shortest_path(w.G, word, obj)
  for i in w.prev:
    distance_to_prev = distance_to_prev + len(nx.shortest_path(w.G, i, word))
  print('towards, random', word, time, len(distance), distance_to_prev/len(w.prev))


  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = False, start_word = obj, optimized = False, maximal = False)
  distance_to_prev = 0
  word, time = run_walk()
  distance = nx.shortest_path(w.G, word, obj)
  for i in w.prev:
    distance_to_prev = distance_to_prev + len(nx.shortest_path(w.G, i, word))
  print('away, random', word, time, len(distance), distance_to_prev/len(w.prev))

  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = True, start_word = obj, optimized = True, maximal = False)
  distance_to_prev = 0
  word, time = run_walk()
  distance = nx.shortest_path(w.G, word, obj)
  for i in w.prev:
    distance_to_prev = distance_to_prev + len(nx.shortest_path(w.G, i, word))
  print('towards, optimized', word, time, len(distance), distance_to_prev/len(w.prev))


  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = False, start_word = obj, optimized = True, maximal = False)
  distance_to_prev = 0
  word, time = run_walk()
  distance = nx.shortest_path(w.G, word, obj)
  for i in w.prev:
    distance_to_prev = distance_to_prev + len(nx.shortest_path(w.G, i, word))
  print('away, optimized', word, time, len(distance), distance_to_prev/len(w.prev))


  n = datetime.now()
  w = WeightedRandomWalker(previous_phrases = phrases, directed_towards_previous_ideas = False, start_word = obj, optimized = True, maximal = False)
  distance_to_prev = 0
  word, time = run_walk()
  distance = nx.shortest_path(w.G, word, obj)
  for i in w.prev:
    distance_to_prev = distance_to_prev + len(nx.shortest_path(w.G, i, word))
  print('away, optimized matrix', word, time, len(distance), distance_to_prev/len(w.prev))





"""
words = {}
for obj in ['brick', 'paperclip', 'shoe', 'bucket', 'match', 'ball']:
  n = 2
  print('OBJECT: ', obj)
  phrases = ['build a house', 'build a wall', 'lift weights at gym', 'build a pizza oven']
  w = WeightedRandomWalker(previous_phrases=phrases, directed_towards_previous_ideas = 'Towards', start_word = obj, optimized = False)
  
  num = w.get_min_max_words_optimized(n)
  words[obj] = num


for w in ['brick', 'paperclip', 'shoe', 'bucket', 'match', 'ball']:
  for j in ['brick', 'paperclip', 'shoe', 'bucket', 'match', 'ball']:
    print(w, j, (len(set(words[w]) & set(words[j])) / float(len(set(words[w]) | set(words[j]))) * 100))
 



"""

"""
for obj in ['brick', 'paperclip', 'shoe', 'bucket', 'match', 'ball']:
  n = 2
  print('OBJECT: ', obj)
  phrases = ['build a house', 'build a wall', 'lift weights at gym', 'build a pizza oven']
  w = WeightedRandomWalker(previous_phrases=phrases, directed_towards_previous_ideas = 'Towards', start_word = obj, optimized = False)
  
  num = w.get_min_max_words_optimized(n)

  print(num)
  

  #check expansion
  print(nx.node_expansion(w.G, ['brick', 'paperclip', 'shoe', 'bucket', 'match', 'ball']))
  print(nx.boundary_expansion(w.G, ['brick', 'paperclip', 'shoe', 'bucket', 'match', 'ball']))
  print(nx.edge_expansion(w.G, ['brick', 'paperclip', 'shoe', 'bucket', 'match', 'ball']))
  print(nx.mixing_expansion(w.G, ['brick', 'paperclip', 'shoe', 'bucket', 'match', 'ball']))

  L = nx.normalized_laplacian_matrix(w.G)
  e = np.linalg.eigvals(L.A)
  print(e, e[0] - e[1])
  break

  
  num = w.get_min_max_words_optimized(n)

  print(num)
  



  print([x for x in nx.neighbors(w.G, 'brick')])
  for i in range(1, n):
    all_nodes_n = [x for x, y in num.items() if y == i]
    all_nodes_distance = {}
    print(i, len(all_nodes_n))
    for node in all_nodes_n:
      distance = 0
      for word in w.prev:
        distance += nx.shortest_path_length(w.G, source=node, target=word)
      all_nodes_distance[node] = distance/len(w.prev)
    print(all_nodes_distance)
    print('max ', max(all_nodes_distance.items(), key = lambda k : k[1]))
    print('min ', min(all_nodes_distance.items(), key = lambda k : k[1]))

  break
  """


        


