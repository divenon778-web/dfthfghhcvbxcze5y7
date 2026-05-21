import random

TOTAL_TILES = 25

def aspect_algo(history, count):
    scores = [0] * TOTAL_TILES
    x = []
    for r in history:
        x.extend(r.get('mineLocations', []))
    
    for i in range(len(x)):
        val = min(abs(x[i] - i), 24)
        scores[val] -= 10
        
    indexed = [{'index': i, 'value': v} for i, v in enumerate(scores)]
    indexed.sort(key=lambda k: k['value'], reverse=True)
    return [item['index'] for item in indexed[:count]]

def algorithm2(history, count):
    scores = [0] * TOTAL_TILES
    x = []
    for r in history:
        x.extend(r.get('mineLocations', []))
        
    def is_neighbor(pos1, pos2):
        r1, c1 = divmod(pos1, 5)
        r2, c2 = divmod(pos2, 5)
        return ((r2-r1)**2 + (c2-c1)**2) < 1
        
    for ind in range(min(25, len(x))):
        next_idx = min(ind + 1, len(x) - 1)
        if not is_neighbor(x[ind], x[next_idx]):
            scores[x[ind]] -= 15
            
    indexed = [{'index': i, 'value': v} for i, v in enumerate(scores)]
    indexed.sort(key=lambda k: k['value'], reverse=True)
    return [item['index'] for item in indexed[:count]]

def coxy_mines2(history, count):
    y_field = [0] * TOTAL_TILES
    upper = 0
    max_entries = min(len(history), 15)
    
    for h in range(max_entries):
        v = history[h]
        locations = v.get('uncoveredLocations', []) if h % 2 == 0 else v.get('mineLocations', [])
        for loc in locations:
            if upper >= count * 3: break
            y_field[loc] = y_field[loc] + 1
            upper += 1
            
    scores = [1 if v == 0 else -v * 5 for v in y_field]
    indexed = [{'index': i, 'value': v} for i, v in enumerate(scores)]
    indexed.sort(key=lambda k: k['value'], reverse=True)
    return [item['index'] for item in indexed[:count]]

def past_games(history, count):
    board = [0] * TOTAL_TILES
    x = []
    for r in history:
        x.extend(r.get('mineLocations', []))
        
    for i in range(min(count, len(x))):
        board[x[i]] = 1
        
    return [i for i in range(TOTAL_TILES) if board[i] == 1][:count]

def vain_algo(history, count, prediction_history=None):
    a = aspect_algo(history, count)
    b = algorithm2(history, count)
    c = coxy_mines2(history, count)
    
    votes = [0] * TOTAL_TILES
    for i in a: votes[i] += 1
    for i in b: votes[i] += 1
    for i in c: votes[i] += 1
    
    if prediction_history:
        recent_safe = set()
        for round_data in prediction_history[:5]:
            mines = round_data.get('mineLocations', [])
            for i in range(TOTAL_TILES):
                if i not in mines:
                    recent_safe.add(i)
        for i in recent_safe:
            votes[i] -= 2
            
    indexed = [{'index': i, 'value': v} for i, v in enumerate(votes)]
    indexed.sort(key=lambda k: k['value'], reverse=True)
    return [item['index'] for item in indexed[:count]]
