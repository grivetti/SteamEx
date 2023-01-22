import numpy as np
import pandas as pd
from typing import Dict, Text

def process(epochs: int) -> None:
    import tensorflow as tf
    import tensorflow_recommenders as tfrs
    df = pd.read_csv("Data/steam.csv", index_col=False, names=[
        " Name", "Genres", "Price", "Developers", "Publishers", "Popularity", "Review"])


    games = df[['Genres']]
    ratings = df[['Genres', 'Popularity', 'Review']]

    ratings = tf.data.Dataset.from_tensor_slices(dict(ratings))
    games = tf.data.Dataset.from_tensor_slices(dict(games))


    ratings = ratings.map(lambda x: {
        "Genres": x["Genres"],
        "Popularity": x["Popularity"]
    })

    games = games.map(lambda x: x["Genres"])

    pop_ids_vocabulary = tf.keras.layers.IntegerLookup(mask_token=None)
    pop_ids_vocabulary.adapt(ratings.map(lambda x: x["Popularity"]))


    game_titles_vocabulary = tf.keras.layers.StringLookup(mask_token=None)
    game_titles_vocabulary.adapt(games)


    class GamesLenModel(tfrs.Model):
        # We derive from a custom base class to help reduce boilerplate. Under the hood,
        # these are still plain Keras Models.

        def __init__(
                self,
                genre_model: tf.keras.Model,
                popularity_model: tf.keras.Model,
                task: tfrs.tasks.Retrieval):
            super().__init__()

            self.genre_model = genre_model
            self.popularity_model = popularity_model

            # Set up a retrieval task.
            self.task = task

        def compute_loss(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor:
            # Define how the loss is computed.
            genre_embeddings = self.genre_model(features["Genres"])
            popularity_embeddings = self.popularity_model(features["Popularity"])

            return self.task(genre_embeddings, popularity_embeddings)


    pop_model = tf.keras.Sequential([
        pop_ids_vocabulary,
        tf.keras.layers.Embedding(pop_ids_vocabulary.vocabulary_size(), 64)
    ])

    game_model = tf.keras.Sequential([
        game_titles_vocabulary,
        tf.keras.layers.Embedding(game_titles_vocabulary.vocabulary_size(), 64)
    ])

    # Define your objectives.
    task = tfrs.tasks.Retrieval(metrics=tfrs.metrics.FactorizedTopK(
        games.batch(128).map(game_model)
    ))
    model = GamesLenModel(game_model, pop_model, task)
    model.compile(optimizer=tf.keras.optimizers.Adagrad(0.5))

    model.fit(ratings.batch(4096), epochs=epochs)

    # Use brute-force search to set up retrieval using the trained representations.
    index = tfrs.layers.factorized_top_k.BruteForce(model.popularity_model)
    index.index_from_dataset(
        games.batch(100).map(lambda title: (title, model.genre_model(title))))

    # Get some recommendations.
    _, genres = index(np.array([1]))
    print(f"Top 10 recommendations : {genres[0, :10]}")
