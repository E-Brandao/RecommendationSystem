from surprise import accuracy
import itertools
import utils

def hitRate(topNPredicted, leftOutPredictions):
  hits = 0
  total = 0

 # For each left-out rating
  for leftOut in leftOutPredictions:
      userID = leftOut[0]
      leftOutMovieID = leftOut[1]
      # Is it in the predicted top 10 for this user?
      hit = False
      for movieID, predictedRating in topNPredicted[int(userID)]:
          if (int(leftOutMovieID) == int(movieID)):
              hit = True
              break
      if (hit) :
          hits += 1

      total += 1

  # Compute overall precision
  return hits/total

def Diversity(topNPredicted, simsAlgo):
  n = 0
  total = 0
  simsMatrix = simsAlgo.compute_similarities()

  for userID in topNPredicted.keys():
    pairs = itertools.combinations(topNPredicted[userID], 2)

    for pair in pairs:
      book1 = pair[0][0]
      book2 = pair[1][0]
      innerID1 = simsAlgo.trainset.to_inner_iid(str(book1))
      innerID2 = simsAlgo.trainset.to_inner_iid(str(book2))
      similarity = simsMatrix[innerID1][innerID2]
      total += similarity
      n += 1

  S = total / n
  return (1-S)

def Novelty(topNPredicted, df):
  n = 0
  total = 0
  for userID in topNPredicted.keys():
    for rating in topNPredicted[userID]:
      bookID = rating[0]
      rank = utils.getBookPopularity(bookID, df)
      total += rank
      n += 1

  return total / n

def RMSE(predictions):
  return accuracy.rmse(predictions, verbose=False)