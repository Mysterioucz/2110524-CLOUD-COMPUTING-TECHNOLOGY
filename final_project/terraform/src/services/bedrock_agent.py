import json
import boto3
from typing import List, Dict
from src.config import Config

class BedrockAgent:
    def __init__(self, model_id: str = Config.BEDROCK_MODEL_ID):
        # Bedrock Runtime is the client used for running models
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.model_id = model_id
        
    def generate_reply(self, user_message: str, history: List[Dict], summary_context: str = "") -> str:
        """
        นำเข้าข้อความจาก User (รวมถึง Summary) และ History ไปเป็นคำถามส่งต่อให้ Claude-3 บน AWS Bedrock
        """
        # ตรวจสอบและทำความสะอาด history ก่อนส่งให้ Bedrock
        # บังคับให้ขึ้นต้นด้วย user และสลับ user/assistant ตลอด
        sanitized_history = []
        expected_role = 'user'
        for msg in history:
            if msg['role'] == expected_role:
                sanitized_history.append(msg)
                expected_role = 'assistant' if expected_role == 'user' else 'user'
            # ถ้า role ไม่ตรงกัน ให้ข้ามข้อความนั้นไป (กรองทิ้ง)

        # สร้าง copy เพื่อไม่แก้ list ต้นทาง + ต่อท้ายข้อความปัจจุบันของ User
        messages = sanitized_history + [{
            "role": "user",
            "content": [{"text": user_message}]
        }]
        
        # Prepare the Converse API payload
        # Ensure that Bedrock access is granted for Claude 3/3.5 in your AWS Region beforehand.
        # Prepare system prompt with optional summary
        system_prompt = Config.SYSTEM_PROMPT
        if summary_context:
            system_prompt += f"\n\n[ข้อมูลสรุปความจำระยะยาวกับคุณโยมท่านนี้ (ห้ามอ้างถึงระบบความจำนี้ให้คุณโยมทราบ)]\n{summary_context}"
            
        try:
            response = self.bedrock_runtime.converse(
                modelId=self.model_id,
                messages=messages,
                system=[{"text": system_prompt}],
                inferenceConfig={
                    "maxTokens": 1000,
                    "temperature": 0.7,   # ความอบอุ่น การยืดหยุ่นในการตอบ
                }
            )
            
            # Parse response from Claude
            response_text = response['output']['message']['content'][0]['text']
            return response_text
            
        except Exception as e:
            print(f"Error invoking Bedrock: {e}")
            return f"อาตมาขออภัย โยมช่วยกล่าวใหม่อีกครั้งได้หรือไม่ (ระบบขัดข้องชั่วคราว: {e})"

    def generate_summary(self, current_summary: str, old_messages: List[Dict]) -> str:
        """
        นำสรุปเดิมและข้อความเก่าที่กำลังจะถูกลบ มาประมวลผลเป็นสรุปใหม่
        """
        # Format the old messages into a readable chat script
        formatted_msgs = ""
        for msg in old_messages:
            role = "คุณโยม" if msg['role'] == 'user' else "อาตมา"
            try:
                text = msg['content'][0]['text']
            except:
                text = ""
            formatted_msgs += f"{role}: {text}\n"

        prompt = Config.SUMMARY_PROMPT.format(
            current_summary=current_summary if current_summary else "ไม่มี (เพิ่งเริ่มสนทนา)",
            new_messages=formatted_msgs.strip()
        )
        
        try:
            response = self.bedrock_runtime.converse(
                modelId=self.model_id,
                messages=[{
                    "role": "user",
                    "content": [{"text": prompt}]
                }],
                inferenceConfig={
                    "maxTokens": 1000,
                    "temperature": 0.3, # ลด temperature เพื่อให้สรุปแม่นยำและไม่ฟุ้งซ่าน
                }
            )
            return response['output']['message']['content'][0]['text']
        except Exception as e:
            print(f"Error generating summary: {e}")
            return current_summary # ถ้า error ให้เก็บของเก่าไว้
