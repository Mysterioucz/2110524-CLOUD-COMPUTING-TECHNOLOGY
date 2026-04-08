import os
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

class LineService:
    def __init__(self, channel_secret: str, channel_access_token: str):
        self.line_bot_api = LineBotApi(channel_access_token)
        self.parser = WebhookParser(channel_secret)
        
    def parse_events(self, body: str, signature: str) -> list:
        """
        ตรวจสอบ Line Signature ป้องกันการส่ง Request ปลอม
        และแยก Event เป็น List (เนื่องจาก Line อาจส่งมาพร้อมกันหลายอัน)
        """
        try:
            events = self.parser.parse(body, signature)
            return events
        except InvalidSignatureError:
            print("Invalid signature. Please check your channel access token/channel secret.")
            raise ValueError("Invalid Signature")
            
    def reply_message(self, reply_token: str, message: str):
        """
        ตอบกลับไปหาผู้ใช้ผ่าน LINE Reply API (ฟรี)
        """
        try:
            self.line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=message)
            )
        except Exception as e:
            print(f"Failed to send LINE reply: {e}")
