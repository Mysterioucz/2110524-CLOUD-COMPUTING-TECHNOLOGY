import boto3
import time
from boto3.dynamodb.conditions import Key
import os

class DynamoDBMemory:
    def __init__(self, table_name: str):
        # When running in AWS Lambda, boto3 automatically uses the Lambda's IAM role.
        # Make sure the Lambda Execution Role has dynamodb:PutItem and dynamodb:Query permissions!
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        
    def save_message(self, user_id: str, role: str, content: str) -> int:
        """
        บันทึกข้อความ 1 ชิ้นลง DynamoDB
        role ต้องเป็น 'user' หรือ 'assistant'
        คืนค่า timestamp ที่ใช้บันทึก
        """
        timestamp = int(time.time() * 1000)
        try:
            self.table.put_item(
                Item={
                    'user_id': user_id,       # Partition key
                    'timestamp': timestamp,   # Sort key
                    'role': role,
                    'content': content
                }
            )
            return timestamp
        except Exception as e:
            print(f"Error saving to DynamoDB: {e}")
            return timestamp
        
    def get_history(self, user_id: str, limit: int = 50, since_timestamp: int = 0) -> tuple:
        """
        ดึงประวัติการสนทนาที่ใหม่กว่า since_timestamp
        เปลี่ยน format ให้อยู่ในรูปแบบที่ Bedrock (Claude) ต้องการรับ
        คืนค่า (history_for_bedrock, list_of_timestamps)
        """
        try:
            # ใช้ > since_timestamp เพื่อดึงเฉพาะข้อความชั่วคราวที่ยังไม่ถูกสรุป
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id) & Key('timestamp').gt(since_timestamp),
                ScanIndexForward=False, # ดึงจากเวลาล่าสุดก่อน
                Limit=limit
            )
            
            items = response.get('Items', [])
            # Query ScanIndexForward=False จะได้ ใหม่สุด -> เก่าสุด
            # เวลาส่งเข้า LLM ต้องเรียงจาก เก่าสุด -> ใหม่สุด (Chronological)
            items.reverse()
            
            history = []
            timestamps = []
            for item in items:
                history.append({
                    "role": 'user' if item['role'] == 'user' else 'assistant',
                    "content": [{"text": item['content']}]
                })
                timestamps.append(int(item['timestamp']))
                
            return history, timestamps
        except Exception as e:
            print(f"Error querying DynamoDB: {e}")
            return [], []

    def get_summary(self, user_id: str) -> tuple:
        """
        ดึงข้อมูล Summary ของ User ออกมา 
        คืนค่า (summary_text, last_summarized_timestamp)
        """
        try:
            response = self.table.get_item(
                Key={
                    'user_id': user_id,
                    'timestamp': 0
                }
            )
            item = response.get('Item')
            if item:
                return item.get('content', ''), int(item.get('last_summarized_timestamp', 0))
            return "", 0
        except Exception as e:
            print(f"Error getting summary: {e}")
            return "", 0

    def save_summary(self, user_id: str, summary_text: str, last_summarized_timestamp: int = 0):
        """
        บันทึก Summary ลง DynamoDB พร้อมกับประทับตรา checkpoint timestamp ล่าสุด
        """
        try:
            self.table.put_item(
                Item={
                    'user_id': user_id,
                    'timestamp': 0,
                    'role': 'summary',
                    'content': summary_text,
                    'last_summarized_timestamp': last_summarized_timestamp
                }
            )
        except Exception as e:
            print(f"Error saving summary: {e}")

    def delete_messages(self, user_id: str, timestamps: list):
        """
        ลบข้อความเก่าๆ ที่นำไปสรุปแล้วทิ้ง เพื่อเคลียร์พื้นที่
        """
        for ts in timestamps:
            try:
                self.table.delete_item(
                    Key={
                        'user_id': user_id,
                        'timestamp': ts
                    }
                )
            except Exception as e:
                print(f"Error deleting message {ts}: {e}")
