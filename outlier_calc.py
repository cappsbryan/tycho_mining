import pandas as pd
import numpy as np
from collections import defaultdict

highest_k_val = 5
w = 1.5

# Occurence for all diseases will be tied to population
# But over all diseases, can calculate outliers of fatality %
def top_outliers(df, max_rows, type, method):
    col = ""
    if type == "pct_fatal":
        col = 'Fatality_Pct'
        df[col] = (df["Fatalities"]/df["Occurences"]).fillna(value=0)
    if type == "occurrence":
        col = "Occurences"
    if type == "fatalities":
        col = "Fatalities"
#    df.drop(fatal_col, axis=1, inplace=True)
#    df.drop(count_col, axis=1, inplace=True)
    if method == "knn":
        df = knn(df, col, highest_k_val)
        outliers = df.sort_values(by=['outlier_score2'], ascending=False)
        return outliers.iloc[:max_rows]
    else:
        outliers = parametric_method(df, col, w= w)
        outliers = outliers.sort_values(by=['Z-scores'], ascending=False)
        return outliers


#Parametric Method: Outlier Detection for Univariate Outliers based on Normal Distribution
def parametric_method(data, col, w):
    print('w =', w)
    outliers = pd.DataFrame(columns=data.columns)
    d_mean = np.mean(data[col])
    d_stddev = np.std(data[col])
    outlier_rows = []
    outlier_indices = []
    zscores = []
    for index, row in data.iterrows():
        z_score = (row[col] - d_mean) / d_stddev
        if z_score < -w or z_score > w:
            outlier_indices.append(index)
            outlier = {"Fatalities": row["Fatalities"], "Occurences": row["Occurences"]}
            outlier_rows.append(outlier)
            zscores.append(z_score)
    outliers = data.loc[outlier_indices]
  #  outliers = pd.DataFrame(outlier_rows)
    outliers["Z-scores"] = zscores

    return outliers

# apply the k-nearest-neighbor method to compute outlier distance
def knn(data, col, max_k):
    #normalized_df = (data - data.mean()) / data.std()
    print("Executing knn")
    all_scores = []
    outlier_scores = defaultdict(float)
    for index, row in data.iterrows():
        # index of 1 skips the first column which is the city name
        dist = [np.abs(row[col] - inner_row[col]) for inner_index, inner_row in data.iterrows() if index != inner_index]
        for k in range(2,max_k):
            if len(dist) > k:
                outlier_scores[k]= (sorted(dist))[k]
            else:
                outlier_scores[k] = 0
        all_scores.append(outlier_scores.copy())

    for k in range(2,max_k):
        scores = [score[k] for score in all_scores]
        data['outlier_score' + str(k)] = scores
    return data


