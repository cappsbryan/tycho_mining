import pandas as pd
import numpy as np
import math


# Occurence for all diseases will be tied to population
# But over all diseases, can calculate outliers of fatality %
def top_outliers(df, max_rows):
    df['Fatality_Pct'] = df["Fatalities"]/df["Occurences"]
#    df.drop(fatal_col, axis=1, inplace=True)
#    df.drop(count_col, axis=1, inplace=True)
    for k in range(2,4):
        df['outlier_score' + str(k)] = knn_method(df, k)

    outliers = df.sort_values(by=['outlier_score3'], ascending=False)
    return outliers.iloc[:max_rows]

# apply the k-nearest-neighbor method to compute outlier distance
def knn_method(data, k):
    outlier_scores = []
    print('knn with k =', k)
    for index, row in data.iterrows():
        # index of 1 skips the first column which is the city name
        dist = [np.abs(row["Fatality_Pct"] - inner_row["Fatality_Pct"]) for inner_index, inner_row in data.iterrows() if index != inner_index]
        outlier_scores.append((sorted(dist))[k])
    return outlier_scores


