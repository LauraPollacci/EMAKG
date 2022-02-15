import numpy as np
from scholarmetrics import hindex


def h_index_array(citations):
    citations = np.array(citations)
    n = citations.shape[0]
    array = np.arange(1, n + 1)

    # total number of citations for each k; k varies from 1 to n
    result = citations >= array.reshape((-1, 1))
    # print(result)
    result = result.sum(axis=1)

    # selecting articles with least k citations for each k;
    result = result >= array

    # choosing the highest value of k
    try:
        h_idx = array[result][-1]
    except IndexError:
        h_idx = 0

    return h_idx


def h_index_expert(citations):
    citations = np.array(citations)
    n = citations.shape[0]
    array = np.arange(1, n + 1)

    # reverse sorting
    citations = np.sort(citations)[::-1]

    # intersection of citations and k
    try:
        h_idx = np.max(np.minimum(citations, array))
    except ValueError:
        h_idx = 0

    return h_idx

