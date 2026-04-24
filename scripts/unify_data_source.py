#!/usr/bin/env python3
"""
统一数据源修复脚本
修复所有使用 repo/data 的脚本，改为使用 canonical 数据源
"""

import pathlib
import re

SCRIPTS_TO_FIX = [
    'scripts/sync_agent_config.py',
    'scripts/sync_officials_stats.py',
    'scripts/fetch_morning_news.py',
    'scripts/apply_model_changes.py',
    'scripts/sync_from_openclaw_runtime.py',
]

FIX_PATTERN = r'''
# 原始模式
DATA = BASE / 'data'
或
DATA = pathlib.Path(__file__).resolve().parent.parent / 'data'

# 修复后
def get_canonical_data_dir():
    """获取 canonical 数据目录（与 dashboard 一致）"""
    import os
    from pathlib import Path
    
    # 优先级 1: 环境变量
    env_dir = os.environ.get('EDICT_TASK_DATA_DIR', '').strip()
    if env_dir:
        return Path(env_dir).expanduser()
    
    # 优先级 2: canonical 路径
    canonical = Path.home() / '.openclaw' / 'workspace-main' / 'data'
    if canonical.is_dir():
        return canonical
    
    # 优先级 3: 回退到 repo/data
    return BASE / 'data'

DATA = get_canonical_data_dir()
'''

repo_root = pathlib.Path('/opt/fnos-media/services/edict-localized/repo')

print("统一数据源修复")
print("=" * 70)

for script_rel in SCRIPTS_TO_FIX:
    script_path = repo_root / script_rel
    if not script_path.exists():
        print(f"\n✗ {script_rel}: 文件不存在")
        continue
    
    content = script_path.read_text(encoding='utf-8')
    
    # 检查是否已经有 get_canonical_data_dir
    if 'get_canonical_data_dir' in content:
        print(f"\n✓ {script_rel}: 已修复")
        continue
    
    # 查找 DATA 定义
    patterns = [
        (r"^DATA\s*=\s*BASE\s*/\s*['\"]data['\"]", 'DATA = BASE / "data"'),
        (r"^DATA\s*=\s*pathlib\.Path\(__file__\)\.resolve\(\)\.parent\.parent\s*/\s*['\"]data['\"]", 
         'DATA = pathlib.Path(__file__).resolve().parent.parent / "data"'),
    ]
    
    modified = False
    for pattern, old_text in patterns:
        if re.search(pattern, content, re.MULTILINE):
            # 插入函数定义
            func_def = '''
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

'''
            
            # 在 import 后插入函数
            import_end = content.find('\n\n', content.find('import'))
            if import_end > 0:
                content = content[:import_end] + '\n' + func_def + content[import_end:]
            else:
                content = func_def + content
            
            # 替换 DATA 定义
            content = re.sub(pattern, 'DATA = get_canonical_data_dir()', content, flags=re.MULTILINE)
            modified = True
            break
    
    if modified:
        script_path.write_text(content, encoding='utf-8')
        print(f"\n✓ {script_rel}: 已修复")
    else:
        print(f"\n⊘ {script_rel}: 未找到 DATA 定义或已修复")

print("\n" + "=" * 70)
print("修复完成")
print("=" * 70)
