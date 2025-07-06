# example for testing chapter

import numpy as np
from typing import List

def find_outliers(data: List[float], threshold: float = 2.0) -> List[int]:
    """
    Find outliers in a dataset using z-score method.
    
    Parameters
    ----------
    data : List[float]
        List of numerical values.
    threshold : float, default=2.0
        Number of standard deviations from the mean to consider a value as an outlier.
    
    Returns
    -------
    List[int]
        List of indices of outliers in the data.
    """
    
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std = variance ** 0.5
    if std == 0:
        # If standard deviation is zero, all values are identical, so no outliers
        return []
    
    # Bug: division by zero when std is 0 (all values are identical)
    # This only happens when all data points are the same
    outliers = []
    for i, value in enumerate(data):
        z_score = abs(value - mean) / std  # Bug: std can be 0!
        if z_score > threshold:
            outliers.append(i)
    
    return outliers


def test_find_outliers_normal_case():
    data = [1, 2, 3, 4, 5, 100]  # 100 is clearly an outlier
    outliers = find_outliers(data, threshold=2.0)
    
    # Should find the outlier at index 5
    # Should find the outlier at index 5
    assert 5 in outliers, f"Failed to detect outlier: {outliers}"
    assert len(outliers) == 1, f'Expected exactly one outlier, got: {len(outliers)}'

def test_find_outliers_identical_values():
    data = [5, 5, 5, 5, 5]  # All identical values
    
    outliers = find_outliers(data, threshold=2.0)
    assert outliers == [], f"Expected no outliers for identical values, got {outliers}"


# def test_find_outliers_edge_cases():
#     """Test find_outliers with edge cases."""
#     # Empty list
#     assert find_outliers([]) == []
    
#     # Single element
#     assert find_outliers([5]) == []
    
#     # Two identical elements
#     try:
#         outliers = find_outliers([5, 5])
#         assert outliers == []
#     except ZeroDivisionError:
#         assert False, "Function crashed with two identical values"


if __name__ == "__main__":
    # Example usage
    data = [1, 2, 3, 4, 5]
    print("Outliers in data:", find_outliers(data))