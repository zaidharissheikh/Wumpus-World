import React, { useState, useEffect } from 'react';

const WumpusAgent = () => {
  const [gridSize, setGridSize] = useState(4);
  const [state, setState] = useState(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  const API_URL = 'http://localhost:5000';

  const initGame = async () => {
    try {
      const response = await fetch(`${API_URL}/init`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: gridSize, cols: gridSize })
      });
      const data = await response.json();
      setState(data);
      setGameStarted(true);
      setIsRunning(false);
    } catch (error) {
      console.error('Init error:', error);
    }
  };

  const takeStep = async () => {
    // Don't step if agent is already dead or won
    if (state && (!state.is_alive || state.is_won)) {
      setIsRunning(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/step`, {
        method: 'POST'
      });
      const data = await response.json();
      setState(data.state);
      // Stop auto-play if agent just died or won
      if (data.state && (!data.state.is_alive || data.state.is_won)) {
        setIsRunning(false);
      }
    } catch (error) {
      console.error('Step error:', error);
      setIsRunning(false);
    }
  };

  useEffect(() => {
    if (!isRunning) return;
    
    const interval = setInterval(() => {
      takeStep();
    }, 500);
    
    return () => clearInterval(interval);
  }, [isRunning, state]);

  const getDeathMessage = () => {
    if (!state || state.is_alive) return null;
    
    const deathMessages = {
      'pit': {
        emoji: '🕳️',
        title: 'Fell into a Pit!',
        description: 'The agent fell into a pit and died.'
      },
      'wumpus': {
        emoji: '👹',
        title: 'Eaten by Wumpus!',
        description: 'The agent was eaten by the Wumpus.'
      }
    };
    
    return deathMessages[state.death_reason] || {
      emoji: '💀',
      title: 'Agent Died',
      description: 'The agent did not survive.'
    };
  };

  const getVictoryMessage = () => {
    if (!state || !state.is_won) return null;
    
    return {
      emoji: '✨',
      title: 'Victory!',
      description: 'The agent successfully found the gold and completed the mission!'
    };
  };

  const handleNewGame = () => {
    setState(null);
    setGameStarted(false);
    setIsRunning(false);
    initGame();
  };

  const deathInfo = getDeathMessage();
  const victoryInfo = getVictoryMessage();

  const getCellColor = (status) => {
    switch(status) {
      case 'safe': return '#10b981';
      case 'agent': return '#3b82f6';
      case 'pit': return '#ef4444';
      case 'wumpus': return '#f59e0b';
      case 'gold': return '#fbbf24';
      default: return '#9ca3af';
    }
  };

  const getCellLabel = (status) => {
    switch(status) {
      case 'agent': return '🤖';
      case 'pit': return '🕳️';
      case 'wumpus': return '👹';
      case 'gold': return '💎';
      case 'safe': return '✓';
      default: return '?';
    }
  };

  return (
    <div style={styles.container}>
      <style>{globalStyles}</style>
      
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>Wumpus World Agent</h1>
        <p style={styles.subtitle}>Propositional Logic Pathfinding</p>
      </div>

      {/* Controls */}
      <div style={styles.controls}>
        <div style={styles.controlGroup}>
          <label style={styles.label}>Grid Size:</label>
          <input
            type="number"
            min="3"
            max="8"
            value={gridSize}
            onChange={(e) => setGridSize(parseInt(e.target.value))}
            disabled={gameStarted}
            style={styles.input}
          />
        </div>

        <button 
          onClick={initGame}
          style={styles.buttonPrimary}
        >
          {gameStarted ? '🔄 New Game' : '▶ Start Game'}
        </button>

        {gameStarted && (
          <>
            <button
              onClick={() => setIsRunning(!isRunning)}
              disabled={!state || !state.is_alive || state.is_won}
              style={{
                ...styles.buttonSecondary, 
                backgroundColor: isRunning ? '#ef4444' : '#10b981',
                opacity: (state && (!state.is_alive || state.is_won)) ? 0.5 : 1,
                cursor: (state && (!state.is_alive || state.is_won)) ? 'not-allowed' : 'pointer'
              }}
            >
              {isRunning ? '⏸ Pause' : '▶ Auto-Play'}
            </button>
            <button
              onClick={takeStep}
              disabled={isRunning || !state || !state.is_alive || state.is_won}
              style={{
                ...styles.buttonSecondary,
                opacity: (isRunning || !state || !state.is_alive || state.is_won) ? 0.5 : 1,
                cursor: (isRunning || !state || !state.is_alive || state.is_won) ? 'not-allowed' : 'pointer'
              }}
            >
              ⏭ Step
            </button>
          </>
        )}
      </div>

      {gameStarted && state && (
        <div style={styles.gameContainer}>
          {/* Grid Visualization */}
          <div style={styles.gridSection}>
            <h2 style={styles.sectionTitle}>Environment</h2>
            <div style={styles.gridWrapper}>
              <div 
                style={{
                  ...styles.grid,
                  gridTemplateColumns: `repeat(${gridSize}, 1fr)`
                }}
              >
                {state.grid.flat().map((cell, idx) => (
                  <div
                    key={idx}
                    style={{
                      ...styles.cell,
                      backgroundColor: getCellColor(cell.status),
                      boxShadow: cell.status === 'agent' 
                        ? '0 0 0 3px rgba(59, 130, 246, 0.5)' 
                        : (!state.is_alive && cell.status === 'agent')
                        ? '0 0 15px rgba(239, 68, 68, 0.8), inset 0 0 10px rgba(0,0,0,0.2)'
                        : 'none',
                      border: (!state.is_alive && cell.status === 'agent') ? '3px solid #dc2626' : 'none'
                    }}
                  >
                    <span style={styles.cellLabel}>{getCellLabel(cell.status)}</span>
                    <span style={styles.cellCoord}>{cell.row},{cell.col}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Legend */}
            <div style={styles.legend}>
              <div style={styles.legendItem}>
                <div style={{...styles.legendColor, backgroundColor: '#10b981'}}></div>
                <span>Safe (Visited)</span>
              </div>
              <div style={styles.legendItem}>
                <div style={{...styles.legendColor, backgroundColor: '#9ca3af'}}></div>
                <span>Unknown</span>
              </div>
              <div style={styles.legendItem}>
                <div style={{...styles.legendColor, backgroundColor: '#ef4444'}}></div>
                <span>Pit</span>
              </div>
              <div style={styles.legendItem}>
                <div style={{...styles.legendColor, backgroundColor: '#f59e0b'}}></div>
                <span>Wumpus</span>
              </div>
              <div style={styles.legendItem}>
                <div style={{...styles.legendColor, backgroundColor: '#fbbf24'}}></div>
                <span>Gold</span>
              </div>
              <div style={styles.legendItem}>
                <div style={{...styles.legendColor, backgroundColor: '#3b82f6'}}></div>
                <span>Agent</span>
              </div>
            </div>
          </div>

          {/* Metrics Dashboard */}
          <div style={styles.metricsSection}>
            <h2 style={styles.sectionTitle}>Metrics</h2>
            
            <div style={styles.metricCard}>
              <div style={styles.metricLabel}>Agent Position</div>
              <div style={styles.metricValue}>
                ({state.agent_pos[0]}, {state.agent_pos[1]})
              </div>
            </div>

            <div style={styles.metricCard}>
              <div style={styles.metricLabel}>Cells Explored</div>
              <div style={styles.metricValue}>{state.visited_count}</div>
            </div>

            <div style={styles.metricCard}>
              <div style={styles.metricLabel}>Inference Steps</div>
              <div style={styles.metricValue}>{state.inference_steps}</div>
            </div>

            <div style={styles.metricCard}>
              <div style={styles.metricLabel}>Score</div>
              <div style={styles.metricValue}>{state.score}</div>
            </div>

            <div style={styles.metricCard}>
              <div style={styles.metricLabel}>Status</div>
              <div style={{
                ...styles.metricValue,
                color: state.is_alive ? '#10b981' : '#ef4444'
              }}>
                {state.is_alive ? '🟢 Alive' : '🔴 Dead'}
              </div>
            </div>

            {/* Current Percepts */}
            <div style={styles.perceptsCard}>
              <div style={styles.metricLabel}>Current Percepts</div>
              <div style={styles.perceptsList}>
                {Object.entries(state.current_percepts).map(([key, value]) => (
                  <div key={key} style={styles.perceptItem}>
                    <span style={styles.perceptLabel}>{key}:</span>
                    <span style={{
                      color: value ? '#10b981' : '#9ca3af',
                      fontWeight: 'bold'
                    }}>
                      {value ? '✓' : '✗'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Game Over Modal */}
      {gameStarted && state && !state.is_alive && deathInfo && (
        <div style={styles.modalOverlay}>
          <div style={styles.gameOverModal}>
            <div style={styles.deathIcon}>{deathInfo.emoji}</div>
            <h2 style={styles.gameOverTitle}>{deathInfo.title}</h2>
            <p style={styles.gameOverDescription}>{deathInfo.description}</p>
            
            {/* Final Metrics */}
            <div style={styles.finalMetrics}>
              <div style={styles.finalMetricItem}>
                <span style={styles.finalMetricLabel}>Cells Explored:</span>
                <span style={styles.finalMetricValue}>{state.visited_count}</span>
              </div>
              <div style={styles.finalMetricItem}>
                <span style={styles.finalMetricLabel}>Final Score:</span>
                <span style={styles.finalMetricValue}>{state.score}</span>
              </div>
              <div style={styles.finalMetricItem}>
                <span style={styles.finalMetricLabel}>Agent Position:</span>
                <span style={styles.finalMetricValue}>({state.agent_pos[0]}, {state.agent_pos[1]})</span>
              </div>
              <div style={styles.finalMetricItem}>
                <span style={styles.finalMetricLabel}>Inference Steps:</span>
                <span style={styles.finalMetricValue}>{state.inference_steps}</span>
              </div>
            </div>

            <button 
              onClick={initGame}
              style={styles.restartButton}
            >
              🔄 Start New Game
            </button>
          </div>
        </div>
      )}

      {/* Victory Modal */}
      {gameStarted && state && state.is_won && victoryInfo && (
        <div style={styles.modalOverlay}>
          <div style={{...styles.gameOverModal, ...styles.victoryModal}}>
            <div style={{...styles.deathIcon, animation: 'bounce 0.6s infinite'}}>{victoryInfo.emoji}</div>
            <h2 style={{...styles.gameOverTitle, color: '#10b981'}}>{victoryInfo.title}</h2>
            <p style={styles.gameOverDescription}>{victoryInfo.description}</p>
            
            {/* Final Metrics */}
            <div style={styles.finalMetrics}>
              <div style={styles.finalMetricItem}>
                <span style={styles.finalMetricLabel}>Cells Explored:</span>
                <span style={styles.finalMetricValue}>{state.visited_count}</span>
              </div>
              <div style={styles.finalMetricItem}>
                <span style={styles.finalMetricLabel}>Final Score:</span>
                <span style={styles.finalMetricValue}>{state.score}</span>
              </div>
              <div style={styles.finalMetricItem}>
                <span style={styles.finalMetricLabel}>Agent Position:</span>
                <span style={styles.finalMetricValue}>({state.agent_pos[0]}, {state.agent_pos[1]})</span>
              </div>
              <div style={styles.finalMetricItem}>
                <span style={styles.finalMetricLabel}>Inference Steps:</span>
                <span style={styles.finalMetricValue}>{state.inference_steps}</span>
              </div>
            </div>

            <button 
              onClick={initGame}
              style={{...styles.restartButton, backgroundColor: '#10b981'}}
            >
              🔄 Play Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    padding: '20px',
    fontFamily: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif'
  },
  header: {
    textAlign: 'center',
    color: 'white',
    marginBottom: '30px',
    marginTop: '20px'
  },
  title: {
    fontSize: '48px',
    fontWeight: 'bold',
    margin: '0 0 10px 0',
    textShadow: '0 2px 10px rgba(0,0,0,0.2)'
  },
  subtitle: {
    fontSize: '18px',
    opacity: 0.9,
    margin: 0
  },
  controls: {
    display: 'flex',
    gap: '15px',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: '30px',
    flexWrap: 'wrap',
    backgroundColor: 'rgba(255,255,255,0.1)',
    padding: '20px',
    borderRadius: '12px',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255,255,255,0.2)'
  },
  controlGroup: {
    display: 'flex',
    gap: '10px',
    alignItems: 'center'
  },
  label: {
    color: 'white',
    fontWeight: '500',
    fontSize: '14px'
  },
  input: {
    padding: '8px 12px',
    borderRadius: '6px',
    border: 'none',
    fontSize: '16px',
    width: '60px',
    textAlign: 'center'
  },
  buttonPrimary: {
    padding: '10px 20px',
    borderRadius: '6px',
    border: 'none',
    backgroundColor: '#3b82f6',
    color: 'white',
    fontWeight: 'bold',
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)'
  },
  buttonSecondary: {
    padding: '10px 20px',
    borderRadius: '6px',
    border: 'none',
    backgroundColor: '#10b981',
    color: 'white',
    fontWeight: 'bold',
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'all 0.3s ease'
  },
  gameContainer: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
    maxWidth: '1200px',
    margin: '0 auto'
  },
  gridSection: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
  },
  metricsSection: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column',
    gap: '15px'
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: '0 0 15px 0'
  },
  gridWrapper: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '20px'
  },
  grid: {
    display: 'grid',
    gap: '8px',
    padding: '15px',
    backgroundColor: '#f3f4f6',
    borderRadius: '8px'
  },
  cell: {
    width: '70px',
    height: '70px',
    borderRadius: '8px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    position: 'relative',
    color: 'white',
    fontWeight: 'bold'
  },
  cellLabel: {
    fontSize: '28px',
    marginBottom: '4px'
  },
  cellCoord: {
    fontSize: '10px',
    opacity: 0.8
  },
  legend: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '10px',
    padding: '15px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px'
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '13px',
    color: '#4b5563'
  },
  legendColor: {
    width: '20px',
    height: '20px',
    borderRadius: '4px'
  },
  metricCard: {
    backgroundColor: '#f9fafb',
    padding: '15px',
    borderRadius: '8px',
    borderLeft: '4px solid #667eea'
  },
  metricLabel: {
    fontSize: '12px',
    color: '#6b7280',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    marginBottom: '5px',
    fontWeight: '600'
  },
  metricValue: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#1f2937'
  },
  perceptsCard: {
    backgroundColor: '#f9fafb',
    padding: '15px',
    borderRadius: '8px',
    borderLeft: '4px solid #f59e0b'
  },
  perceptsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    marginTop: '10px'
  },
  perceptItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '13px'
  },
  perceptLabel: {
    color: '#6b7280',
    textTransform: 'capitalize',
    fontWeight: '500'
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    animation: 'fadeIn 0.3s ease'
  },
  gameOverModal: {
    backgroundColor: 'white',
    borderRadius: '16px',
    padding: '40px',
    maxWidth: '500px',
    width: '90%',
    textAlign: 'center',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
    animation: 'slideUp 0.4s ease'
  },
  victoryModal: {
    borderTop: '5px solid #10b981',
    boxShadow: '0 20px 60px rgba(16, 185, 129, 0.3)'
  },
  deathIcon: {
    fontSize: '80px',
    marginBottom: '20px',
    display: 'block',
    animation: 'pulse 2s infinite'
  },
  gameOverTitle: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#ef4444',
    margin: '0 0 10px 0'
  },
  gameOverDescription: {
    fontSize: '16px',
    color: '#6b7280',
    margin: '0 0 30px 0',
    lineHeight: '1.6'
  },
  finalMetrics: {
    backgroundColor: '#f9fafb',
    borderRadius: '12px',
    padding: '20px',
    marginBottom: '30px',
    border: '1px solid #e5e7eb'
  },
  finalMetricItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '10px 0',
    fontSize: '14px',
    alignItems: 'center'
  },
  finalMetricLabel: {
    color: '#6b7280',
    fontWeight: '500'
  },
  finalMetricValue: {
    color: '#1f2937',
    fontWeight: 'bold',
    fontSize: '16px'
  },
  restartButton: {
    padding: '12px 32px',
    borderRadius: '8px',
    border: 'none',
    backgroundColor: '#3b82f6',
    color: 'white',
    fontWeight: 'bold',
    cursor: 'pointer',
    fontSize: '16px',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)',
    width: '100%'
  }
};

const globalStyles = `
  * {
    box-sizing: border-box;
  }
  
  body {
    margin: 0;
    padding: 0;
  }
  
  button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
  }
  
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  button:active {
    transform: translateY(0);
  }
  
  input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.1);
    }
  }

  @keyframes bounce {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-20px);
    }
  }

  @media (max-width: 1024px) {
    div[style*="gridTemplateColumns: 1fr 1fr"] {
      grid-template-columns: 1fr !important;
    }
  }
`;

export default WumpusAgent;