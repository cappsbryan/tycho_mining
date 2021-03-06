from flask import Flask, render_template, request
import similarity_queries
import outlier_queries
from association_rules import association_rules
import clustering.clustering as cluster
import clustering.data_types as cluster_types

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/association_rules')
def association_rules_page():
    return render_template('association_rules.html')


@app.route('/association_rules_results')
def association_rules_results():
    data = request.args
    min_support = float(data['min_support'])
    min_confidence = float(data['min_confidence'])
    confidences = association_rules(min_support, min_confidence)
    return render_template('association_rules_results.html', confidences=confidences)


@app.route('/outliers')
def outliers():
    return render_template('outliers.html', conditions=outlier_queries.popular_conditions())

@app.route('/outlier_results')
def outlier_results():
    data = request.args
    condition = data['condition']
    pct_knn, pct_normal, occ_knn, occ_normal, fatal_knn, fatal_normal = outlier_queries.find_outliers(condition)
    return render_template('outlier_results.html', condition=condition,  pct_knn = pct_knn, pct_normal = pct_normal, occ_knn = occ_knn, occ_normal = occ_normal, fatal_knn = fatal_knn, fatal_normal= fatal_normal)


@app.route('/similarity')
def similarity():
    return render_template('similarity.html', conditions=similarity_queries.get_condition_names(),
                           state_names=similarity_queries.get_state_names())


@app.route('/similarity_results')
def similarity_results():
    data = request.args
    condition1 = data['condition1']
    condition2 = data['condition2']
    state = data['state']
    start_date = data['start_date']
    end_date = data['end_date']
    similarity_data = similarity_queries.compute_similarity(condition1, condition2, state, start_date, end_date)
    return render_template('similarity_results.html', condition1=condition1, condition2=condition2, state=state,
                           start_date=start_date, end_date=end_date, similarity=similarity_data)


@app.route('/clustering', methods=['GET', 'POST'])
def dragon():
    k_clusters = 2
    decade = 1880

    if request.method == 'POST':
        k_clusters = int(request.form['clusters'])
        decade = int(request.form['selectedDecade'])
        if not request.form['clusters'] or not request.form['selectedDecade']:
            k_clusters = 2
            decade = 1880


    clusters, total_sum, sse_list = cluster.k_means(k_clusters, decade)

    print(sse_list)
    return render_template('clustering.html', clusters=clusters, decades=cluster_types.decades, k=k_clusters,
                           decade=decade, total_sum=round(total_sum, 2), sse_list=sse_list)


if __name__ == '__main__':
    app.run()
