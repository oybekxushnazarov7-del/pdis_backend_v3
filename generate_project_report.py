import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
    PageBreak,
    Table,
    TableStyle,
    Image,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line


OUTPUT_FILE = "PDIS_Project_Report_EN_UZ.pdf"
SCREENSHOT_PATH = (
    "C:/Users/hp/.cursor/projects/c-Users-hp-OneDrive-Desktop-PDIS/assets/"
    "c__Users_hp_AppData_Roaming_Cursor_User_workspaceStorage_1d8a5ee7b8a93bf89460b17cfdd9d798_images_"
    "photo_2026-04-25_22-45-03-6f1abd5b-f218-4bf1-be28-49b9c4b8cff7.png"
)


def p(text, style):
    return Paragraph(text, style)


def bullet_list(items, style):
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=8) for item in items],
        bulletType="bullet",
        start="circle",
        bulletColor=colors.HexColor("#4B4B4B"),
    )


def architecture_diagram():
    d = Drawing(500, 170)

    # Boxes
    d.add(Rect(10, 95, 140, 45, rx=8, ry=8, fillColor=colors.HexColor("#EAF2FF"), strokeColor=colors.HexColor("#5B7CFF")))
    d.add(Rect(180, 95, 140, 45, rx=8, ry=8, fillColor=colors.HexColor("#EEFCEA"), strokeColor=colors.HexColor("#4AA96C")))
    d.add(Rect(350, 95, 140, 45, rx=8, ry=8, fillColor=colors.HexColor("#FFF4EA"), strokeColor=colors.HexColor("#E58F3A")))

    # Labels
    d.add(String(33, 116, "Frontend (index.html)", fontSize=10))
    d.add(String(210, 116, "FastAPI Backend", fontSize=10))
    d.add(String(392, 116, "PostgreSQL", fontSize=10))

    # Arrows
    d.add(Line(150, 117, 180, 117, strokeColor=colors.black))
    d.add(Line(320, 117, 350, 117, strokeColor=colors.black))
    d.add(Line(180, 108, 150, 108, strokeColor=colors.black))
    d.add(Line(350, 108, 320, 108, strokeColor=colors.black))

    # Arrow heads (simple)
    d.add(Line(176, 117, 170, 121, strokeColor=colors.black))
    d.add(Line(176, 117, 170, 113, strokeColor=colors.black))
    d.add(Line(346, 117, 340, 121, strokeColor=colors.black))
    d.add(Line(346, 117, 340, 113, strokeColor=colors.black))
    d.add(Line(154, 108, 160, 112, strokeColor=colors.black))
    d.add(Line(154, 108, 160, 104, strokeColor=colors.black))
    d.add(Line(324, 108, 330, 112, strokeColor=colors.black))
    d.add(Line(324, 108, 330, 104, strokeColor=colors.black))

    d.add(String(205, 76, "JWT access/refresh auth, REST APIs: /auth, /users, /expenses", fontSize=9))
    d.add(String(10, 48, "Deploy: Render | DB: Supabase/PostgreSQL | Client: mobile + desktop responsive UI", fontSize=9))
    return d


def build():
    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="PDIS Project Report (English + Uzbek)",
        author="PDIS Team",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        spaceAfter=10,
    )
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=14, leading=18, spaceAfter=6)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, leading=16, spaceAfter=4)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=15)
    small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=9.5, leading=13)

    story = []

    # Cover page
    story.append(p("PDIS Project Full Documentation", title_style))
    story.append(p("Comprehensive Technical and Practical Report", h2))
    story.append(Spacer(1, 8))
    story.append(p(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", small))
    story.append(p("Prepared in two languages: English and Uzbek", small))
    story.append(Spacer(1, 16))
    story.append(p("Project Scope", h1))
    story.append(
        bullet_list(
            [
                "Project background, architecture, stack, and workflow",
                "Detailed list of implemented improvements in this session",
                "Deployment instructions and real-life usage scenarios",
                "Bilingual explanation for presentation, learning, and documentation",
            ],
            body,
        )
    )
    story.append(Spacer(1, 14))
    story.append(p("Quick Architecture Snapshot", h1))
    story.append(architecture_diagram())

    if os.path.exists(SCREENSHOT_PATH):
        story.append(Spacer(1, 12))
        story.append(p("Current Mobile UI Screenshot", h2))
        story.append(Image(SCREENSHOT_PATH, width=62 * mm, height=112 * mm))

    story.append(PageBreak())

    # English section
    story.append(p("PDIS Project Full Documentation", title_style))
    story.append(p("Language 1: English", small))
    story.append(Spacer(1, 8))

    story.append(p("1) Executive Summary", h1))
    story.append(
        p(
            "PDIS is a lightweight Personal Management and Expense Tracking web application. "
            "It allows account registration/login, user management, and expense recording with a dashboard. "
            "The stack is intentionally simple: FastAPI backend, PostgreSQL database, and a static frontend page.",
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("2) Why This Website Exists (Real-Life Purpose)", h1))
    story.append(
        bullet_list(
            [
                "Track daily/weekly/monthly personal or small-team expenses in one place.",
                "Manage a private list of related users/contacts under one account.",
                "Provide a simple dashboard view for quick operational decisions.",
                "Serve as a practical starter project for full-stack portfolio and deployment practice.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("3) Technologies Used and Why", h1))
    story.append(
        bullet_list(
            [
                "<b>FastAPI</b>: fast API development, built-in docs pattern, clean routing.",
                "<b>PostgreSQL + psycopg2</b>: reliable relational storage with SQL control.",
                "<b>JWT (python-jose)</b>: stateless authentication (access + refresh tokens).",
                "<b>Passlib</b>: password hashing/verification for safer credential handling.",
                "<b>Vanilla HTML/CSS/JS</b>: no build-step frontend, easy deployment and learning curve.",
                "<b>Render</b>: cloud deployment for public hosting and continuous delivery.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("4) Architecture and Data Flow", h1))
    story.append(
        bullet_list(
            [
                "Client opens website and authenticates via /auth/login.",
                "Server validates credentials against accounts table.",
                "Server returns access_token + refresh_token.",
                "Frontend stores tokens in localStorage and uses Authorization header for API calls.",
                "Protected endpoints (/users, /expenses) read account_id from JWT payload.",
                "Database operations are done with SQL queries and returned as JSON.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("5) Project Structure (Core Files)", h1))
    story.append(
        bullet_list(
            [
                "<b>app/main.py</b>: API app initialization, CORS, table creation on startup, static routing.",
                "<b>app/routes/users.py</b>: register/login/refresh flow and user CRUD endpoints.",
                "<b>app/routes/expenses.py</b>: expense create/list/delete endpoints.",
                "<b>app/auth.py</b>: password hashing and JWT creation/validation logic.",
                "<b>app/db.py</b>: PostgreSQL connection configuration.",
                "<b>static/index.html</b>: full frontend UI and browser-side logic.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("6) What You Implemented in This Session", h1))
    story.append(
        bullet_list(
            [
                "Diagnosed mobile layout issue where sidebar consumed screen space.",
                "Added left-top hamburger button and sidebar overlay behavior for mobile.",
                "Extended sidebar toggle behavior for desktop and mobile compatibility.",
                "Added mobile bottom navigation (Home, Users, Expenses).",
                "Added quick-add floating button and modal to create expenses rapidly.",
                "Added expense time filters: All, Today, Week, Month.",
                "Kept backend business logic unchanged (safe UX enhancement approach).",
            ],
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("7) Security and Quality Notes", h1))
    story.append(
        bullet_list(
            [
                "Current SECRET_KEY and DATABASE_URL are hardcoded; move them to environment variables.",
                "CORS is fully open (*) for development convenience; restrict origins in production.",
                "No automated tests yet; add endpoint and UI smoke tests.",
                "Use migration tooling (e.g., Alembic) instead of runtime table creation for long-term maintainability.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("8) How to Use This Site in Daily Life", h1))
    story.append(
        bullet_list(
            [
                "Freelancers: track client-related costs and small operating expenses.",
                "Small businesses: monitor routine purchases and maintain team member records.",
                "Students: keep monthly budget discipline and spending visibility.",
                "Families: log household categories and review trends over time.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("9) Suggested Next Roadmap", h1))
    story.append(
        bullet_list(
            [
                "Add .env configuration and settings management.",
                "Add requirements lock and structured README update.",
                "Add pagination + advanced date range filters.",
                "Add CSV export/import and category analytics charts.",
                "Turn app into PWA (installable mobile experience).",
            ],
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("10) Deployment Steps (Render)", h1))
    deploy_table = Table(
        [
            ["Step", "Action"],
            ["1", "Commit local changes and push to GitHub repository."],
            ["2", "Open Render dashboard and ensure the correct branch is connected."],
            ["3", "Confirm start command points to the intended app entrypoint."],
            ["4", "Trigger deploy (or wait for auto-deploy after push)."],
            ["5", "After deploy, hard-refresh browser/mobile cache to see latest UI."],
        ],
        colWidths=[20 * mm, 145 * mm],
    )
    deploy_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ECECFA")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8B8D9")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(deploy_table)

    # English summary section
    story.append(PageBreak())
    story.append(p("Language 2: English", h1))

    story.append(p("1) Summary", h2))
    story.append(
        p(
            "PDIS is a lightweight web app for personal management and expense tracking. "
            "It supports account registration/login, user management, expense entry, and a dashboard. "
            "The technical stack is practical and simple: FastAPI, PostgreSQL, and a static frontend.",
            body,
        )
    )
    story.append(Spacer(1, 6))

    story.append(p("2) What is this app for?", h2))
    story.append(
        bullet_list(
            [
                "Track daily, weekly, and monthly expenses in one place.",
                "Manage a list of related users under a single account.",
                "Use the dashboard for quick analysis to support decisions.",
                "Use it as a full-stack portfolio project with real deployment experience.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 6))

    story.append(p("3) Why these technologies?", h2))
    story.append(
        bullet_list(
            [
                "<b>FastAPI</b>: for fast API development and clean routing.",
                "<b>PostgreSQL + psycopg2</b>: for reliable SQL database access.",
                "<b>JWT</b>: for secure session management with tokens.",
                "<b>Passlib</b>: for securely hashing passwords.",
                "<b>HTML/CSS/JS</b>: for a quick build-free frontend.",
                "<b>Render</b>: for cloud deployment and automated hosting.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 6))

    story.append(p("4) How it works", h2))
    story.append(
        bullet_list(
            [
                "The user logs in via /auth/login and receives a token.",
                "Access/refresh tokens are stored in localStorage.",
                "Subsequent /users and /expenses requests use the Bearer token.",
                "The backend validates account scope with user_id from the token.",
                "Data is stored in Postgres and returned as JSON to the UI.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 6))

    story.append(p("5) Improvements made", h2))
    story.append(
        bullet_list(
            [
                "Fixed the mobile-style sidebar behavior.",
                "Added a top-left hamburger menu overlay for mobile.",
                "Unified sidebar toggling for desktop and mobile.",
                "Added mobile bottom navigation.",
                "Added a quick add (+) modal for fast expense entry.",
                "Added expense time filters: All, Today, Week, Month.",
                "Kept backend logic intact while improving UX.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 6))

    story.append(p("6) Benefit in real use", h2))
    story.append(
        bullet_list(
            [
                "For freelancers: track project expenses.",
                "For small businesses: manage team and spending.",
                "For students: keep monthly expenses disciplined.",
                "For family use: monitor expense categories.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 6))

    story.append(p("7) Next improvement suggestions", h2))
    story.append(
        bullet_list(
            [
                "Move secrets into .env instead of code.",
                "Update the README fully and clearly.",
                "Add automated tests with pytest.",
                "Add PWA support for installable mobile use.",
                "Add charts/analytics and export functions.",
            ],
            body,
        )
    )
    story.append(Spacer(1, 8))

    story.append(p("8) Deploy steps to Render", h2))
    deploy_table_uz = Table(
        [
            ["Step", "Action"],
            ["1", "Commit local changes and push them to GitHub."],
            ["2", "Verify the correct branch is connected in Render dashboard."],
            ["3", "Ensure the start command targets the correct entrypoint."],
            ["4", "Run deploy or wait for auto-deploy."],
            ["5", "After deploy, hard refresh in browser on mobile/desktop."],
        ],
        colWidths=[20 * mm, 145 * mm],
    )
    deploy_table_uz.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF7EE")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#A9D1B5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(deploy_table_uz)
    story.append(Spacer(1, 10))

    story.append(
        p(
            "Prepared for: Project owner (bilingual technical and practical documentation).",
            small,
        )
    )

    doc.build(story)
    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    build()
