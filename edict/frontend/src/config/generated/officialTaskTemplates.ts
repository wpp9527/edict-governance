// Stage10 generated canonical official task templates
export type OfficialTaskTemplate = {
  id: string;
  title: string;
  owners: string[];
  tags: string[];
  desc: string;
};

export const OFFICIAL_TASK_TEMPLATES: OfficialTaskTemplate[] = [
  {
    "id": "long-input-preprocess",
    "title": "大文件/长文档预处理",
    "owners": [
      "taixuesi",
      "zhongshu"
    ],
    "tags": [
      "资料分析",
      "预处理"
    ],
    "desc": "拆分、去重、提纲化，为规划链减压"
  },
  {
    "id": "risk-supply-chain-audit",
    "title": "外部脚本/技能供应链审查",
    "owners": [
      "jinyiwei",
      "menxia",
      "xingbu"
    ],
    "tags": [
      "工程开发",
      "审计"
    ],
    "desc": "审查插件、脚本、技能与权限边界"
  },
  {
    "id": "budget-model-gating",
    "title": "高成本模型预算评估",
    "owners": [
      "duzhisi",
      "hubu",
      "zhongshu"
    ],
    "tags": [
      "数据分析",
      "预算"
    ],
    "desc": "对远程模型、高成本调用进行预算与熔断评估"
  },
  {
    "id": "intel-radar",
    "title": "平台活动/资讯雷达",
    "owners": [
      "qingbaoshi",
      "zaochao"
    ],
    "tags": [
      "日常办公",
      "情报"
    ],
    "desc": "低成本追踪外部活动、平台变化与高价值线索"
  },
  {
    "id": "skill-template-distill",
    "title": "经验沉淀为技能模板",
    "owners": [
      "jinengdaoshi",
      "gongbu",
      "shangshu"
    ],
    "tags": [
      "内容创作",
      "工程开发"
    ],
    "desc": "把修复经验转成技能、模板、规范"
  }
] as OfficialTaskTemplate[];
