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


TOWER_ROWS = 8
TOWER_COLS = 3
TOWER_TOTAL = TOWER_ROWS * TOWER_COLS

def parse_tower_rows(history):
    rows = []
    for game in history:
        raw = game.get('tiles') or game.get('bombPositions') or game.get('grid', [])
        if isinstance(raw, list) and len(raw) >= 8:
            for r in raw[:8]:
                if isinstance(r, list) and len(r) >= 3:
                    rows.append([int(x) if x in (0,1) else 0 for x in r[:3]])
        elif isinstance(game, dict):
            for i in range(8):
                key = f'row{i}'
                r = game.get(key)
                if isinstance(r, list) and len(r) >= 3:
                    rows.append([int(x) if x in (0,1) else 0 for x in r[:3]])
    return rows

def tower_pathfinding(history, count, prediction_history=None):
    scores = [0] * TOWER_TOTAL
    rows = parse_tower_rows(history)
    if not rows:
        return list(range(min(count, TOWER_TOTAL)))
    for i in range(min(len(rows) - 1, 50)):
        cur = rows[i]
        nxt = rows[i + 1]
        bomb = cur.index(1) if 1 in cur else 0
        safe = [c for c in range(TOWER_COLS) if c < len(nxt) and nxt[c] == 0]
        for s in safe:
            idx = ((i + 1) % TOWER_ROWS) * TOWER_COLS + min(bomb + s, TOWER_COLS - 1)
            if idx < TOWER_TOTAL:
                scores[idx] += 1
    indexed = sorted([{'i': i, 'v': v} for i, v in enumerate(scores)], key=lambda k: k['v'], reverse=True)
    return [x['i'] for x in indexed[:count]]

def tower_probability(history, count, prediction_history=None):
    scores = [0] * TOWER_TOTAL
    rows = parse_tower_rows(history)
    if not rows:
        return list(range(min(count, TOWER_TOTAL)))
    for i in range(len(rows)):
        row = rows[i]
        for c in range(TOWER_COLS):
            if c < len(row) and row[c] == 0:
                idx = (i % TOWER_ROWS) * TOWER_COLS + c
                if idx < TOWER_TOTAL:
                    scores[idx] += 1
    indexed = sorted([{'i': i, 'v': v} for i, v in enumerate(scores)], key=lambda k: k['v'], reverse=True)
    return [x['i'] for x in indexed[:count]]

def vain_tower_algo(history, count, prediction_history=None):
    a = set(tower_pathfinding(history, count * 2))
    b = set(tower_probability(history, count * 2))
    combined = list(a & b) + list(a ^ b)
    if len(combined) >= count:
        return combined[:count]
    remaining = [i for i in range(TOWER_TOTAL) if i not in combined]
    return combined + remaining[:count - len(combined)]
