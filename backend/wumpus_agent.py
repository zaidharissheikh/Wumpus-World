import json
import random
from typing import Set, List, Tuple, Dict

class WumpusWorld:
    """Wumpus World environment"""
    
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.agent_pos = (1, 1)
        self.wumpus_pos = self._random_pos()
        self.pit_positions = set()
        
        # Add pits (10% of cells, excluding agent start and wumpus)
        num_pits = max(1, (rows * cols) // 10)
        while len(self.pit_positions) < num_pits:
            pos = self._random_pos()
            if pos != self.agent_pos and pos != self.wumpus_pos:
                self.pit_positions.add(pos)
        
        self.gold_pos = self._random_pos()
        self.wumpus_alive = True
        
    def _random_pos(self) -> Tuple[int, int]:
        return (random.randint(1, self.rows), random.randint(1, self.cols))
    
    def get_percepts(self, pos: Tuple[int, int]) -> Dict:
        """Get percepts for current position"""
        percepts = {
            'breeze': False,
            'stench': False,
            'glitter': False,
            'bump': False,
            'scream': False
        }
        
        # Check adjacent cells
        adjacent = self._get_adjacent(pos)
        
        # Breeze if adjacent to pit
        for pit in self.pit_positions:
            if pit in adjacent:
                percepts['breeze'] = True
                break
        
        # Stench if adjacent to wumpus
        if self.wumpus_alive and self.wumpus_pos in adjacent:
            percepts['stench'] = True
        
        # Glitter if at gold
        if pos == self.gold_pos:
            percepts['glitter'] = True
        
        return percepts
    
    def _get_adjacent(self, pos: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """Get adjacent cell positions"""
        r, c = pos
        adjacent = set()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 1 <= nr <= self.rows and 1 <= nc <= self.cols:
                adjacent.add((nr, nc))
        return adjacent
    
    def move_agent(self, new_pos: Tuple[int, int]) -> bool:
        """Move agent and check for death"""
        if not self._is_valid(new_pos):
            return False
        
        self.agent_pos = new_pos
        
        # Check if agent dies
        if new_pos in self.pit_positions or (new_pos == self.wumpus_pos and self.wumpus_alive):
            return False
        return True
    
    def _is_valid(self, pos: Tuple[int, int]) -> bool:
        r, c = pos
        return 1 <= r <= self.rows and 1 <= c <= self.cols


class KnowledgeBase:
    """Propositional Logic Knowledge Base with Resolution"""
    
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.facts = set()  # Store known facts
        self.inference_steps = 0
    
    def tell_breeze(self, pos: Tuple[int, int], adjacent: Set[Tuple[int, int]]):
        """Tell KB about breeze at position"""
        r, c = pos
        # Breeze at (r,c) means at least one adjacent pit exists
        self.facts.add(('breeze', r, c))
        
        # Add rule: if breeze, then one of adjacent cells has pit
        for adj_pos in adjacent:
            self.facts.add(('pit_possible', adj_pos[0], adj_pos[1]))
    
    def tell_no_breeze(self, pos: Tuple[int, int], adjacent: Set[Tuple[int, int]]):
        """Tell KB about no breeze at position"""
        r, c = pos
        self.facts.add(('no_breeze', r, c))
        
        # No breeze means all adjacent cells are safe from pits
        for adj_pos in adjacent:
            self.facts.add(('safe_pit', adj_pos[0], adj_pos[1]))
    
    def tell_stench(self, pos: Tuple[int, int], adjacent: Set[Tuple[int, int]]):
        """Tell KB about stench at position"""
        r, c = pos
        self.facts.add(('stench', r, c))
        
        # Stench means wumpus adjacent
        for adj_pos in adjacent:
            self.facts.add(('wumpus_possible', adj_pos[0], adj_pos[1]))
    
    def tell_no_stench(self, pos: Tuple[int, int], adjacent: Set[Tuple[int, int]]):
        """Tell KB about no stench at position"""
        r, c = pos
        self.facts.add(('no_stench', r, c))
        
        # No stench means all adjacent cells are safe from wumpus
        for adj_pos in adjacent:
            self.facts.add(('safe_wumpus', adj_pos[0], adj_pos[1]))
    
    def tell_visited(self, pos: Tuple[int, int]):
        """Mark cell as visited (safe)"""
        self.facts.add(('visited', pos[0], pos[1]))
        self.facts.add(('safe_pit', pos[0], pos[1]))
        self.facts.add(('safe_wumpus', pos[0], pos[1]))
    
    def ask_safe(self, pos: Tuple[int, int]) -> bool:
        """Ask if a cell is safe using forward chaining"""
        self.inference_steps = 0
        
        # Simple forward chaining inference
        r, c = pos
        
        # If already visited, it's safe
        if ('visited', r, c) in self.facts:
            return True
        
        # If marked as pit or wumpus, not safe
        if ('pit', r, c) in self.facts or ('wumpus', r, c) in self.facts:
            return False
        
        # If both pit and wumpus safe, then safe
        safe_pit = ('safe_pit', r, c) in self.facts
        safe_wumpus = ('safe_wumpus', r, c) in self.facts
        
        self.inference_steps += 1
        
        return safe_pit and safe_wumpus


class WumpusAgent:
    """Intelligent agent using propositional logic"""
    
    def __init__(self, rows: int, cols: int):
        self.world = WumpusWorld(rows, cols)
        self.kb = KnowledgeBase(rows, cols)
        self.visited = set()
        self.current_percepts = {}
        self.score = 0
        self.is_alive = True
        
        # Initialize at starting position
        self._explore_cell(self.world.agent_pos)
    
    def _explore_cell(self, pos: Tuple[int, int]):
        """Explore a cell and update KB"""
        self.visited.add(pos)
        self.kb.tell_visited(pos)
        self.current_percepts = self.world.get_percepts(pos)
        
        # Tell KB about percepts
        adjacent = self.world._get_adjacent(pos)
        
        if self.current_percepts['breeze']:
            self.kb.tell_breeze(pos, adjacent)
        else:
            self.kb.tell_no_breeze(pos, adjacent)
        
        if self.current_percepts['stench']:
            self.kb.tell_stench(pos, adjacent)
        else:
            self.kb.tell_no_stench(pos, adjacent)
    
    def step(self) -> bool:
        """Take one step: find safe adjacent cell and move"""
        current_pos = self.world.agent_pos
        adjacent = self.world._get_adjacent(current_pos)
        
        # Find safe unvisited cells
        safe_moves = []
        for pos in adjacent:
            if pos not in self.visited and self.kb.ask_safe(pos):
                safe_moves.append(pos)
        
        # If no safe moves, try any unvisited
        if not safe_moves:
            for pos in adjacent:
                if pos not in self.visited:
                    safe_moves.append(pos)
        
        if not safe_moves:
            return False  # No moves available
        
        # Move to first safe cell
        new_pos = safe_moves[0]
        
        if not self.world.move_agent(new_pos):
            self.is_alive = False
            return False
        
        self._explore_cell(new_pos)
        self.score += 1
        
        return True
    
    def get_state(self) -> Dict:
        """Get current state for frontend"""
        grid = []
        for r in range(1, self.world.rows + 1):
            row = []
            for c in range(1, self.world.cols + 1):
                cell = {
                    'row': r,
                    'col': c,
                    'status': 'unknown'
                }
                
                if (r, c) in self.visited:
                    cell['status'] = 'safe'
                elif (r, c) == self.world.agent_pos:
                    cell['status'] = 'agent'
                elif (r, c) in self.world.pit_positions:
                    cell['status'] = 'pit'
                elif (r, c) == self.world.wumpus_pos:
                    cell['status'] = 'wumpus'
                
                row.append(cell)
            grid.append(row)
        
        return {
            'grid': grid,
            'agent_pos': self.world.agent_pos,
            'current_percepts': self.current_percepts,
            'visited_count': len(self.visited),
            'score': self.score,
            'inference_steps': self.kb.inference_steps,
            'is_alive': self.is_alive
        }


# Flask app to serve the agent
from flask import Flask, jsonify, request

app = Flask(__name__)
agent = None

@app.route('/init', methods=['POST'])
def init():
    """Initialize a new game"""
    global agent
    data = request.json
    rows = data.get('rows', 4)
    cols = data.get('cols', 4)
    agent = WumpusAgent(rows, cols)
    return jsonify(agent.get_state())

@app.route('/step', methods=['POST'])
def step():
    """Take one step"""
    global agent
    if agent is None:
        return jsonify({'error': 'Game not initialized'}), 400
    
    success = agent.step()
    return jsonify({
        'success': success,
        'state': agent.get_state()
    })

@app.route('/state', methods=['GET'])
def get_state():
    """Get current state"""
    global agent
    if agent is None:
        return jsonify({'error': 'Game not initialized'}), 400
    return jsonify(agent.get_state())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
