from flask import Flask
from jinja2 import Environment, select_autoescape, FileSystemLoader

app = Flask(__name__)

env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html'])
)


@app.route('/')
def hello_world():
    template = env.get_template('home.html')
    return template.render()


@app.route('/bryan')
def bryan():
    template = env.get_template('bryan.html')
    return template.render(users=['Dragon', 'Aaron', 'Caleb'])


if __name__ == '__main__':
    app.run()
