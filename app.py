from flask import Flask, render_template

import simple_queries

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


@app.route('/dragon')
def dragon():
    return render_template('clustering.html')


if __name__ == '__main__':
    app.run()
