"""消息推送渠道模块"""
import subprocess
import urllib.request
import urllib.error
import json
import logging
import time

log = logging.getLogger('channels')


class BaseChannel:
    """推送渠道基类"""
    key: str = ''
    label: str = ''
    
    @classmethod
    def validate_webhook(cls, url: str) -> bool:
        return bool(url)
    
    @classmethod
    def send(cls, webhook: str, title: str, content: str, url: str = '') -> bool:
        raise NotImplementedError


class FeishuAppChannel(BaseChannel):
    """飞书应用推送（使用 App ID + App Secret）"""
    key = 'feishu'
    label = '飞书'
    
    # 飞书 API 端点
    TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    MESSAGE_URL = "https://open.feishu.cn/open-apis/im/v1/messages"
    
    @classmethod
    def validate_webhook(cls, url: str) -> bool:
        # webhook 格式: app_id:app_secret:receive_id 或 app_id:app_secret
        return ':' in url
    
    @classmethod
    def get_tenant_access_token(cls, app_id: str, app_secret: str) -> str:
        """获取 tenant_access_token"""
        payload = {
            "app_id": app_id,
            "app_secret": app_secret
        }
        try:
            req = urllib.request.Request(
                cls.TOKEN_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                if result.get('code') == 0:
                    return result.get('tenant_access_token', '')
        except Exception as e:
            log.error(f'获取飞书 token 失败: {e}')
        return ''
    
    @classmethod
    def send(cls, webhook: str, title: str, content: str, url: str = '') -> bool:
        """发送消息到飞书
        
        webhook 格式: app_id:app_secret:receive_id
        receive_id 可以是:
        - ou_xxx (用户 open_id，发送私聊)
        - oc_xxx (群 chat_id，发送群消息)
        - email (用户邮箱)
        """
        parts = webhook.split(':')
        if len(parts) < 2:
            log.error('飞书 webhook 格式错误，应为 app_id:app_secret[:receive_id]')
            return False
        
        app_id = parts[0]
        app_secret = parts[1]
        receive_id = parts[2] if len(parts) > 2 else None
        
        if not receive_id:
            log.error('飞书 webhook 缺少 receive_id，格式: app_id:app_secret:receive_id')
            return False
        
        # 获取 token
        token = cls.get_tenant_access_token(app_id, app_secret)
        if not token:
            log.error('获取飞书 token 失败')
            return False
        
        # 构建消息内容
        message_content = f"**{title}**\n\n{content}"
        if url:
            message_content += f"\n\n[查看详情]({url})"
        
        # 发送消息
        payload = {
            "receive_id_type": "open_id",
            "content": json.dumps({
                "zh_cn": {
                    "title": title,
                    "content": [[{"tag": "text", "text": content}]]
                }
            })
        }
        
        # 根据 receive_id 前缀判断类型
        if receive_id.startswith('oc_'):
            payload["receive_id_type"] = "chat_id"
        elif '@' in receive_id:
            payload["receive_id_type"] = "email"
        # open_id 默认
        
        try:
            req_url = f"{cls.MESSAGE_URL}?receive_id_type={payload['receive_id_type']}&receive_id={receive_id}"
            req = urllib.request.Request(
                req_url,
                data=json.dumps({"content": payload["content"]}).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                if result.get('code') == 0:
                    log.info(f'飞书推送成功')
                    return True
                else:
                    log.error(f'飞书推送失败: {result}')
        except Exception as e:
            log.error(f'飞书推送失败: {e}')
        return False


class FeishuWebhookChannel(BaseChannel):
    """飞书群机器人 Webhook 推送"""
    key = 'feishu_webhook'
    label = '飞书群机器人'
    
    @classmethod
    def validate_webhook(cls, url: str) -> bool:
        return url.startswith('https://open.feishu.cn/open-apis/bot/v2/hook/')
    
    @classmethod
    def send(cls, webhook: str, title: str, content: str, url: str = '') -> bool:
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": title},
                    "template": "blue"
                },
                "elements": [
                    {"tag": "markdown", "content": content},
                ]
            }
        }
        if url:
            payload["card"]["elements"].append({
                "tag": "action",
                "actions": [
                    {"tag": "button", "text": {"tag": "plain_text", "content": "查看详情"}, "url": url, "type": "primary"}
                ]
            })
        try:
            req = urllib.request.Request(
                webhook,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result.get('code') == 0
        except Exception as e:
            log.error(f'飞书推送失败: {e}')
            return False


class OpenClawChannel(BaseChannel):
    """OpenClaw 会话推送（推送到太子窗口）"""
    key = 'openclaw'
    label = 'OpenClaw'
    
    @classmethod
    def validate_webhook(cls, url: str) -> bool:
        return bool(url)
    
    @classmethod
    def send(cls, webhook: str, title: str, content: str, url: str = '') -> bool:
        message = f"**{title}**\n\n{content}"
        if url:
            message += f"\n\n[查看详情]({url})"
        
        try:
            result = subprocess.run(
                ['openclaw', 'system', 'event', '--text', message, '--mode', 'now'],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0 and 'ok' in result.stdout.lower()
        except Exception as e:
            log.error(f'OpenClaw 推送失败: {e}')
            return False


# 注册所有渠道
CHANNELS = {
    'feishu': FeishuAppChannel,
    'feishu_webhook': FeishuWebhookChannel,
    'openclaw': OpenClawChannel,
}


def get_channel(key: str):
    """获取推送渠道类"""
    return CHANNELS.get(key)


def get_channel_info():
    """获取所有渠道信息"""
    return {k: {'key': k, 'label': v.label} for k, v in CHANNELS.items()}
