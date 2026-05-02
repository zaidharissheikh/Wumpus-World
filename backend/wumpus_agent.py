import json
import random
from typing import Set, List, Tuple, Dict

class WumpusWorld:  
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
        while self.gold_pos == self.agent_pos or self.gold_pos == self.wumpus_pos or self.gold_pos in self.pit_positions:
            self.gold_pos = self._random_pos()
        
        self.wumpus_alive = True
        
    def _random_pos(self) -> Tuple[int, int]:
        return (random.randint(1, self.rows), random.randint(1, self.cols))
    
    def get_percepts(self, pos: Tuple[int, int]) -> Dict:
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
        
        # Glitter if at gold OR adjacent to gold
        if pos == self.gold_pos:
            percepts['glitter'] = True
        
        return percepts
    
    def _get_adjacent(self, pos: Tuple[int, int]) -> Set[Tuple[int, int]]:
        r, c = pos
        adjacent = set()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 1 <= nr <= self.rows and 1 <= nc <= self.cols:
                adjacent.add((nr, nc))
        return adjacent
    
    def move_agent(self, new_pos: Tuple[int, int]) -> bool:
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
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.clauses = set()  #store CNF clauses 
        self.inference_steps = 0
    
    def add_clause(self, clause):
        # Convert to frozenset for hashability
        if isinstance(clause, (list, tuple)):
            clause = frozenset(clause)
        self.clauses.add(clause)
    
    def tell_breeze(self, pos: Tuple[int, int], adjacent: Set[Tuple[int, int]]):
        r, c = pos
        # Breeze means at least one adjacent cell has a pit
        pit_literals = [f'P_{adj[0]},{adj[1]}' for adj in adjacent]
        if pit_literals:
            self.add_clause(pit_literals)
    
    def tell_no_breeze(self, pos: Tuple[int, int], adjacent: Set[Tuple[int, int]]):
        r, c = pos
        # No breeze means no adjacent cell has a pit
        for adj_pos in adjacent:
            self.add_clause([f'¬P_{adj_pos[0]},{adj_pos[1]}'])
    
    def tell_stench(self, pos: Tuple[int, int], adjacent: Set[Tuple[int, int]]):
        r, c = pos
        # Stench means at least one adjacent cell has the wumpus
        wumpus_literals = [f'W_{adj[0]},{adj[1]}' for adj in adjacent]
        if wumpus_literals:
            self.add_clause(wumpus_literals)
    
    def tell_no_stench(self, pos: Tuple[int, int], adjacent: Set[Tuple[int, int]]):
        r, c = pos
        # No stench means no adjacent cell has wumpus
        for adj_pos in adjacent:
            self.add_clause([f'¬W_{adj_pos[0]},{adj_pos[1]}'])
    
    def tell_visited(self, pos: Tuple[int, int]):
        r, c = pos
        # Cell is safe from pit
        self.add_clause([f'¬P_{r},{c}'])
        self.add_clause([f'¬W_{r},{c}'])
    
    def resolve_clauses(self, clause1, clause2):
        # Find complementary literals (A and ¬A)
        for literal in clause1:
            complement = self._negate_literal(literal)
            if complement in clause2:
                # Resolve: remove the complementary pair and combine
                resolvent = (clause1 - {literal}) | (clause2 - {complement})
                return frozenset(resolvent)
        return None
    
    def _negate_literal(self, literal):
        if literal.startswith('¬'):
            return literal[1:]
        else:
            return f'¬{literal}'
    
    def ask_safe(self, pos: Tuple[int, int]) -> bool:
        r, c = pos
        pit_unsafe = f'P_{r},{c}'
        wumpus_unsafe = f'W_{r},{c}'
        
        # Try to prove no pit
        pit_safe = self._prove_by_contradiction(pit_unsafe)
        # Try to prove no wumpus
        wumpus_safe = self._prove_by_contradiction(wumpus_unsafe)
        
        # Cell is safe if both pit and wumpus are ruled out
        return pit_safe and wumpus_safe
    
    def _prove_by_contradiction(self, goal):
        working_clauses = set(self.clauses)
        negated_goal = frozenset([goal])
        working_clauses.add(negated_goal)
        
        # Apply resolution until we get empty clause or no more resolutions possible
        resolved_steps = 0
        while resolved_steps < 100:  # Limit iterations to prevent infinite loops
            new_clauses = set()
            clauses_list = list(working_clauses)
            
            # Try to resolve all pairs of clauses
            found_resolution = False
            for i in range(len(clauses_list)):
                for j in range(i + 1, len(clauses_list)):
                    resolvent = self.resolve_clauses(clauses_list[i], clauses_list[j])
                    
                    if resolvent is not None:
                        # Check for empty clause (contradiction found!)
                        if len(resolvent) == 0:
                            return True
                        
                        # Add new clause if not already present
                        if resolvent not in working_clauses:
                            new_clauses.add(resolvent)
                            found_resolution = True

            if not found_resolution:
                break
            
            working_clauses.update(new_clauses)
            resolved_steps += 1
        
        # No contradiction found, so the goal cannot be proven true
        return False
    
    def get_danger_level(self, pos: Tuple[int, int]) -> int:
        r, c = pos
        danger = 0
  
        pit_possible = f'P_{r},{c}'
        if not self._prove_by_contradiction(pit_possible):
            danger += 1  
    
        wumpus_possible = f'W_{r},{c}'
        if not self._prove_by_contradiction(wumpus_possible):
            danger += 2  
        
        return danger


class WumpusAgent:
    def __init__(self, rows: int, cols: int):
        self.world = WumpusWorld(rows, cols)
        self.kb = KnowledgeBase(rows, cols)
        self.visited = set()
        self.current_percepts = {}
        self.score = 0
        self.is_alive = True
        self.death_reason = None  
        self.has_gold = False  
        self.is_won = False  
        
        # Initialize at starting position
        self._explore_cell(self.world.agent_pos)
    
    def _explore_cell(self, pos: Tuple[int, int]):
        self.visited.add(pos)
        self.kb.tell_visited(pos)
        self.current_percepts = self.world.get_percepts(pos)

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
        current_pos = self.world.agent_pos
        adjacent = self.world._get_adjacent(current_pos)
        
        # Find safe unvisited cells
        safe_moves = []
        for pos in adjacent:
            if pos not in self.visited:
                is_safe = self.kb.ask_safe(pos)
                if is_safe:
                    safe_moves.append(pos)
        
        # If no safe moves, find the least dangerous unvisited cell
        if not safe_moves:
            unvisited = [pos for pos in adjacent if pos not in self.visited]
            if unvisited:
                # Find minimum danger level
                min_danger = min(self.kb.get_danger_level(pos) for pos in unvisited)
                # Get all cells with minimum danger (ties broken randomly)
                least_dangerous = [pos for pos in unvisited if self.kb.get_danger_level(pos) == min_danger]
                safe_moves = [random.choice(least_dangerous)]
        
        if not safe_moves:
            return False  # No moves available

        self.kb.inference_steps += 1
        
        # Randomly choose among safe moves
        new_pos = random.choice(safe_moves)
        
        # Check if the new position is a death cell BEFORE moving
        if new_pos in self.world.pit_positions or (new_pos == self.world.wumpus_pos and self.world.wumpus_alive):
            self.world.agent_pos = new_pos
            self.is_alive = False
            if new_pos in self.world.pit_positions:
                self.death_reason = "pit"
            elif new_pos == self.world.wumpus_pos and self.world.wumpus_alive:
                self.death_reason = "wumpus"
            return False
        
        # Safe move
        if not self.world.move_agent(new_pos):
            return False
        
        self._explore_cell(new_pos)
        self.score += 1
        
        # Check if agent reached gold and won
        if new_pos == self.world.gold_pos:
            self.has_gold = True
            self.is_won = True
        
        return True
    
    def get_state(self) -> Dict:
        grid = []
        for r in range(1, self.world.rows + 1):
            row = []
            for c in range(1, self.world.cols + 1):
                cell = {
                    'row': r,
                    'col': c,
                    'status': 'unknown'
                }
                
                if (r, c) == self.world.agent_pos:
                    cell['status'] = 'agent'
                elif (r, c) in self.visited:
                    cell['status'] = 'safe'
                elif (r, c) == self.world.gold_pos:
                    cell['status'] = 'gold'
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
            'is_alive': self.is_alive,
            'death_reason': self.death_reason,
            'has_gold': self.has_gold,
            'is_won': self.is_won
        }


from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
agent = None

@app.route('/init', methods=['POST'])
def init():
    global agent
    data = request.json
    rows = data.get('rows', 4)
    cols = data.get('cols', 4)
    agent = WumpusAgent(rows, cols)
    return jsonify(agent.get_state())

@app.route('/step', methods=['POST'])
def step():
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
    global agent
    if agent is None:
        return jsonify({'error': 'Game not initialized'}), 400
    return jsonify(agent.get_state())

if __name__ == '__main__':
    import os
    import sys
    
    port = int(os.environ.get('PORT', 5000))
    
    # Also support --port argument if provided
    if len(sys.argv) > 1 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    
    app.run(host='0.0.0.0', debug=False, port=port)
