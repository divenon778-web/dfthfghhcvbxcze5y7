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

def _find_nested_list(obj, depth=0):
    """Recursively search for the first list-of-lists or 24-length flat list in any nested structure."""
    if depth > 3:
        return None
    if isinstance(obj, list):
        if len(obj) == TOWER_ROWS and all(isinstance(r, (list, tuple)) and len(r) >= TOWER_COLS for r in obj):
            return obj
        if len(obj) == TOWER_TOTAL and all(not isinstance(v, (list, tuple)) for v in obj):
            return obj
        if len(obj) > 0 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in obj):
            return obj
        return None
    if isinstance(obj, dict):
        for v in obj.values():
            found = _find_nested_list(v, depth + 1)
            if found is not None:
                return found
    return None

def parse_tower_rows(history):
    rows = []
    if not isinstance(history, list):
        return rows
    for game in history:
        if not isinstance(game, dict):
            continue
        found = None
        # Try common field names first
        for key in ('tiles', 'bombPositions', 'grid', 'board', 'rows', 'data', 'mineLocations', 'tower_tiles', 'positions'):
            raw = game.get(key)
            if isinstance(raw, list) and len(raw) >= 3:
                found = raw
                break
        # Scan all values recursively
        if found is None:
            found = _find_nested_list(game)
        if found is None:
            continue
        # Case 1: list of 8 rows, each a list of 3 ints
        if len(found) == TOWER_ROWS and all(isinstance(r, (list, tuple)) and len(r) >= TOWER_COLS for r in found):
            for r in found[:TOWER_ROWS]:
                row = []
                for x in r[:TOWER_COLS]:
                    try:
                        row.append(1 if int(x) == 1 else 0)
                    except (ValueError, TypeError):
                        row.append(0)
                rows.append(row)
        # Case 2: flat list of 24 ints (tower flat)
        elif len(found) >= TOWER_TOTAL and all(not isinstance(v, (list, tuple)) for v in found[:TOWER_TOTAL]):
            for ri in range(TOWER_ROWS):
                start = ri * TOWER_COLS
                row = []
                for c in range(TOWER_COLS):
                    try:
                        row.append(1 if int(found[start + c]) == 1 else 0)
                    except (ValueError, TypeError, IndexError):
                        row.append(0)
                rows.append(row)
        # Case 3: mine locations as array of indices
        elif len(found) > 0 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in found):
            grid_flat = [0] * TOWER_TOTAL
            for loc in found:
                loc_i = int(loc)
                if 0 <= loc_i < TOWER_TOTAL:
                    grid_flat[loc_i] = 1
            for ri in range(TOWER_ROWS):
                start = ri * TOWER_COLS
                rows.append(grid_flat[start:start + TOWER_COLS])
    return rows

def tower_pathfinding(history, count=None, prediction_history=None):
    rows = parse_tower_rows(history)
    result = []
    for row_i in range(TOWER_ROWS):
        scores = [0] * TOWER_COLS
        for i in range(len(rows) - 1):
            target_row = (i + 1) % TOWER_ROWS
            if target_row != row_i:
                continue
            cur = rows[i]
            nxt = rows[i + 1]
            bomb = cur.index(1) if 1 in cur else 0
            for c in range(TOWER_COLS):
                if c < len(nxt) and nxt[c] == 0:
                    scores[min(bomb + c, TOWER_COLS - 1)] += 1
        if any(s > 0 for s in scores):
            best = max(range(TOWER_COLS), key=lambda c: scores[c])
        else:
            best = (row_i * 2) % TOWER_COLS
        result.append(row_i * TOWER_COLS + best)
    return result

def tower_probability(history, count=None, prediction_history=None):
    rows = parse_tower_rows(history)
    result = []
    for row_i in range(TOWER_ROWS):
        scores = [0] * TOWER_COLS
        for i in range(len(rows)):
            if i % TOWER_ROWS != row_i:
                continue
            row = rows[i]
            for c in range(TOWER_COLS):
                if c < len(row) and row[c] == 0:
                    scores[c] += 1
        if any(s > 0 for s in scores):
            best = max(range(TOWER_COLS), key=lambda c: scores[c])
        else:
            best = (row_i + 1) % TOWER_COLS
        result.append(row_i * TOWER_COLS + best)
    return result

def vain_tower_algo(history, count=None, prediction_history=None):
    path = tower_pathfinding(history)
    prob = tower_probability(history)
    result = []
    for row_i in range(TOWER_ROWS):
        p_col = path[row_i] % TOWER_COLS
        r_col = prob[row_i] % TOWER_COLS
        if p_col == r_col:
            result.append(row_i * TOWER_COLS + p_col)
        else:
            rows = parse_tower_rows(history)
            safe_scores = [0] * TOWER_COLS
            for i in range(len(rows)):
                if i % TOWER_ROWS != row_i:
                    continue
                row = rows[i]
                for c in range(TOWER_COLS):
                    if c < len(row) and row[c] == 0:
                        safe_scores[c] += 1
            if any(s > 0 for s in safe_scores):
                best = max(range(TOWER_COLS), key=lambda c: safe_scores[c])
            else:
                best = (row_i + 2) % TOWER_COLS
            result.append(row_i * TOWER_COLS + best)
    return result
