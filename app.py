from flask import Flask, render_template

import simple_queries
import similarity_queries

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/bryan')
def bryan():
    return render_template('bryan.html', users=['Dragon', 'Aaron', 'Caleb'])


@app.route('/caleb')
def caleb():
    # similarity = similarity_queries.compute_similarity('Dengue', 'Ornithosis')
    condition_names = similarity_queries.condition_names()
    return render_template('caleb.html', similarity='', conditions=condition_names)


if __name__ == '__main__':
    app.run()
