from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import os
from datetime import datetime
from queue import Queue
from threading import Thread

from supervisor import initiate_research

app = Flask(__name__)
CORS(app)

# Ensure a directory exists for saving research results
RESEARCH_RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'research_results')
os.makedirs(RESEARCH_RESULTS_DIR, exist_ok=True)

# Global dictionary to store research queues
research_queues = {}

def format_sse(data: str, event=None) -> str:
    """Format server-sent event."""
    msg = f"data: {data}\n\n"
    if event is not None:
        msg = f"event: {event}\n{msg}"
    return msg

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the main research interface"""
    if request.method == 'POST':
        return start_research()
    return render_template('index.html')

@app.route('/events/<session_id>')
def listen_for_events(session_id):
    def event_stream():
        if session_id not in research_queues:
            research_queues[session_id] = Queue()
        queue = research_queues[session_id]
        
        while True:
            message = queue.get()
            if message == 'DONE':
                yield format_sse(json.dumps({'status': 'complete'}))
                break
            yield format_sse(json.dumps(message))
    
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/research', methods=['POST'])
def start_research():
    """
    Initiate research cycle and process results
    
    Supports both JSON and form data
    """
    try:
        # Generate session ID
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        research_queues[session_id] = Queue()
        
        # Get research parameters
        data = request.get_json() if request.is_json else request.form
        research_goal = data.get('research_goal') or data.get('goal')
        iterations = int(data.get('iterations', 3))
        
        if not research_goal:
            return jsonify({"error": "Research goal is required", "status": "failed"}), 400
        
        # Start research in background thread
        def run_research():
            try:
                queue = research_queues[session_id]
                research_results = initiate_research(
                    research_goal,
                    iterations=iterations,
                    progress_callback=lambda msg: queue.put({
                        'type': 'progress',
                        'data': msg
                    })
                )
                
                # Save results
                filename = f"research_{session_id}.json"
                filepath = os.path.join(RESEARCH_RESULTS_DIR, filename)
                with open(filepath, 'w') as f:
                    json.dump(research_results, f, indent=2)
                
                # Send final results
                queue.put({
                    'type': 'results',
                    'data': research_results
                })
                queue.put('DONE')
                
            except Exception as e:
                queue.put({
                    'type': 'error',
                    'data': str(e)
                })
                queue.put('DONE')
        
        Thread(target=run_research).start()
        
        return jsonify({
            "status": "started",
            "session_id": session_id
        })

    except Exception as e:
        app.logger.error(f"Research cycle error: {str(e)}")
        
        # If it's a form submission, render template with error
        if not request.is_json:
            return render_template('index.html', 
                                   goal=research_goal, 
                                   error=str(e)), 500

        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

@app.route('/saved_research', methods=['GET'])
def list_saved_research():
    """List all saved research results"""
    try:
        saved_files = sorted(
            [f for f in os.listdir(RESEARCH_RESULTS_DIR) if f.endswith('.json')], 
            reverse=True
        )
        return jsonify({
            "saved_research_files": saved_files
        })
    except Exception as e:
        app.logger.error(f"Error listing saved research: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

@app.route('/saved_research/<filename>', methods=['GET'])
def get_saved_research(filename):
    """Retrieve a specific saved research result"""
    try:
        filepath = os.path.join(RESEARCH_RESULTS_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                "error": "Research file not found",
                "status": "failed"
            }), 404

        with open(filepath, 'r') as f:
            research_data = json.load(f)

        return jsonify(research_data)
    
    except Exception as e:
        app.logger.error(f"Error retrieving saved research: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0', 
        port=5003, 
        debug=True
    )
