#!/bin/bash
# 推送天下要闻到 OpenClaw 会话

# Support environment variable override for data directory
if [ -n "$EDICT_TASK_DATA_DIR" ]; then
  DATA_DIR="$EDICT_TASK_DATA_DIR"
elif [ -n "$OPENCLAW_HOME" ]; then
  DATA_DIR="$OPENCLAW_HOME/workspace-main/data"
else
  DATA_DIR="$HOME/.openclaw/workspace-main/data"
fi
BRIEF_FILE="$DATA_DIR/morning_brief.json"
CONFIG_FILE="$DATA_DIR/morning_brief_config.json"

# 检查配置
if ! command -v jq &> /dev/null; then
    echo "jq not found" >&2
    exit 1
fi

# 读取配置
NOTIFICATION=$(jq -r '.notification // empty' "$CONFIG_FILE" 2>/dev/null)
if [ -z "$NOTIFICATION" ] || [ "$NOTIFICATION" = "null" ]; then
    echo "No notification config" >&2
    exit 0
fi

ENABLED=$(jq -r '.notification.enabled // true' "$CONFIG_FILE")
if [ "$ENABLED" != "true" ]; then
    echo "Notification disabled" >&2
    exit 0
fi

# 读取要闻
DATE=$(jq -r '.date // ""' "$BRIEF_FILE" 2>/dev/null)
if [ -z "$DATE" ] || [ "$DATE" = "null" ]; then
    echo "No morning brief data" >&2
    exit 0
fi

# 格式化日期
if [ ${#DATE} -eq 8 ]; then
    DATE_FMT="${DATE:0:4}年${DATE:4:2}月${DATE:6:2}日"
else
    DATE_FMT="$DATE"
fi

# 统计新闻
TOTAL=$(jq '[.categories // {} | .[] | length] | add // 0' "$BRIEF_FILE")
if [ "$TOTAL" -eq 0 ]; then
    echo "No news items" >&2
    exit 0
fi

# 构建消息
MESSAGE="📰 **天下要闻 · $DATE_FMT**\n\n"
MESSAGE+="共 **$TOTAL** 条要闻已更新\n\n"

# 添加分类统计
CATEGORIES=$(jq -r '.categories // {} | keys[]' "$BRIEF_FILE" 2>/dev/null)
for CAT in $CATEGORIES; do
    COUNT=$(jq -r ".categories[\"$CAT\"] | length" "$BRIEF_FILE")
    if [ "$COUNT" -gt 0 ]; then
        MESSAGE+="• $CAT: $COUNT 条\n"
    fi
done

MESSAGE+="\n查看详情: http://kb.19930901.xyz:5000"

# 写入推送队列（由心跳处理）
QUEUE_FILE="$DATA_DIR/pending_push.json"
cat > "$QUEUE_FILE" << JSON
{
    "message": "$MESSAGE",
    "target": "agent:main:main",
    "created_at": "$(date -Iseconds)"
}
JSON

echo "Push message queued: $QUEUE_FILE"
