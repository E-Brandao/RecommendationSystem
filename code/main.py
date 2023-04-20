from surprise import accuracy, SVD, KNNBaseline, SlopeOne, CoClustering
from surprise.model_selection import GridSearchCV
from surprise.model_selection import train_test_split
import pandas as pd
import prepare_data
import content_based
import utils
import evaluating

data = prepare_data.load_data()
df_content = content_based.load_data()
df_recents = content_based.load_recents()
df_recents = df_recents[df_recents['user_id'].isin(data.df['user_id'].unique())]
df_recents.reset_index(inplace=True)
df_recents.drop(['index'], axis=1)
teste1 = df_recents['new_id'].to_list()
teste2 = df_content['new_id'].to_list()
x = set(teste1).intersection(teste2)
df_content = df_content[df_content['new_id'].isin(x)]
df_content.reset_index(inplace=True)
df_content.drop(['index'], axis=1)
df_content["counter"] = df_content.index

users_list = df_recents['user_id'].unique().tolist()
users_weights = dict.fromkeys(users_list, None)

content_cosine = content_based.get_cosine(df_content)

count = 0
for user in users_list:
    count += 1
    print(count)
    users_weights[user] = content_based.get_weights(user, df_content, df_recents, content_cosine)

#users_weights = pd.read_json('../data/data_weights.json')
trainset, testset = train_test_split(data, test_size=0.25)

# algoritimo SVD

#param_grid = {'n_factors':[50,100,150],'n_epochs':[20,30],  'lr_all':[0.005,0.01],'reg_all':[0.02,0.1]}
#gs = GridSearchCV(SVD, param_grid, measures=['rmse'], cv=3)
#gs.fit(data)
#params = gs.best_params['rmse']
#print(params)
svdtuned = SVD(n_factors=150, n_epochs=30, lr_all=0.01, reg_all=0.1)
svdtuned.fit(trainset)
predictions_svd = svdtuned.test(testset)

# algoritmo KNN
sim_options = {'name': 'pearson',
               'user_based': True
               }

algo_knn_baseline = KNNBaseline(sim_options=sim_options)
predictions_knnBaseline = algo_knn_baseline.fit(trainset).test(testset)

# algoritmo Slope One
algo_slope_one = SlopeOne()
predictions_slope_one = algo_slope_one.fit(trainset).test(testset)

# algoritmo Co clustering
algo_co_clustering = CoClustering()
predictions_co_clustering = algo_co_clustering.fit(trainset).test(testset)

# metrica de erro da base de teste
accuracy.rmse(predictions_svd)
accuracy.rmse(predictions_knnBaseline)
accuracy.rmse(predictions_slope_one)
accuracy.rmse(predictions_co_clustering)

topNPredicted_svd, leftOutPredictions_svd, similarity_last4 = utils.generateTopNPredictedV2(predictions_svd,
                                                                                          users_weights,
                                                                                          df_content,
                                                                                          df_recents,
                                                                                          content_cosine)
print(similarity_last4["weight"])

notas_reduced = pd.read_csv('../data/ratings_smallv2.csv')
hr_svd = evaluating.hitRate(topNPredicted_svd, leftOutPredictions_svd)
novelty_svd = evaluating.Novelty(topNPredicted_svd, notas_reduced)