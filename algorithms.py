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
    if depth > 5:
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
        for key in ('tiles', 'bombPositions', 'grid', 'board', 'rows', 'data', 'mineLocations', 'tower_tiles', 'positions', 'bombIndices', 'bombLocations', 'bombs'):
            raw = game.get(key)
            if isinstance(raw, list) and len(raw) >= 3:
                found = raw
                break
        if found is None:
            found = _find_nested_list(game)
        # Handle revealed+bombIndices combo (common Bloxflip pattern)
        if found is None:
            revealed = game.get('revealed') or game.get('uncoveredLocations') or game.get('safeTiles')
            bombs = game.get('bombIndices') or game.get('bombLocations') or game.get('bombs') or game.get('mineLocations')
            if isinstance(revealed, list) and isinstance(bombs, list):
                grid_flat = [0] * TOWER_TOTAL
                for loc in bombs:
                    if isinstance(loc, (int, float)) and 0 <= int(loc) < TOWER_TOTAL:
                        grid_flat[int(loc)] = 1
                for loc in revealed:
                    if isinstance(loc, (int, float)) and 0 <= int(loc) < TOWER_TOTAL:
                        if grid_flat[int(loc)] != 1:
                            grid_flat[int(loc)] = 0
                for ri in range(TOWER_ROWS):
                    start = ri * TOWER_COLS
                    rows.append(grid_flat[start:start + TOWER_COLS])
                continue
        if found is None:
            continue
        if len(found) == TOWER_ROWS and all(isinstance(r, (list, tuple)) and len(r) >= TOWER_COLS for r in found):
            for r in found[:TOWER_ROWS]:
                row = []
                for x in r[:TOWER_COLS]:
                    try:
                        row.append(1 if int(x) == 1 else 0)
                    except (ValueError, TypeError):
                        row.append(0)
                rows.append(row)
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

def tower_frequency(history, count=None, prediction_history=None):
    """For each row, pick the column that was safe most often across all history."""
    rows = parse_tower_rows(history)
    result = []
    for row_i in range(TOWER_ROWS):
        safe_scores = [0] * TOWER_COLS
        bomb_scores = [0] * TOWER_COLS
        for i in range(len(rows)):
            if i % TOWER_ROWS != row_i:
                continue
            row = rows[i]
            for c in range(TOWER_COLS):
                if row[c] == 0:
                    safe_scores[c] += 1
                else:
                    bomb_scores[c] += 1
        total = [safe_scores[c] + bomb_scores[c] for c in range(TOWER_COLS)]
        # If no data, cycle columns
        if all(t == 0 for t in total):
            best = (row_i + 1) % TOWER_COLS
        else:
            # Pick column with highest safe ratio
            ratios = [safe_scores[c] / total[c] if total[c] > 0 else 0 for c in range(TOWER_COLS)]
            best = max(range(TOWER_COLS), key=lambda c: (ratios[c], safe_scores[c]))
        result.append(row_i * TOWER_COLS + best)
    return result

def tower_pathfinding(history, count=None, prediction_history=None):
    """For each row, use bomb in previous row to predict safe column."""
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

def tower_pattern(history, count=None, prediction_history=None):
    """Look at bomb→safe transition patterns between consecutive rows."""
    rows = parse_tower_rows(history)
    result = []
    for row_i in range(TOWER_ROWS):
        transition_counts = [[0]*TOWER_COLS for _ in range(TOWER_COLS)]
        for i in range(len(rows) - 1):
            target_row = (i + 1) % TOWER_ROWS
            if target_row != row_i:
                continue
            cur = rows[i]
            nxt = rows[i + 1]
            bomb = cur.index(1) if 1 in cur else 0
            safe = nxt.index(0) if 0 in nxt else 0
            transition_counts[bomb][safe] += 1
        safe_freq = [0] * TOWER_COLS
        for i in range(len(rows)):
            if i % TOWER_ROWS != row_i:
                continue
            row = rows[i]
            for c in range(TOWER_COLS):
                if row[c] == 0:
                    safe_freq[c] += 1
        # Use transitions weighted by frequency
        scores = [0] * TOWER_COLS
        for bomb_col in range(TOWER_COLS):
            for safe_col in range(TOWER_COLS):
                scores[safe_col] += transition_counts[bomb_col][safe_col]
        # Boost by frequency
        for c in range(TOWER_COLS):
            scores[c] += safe_freq[c] * 2
        if any(s > 0 for s in scores):
            best = max(range(TOWER_COLS), key=lambda c: scores[c])
        else:
            best = (row_i * 3) % TOWER_COLS
        result.append(row_i * TOWER_COLS + best)
    return result

def tower_pastgames(history, count=None, prediction_history=None):
    """Mark most recent game's safe tiles as predictions."""
    rows = parse_tower_rows(history)
    if len(rows) < TOWER_ROWS:
        return [(row_i * TOWER_COLS + (row_i * 2) % TOWER_COLS) for row_i in range(TOWER_ROWS)]
    latest = rows[-TOWER_ROWS:]
    result = []
    for row_i in range(TOWER_ROWS):
        row = latest[row_i]
        safe = [c for c in range(TOWER_COLS) if row[c] == 0]
        if safe:
            result.append(row_i * TOWER_COLS + safe[0])
        else:
            result.append(row_i * TOWER_COLS + (row_i % TOWER_COLS))
    return result

def tower_vain(history, count=None, prediction_history=None):
    """Combine frequency, pathfinding, and pattern via weighted voting."""
    freq = tower_frequency(history)
    path = tower_pathfinding(history)
    patt = tower_pattern(history)
    result = []
    for row_i in range(TOWER_ROWS):
        votes = [0] * TOWER_COLS
        votes[freq[row_i] % TOWER_COLS] += 2
        votes[path[row_i] % TOWER_COLS] += 1
        votes[patt[row_i] % TOWER_COLS] += 2
        best = max(range(TOWER_COLS), key=lambda c: (votes[c], c))
        result.append(row_i * TOWER_COLS + best)
    return result
