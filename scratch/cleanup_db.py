import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def cleanup():
    if not DATABASE_URL:
        print("DATABASE_URL topilmadi!")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("Ma'lumotlar o'chirilmoqda...")
        
        # Foreign keylar borligi sababli tartib bilan o'chiramiz
        # Avval xarajatlar, keyin sub-userlar, keyin asosiy accountlar
        cursor.execute("DELETE FROM expenses")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM accounts")
        
        conn.commit()
        print("Barcha ma'lumotlar muvaffaqiyatli o'chirildi!")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Xatolik: {e}")

if __name__ == "__main__":
    cleanup()
