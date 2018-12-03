from statistics import mean
import math


def main():
    indexes, data = load_data()

    query_data = []
    query_index = []
    for i, index in enumerate(indexes):
        if index[1] == 1880:
            query_data.append(data[i])
            query_index.append(indexes[i])

    total_sum, sse_list, new_centroids, new_k_clusters = k_means_clustering(3, query_data, query_index)

    for cluster in new_k_clusters:
        print(cluster)


def k_means_clustering(k, data, data_indices=None):
    # select k points to be initial centroids
    initial_centroids = data[0:k]

    # repeat
    while True:
        # form k clusters
        k_clusters = [[] for i in range(k)]
        new_k_clusters = [[] for i in range(k)]

        # calculate distance between each centroid
        for data_item_index, data_item in enumerate(data):
            distances = []
            for i in range(k):
                distances.append(distance(data_item, initial_centroids[i]))

            # assign point to closest centroid cluster
            minimum_distance_from_point_to_centroid = min(distances)
            cluster_with_min_distance = distances.index(minimum_distance_from_point_to_centroid)
            k_clusters[cluster_with_min_distance].append(data_item)

            # add corresponding index value to cluster
            new_k_clusters[cluster_with_min_distance].append(data_indices[data_item_index][0])

        # recompute centroids of each cluster
        new_centroids = []
        for i in range(k):
            cluster_mean = list(map(mean, zip(*k_clusters[i])))
            new_centroids.append(cluster_mean)

        # check if any empty lists occur. replace with current centroid if empty
        for index, centroid in enumerate(new_centroids):
            if not centroid:
                new_centroids[index] = initial_centroids[index]

        # check if centroids have changed
        if new_centroids == initial_centroids:
            sse_list = []
            for i in range(k):
                sse_list.append(calculate_sse(new_centroids[i], k_clusters[i]))

            total_sum = sum(sse_list)
            return total_sum, sse_list, new_centroids, new_k_clusters

        else:
            # establish new centroids and continue kmeans
            initial_centroids = new_centroids


def calculate_sse(centroid, cluster):
    sum_of_squared_error = 0
    for point in cluster:
        sum_of_squared_error += distance(centroid, point) ** 2
    return sum_of_squared_error


def distance(x, y):
    # euclid distance via list comprehension
    try:
        summation = sum((x[dim] - y[dim]) ** 2 for dim in range(len(x)))
        return math.sqrt(summation)
    except IndexError:
        print("Indexing error")


def load_data():
    fp = open('real_cluster_data.csv', 'r+')
    indices = []
    dataset = []
    for line in fp.readlines():
        list = [int(data_item) if data_item.isdigit() else data_item for data_item in line.split(',')]
        indices.append(list[:2])
        dataset.append(list[2:])
    fp.close()

    # remove header row
    del dataset[0]
    del indices[0]

    # remove \n from last item in row
    for data in dataset:
        data[-1] = int(data[-1].strip('\n'))

    return indices, dataset


main()
