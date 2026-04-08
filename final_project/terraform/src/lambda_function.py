import json
import os
import sys

# ให้ Python สามารถ Import หาโฟลเดอร์ src เจอได้เมื่อรันซ้ายบน AWS Lambda
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.services.line_service import LineService
from src.services.dynamodb_memory import DynamoDBMemory
from src.services.bedrock_agent import BedrockAgent
from linebot.models import MessageEvent, TextMessage

# Cold Start Initialization
# ทำตรงนี้เพื่อให้เชื่อมต่อ Base Service ค้างไว้ใน Ram ของ AWS (ลด Latency ในการรันครั้งถัดไป)
line_service = LineService(Config.LINE_CHANNEL_SECRET, Config.LINE_CHANNEL_ACCESS_TOKEN)
memory_service = DynamoDBMemory(Config.DYNAMODB_TABLE_NAME)
bedrock_agent = BedrockAgent(Config.BEDROCK_MODEL_ID)

def lambda_handler(event, context):
    """
    ประตูรับ Request (Entry Point) ของ AWS Lambda
    Event นี้ถูกส่งมาจาก AWS API Gateway เวลามีการขยับของ Webhook
    """
    # 1. ตรวจสอบรายละเอียดของ Webhook ที่ LINE ส่งมา
    body = event.get('body', "")
    headers = event.get('headers', {})
    
    # ดึง Signature (มักจะเป็น X-Line-Signature แล้วแต่การตั้งค่า API Gateway)
    signature = headers.get('x-line-signature') or headers.get('X-Line-Signature')
    
    if not body or not signature:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing body or signature')
        }
        
    # 2. แกะไข Event ผ่าน LINE Parser
    try:
        events = line_service.parse_events(body, signature)
    except ValueError:
        return {
            'statusCode': 403,
            'body': json.dumps('Invalid Signature Error')
        }
        
    # 3. ลุยประมวลผลทีละ Event แบบ Asynchronous (เนื่องจาก Python Lambda พื้นฐานรันเป็นรอบ)
    for line_event in events:
        if not isinstance(line_event, MessageEvent) or not isinstance(line_event.message, TextMessage):
            continue # ถ้าไม่ได้ส่ง Message หาพระ หรือไม่ได้พิมพ์ Text ให้ข้ามไป
            
        user_id = line_event.source.user_id
        user_text = line_event.message.text
        reply_token = line_event.reply_token
        
        # 3.1 บันทึกสิ่งที่โยมถาม (The Soul)
        memory_service.save_message(user_id=user_id, role="user", content=user_text)
        
        # 3.2 ระลึกความจำ และดึง Summary พร้อม Checkpoint
        summary_context, last_summarized_timestamp = memory_service.get_summary(user_id=user_id)
        # ดึงประวัติแบบจุใจ (เผื่อไว้ 20) โดยดึงเฉพาะที่ใหม่กว่า Checkpoint
        history, _ = memory_service.get_history(user_id=user_id, limit=20, since_timestamp=last_summarized_timestamp)
        
        # ป้องกันการส่ง User Message เบิ้ลซ้ำ (เพราะ generate_reply จะทำการ append ให้ในตัว)
        history_for_bedrock = history[:-1] if history and history[-1]['role'] == 'user' else history
        
        # 3.3 เอาประวัติ + คำถาม โยนเข้าสมอง (Claude Haiku บน Bedrock) ให้คิดคำตอบรสพระธรรม (The Brain)
        bot_response = bedrock_agent.generate_reply(
            user_message=user_text, 
            history=history_for_bedrock,
            summary_context=summary_context
        )
        
        # 3.4 ส่งคำตอบพระสงฆ์กลับไปให้โยมได้อ่านผ่านปากของบอท (The Mouth)
        line_service.reply_message(reply_token, bot_response)
        
        # 3.5 บันทึกว่าพระเทศน์ตอบว่าอะไร 
        memory_service.save_message(user_id=user_id, role="assistant", content=bot_response)

        # 3.6 Long-Term Memory Evaluation (Synchronous / Sliding Checkpoint)
        # Lambda freeze ทันทีที่ return → ต้องรันก่อน return เสมอ
        full_history, full_timestamps = memory_service.get_history(
            user_id=user_id, since_timestamp=last_summarized_timestamp
        )
        
        # ถ้ามีเกิน 10 ข้อความ (5 Turns) ให้ทำการสรุป
        if len(full_history) >= 10:
            print(f"[Summary] ข้อมูลถึงเกณฑ์ {len(full_history)} ข้อความ กำลังสรุปรวบยอด...")
            
            # เก็บ 6 ข้อความล่าสุด (3 Turns) ไว้ใน Short-term memory ให้บอทยังจำได้ว่าเพิ่งคุยอะไรไป
            # และดึงส่วนที่เหลือ (เก่ากว่า 6 ข้อความนั้น) ไปสรุป
            messages_to_summarize = full_history[:-6]
            timestamps_to_summarize = full_timestamps[:-6]
            
            new_summary = bedrock_agent.generate_summary(
                current_summary=summary_context, old_messages=messages_to_summarize
            )
            
            # เลื่อน Checkpoint มายังข้อความที่ใหม่ที่สุด "ในกลุ่มที่เพิ่งถูกสรุปเท่านั้น"
            new_checkpoint_ts = max(timestamps_to_summarize)
            
            memory_service.save_summary(
                user_id=user_id, summary_text=new_summary, last_summarized_timestamp=new_checkpoint_ts
            )
            print(f"[Summary] เสร็จสิ้น — สรุปไป {len(messages_to_summarize)} ข้อความ | Checkpoint ใหม่={new_checkpoint_ts}")

    # 4. จบพิธี ตอบ 200 OK ให้ LINE ทราบว่าได้รับสารแล้ว
    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }
