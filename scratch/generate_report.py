from fpdf import FPDF

class ProjectReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'FinPulse: Project Technical Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_report():
    pdf = ProjectReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # English Version
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(108, 99, 255)
    pdf.cell(0, 10, '1. Project Overview (English)', 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 7, (
        "FinPulse is a professional-grade, full-stack web application designed for comprehensive financial tracking. "
        "It allows users to manage multiple profiles under a single account, track expenses with categorical precision, "
        "and visualize financial health through real-time analytics."
    ))
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, '2. Technology Stack', 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 7, (
        "- Backend: Python (FastAPI)\n"
        "- Database: PostgreSQL (Supabase)\n"
        "- Frontend: HTML5, CSS3, JavaScript (Vanilla SPA)\n"
        "- Authentication: JWT with Refresh Tokens\n"
        "- Email: Brevo HTTP API for 2FA\n"
        "- Charts: Chart.js"
    ))
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, '3. Key Features', 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 7, (
        "- Secure Registration & Email Verification (2FA)\n"
        "- Multi-user support within one account\n"
        "- Real-time Analytics Dashboard & Visual Charts\n"
        "- CSV Export for financial reporting\n"
        "- Restricted Admin Command Center (Real-time tracking)\n"
        "- Uzbekistan Timezone Synchronization (UTC+5)"
    ))
    pdf.ln(10)

    # Uzbek Version (Simplified characters for PDF compatibility)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(255, 101, 132)
    pdf.cell(0, 10, "2. Loyiha haqida (O'zbekcha)", 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 7, (
        "FinPulse - bu to'liq funksional, professional moliyaviy boshqaruv tizimi. "
        "U bitta akkauntda bir nechta profilni boshqarish, xarajatlarni kuzatish va "
        "grafiklar orqali tahlil qilish imkonini beradi."
    ))
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Texnologiyalar:', 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 7, (
        "- Backend: Python (FastAPI)\n"
        "- Baza: PostgreSQL (Supabase)\n"
        "- Frontend: JS, HTML, CSS (SPA)\n"
        "- Email: Brevo API (Tasdiqlash kodlari uchun)\n"
        "- Grafiklar: Chart.js"
    ))
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Imkoniyatlar:', 0, 1)
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(0, 7, (
        "- Xavfsiz login va Email tasdiqlash (2FA)\n"
        "- Bir nechta foydalanuvchini qo'shish\n"
        "- Real-vaqt diagrammalari va hisobotlar\n"
        "- Excel formatida (CSV) yuklab olish\n"
        "- Maxfiy Admin Boshqaruv Markazi (Oybek uchun)\n"
        "- Uzbekistan vaqti (UTC+5) bilan sinxronizatsiya"
    ))

    pdf.output('PDIS_Project_Report_EN_UZ.pdf')
    print("PDF muvaffaqiyatli yaratildi!")

if __name__ == '__main__':
    create_report()
