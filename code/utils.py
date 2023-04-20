from surprise.model_selection import LeaveOneOut
from collections import defaultdict
from surprise import accuracy

def getTopN(predictions, weights, df_content, df_recents, content_cosine, n=10, minimumRating=4.0):
    _pred = []
    similarity = {"weight": 0}
    topN = defaultdict(list)
    topN_no_weight = defaultdict(list)
    for userID, bookID, actualRating, estimatedRating, _ in predictions:
        try:
            estimatedRating += weights[userID][bookID]
            _pred.append([userID, bookID, actualRating, estimatedRating, None])
        except:
            _pred.append([userID, bookID, actualRating, estimatedRating, None])
            pass

        if (estimatedRating >= minimumRating):
            topN[int(userID)].append((int(bookID), estimatedRating))

    for userID, ratings in topN.items():
        ratings.sort(key=lambda x: x[1], reverse=True)
        last4 = df_recents.loc[df_recents['user_id'] == userID, 'new_id'].tolist()

        for tuple in ratings[:n]:
            try:
                #new_book_id = df_content.loc[df_content['new_id'] == tuple[0], 'book_id'].values[0]
                for book in last4:
                    _book = df_content.loc[df_content['new_id'] == str(tuple[0]), 'counter'].values[0]
                    try:
                        _book2 = df_content.loc[df_content['new_id'] == book, 'counter'].values[0]
                        similarity["weight"] += content_cosine[int(_book)][int(_book2)]
                    except:
                        last4.remove(book)
            except:
                pass
        topN[int(userID)] = ratings[:n]

    print(accuracy.rmse(_pred))
    return topN, similarity



def generateTopNPredicted(algoritmo, data, weights, df_content, df_recents, content_cosine):
  LOOCV = LeaveOneOut(n_splits=1, random_state=1)

  for trainSet, testSet in LOOCV.split(data):
      # Train model without left-out ratings
      algoritmo.fit(trainSet)
      # Predicts ratings for left-out ratings only
      leftOutPredictions = algoritmo.test(testSet)
      # Build predictions for all ratings not in the training set
      bigTestSet = trainSet.build_anti_testset()
      allPredictions = algoritmo.test(bigTestSet)
      # Compute top 10 recs for each user
      topNPredicted, similarity_last4 = getTopN(allPredictions, weights, df_content,
                                                df_recents, content_cosine, n=10)

      return topNPredicted, leftOutPredictions, similarity_last4

def generateTopNPredictedV2(predictions, weights, df_content, df_recents, content_cosine):

    topNPredicted, similarity_last4 = getTopN(predictions, weights, df_content,
                                                df_recents, content_cosine, n=10)

    return topNPredicted, similarity_last4


def returnTrainUsers(df, trainset):
    valid_train_users = []

    for user in df['user_id'].unique():
        try:
            trainset.to_inner_uid(user)
            valid_train_users.append(user)
        except:
            pass

    return valid_train_users

def getBookPopularity(bookID, df_ratings):
  return df_ratings['new_id'].value_counts()[bookID]