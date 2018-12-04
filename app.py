from flask import Flask, render_template, request

import similarity_queries
from association_rules import association_rules

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
    return render_template('association_rules_results.html',
                           confidences=confidences)


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
