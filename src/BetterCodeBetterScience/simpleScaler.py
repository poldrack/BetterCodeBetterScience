# custom scaler class for testing example
import numpy as np

class SimpleScaler:
    def __init__(self):
        self.transformed_ = None

    def fit(self, X):
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0)

    def transform(self, X):
        self.transformed_ = (X - self.mean_) / self.std_
        return self.transformed_

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)

def test_simple_scaler_internals():

    X = np.array([[1, 2], [3, 4], [5, 6]])
    scaler = SimpleScaler()
    _ = scaler.fit_transform(X)
    
    # Test that the transformed data is correct using the internal
    assert np.allclose(scaler.transformed_.mean(axis=0), np.array([0, 0]))
    assert np.allclose(scaler.transformed_.std(axis=0), np.array([1, 1]))


def test_simple_scaler_interface():
    X = np.array([[1, 2], [3, 4], [5, 6]])
    scaler = SimpleScaler()
    
    # Test the interface without accessing internals
    transformed_X = scaler.fit_transform(X)
    assert np.allclose(transformed_X.mean(axis=0), np.array([0, 0]))
    assert np.allclose(transformed_X.std(axis=0), np.array([1, 1]))