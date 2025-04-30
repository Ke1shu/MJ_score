from collections import defaultdict

def calculate_points(raw_scores: dict, setting, tie_rule: str = 'split'):
    def round_5_6(x):
        pt = x / 1000
        decimal = pt - int(pt)
        return int(pt) if decimal < 0.6 else int(pt) + 1  # 5捨6入（0.6以上切り上げ）

    # ✅ 差分計算: pt - 30（30からの距離）
    point_diffs = {
        pid: round_5_6(score) - (setting.return_score // 1000)
        for pid, score in raw_scores.items()
    }

    # ✅ 順位決定
    sorted_players = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    rank_groups = defaultdict(list)
    rank = 1
    current_score = None
    for pid, score in sorted_players:
        if score != current_score:
            current_rank = rank
        rank_groups[current_rank].append(pid)
        current_score = score
        rank += 1

    # ✅ ウマ設定
    uma_table = {
        2: setting.uma_2,
        3: setting.uma_3,
        4: setting.uma_4,
    }

    player_uma = {}
    first_place_ids = rank_groups[1]
    all_ranks = sorted(rank_groups.keys())
    used_ranks = set()

    # ✅ ウマ分配処理
    for rank in all_ranks:
        if rank == 1:
            continue
        pids = rank_groups[rank]
        num = len(pids)

        # 使用可能なウマを順位から順に拾って合計
        uma_sum = 0
        collected = 0
        for r in range(rank, 5):  # 2位〜4位まで
            if r in used_ranks:
                continue
            if r in uma_table:
                uma_sum += uma_table[r]
                used_ranks.add(r)
                collected += 1
            if collected >= num:
                break

        # 分配
        if tie_rule == 'split':
            share = uma_sum / num if num else 0
            for pid in pids:
                player_uma[pid] = share
        elif tie_rule == 'prefer_early':
            for i, pid in enumerate(pids):
                uma_rank = rank + i
                player_uma[pid] = uma_table.get(uma_rank, 0)
        else:
            share = uma_sum / num if num else 0
            for pid in pids:
                player_uma[pid] = share

    # ✅ 他プレイヤーの合計点算出（点差 + ウマ）
    others_total = sum(
        point_diffs[pid] + player_uma.get(pid, 0)
        for pid in raw_scores
        if pid not in first_place_ids
    )

    # ✅ 1位の調整: 残りの合計を打ち消すように調整
    correction = -others_total / len(first_place_ids)
    for pid in first_place_ids:
        player_uma[pid] = correction - point_diffs[pid]

    # ✅ 最終結果 = 点差 + ウマ
    return {
        pid: round(point_diffs[pid] + player_uma[pid], 1)
        for pid in raw_scores
    }
