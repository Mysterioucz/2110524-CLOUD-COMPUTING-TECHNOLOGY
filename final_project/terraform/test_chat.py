import sys
import os
from dotenv import load_dotenv

# โหลด Environment Variables จากไฟล์ .env เผื่อไว้
load_dotenv()

# ชี้ให้ Python มองเห็นโฟลเดอร์ src เพื่อ import service ต่างๆ เหมือนที่ Lambda รัน
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.services.dynamodb_memory import DynamoDBMemory
from src.services.bedrock_agent import BedrockAgent

def run_test():
    # ใช้ Config จากการดึง Environment Variables หรือ Default 
    memory_service = DynamoDBMemory(Config.DYNAMODB_TABLE_NAME)
    bedrock_agent = BedrockAgent(Config.BEDROCK_MODEL_ID)
    
    # สมมติ User ID สำหรับการทดสอบ
    user_id = "test_user_001"
    
    print("======================================================")
    print("🙏 เริ่มการทดสอบสนทนากับหลวงพี่ (พิมพ์ 'exit' เพื่อออก) 🙏")
    print(f"ตาราง DynamoDB ที่เชื่อมต่อ: {Config.DYNAMODB_TABLE_NAME}")
    print(f"โมเดลจำลอง: {Config.BEDROCK_MODEL_ID}")
    print("======================================================")
    
    while True:
        user_text = input("\n[โยม]: ")
        if user_text.lower() in ['exit', 'quit']:
            break
            
        print("หลวงพี่กำลังพิจารณา...")
        
        # 1. จำลองการเซฟข้อความ (The Soul)
        memory_service.save_message(user_id=user_id, role="user", content=user_text)
        
        # 2. ดึงบริบท
        summary_context, last_summarized_timestamp = memory_service.get_summary(user_id=user_id)
        history, _ = memory_service.get_history(user_id=user_id, limit=9, since_timestamp=last_summarized_timestamp)
        
        # 3. จัดเตรียมประวัติ
        history_for_bedrock = history[:-1] if history and history[-1]['role'] == 'user' else history
        
        print(f"   [Debug]: ดึง Short-term history มาได้ {len(history_for_bedrock)} ชิ้น (นับตั้งแต่ Checkpoint ล่าสุด)")
        if summary_context:
            print(f"   [Debug]: มี Summary จากความจำระยะยาวอยู่ด้วย")
            
        # 4. เรียกโมเดล
        bot_response = bedrock_agent.generate_reply(
            user_message=user_text, 
            history=history_for_bedrock,
            summary_context=summary_context
        )
        
        print(f"\n[หลวงพี่]: {bot_response}")
        
        # 5. เซฟข้อความตอบกลับ
        memory_service.save_message(user_id=user_id, role="assistant", content=bot_response)

        # 6. Long-Term Memory Evaluation (Chunked Summary)
        full_history, full_timestamps = memory_service.get_history(user_id=user_id, limit=10, since_timestamp=last_summarized_timestamp)
        if len(full_history) >= 8: # ตั้งค่าเป็น 8 (4 Turns)
            print("\n   [Debug]: ⚠️ ประวัติ Short-term ถึง 4 Turns (8 ข้อความ) แล้ว! กำลังทำการรวบยอด (Sum) เข้าไปใน Summary...")
            new_summary = bedrock_agent.generate_summary(current_summary=summary_context, old_messages=full_history)
            
            max_timestamp = max(full_timestamps) if full_timestamps else 0
            memory_service.save_summary(user_id=user_id, summary_text=new_summary, last_summarized_timestamp=max_timestamp)
            print("   [Debug]: ✅ บันทึก Summary ใหม่เสร็จสิ้น พร้อมแปะ Checkpoint (ข้อความจะเริ่มนับ 0 ใหม่ในตาหน้า)")

if __name__ == "__main__":
    # ต้องตั้งค่า AWS Access Key ในเครื่องก่อน (เช่นใช้ aws configure)
    try:
        run_test()
    except Exception as e:
        print(f"\nเกิดข้อผิดพลาด: {e}")
        print("\nคำแนะนำ: คุณอาจจะยังไม่ได้สร้าง Table ใน DynamoDB หรือยังไม่ได้ล็อกอิน AWS CLI (รันคำสั่ง aws configure)")
