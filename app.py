from flask import Flask, render_template, request
import similarity_queries
import outlier_queries

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/bryan')
def bryan():
    return render_template('bryan.html', users=['Dragon', 'Aaron', 'Caleb'])


@app.route('/outliers')
def outliers():
    return render_template('outliers.html', conditions=outlier_queries.popular_conditions())

@app.route('/outlier_results')
def outlier_results():
    data = request.args
    condition = data['condition']
    outlier_data = outlier_queries.find_outliers(condition)
    return render_template('outlier_results.html', condition=condition, outliers=outlier_data)


@app.route('/similarity')
def similarity():
    return render_template('similarity.html', conditions=similarity_queries.condition_names())


@app.route('/similarity_results')
def similarity_results():
    data = request.args
    condition1 = data['condition1']
    condition2 = data['condition2']
    similarity_data = similarity_queries.compute_similarity(condition1, condition2)
    return render_template('similarity_results.html', condition1=condition1, condition2=condition2,
                           similarity=similarity_data)


if __name__ == '__main__':
    app.run()
