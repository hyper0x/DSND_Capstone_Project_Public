import pandas as pd
from sklearn import cluster
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler

import os
import constant
import time
import storer as sto


def main(input_dir, output_dir):
    """The main function.
    """
    print('Build the clustering model...')
    response_agg_path = os.path.join(input_dir, constant.PICKLE_RESPONSE_AGG)

    print('Load aggregated data...')
    response_agg = sto.load(response_agg_path)

    print('Separate the column named gender for model...')
    gender_type_df = pd.get_dummies(
        response_agg['gender'], prefix='gender', prefix_sep='_')

    response_model = response_agg.join(gender_type_df)

    print('Drop the useless columns...')
    response_model = response_model.drop(
        columns=['gender', 'age_backet', 'income_backet'])

    print('Drop columns that are not relevant...')
    # The reason why I exclude the year of membership registration is that I think it has poor compatibility.
    # The value of this column in the new data will most likely not exist in the existing data.
    response_model = response_model.drop(columns=['profile_id', 'reg_year'])

    print('Scale the data for model...')
    X = response_model
    scaler = MinMaxScaler()
    scaler.fit(X)
    X_scaled = scaler.transform(X)

    print('Initialize the clustering model...')
    selected_number = 6
    clustering_model = cluster.AgglomerativeClustering(
        n_clusters=selected_number, affinity='manhattan', linkage='average')

    print('Train the clustering model... (waiting for a moment)')
    start_time = time.time()
    labels = clustering_model.fit_predict(X_scaled)
    end_time = time.time()
    print('The time spent training model and prediction: {}s'.\
        format(end_time - start_time))

    print('Evaluate the clustering model... (waiting for a moment)')
    print("Score: {}\n".format(
        silhouette_score(X_scaled, labels, metric='manhattan')))

    print('Generate labeled response data...')
    cluster_col_name = 'cluster_' + str(selected_number)
    response_labeled = response_agg.copy()
    response_labeled.insert(0, cluster_col_name, labels)

    print('Store data...')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    clustering_model_path, response_labeled_path = get_output_file_paths(
        output_dir)

    sto.store(clustering_model, clustering_model_path)
    sto.store(response_labeled, response_labeled_path)

    print('Done.\n')


def check(output_dir):
    """Checks the validity for the pickle files.
    """
    print('Check the validity for the pickle files...')
    clustering_model_path, response_labeled_path = get_output_file_paths(
        output_dir)

    print(
        'Check the output file located at {}...'.format(clustering_model_path))
    clustering_model = sto.load(clustering_model_path)
    num_labels = len(clustering_model.labels_)
    print('len(clustering_model.labels_): {}'.format(num_labels))
    assert num_labels == 16928, "The number of labels in clustering model is incorrect!"

    print(
        'Check the output file located at {}...'.format(response_labeled_path))
    response_labeled = sto.load(response_labeled_path)
    print('response_labeled.shape: {}'.format(response_labeled.shape))
    assert response_labeled.shape == (
        16928, 23), "The shape of labeled response is incorrect!"

    print('OK\n')


def get_output_file_paths(output_dir):
    """Returns the full path of output files.
    """
    clustering_model_path = os.path.join(output_dir,
                                         constant.PICKLE_CLUSTERING_MODEL)
    response_labeled_path = os.path.join(output_dir,
                                         constant.PICKLE_RESPONSE_LABELED)

    return (clustering_model_path, response_labeled_path)


if __name__ == "__main__":
    main(constant.PROCESSED_DATA_DIR, constant.MODEL_DIR)
    check(constant.MODEL_DIR)