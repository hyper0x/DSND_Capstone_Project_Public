from sklearn.externals import joblib


def store(obj, file_path):
    """Stores an object to a specified file.
    """
    filenames = joblib.dump(obj, file_path, compress=('gzip', 6), protocol=4)

    return filenames


def load(file_path):
    """Loads an object from the specified file.
    """
    return joblib.load(file_path)
