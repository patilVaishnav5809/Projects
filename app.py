from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Graph structure
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['G'],
    'F': [],
    'G': []
}

search_steps = []

def depth_limited_search(node, goal, limit, path):
    global search_steps
    
    path.append(node)
    
    step = {
        'action': 'visit',
        'node': node,
        'path': path.copy(),
        'remaining_battery': limit,
        'message': f"Visiting {node}, Remaining battery: {limit}",
        'code_line': 24
    }
    search_steps.append(step)
    
    if node == goal:
        step = {
            'action': 'goal',
            'node': node,
            'path': path.copy(),
            'remaining_battery': limit,
            'message': f"Goal found! Path: {' -> '.join(path)}",
            'code_line': 38
        }
        search_steps.append(step)
        return True
    
    if limit <= 0:
        step = {
            'action': 'cutoff',
            'node': node,
            'path': path.copy(),
            'remaining_battery': 0,
            'message': f"Battery depleted at {node}. Backtracking...",
            'code_line': 50
        }
        search_steps.append(step)
        path.pop()
        return False
    
    for neighbor in graph[node]:
        if depth_limited_search(neighbor, goal, limit - 1, path):
            return True
    
    step = {
        'action': 'backtrack',
        'node': node,
        'path': path.copy(),
        'remaining_battery': limit,
        'message': f"No path from {node}. Backtracking...",
        'code_line': 71
    }
    search_steps.append(step)
    path.pop()
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/api/search', methods=['POST'])
def run_search():
    global search_steps
    search_steps = []
    
    data = request.json
    battery_limit = data.get('battery_limit', 3)
    start = data.get('start', 'A')
    goal = data.get('goal', 'G')
    
    result = depth_limited_search(start, goal, battery_limit, [])
    
    if not result:
        search_steps.append({
            'action': 'failure',
            'node': None,
            'path': [],
            'remaining_battery': 0,
            'message': 'Goal not found within battery limit.',
            'code_line': 0
        })
    
    return jsonify({
        'success': result,
        'steps': search_steps,
        'graph': graph
    })

@app.route('/api/graph')
def get_graph():
    return jsonify({'graph': graph})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
