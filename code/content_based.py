from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import nltk
nltk.download('stopwords')

def load_data():
    df_content = pd.read_json('../data/data_books_reduced.json', dtype = {'new_id': str})
    df_content = df_content.drop_duplicates(subset='new_id', keep="first")
    #df_content.drop(['index'], axis=1, inplace=True)
    #df_content.reset_index(inplace=True)

    return df_content

def get_cosine(df_content):
    stop = list(nltk.corpus.stopwords.words('portuguese'))

    # Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
    tfidf = TfidfVectorizer(stop_words=stop)

    # Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(df_content['synopsis'])

    cosine_sim = cosine_similarity(tfidf_matrix)

    # Output the shape of tfidf_matrix
    return cosine_sim

# Function that takes in movie title as input and outputs most similar movies
def get_recommendations(df_content, book_id, cosine_sim):
    df_content = df_content.reset_index(drop=True)
    indices = pd.Series(df_content.index, index=df_content['new_id']).drop_duplicates()

    # Get the index of the movie that matches the title
    idx = indices[book_id]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    #sim_scores = sim_scores[1:11]
    sim_scores = sim_scores[1:100]

    # Get the movie indices
    book_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar movies
    return df_content['new_id'].iloc[book_indices]

def load_recents():
    df_recents = pd.read_csv('../data/recent_readings.csv', dtype={'new_id': str})
    #df_recents.drop(df_recents[df_recents.order > 3].index, inplace=True)
    #df_recents.reset_index(inplace=True)

    return df_recents

def get_weights(user, df_content, df_recents, cosine_similarity):
  dict_weights = {key: 0 for key in df_content.new_id.tolist()}
  _book_list = df_recents.new_id[df_recents['user_id']==user].tolist()
  loop = 3 if len(_book_list) > 3 else len(_book_list)

  for i in range(loop):
    try:
        _book = df_content.loc[df_content['new_id'] == str(_book_list[i]), 'counter'].values[0]
    except:
        continue
    for j in df_content['new_id'].unique():
        try:
            _book2 = df_content.loc[df_content['new_id'] == str(j), 'counter'].values[0]
            dict_weights[j] += cosine_similarity[_book][_book2]
        except:
            pass

  return dict_weights