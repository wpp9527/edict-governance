import { OFFICIAL_ROLES, OFFICIAL_ROLE_ID_SET } from './officialRoles';

export const OFFICIAL_ROLE_LABEL_MAP: Record<string, string> =
  Object.fromEntries(OFFICIAL_ROLES.map(r => [r.id, r.label]));

export const OFFICIAL_ROLE_EMOJI_MAP: Record<string, string> =
  Object.fromEntries(OFFICIAL_ROLES.map(r => [r.id, r.emoji]));

export const OFFICIAL_ROLE_ROLE_MAP: Record<string, string> =
  Object.fromEntries(OFFICIAL_ROLES.map(r => [r.id, r.role]));

export const OFFICIAL_ROLE_COLOR_MAP: Record<string, string> = {
  taizi: '#e8a040',
  zhongshu: '#a07aff',
  menxia: '#6a9eff',
  shangshu: '#6aef9a',
  libu: '#f5c842',
  hubu: '#ff9a6a',
  bingbu: '#ff5270',
  xingbu: '#cc4444',
  gongbu: '#44aaff',
  libu_hr: '#9b59b6',
  zaochao: '#4cc9f0',
  duzhisi: '#d4af37',
  taixuesi: '#7cc576',
  jinyiwei: '#6c7ae0',
  qingbaoshi: '#22c55e',
  jinengdaoshi: '#f59e0b',
};

export function filterSemanticAgents<T extends { id: string }>(agents: T[]): T[] {
  return (agents || []).filter(a => OFFICIAL_ROLE_ID_SET.has(a.id));
}
