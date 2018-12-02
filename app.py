from flask import Flask, render_template, request

import simple_queries
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
    max_size = int(data['max_size'])
    confidences = association_rules(min_support, min_confidence, max_size)
    return render_template('association_rules_results.html',
                           confidences=confidences)


@app.route('/caleb')
def caleb():
    data = simple_queries.fatality_data()
    average_fatalities, min_fatalities, max_fatalities = data
    return render_template('caleb.html', avg=average_fatalities, min=min_fatalities, max=max_fatalities)


if __name__ == '__main__':
    app.run()
