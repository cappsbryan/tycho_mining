from flask import Flask, render_template, request

import simple_queries
import clustering.clustering as cluster
import clustering.data_types as cluster_types

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/bryan')
def bryan():
    return render_template('bryan.html', users=['Dragon', 'Aaron', 'Caleb'])


@app.route('/caleb')
def caleb():
    data = simple_queries.fatality_data()
    average_fatalities, min_fatalities, max_fatalities = data
    return render_template('caleb.html', avg=average_fatalities, min=min_fatalities, max=max_fatalities)


@app.route('/dragon', methods=['GET', 'POST'])
def dragon():
    k_clusters = 2
    decade = 1880

    if request.method == 'POST':
        k_clusters = int(request.form['clusters'])
        decade = int(request.form['selectedDecade'])
        if not request.form['clusters'] or not request.form['selectedDecade']:
            k_clusters = 2
            decade = 1880

    clusters = cluster.k_means(k_clusters, decade)
    return render_template('clustering.html', clusters=clusters, decades=cluster_types.decades, k=k_clusters,
                           decade=decade)


if __name__ == '__main__':
    app.run()
