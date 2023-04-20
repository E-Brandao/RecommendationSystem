import pandas as pd
from surprise import Dataset, Reader

def load_data():
    notas_reduced = pd.read_csv('../data/ratings_smallv2.csv', dtype = {'new_id': str})
    reader = Reader(rating_scale=(0.5, 5))  # as notas no nosso problema variam entre 1 e 5

    data_reduced = Dataset.load_from_df(notas_reduced[['user_id', 'new_id', 'evaluation']], reader)
    return data_reduced