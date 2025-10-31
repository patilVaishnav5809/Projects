from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Your exact graph structure from the code
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['G'],
    'F': [],
    'G': []
}

# Store search steps for visualization
search_steps = []

def depth_limited_search(node, goal, limit, path):
    
    """Here is the  exact Python DLS function with step tracking"""
    global search_steps
    
    path.append(node)
    
    # Log this step
    step = {
        'action': 'visit',
        'node': node,
        'path': path.copy(),
        'remaining_battery': limit,
        'message': f"Visiting {node}, Remaining battery: {limit}"
    }
    search_steps.append(step)
    
    # Goal check
    if node == goal:
        step = {
            'action': 'goal',
            'node': node,
            'path': path.copy(),
            'remaining_battery': limit,
            'message': f"Goal found! Path: {' -> '.join(path)}"
        }
        search_steps.append(step)
        return True
    
    # Battery limit check
    if limit <= 0:
        step = {
            'action': 'cutoff',
            'node': node,
            'path': path.copy(),
            'remaining_battery': 0,
            'message': f"Battery depleted at {node}. Backtracking..."
        }
        search_steps.append(step)
        path.pop()
        return False
    
    # Explore neighbors
    for neighbor in graph[node]:
        if depth_limited_search(neighbor, goal, limit - 1, path):
            return True
    
    # Backtrack - LOG BEFORE POPPING (FIXED)
    step = {
        'action': 'backtrack',
        'node': node,
        'path': path.copy(),  # Copy path BEFORE popping
        'remaining_battery': limit,
        'message': f"No path from {node}. Backtracking..."
    }
    search_steps.append(step)
    path.pop()  # Pop AFTER logging
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def run_search():
    """Run DLS and return all steps"""
    global search_steps
    search_steps = []
    
    data = request.json
    battery_limit = data.get('battery_limit', 3)
    start = data.get('start', 'A')
    goal = data.get('goal', 'G')
    
    # Run your exact DLS algorithm
    result = depth_limited_search(start, goal, battery_limit, [])
    
    if not result:
        search_steps.append({
            'action': 'failure',
            'node': None,
            'path': [],
            'remaining_battery': 0,
            'message': 'Goal not found within battery limit.'
        })
    
    return jsonify({
        'success': result,
        'steps': search_steps,
        'graph': graph
    })

@app.route('/api/graph')
def get_graph():
    """Return graph structure"""
    return jsonify({'graph': graph})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
