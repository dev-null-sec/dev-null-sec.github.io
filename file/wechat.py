#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业微信告警脚本
"""

import requests
import sys
import json

# 移除is_markdown函数，不再检测消息格式

def send_wechat_alert(webhook_url, message):
    """
    发送企业微信告警。
    直接以text类型发送原始数据，避免Markdown解析导致的乱码问题。
    """
    # 始终使用text类型发送消息
    msg_type = 'text'
    payload = {
        "msgtype": msg_type,
        "text": {
            "content": message
        }
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result.get("errcode") == 0:
            print("消息发送成功")
        else:
            print(f"消息发送失败: {result.get('errmsg')}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"发送消息时发生未知错误: {e}")


if __name__ == "__main__":
    webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=cf367029-1ab1-462c-8e4a-944b4547df94"

    if not webhook_url:
        print("错误: 请设置WECOM_WEBHOOK_URL")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("用法: python3 wechat.py \'你的消息\'")
        sys.exit(1)

    message_content = sys.argv[1]
    # 不再使用unicode_escape解码，直接使用原始数据
    # message_content = codecs.decode(message_content, 'unicode_escape')
    # --------------------------

    send_wechat_alert(webhook_url, message_content)