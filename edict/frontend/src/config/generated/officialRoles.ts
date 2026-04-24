// Stage10 generated canonical official registry
export type OfficialRole = {
  id: string;
  label: string;
  emoji: string;
  role: string;
  rank: string;
  group: 'core' | 'ministry' | 'support' | 'extended';
  org: string;
};

export const OFFICIAL_ROLES: OfficialRole[] = [
  {
    "id": "taizi",
    "label": "太子",
    "emoji": "👑",
    "role": "太子",
    "rank": "储君",
    "group": "core",
    "org": "太子"
  },
  {
    "id": "zhongshu",
    "label": "中书省",
    "emoji": "📜",
    "role": "中书令",
    "rank": "正一品",
    "group": "core",
    "org": "中书省"
  },
  {
    "id": "menxia",
    "label": "门下省",
    "emoji": "🔎",
    "role": "侍中",
    "rank": "正一品",
    "group": "core",
    "org": "门下省"
  },
  {
    "id": "shangshu",
    "label": "尚书省",
    "emoji": "📕",
    "role": "尚书令",
    "rank": "正一品",
    "group": "core",
    "org": "尚书省"
  },
  {
    "id": "hubu",
    "label": "户部",
    "emoji": "💰",
    "role": "户部尚书",
    "rank": "正二品",
    "group": "ministry",
    "org": "户部"
  },
  {
    "id": "libu",
    "label": "礼部",
    "emoji": "🧾",
    "role": "礼部尚书",
    "rank": "正二品",
    "group": "ministry",
    "org": "礼部"
  },
  {
    "id": "bingbu",
    "label": "兵部",
    "emoji": "⚔️",
    "role": "兵部尚书",
    "rank": "正二品",
    "group": "ministry",
    "org": "兵部"
  },
  {
    "id": "xingbu",
    "label": "刑部",
    "emoji": "⚖️",
    "role": "刑部尚书",
    "rank": "正二品",
    "group": "ministry",
    "org": "刑部"
  },
  {
    "id": "gongbu",
    "label": "工部",
    "emoji": "🔧",
    "role": "工部尚书",
    "rank": "正二品",
    "group": "ministry",
    "org": "工部"
  },
  {
    "id": "libu_hr",
    "label": "吏部",
    "emoji": "📘",
    "role": "吏部尚书",
    "rank": "正二品",
    "group": "ministry",
    "org": "吏部"
  },
  {
    "id": "zaochao",
    "label": "钦天监",
    "emoji": "🛰️",
    "role": "早朝官",
    "rank": "正三品",
    "group": "support",
    "org": "钦天监"
  },
  {
    "id": "duzhisi",
    "label": "度支司",
    "emoji": "🪙",
    "role": "度支使",
    "rank": "从二品",
    "group": "extended",
    "org": "度支司"
  },
  {
    "id": "taixuesi",
    "label": "太学寺",
    "emoji": "📚",
    "role": "太学祭酒",
    "rank": "从二品",
    "group": "extended",
    "org": "太学寺"
  },
  {
    "id": "jinyiwei",
    "label": "锦衣卫",
    "emoji": "🛡️",
    "role": "锦衣卫指挥使",
    "rank": "正三品",
    "group": "extended",
    "org": "锦衣卫"
  },
  {
    "id": "qingbaoshi",
    "label": "情报使",
    "emoji": "📡",
    "role": "情报使",
    "rank": "从三品",
    "group": "extended",
    "org": "情报使"
  },
  {
    "id": "jinengdaoshi",
    "label": "技能导师",
    "emoji": "🧭",
    "role": "技能导师",
    "rank": "从三品",
    "group": "extended",
    "org": "技能导师"
  }
] as OfficialRole[];

export const OFFICIAL_ROLE_IDS = OFFICIAL_ROLES.map(x => x.id);
export const OFFICIAL_ROLE_ID_SET = new Set(OFFICIAL_ROLE_IDS);
export const OFFICIAL_COUNT = OFFICIAL_ROLES.length;

// main stays runtime-only, not part of official semantic pages
export const RUNTIME_ONLY_AGENT_IDS = ['main'];
