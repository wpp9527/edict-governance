#!/usr/bin/env python3
import datetime
import logging
import pathlib

from file_lock import atomic_json_read, atomic_json_write
from utils import read_json


def get_canonical_data_dir():
    """获取 canonical 数据目录（与 dashboard 一致）"""
    import os
    from pathlib import Path

    env_dir = os.environ.get('EDICT_TASK_DATA_DIR', '').strip()
    if env_dir:
        return Path(env_dir).expanduser()

    canonical = Path.home() / '.openclaw' / 'workspace-main' / 'data'
    if canonical.is_dir():
        return canonical

    return BASE / 'data'


log = logging.getLogger('refresh')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s', datefmt='%H:%M:%S')

BASE = pathlib.Path(__file__).resolve().parent.parent
DATA = get_canonical_data_dir()


def output_meta(path):
    p = pathlib.Path(path)
    if not p.exists():
        return {"exists": False, "lastModified": None}
    ts = datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    return {"exists": True, "lastModified": ts}


def build_heartbeat(task, now_ts):
    if task.get('state') not in ('Doing', 'Assigned', 'Review'):
        return None

    updated_raw = task.get('updatedAt') or task.get('sourceMeta', {}).get('updatedAt')
    age_sec = None
    if updated_raw:
        try:
            if isinstance(updated_raw, (int, float)):
                updated_dt = datetime.datetime.fromtimestamp(updated_raw / 1000, tz=datetime.timezone.utc)
            else:
                updated_dt = datetime.datetime.fromisoformat(str(updated_raw).replace('Z', '+00:00'))
            age_sec = (now_ts - updated_dt).total_seconds()
        except Exception:
            age_sec = None

    if age_sec is None:
        return {'status': 'unknown', 'label': '⚪ 未知', 'ageSec': None}
    if age_sec < 300:
        return {'status': 'active', 'label': f'🟢 活跃 {int(age_sec // 60)}分钟前', 'ageSec': int(age_sec)}
    if age_sec < 900:
        return {'status': 'warn', 'label': f'🟡 可能停滞 {int(age_sec // 60)}分钟前', 'ageSec': int(age_sec)}
    return {'status': 'stalled', 'label': f'🔴 已停滞 {int(age_sec // 60)}分钟', 'ageSec': int(age_sec)}


def main():
    DATA.mkdir(parents=True, exist_ok=True)

    officials_data = read_json(DATA / 'officials_stats.json', {})
    officials = officials_data.get('officials', []) if isinstance(officials_data, dict) else officials_data

    tasks = atomic_json_read(DATA / 'tasks_source.json', [])
    if not tasks:
        tasks = read_json(DATA / 'tasks.json', [])
    if not isinstance(tasks, list):
        tasks = []

    sync_status = read_json(DATA / 'sync_status.json', {})

    org_map = {}
    for official in officials or []:
        label = official.get('label', official.get('name', '')) if isinstance(official, dict) else ''
        if label:
            org_map[label] = label

    now_ts = datetime.datetime.now(datetime.timezone.utc)
    for task in tasks:
        if not isinstance(task, dict):
            continue
        task['org'] = task.get('org') or org_map.get(task.get('official', ''), '')
        task['outputMeta'] = output_meta(task.get('output', ''))
        task['heartbeat'] = build_heartbeat(task, now_ts)

    today_str = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')

    def _is_today_done(task):
        if task.get('state') != 'Done':
            return False
        updated_at = task.get('updatedAt', '')
        if isinstance(updated_at, str) and updated_at[:10] == today_str:
            return True
        last_modified = task.get('outputMeta', {}).get('lastModified', '')
        return isinstance(last_modified, str) and last_modified[:10] == today_str

    today_done = sum(1 for task in tasks if isinstance(task, dict) and _is_today_done(task))
    total_done = sum(1 for task in tasks if isinstance(task, dict) and task.get('state') == 'Done')
    in_progress = sum(1 for task in tasks if isinstance(task, dict) and task.get('state') in ['Doing', 'Review', 'Next', 'Blocked'])
    blocked = sum(1 for task in tasks if isinstance(task, dict) and task.get('state') == 'Blocked')

    history = []
    for task in tasks:
        if not isinstance(task, dict) or task.get('state') != 'Done':
            continue
        last_modified = task.get('outputMeta', {}).get('lastModified')
        history.append({
            'at': last_modified or '未知',
            'official': task.get('official'),
            'task': task.get('title'),
            'out': task.get('output'),
            'qa': '通过' if task.get('outputMeta', {}).get('exists') else '待补成果'
        })

    payload = {
        'generatedAt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'taskSource': 'tasks_source.json' if (DATA / 'tasks_source.json').exists() else 'tasks.json',
        'officials': officials if isinstance(officials, list) else [],
        'tasks': tasks,
        'history': history,
        'metrics': {
            'officialCount': len(officials) if isinstance(officials, list) else 0,
            'todayDone': today_done,
            'totalDone': total_done,
            'inProgress': in_progress,
            'blocked': blocked,
        },
        'syncStatus': sync_status if isinstance(sync_status, dict) else {},
        'health': {
            'syncOk': bool((sync_status or {}).get('ok', False)) if isinstance(sync_status, dict) else False,
            'syncLatencyMs': (sync_status or {}).get('durationMs') if isinstance(sync_status, dict) else None,
            'missingFieldCount': len((sync_status or {}).get('missingFields', {})) if isinstance(sync_status, dict) else 0,
        }
    }

    atomic_json_write(DATA / 'live_status.json', payload)
    log.info(f'updated live_status.json ({len(tasks)} tasks)')


if __name__ == '__main__':
    main()
