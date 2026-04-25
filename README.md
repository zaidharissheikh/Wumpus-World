# 🎮 Wumpus World AI Agent

A React + Flask application implementing an intelligent AI agent for the classic Wumpus World problem using **Propositional Logic and Resolution Refutation**.

## 📋 Project Overview

The Wumpus World is a grid-based environment where an AI agent must:
- ✅ Navigate safely through an unknown grid
- ✅ Avoid pits and the dangerous Wumpus
- ✅ Collect gold and win the game
- ✅ Use **logical deduction** to determine safe moves

The agent employs **Propositional Logic with Resolution Refutation** to answer safety queries before moving to adjacent cells, making all decisions based on proof by contradiction.

## 🎯 Key Features

- **Intelligent Pathfinding**: Agent uses logical inference to identify safe cells
- **Resolution Refutation**: Full CNF-based resolution algorithm for proving cell safety
- **Death Detection**: Game ends immediately when agent encounters pit or Wumpus
- **Victory Condition**: Game ends with success when agent collects gold
- **Configurable Grid**: Create games on 3×3 to 8×8 grids
- **Step-by-Step Gameplay**: Manual or auto-play mode
- **Inference Metrics**: Track logical inference steps during gameplay
- **Interactive UI**: Real-time grid visualization with percepts and game state

## 🏗️ Architecture

### Frontend (React)
- **Technology**: React 19.2.5 with React DOM
- **Framework**: Created with Create React App
- **Key Component**: `WumpusAgent.jsx` - Main game UI
- **Features**:
  - Interactive grid display with cell states
  - Game control buttons (Step, Auto-Play, New Game)
  - Death and victory modals with game statistics
  - Real-time percept display
  - Inference step counter

### Backend (Flask)
- **Technology**: Flask 2.3.2 with CORS support
- **API Endpoints**:
  - `POST /init` - Initialize new game with configurable grid size
  - `POST /step` - Execute one agent decision cycle
- **Response Format**: JSON containing complete game state

## 🧠 AI Agent Logic: Resolution Refutation

### How It Works

The agent uses **Propositional Logic with CNF (Conjunctive Normal Form)** and **Resolution Refutation** to answer safety queries:

```python
# Before moving to an adjacent cell, agent asks:
# "Can I prove this cell is safe (¬pit AND ¬wumpus)?"

ask_safe(pos):
    pit_safe = prove(¬P_r,c)      # Can I prove NO pit exists?
    wumpus_safe = prove(¬W_r,c)   # Can I prove NO wumpus exists?
    return pit_safe AND wumpus_safe
```

### Resolution Algorithm

1. **CNF Representation**: Percepts converted to CNF clauses
   - Breeze at (1,1) → `{P_1,2 ∨ P_2,1 ∨ P_2,2}` (at least one adjacent pit)
   - No breeze at (1,1) → `{¬P_1,2} ∧ {¬P_2,1} ∧ {¬P_2,2}` (no adjacent pits)

2. **Proof by Contradiction**:
   - Goal: Prove ¬P_r,c (cell has no pit)
   - Add: Assume P_r,c (negated goal)
   - Resolve: Apply resolution rule until empty clause derived
   - Result: If empty clause found → goal is proven true

3. **Resolution Rule**:
   ```
   Clause1: {A ∨ B}
   Clause2: {¬A ∨ C}
   ─────────────────
   Resolvent: {B ∨ C}
   ```

### Decision Making

- **Preferred**: Safe moves (cells provably without pit and Wumpus)
- **Fallback**: Least dangerous unvisited cells (random tie-breaker)
- **Result**: One inference step per decision cycle

## 🚀 Getting Started

### Prerequisites
- **Node.js** (v14+) and npm
- **Python** (3.8+) with pip

### Installation

1. **Clone/Extract project**:
   ```bash
   cd wumpus-world
   ```

2. **Install Frontend Dependencies**:
   ```bash
   npm install
   ```

3. **Install Backend Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

## ▶️ Running the Game

### Terminal 1 - Start Backend (Flask)
```bash
cd backend
python wumpus_agent.py
```
Backend runs on `http://localhost:5000`

### Terminal 2 - Start Frontend (React)
```bash
npm start
```
Frontend opens at `http://localhost:3000`

## 🎮 How to Play

1. **New Game**: Click "New Game" to initialize with current grid size
2. **Grid Size**: Adjust grid size (3-8) before starting
3. **Manual Mode**:
   - Click "Step" to make one agent decision
   - Watch the agent move based on logical inference
4. **Auto-Play Mode**:
   - Click "Auto-Play" to run continuous decisions
   - Game pauses on death or victory
5. **Game Ends**:
   - **Death**: Agent hits pit or Wumpus → Game Over modal
   - **Victory**: Agent reaches gold → Victory modal

## 📊 Game State & Metrics

Each game displays:
- **Visited Cells**: Number of explored cells
- **Score**: Points accumulated (1 per step)
- **Inference Steps**: Logical deduction cycles performed
- **Agent Position**: Current grid coordinates
- **Death Reason** (if applicable): "pit" or "wumpus"
- **Victory Status**: Game won/lost

## 📁 Project Structure

```
wumpus-world/
├── README.md                      # This file
├── package.json                   # Frontend dependencies
├── src/
│   ├── App.js                    # Main React component
│   ├── App.css                   # Styling
│   ├── index.js                  # React entry point
│   └── components/
│       └── WumpusAgent.jsx        # Game UI component
├── public/
│   ├── index.html                # HTML template
│   └── manifest.json             # PWA manifest
└── backend/
    ├── requirements.txt          # Python dependencies
    └── wumpus_agent.py          # AI agent & Flask server
```

## 🔧 Backend Components (`wumpus_agent.py`)

### `WumpusWorld` Class
- **Responsibility**: Environment simulator
- **Manages**: Agent position, Wumpus position, pit locations, gold position
- **Methods**:
  - `get_percepts(pos)`: Returns {breeze, stench, glitter, bump, scream}
  - `move_agent(new_pos)`: Validates and executes movement
  - `_get_adjacent(pos)`: Returns set of valid adjacent cells

### `KnowledgeBase` Class
- **Responsibility**: Propositional logic reasoning engine
- **Stores**: CNF clauses as frozensets of string literals
- **Key Methods**:
  - `tell_breeze(pos, adjacent)`: Add breeze percept clause
  - `tell_no_breeze(pos, adjacent)`: Add no-breeze percept clause
  - `tell_stench(pos, adjacent)`: Add stench percept clause
  - `tell_no_stench(pos, adjacent)`: Add no-stench percept clause
  - `tell_visited(pos)`: Mark cell as definitely safe
  - `ask_safe(pos)`: Query if cell is safe using resolution
  - `resolve_clauses(c1, c2)`: Implement resolution rule
  - `_prove_by_contradiction(goal)`: Full resolution refutation algorithm
  - `get_danger_level(pos)`: Rate unvisited cell danger

### `WumpusAgent` Class
- **Responsibility**: Decision making and game state management
- **Methods**:
  - `step()`: Execute one decision cycle
  - `_explore_cell(pos)`: Update KB with percepts
  - `get_state()`: Return complete game state for frontend

### Flask API
- **`POST /init`**: Query: `{rows: int, cols: int}` → New game state
- **`POST /step`**: Execute one agent step → Updated game state

## 💡 Example Gameplay (Logical Inference)

```
Turn 1: Agent at (1,1), senses BREEZE
  → KB learns: P_1,2 ∨ P_2,1 ∨ P_2,2 (pit in one of these cells)
  → Check (1,2): Can't prove safe yet
  → Check (2,1): Can't prove safe yet

Turn 2: Agent moves to (1,2), senses NO BREEZE
  → KB learns: ¬P_1,1 ∧ ¬P_1,3 ∧ ¬P_2,2
  → Resolve against Turn 1 percept → Must be: P_2,1 (pit at 2,1)
  → Check (2,1): Can prove ¬W_2,1 ∧ has pit → UNSAFE
  → Check (2,2): Can prove ¬P_2,2 ∧ ¬W_2,2 → SAFE ✓

Turn 3: Agent moves to (2,2) safely
  → Continues logical deduction...
```

## 🔬 Technical Details

- **Language**: Python 3.10 (backend), JavaScript/React (frontend)
- **Inference**: Resolution Refutation with CNF
- **Reasoning**: Proof by Contradiction
- **Complexity**: O(n²) per resolution pass where n = number of clauses
- **Inference Limit**: Max 100 resolution iterations per proof (prevents infinite loops)

## 📝 Notes

- The agent uses **pure logical deduction**, not probability or heuristics
- Random selection used for tie-breaking (multiple equally-safe moves)
- Game ends immediately on death—no turn is wasted
- Inference steps only count at decision level, not internal resolution operations

## 🎓 Educational Value

This implementation demonstrates:
- ✅ Propositional logic in practice
- ✅ CNF (Conjunctive Normal Form) conversion
- ✅ Resolution rule application
- ✅ Proof by contradiction
- ✅ Knowledge base reasoning
- ✅ AI decision making under uncertainty
- ✅ Full-stack application architecture (React + Flask)
