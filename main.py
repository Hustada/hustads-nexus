from flask import Flask, render_template, request
from utils import process_goal

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    output = ""
    goal = ""
    if request.method == 'POST':
        goal = request.form.get('goal')
        if goal:
            output = process_goal(goal)
    return render_template('index.html', output=output, goal=goal)

if __name__ == '__main__':
    app.run(debug=True)
