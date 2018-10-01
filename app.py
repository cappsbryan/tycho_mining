from flask import Flask
from jinja2 import Environment, select_autoescape, FileSystemLoader

app = Flask(__name__)

env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html'])
)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/heys')
def heys():
    template = env.get_template('hellos.html')
    return template.render(users=['Dragon', 'Aaron', 'Caleb'])


if __name__ == '__main__':
    app.run()
