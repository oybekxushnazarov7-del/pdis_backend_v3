from fpdf import FPDF

class LearningGuidePDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(108, 99, 255)
        self.cell(0, 15, 'FinPulse: Master Learning Guide', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(240, 240, 255)
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 7, body)
        self.ln(5)

def generate():
    pdf = LearningGuidePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Introduction
    pdf.chapter_title("Introduction: Building Modern Apps")
    pdf.chapter_body(
        "To build a project like FinPulse, you need a mix of Backend, Frontend, and Database skills. "
        "This guide breaks down exactly what you need to master."
    )

    # Phase 1: Backend (Python & FastAPI)
    pdf.chapter_title("Phase 1: Backend Mastery (FastAPI)")
    pdf.chapter_body(
        "1. REST API Basics: Understanding GET, POST, PUT, DELETE requests.\n"
        "2. FastAPI Framework: Learning how to create routes, handle JSON data, and use Pydantic for validation.\n"
        "3. Security (JWT): JSON Web Tokens are used for login sessions. You need to learn how to create and verify tokens.\n"
        "4. Bcrypt: Always hash passwords! Never store plain text passwords in your database.\n"
        "5. Dependency Injection: Using 'Depends' in FastAPI to manage database connections and user authentication."
    )

    # Phase 2: Database (PostgreSQL)
    pdf.chapter_title("Phase 2: Database (PostgreSQL & SQL)")
    pdf.chapter_body(
        "1. Relational Design: Creating tables (Accounts, Users, Expenses) and linking them with IDs.\n"
        "2. SQL Queries: Mastering SELECT (fetching), INSERT (adding), and JOIN (linking tables) queries.\n"
        "3. Timezone Management: Storing dates as UTC and converting them to local time (like UTC+5 for Uzbekistan).\n"
        "4. Database Drivers: Using 'psycopg2' to let Python talk to the PostgreSQL database."
    )

    # Phase 3: Frontend (JS & CSS)
    pdf.chapter_title("Phase 3: Frontend (JavaScript & Modern UI)")
    pdf.chapter_body(
        "1. DOM Manipulation: Using JavaScript to update the screen without refreshing the page.\n"
        "2. Fetch API: Communicating with your Backend to send/receive data.\n"
        "3. CSS Mastery: Flexbox and Grid for layout, and Glassmorphism (blur/transparency) for that premium feel.\n"
        "4. SPA (Single Page Application): Creating one HTML file and using JS to swap between 'Home', 'Expenses', and 'Admin' sections."
    )

    # Phase 4: Integrations & Charts
    pdf.chapter_title("Phase 4: Integrations & Visualization")
    pdf.chapter_body(
        "1. Email APIs: Using Brevo (or SendGrid/Mailchimp) to send automated verification codes.\n"
        "2. Chart.js: A powerful library to create Pie, Bar, and Line charts using your financial data.\n"
        "3. CSV Generation: Converting your data arrays into CSV files for Excel users."
    )

    # Phase 5: Personal Tips from the Developer
    pdf.chapter_title("Phase 5: Pro Developer Tips")
    pdf.chapter_body(
        "1. Environment Variables: Always use .env files for secrets (API keys, passwords).\n"
        "2. Polling: Use setInterval() in JS to keep your dashboard updated in real-time.\n"
        "3. Error Handling: Always try/except on the backend and catch errors on the frontend to keep the app from crashing."
    )

    # Uzbek Summary
    pdf.add_page()
    pdf.chapter_title("O'quv qo'llanma (Qisqacha o'zbekcha)")
    pdf.chapter_body(
        "Ushbu loyihani noldan qurish uchun siz quyidagilarni o'rganishingiz kerak:\n\n"
        "1. Python & FastAPI: API yaratish va JWT orqali xavfsizlikni ta'minlash.\n"
        "2. SQL & PostgreSQL: Ma'lumotlarni jadvallarda saqlash va boshqarish.\n"
        "3. JavaScript (ES6+): Sahifani yangilamasdan ma'lumotlar bilan ishlash (Fetch API).\n"
        "4. CSS Dizayn: Zamonaviy 'Glassmorphism' va 'Dark Mode' dizaynlarini yaratish.\n"
        "5. API Integratsiyalari: Brevo (Email yuborish) va Chart.js (Grafiklar chizish).\n"
        "6. Xavfsizlik: Parollarni shifrlash (Bcrypt) va Admin paneli uchun maxfiy kirish tizimi."
    )

    pdf.output('FinPulse_Learning_Guide.pdf')
    print("O'quv qo'llanma PDF shaklida yaratildi!")

if __name__ == '__main__':
    generate()
