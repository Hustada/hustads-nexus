from flask import Flask, render_template, request
from supervisor import run_research_cycle

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        goal = request.form.get('goal')
        results = run_research_cycle(goal)
        return render_template('index.html', goal=goal, results=results)
    return render_template('index.html', goal=None, results=None)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)
