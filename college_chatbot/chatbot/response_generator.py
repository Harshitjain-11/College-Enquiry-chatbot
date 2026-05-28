"""
Response Generator for the College Enquiry Chatbot.
Handles all intents with knowledge-base driven responses.
"""
 
import json
import random
import logging
from pathlib import Path
from difflib import get_close_matches
 
logger = logging.getLogger(__name__)
 
BASE_DIR = Path(__file__).resolve().parent.parent
KB_PATH = BASE_DIR / "data" / "knowledge_base.json"
 
QUICK_REPLIES: dict[str, list[str]] = {
    "greeting":           ["Admission Process", "Courses Offered", "Fee Structure", "Book Appointment"],
    "college_overview":   ["Courses Offered", "Placement Info", "Admission Process", "Contact Us"],
    "about_college":      ["Courses Offered", "Placement Info", "Admission Process", "Contact Us"],
    "admission_process":  ["Documents Needed", "Last Date to Apply", "Eligibility Criteria", "Fee Structure"],
    "courses_offered":    ["Fee Structure", "Eligibility", "Placement Info", "Scholarship Info"],
    "specializations":    ["Fee Structure", "Eligibility Criteria", "Admission Process", "Placement Info"],
    "course_details":     ["Fee Structure", "Eligibility", "Placement Info", "Book Appointment"],
    "eligibility":        ["Courses Offered", "Fee Structure", "Admission Process", "Contact Us"],
    "fees_structure":     ["Scholarship Info", "Apply Now", "Documents Needed", "Contact Us"],
    "placement":          ["Companies List", "Courses Offered", "Book Appointment", "Contact Us"],
    "companies_recruiters":["Placement Info", "Courses Offered", "Fee Structure", "Book Appointment"],
    "campus_timing":      ["Contact Us", "How to Reach", "Book Appointment", "Admission Process"],
    "counselling_info":   ["Documents Needed", "Fee Structure", "Book Appointment", "Contact Us"],
    "course_recommendation":["Courses Offered", "Eligibility", "Fee Structure", "Placement Info"],
    "career_scope":       ["Placement Info", "Courses Offered", "Fee Structure", "Book Appointment"],
    "total_branches":     ["Courses Offered", "Fee Structure", "Eligibility", "Book Appointment"],
    "last_date":          ["Admission Process", "Documents Needed", "Contact Us", "Book Appointment"],
    "documents_needed":   ["Admission Process", "Fee Structure", "Contact Us", "Book Appointment"],
    "hostel_info":        ["Fee Structure", "Contact Us", "Admission Process", "Book Appointment"],
    "contact_info":       ["Admission Process", "Book Appointment", "Courses Offered", "Fee Structure"],
    "scholarship":        ["Eligibility Criteria", "Fee Structure", "Admission Process", "Contact Us"],
    "facilities":         ["Hostel Info", "Courses Offered", "Contact Us", "Book Appointment"],
    "internship":         ["Placement Info", "Courses Offered", "Contact Us", "Book Appointment"],
    "exam_schedule":      ["Admission Process", "Last Date to Apply", "Eligibility", "Contact Us"],
    "result_status":      ["Documents Needed", "Contact Us", "Fee Structure", "Book Appointment"],
    "clubs_activities":   ["Facilities", "Courses Offered", "Contact Us", "Book Appointment"],
    "how_to_reach":       ["Contact Us", "Book Appointment", "Hostel Info", "Admission Process"],
    "slot_booking":       ["Fee Structure", "Courses Offered", "Contact Us"],
    "goodbye":            [],
    "fallback":           ["Admission Process", "Courses Offered", "Fee Structure", "Contact Us"],
    "angry_user":         ["Contact Us", "Book Appointment"],
}
 
FALLBACK_RESPONSES = [
    "🤔 I didn't quite understand that. I can help you with:\n\n"
    "📚 Courses & Specializations (AIML, CSE, IT, MBA...)\n"
    "💰 Fees & Scholarships\n📋 Admission Process\n"
    "🏆 Placement & Companies\n🏠 Hostel\n📅 Book Campus Visit\n\n"
    "Just ask your question! 😊",
    "Hmm, could you rephrase that? Try asking about:\n"
    "Courses | Fees | Admission | Placement | AIML | Hostel\n\n"
    "Or call: +91-7773005065 for direct help!",
]
 
ANGRY_RESPONSE = (
    "I sincerely apologize for the inconvenience! 🙏 "
    "Please call us directly at **+91-7773005065** or email **admission@itmgoi.in** — "
    "our counsellors will be happy to assist you personally."
)
 
 
class ResponseGenerator:
    def __init__(self):
        self.kb = self._load_kb()
        logger.info("ResponseGenerator initialized.")
 
    def generate(self, intent, entities, context, slot_state="IDLE", extra_data=None):
        extra_data = extra_data or {}
        if slot_state not in ("IDLE", "COMPLETED", "CANCELLED") and extra_data.get("slot_prompt"):
            return extra_data["slot_prompt"], []
        handler = self._get_handler(intent)
        response = handler(entities, context, extra_data)
        quick_replies = QUICK_REPLIES.get(intent, QUICK_REPLIES["fallback"])
        return response, quick_replies
 
    def _get_handler(self, intent):
        handlers = {
            "greeting":             self._handle_greeting,
            "goodbye":              self._handle_goodbye,
            "college_overview":    self._handle_about_college,
            "about_college":        self._handle_about_college,
            "admission_process":    self._handle_admission_process,
            "courses_offered":      self._handle_courses_offered,
            "specializations":      self._handle_specializations,
            "course_details":       self._handle_course_details,
            "eligibility":          self._handle_eligibility,
            "fees_structure":       self._handle_fees_structure,
            "placement":            self._handle_placement,
            "companies_recruiters": self._handle_companies,
            "campus_timing":        self._handle_campus_timing,
            "counselling_info":     self._handle_counselling_info,
            "course_recommendation": self._handle_course_recommendation,
            "career_scope":        self._handle_career_scope,
            "total_branches":      self._handle_total_branches,
            "last_date":            self._handle_last_date,
            "documents_needed":     self._handle_documents_needed,
            "hostel_info":          self._handle_hostel_info,
            "contact_info":         self._handle_contact_info,
            "scholarship":          self._handle_scholarship,
            "facilities":           self._handle_facilities,
            "internship":           self._handle_internship,
            "exam_schedule":        self._handle_exam_schedule,
            "result_status":        self._handle_result_status,
            "clubs_activities":     self._handle_clubs,
            "how_to_reach":         self._handle_how_to_reach,
            "slot_booking":         self._handle_slot_booking,
            "angry_user":           self._handle_angry,
            "fallback":             self._handle_fallback,
        }
        return handlers.get(intent, self._handle_fallback)
 
    # ── Handlers ──────────────────────────────────────────────────────────────
 
    def _handle_greeting(self, entities, context, extra):
        return random.choice([
            "Hello! 👋 Welcome to **Institute of Technology & Management, Gwalior**!\n"
            "I'm your virtual admission counsellor. Ask me about admissions, courses, fees, placement, or scholarships!",
            "Hi there! 🎓 I'm the ITM Gwalior chatbot.\n"
            "What would you like to know? Admissions, Fees, Courses, AIML, Placement?",
            "Namaste! 🙏 Welcome to ITM Gwalior — NAAC 'A' Grade Institute.\n"
            "I'm here to guide you through your admission journey. What's on your mind?",
        ])
 
    def _handle_goodbye(self, entities, context, extra):
        return random.choice([
            "Thank you for chatting! 🎓 Best of luck with your admission.\n"
            "Visit **www.itmgoi.in** or call **+91-7773005065** anytime!",
            "Goodbye! 👋 Hope to see you on campus soon.\nFor info: **www.itmgoi.in**",
            "Take care! 😊 All the best for your future!\nITM Gwalior is always here to help.",
        ])
 
    def _handle_about_college(self, entities, context, extra):
        c = self.kb.get("college", {})
        awards = c.get("awards", [])
        awards_text = "\n  ".join(f"🏅 {a}" for a in awards[:4])
        return (
            f"🎓 **About Institute of Technology & Management, Gwalior:**\n\n"
            f"📍 Established: **{c.get('established', 1997)}** (29+ years of excellence)\n"
            f"🏆 NAAC Grade: **'{c.get('naac_grade', 'A')}'** (CGPA {c.get('naac_cgpa', 3.01)}, valid till Nov 2030)\n"
            f"🎖️ NBA Accredited | AICTE Approved | RGPV Affiliated\n"
            f"🌐 Website: **{c.get('website', 'www.itmgoi.in')}**\n\n"
            f"✨ Key Achievements:\n  {awards_text}\n\n"
            f"📞 Admission: **+91-7773005065** | 📧 **admission@itmgoi.in**"
        )
 
    def _handle_admission_process(self, entities, context, extra):
        steps = self.kb.get("admission_process", [])
        if isinstance(steps, dict):
            steps = steps.get("steps", [])
        steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
        return (
            f"📋 **Admission Process at ITM Gwalior:**\n\n"
            f"{steps_text}\n\n"
            f"🌐 Apply: **{self.kb.get('college', {}).get('apply_online', 'http://itmgoi.in/OnlineApply_ITMGOI')}**\n"
            f"📞 Helpline: **+91-7773005065 / +91-7773001624**\n"
            f"📧 Email: **admission@itmgoi.in**"
        )
 
    def _handle_courses_offered(self, entities, context, extra):
        courses = self.kb.get("courses", {})
        ug = courses.get("ug", [])
        pg = courses.get("pg", [])
        ug_list = "\n".join(f"  • {c['short']} ({c['duration']}) — ₹{c['fees_per_year']:,}/year" for c in ug)
        pg_list = "\n".join(f"  • {c['short']} ({c['duration']}) — ₹{c['fees_per_year']:,}/year" for c in pg)
        return (
            f"🎓 **Courses at ITM Gwalior (RGPV Affiliated):**\n\n"
            f"**🔧 B.Tech Engineering:**\n"
            f"  • B.Tech CSE (with AIML, DS, Cyber, IoT, Cloud specializations!)\n"
            f"  • B.Tech IT\n  • B.Tech ECE\n  • B.Tech ME\n  • B.Tech Civil\n\n"
            f"**📚 Other UG Programs:**\n"
            f"  • BCA | BBA | B.Sc | B.Com\n\n"
            f"**🎓 Postgraduate (PG):**\n{pg_list}\n\n"
            f"Ask about any specific course for fees, eligibility & career details!"
        )
 
    def _handle_specializations(self, entities, context, extra):
        courses = self.kb.get("courses", {})
        ug = courses.get("ug", [])
        cse = next((course for course in ug if course.get("short") == "B.Tech CSE"), {})
        it = next((course for course in ug if course.get("short") == "B.Tech IT"), {})
        ece = next((course for course in ug if course.get("short") == "B.Tech ECE"), {})
        me = next((course for course in ug if course.get("short") == "B.Tech ME"), {})
        civil = next((course for course in ug if course.get("short") == "B.Tech Civil"), {})
        return (
            "🤖 **B.Tech Specializations at ITM Gwalior:**\n\n"
            "💻 **B.Tech CSE Specializations:**\n"
            f"  ✅ {', '.join(cse.get('specializations', ['CS-AIML', 'CS-DS', 'CS-Cybersecurity', 'CS-IoT', 'CS-Cloud']))}\n\n"
            "📡 **B.Tech IT Specializations:**\n"
            f"  • {', '.join(it.get('specializations', ['Web Technologies', 'Mobile App Development', 'Network Security', 'Database Management']))}\n\n"
            f"📻 **B.Tech ECE:** {', '.join(ece.get('specializations', ['VLSI Design', 'Embedded Systems', 'Signal Processing']))}\n\n"
            f"⚙️ **B.Tech ME:** {', '.join(me.get('specializations', ['Automobile Engineering', 'Thermal Engineering', 'Manufacturing']))}\n\n"
            f"🏗️ **B.Tech Civil:** {', '.join(civil.get('specializations', ['Structural Engineering', 'Environmental Engineering']))}\n\n"
            "🌟 ITM is **Microsoft Centre of Excellence** & **AWS Academy Member**!\n\n"
            f"💰 B.Tech CSE: ₹{cse.get('fees_per_year', 87000):,}/year\n"
            "📞 Admission: +91-7773005065"
        )

    def _handle_course_details(self, entities, context, extra):
        course_name = (
            entities.get("course")
            or context.get("active_course")
            or context.get("entities_so_far", {}).get("course")
        )
        if course_name:
            course_info = self._find_course(course_name)
            if course_info:
                specializations = course_info.get("specializations", [])
                career_options = course_info.get("career_prospects", [])
                avg_salary = course_info.get("avg_salary", "varies by skill and role")
                is_good_for = course_info.get("is_good_for", "students interested in this field")
                return (
                    f"📘 **{course_info['short']} Details:**\n\n"
                    f"• Name: {course_info.get('name', course_info['short'])}\n"
                    f"• Duration: {course_info.get('duration', 'N/A')}\n"
                    f"• Seats: {course_info.get('seats', 'N/A')}\n"
                    f"• Fees: ₹{course_info.get('fees_per_year', 0):,}/year\n"
                    f"• Eligibility: {course_info.get('eligibility', 'N/A')}\n"
                    f"• Entrance Exam: {course_info.get('entrance_exam', 'N/A')}\n"
                    f"• Specializations: {', '.join(specializations) if specializations else 'N/A'}\n"
                    f"• Career Options: {', '.join(career_options) if career_options else 'N/A'}\n"
                    f"• Avg Salary: {avg_salary}\n"
                    f"• Best For: {is_good_for}"
                )
        return self._handle_courses_offered(entities, context, extra)

    def _handle_course_recommendation(self, entities, context, extra):
        return (
            "🎯 **Course Recommendation Guide:**\n\n"
            "• Coding, software, AI, data, security -> **B.Tech CSE**\n"
            "• Web/app development, IT support -> **B.Tech IT** or **BCA**\n"
            "• Hardware, electronics, telecom -> **B.Tech ECE**\n"
            "• Machines, production, automobiles -> **B.Tech ME**\n"
            "• Civil works, construction, infrastructure -> **B.Tech Civil**\n"
            "• Business, management, entrepreneurship -> **BBA** or **MBA**\n\n"
            "If you share your interest, I can suggest the best branch for you."
        )

    def _handle_career_scope(self, entities, context, extra):
        course_name = entities.get("course") or context.get("entities_so_far", {}).get("course")
        if course_name:
            course_info = self._find_course(course_name)
            if course_info:
                career_options = course_info.get("career_prospects", [])
                return (
                    f"🚀 **Career Scope for {course_info['short']}:**\n\n"
                    f"• Career Roles: {', '.join(career_options) if career_options else 'N/A'}\n"
                    f"• Typical Salary: {course_info.get('avg_salary', 'Depends on role and skills')}\n"
                    f"• Higher Studies: M.Tech / MBA / MCA / MS (as applicable)\n"
                    f"• Govt Jobs: GATE, PSU, SSC, state exams where relevant\n"
                )
        return (
            "🚀 **Career Scope at ITM Gwalior:**\n\n"
            "• B.Tech CSE/IT -> software, product, AI, cloud, cybersecurity jobs\n"
            "• B.Tech ECE -> electronics, telecom, embedded, VLSI roles\n"
            "• B.Tech ME -> core engineering, production, design, automobile roles\n"
            "• B.Tech Civil -> construction, design, infrastructure, govt projects\n"
            "• BCA/MCA -> software development, web/app, IT support\n"
            "• BBA/MBA -> management, marketing, finance, HR, operations\n\n"
            "Share a branch name and I’ll narrow it down."
        )

    def _handle_total_branches(self, entities, context, extra):
        courses = self.kb.get("courses", {})
        ug = courses.get("ug", [])
        pg = courses.get("pg", [])
        btech = [course for course in ug if course.get("short", "").startswith("B.Tech")]
        specializations = sum(len(course.get("specializations", [])) for course in btech)
        ug_text = ", ".join(course.get("short", "") for course in ug if course.get("short"))
        pg_text = ", ".join(course.get("short", "") for course in pg if course.get("short"))
        return (
            f"📚 **Total Programs at ITM Gwalior:**\n\n"
            f"• B.Tech Branches: {len(btech)}\n"
            f"• CSE Specializations: {specializations}\n"
            f"• Other UG Programs: {ug_text}\n"
            f"• PG Programs: {pg_text}\n\n"
            "Ask me about any branch and I’ll give the full details."
        )
 
    def _handle_eligibility(self, entities, context, extra):
        course_name = (
            entities.get("course")
            or context.get("active_course")
            or context.get("entities_so_far", {}).get("course")
        )
        if course_name:
            course_info = self._find_course(course_name)
            if course_info:
                return (
                    f"📚 **Eligibility for {course_info['short']}:**\n\n"
                    f"✅ {course_info['eligibility']}\n"
                    f"📝 Entrance: {course_info['entrance_exam']}\n"
                    f"⏱ Duration: {course_info['duration']}\n"
                    f"💺 Seats: {course_info['seats']}"
                )
        return (
            "📋 **Eligibility Criteria at ITM Gwalior:**\n\n"
            "🔧 **B.Tech (CSE/IT/ECE/ME/Civil):**\n"
            "   60% in PCM in 12th + JEE Mains + RGPV DTE MP Counselling\n\n"
            "💻 **BCA:** 55% in 12th with Mathematics (Direct admission)\n"
            "📊 **BBA / B.Com:** 50% in 12th any stream (Direct admission)\n"
            "🔬 **B.Sc:** 55% in 12th Science stream\n"
            "📚 **M.Tech:** B.Tech with 60% + GATE (preferred)\n"
            "💼 **MBA:** Graduation 50% + CAT/MAT/XAT/MP-MAT\n"
            "🖥️ **MCA:** BCA/B.Sc CS with 55% + Maths\n\n"
            "Which course eligibility would you like details about?"
        )
 
    def _handle_fees_structure(self, entities, context, extra):
        course_name = (
            entities.get("course")
            or context.get("active_course")
            or context.get("entities_so_far", {}).get("course")
        )
        if course_name:
            course_info = self._find_course(course_name)
            if course_info:
                total = course_info['fees_per_year'] * int(course_info['duration'].split()[0])
                return (
                    f"💰 **Fee for {course_info['short']}:**\n\n"
                    f"• Annual Fee: **₹{course_info['fees_per_year']:,}**/year\n"
                    f"• Duration: {course_info['duration']}\n"
                    f"• Total Course Fee: **₹{total:,}** (approx.)\n\n"
                    f"💡 Merit students (>90%) get **50% scholarship!**\n"
                    f"📞 Call: +91-7773005065"
                )
        courses = self.kb.get("courses", {})
        ug = courses.get("ug", [])
        pg = courses.get("pg", [])
        ug_fees = "\n".join(f"  • {c['short']}: ₹{c['fees_per_year']:,}/year" for c in ug)
        pg_fees = "\n".join(f"  • {c['short']}: ₹{c['fees_per_year']:,}/year" for c in pg)
        return (
            f"💰 **Fee Structure at ITM Gwalior:**\n\n"
            f"**🔧 B.Tech & UG:**\n{ug_fees}\n\n"
            f"**📚 PG Programs:**\n{pg_fees}\n\n"
            f"💡 Scholarships: Merit (50%) | EWS (30%) | SC/ST | Sports (20%)\n"
            f"📞 More info: +91-7773005065"
        )
 
    def _handle_placement(self, entities, context, extra):
        p = self.kb.get("placement", {})
        it = p.get("top_recruiters", {}).get("IT_software", [])
        finance = p.get("top_recruiters", {}).get("banking_finance", [])
        core = p.get("top_recruiters", {}).get("core_engineering", [])
        return (
            f"🏆 **Placement at ITM Gwalior:**\n\n"
            f"📊 **Key Stats:**\n"
            f"  • Placement Rate: **{p.get('placement_rate', '90%+')}**\n"
            f"  • Average Package: **{p.get('average_package', 'Rs. 5.5 LPA')}**\n"
            f"  • Highest Package: **{p.get('highest_package', 'Rs. 18 LPA')}**\n"
            f"  • Companies Visiting: **{p.get('companies_count', '300+')} annually**\n\n"
            f"🏢 **Top Recruiters:**\n"
            f"  💻 IT: {', '.join(it[:6])}\n"
            f"  🏦 Finance: {', '.join(finance)}\n"
            f"  🏭 Core: {', '.join(core[:3])}\n\n"
            f"🎯 **TAP Cell:** Dedicated training, mock interviews, internships\n"
            f"📧 {p.get('tap_email', 'placement@itmgoi.in')}\n"
            f"🏅 Best Placement Award — Indian Education Excellence Awards 2022"
        )
 
    def _handle_companies(self, entities, context, extra):
        p = self.kb.get("placement", {}).get("top_recruiters", {})
        it = p.get("IT_software", [])
        tech = p.get("tech_companies", [])
        finance = p.get("banking_finance", [])
        core = p.get("core_engineering", [])
        return (
            f"🏢 **Companies Recruiting from ITM Gwalior:**\n\n"
            f"💻 **IT & Software:**\n  {', '.join(it)}\n\n"
            f"🌐 **Tech Companies:**\n  {', '.join(tech)}\n\n"
            f"🏦 **Banking & Finance:**\n  {', '.join(finance)}\n\n"
            f"🏭 **Core Engineering:**\n  {', '.join(core)}\n\n"
            f"📊 **300+ companies** visit annually!\n"
            f"Avg Package: ₹5.5 LPA | Highest: ₹18 LPA\n\n"
            f"Want to know about placement process or internship opportunities?"
        )
 
    def _handle_campus_timing(self, entities, context, extra):
        c = self.kb.get("college", {})
        return (
            f"⏰ **ITM Gwalior Timings:**\n\n"
            f"🏫 **College & Office:**\n"
            f"  {c.get('office_hours', 'Monday to Saturday, 9:00 AM to 5:00 PM')}\n"
            f"  Sunday: Closed\n\n"
            f"📖 **Library:** {c.get('library_hours', 'Monday to Saturday, 8:00 AM to 8:00 PM')}\n\n"
            f"🏢 **Admission Office:** Mon–Sat, 9 AM – 5 PM\n"
            f"📞 {c.get('admission_phone', ['+91-7773005065'])[0]}"
        )
 
    def _handle_counselling_info(self, entities, context, extra):
        return (
            "📋 **RGPV / DTE MP B.Tech Counselling Process:**\n\n"
            "1️⃣ **JEE Mains Result**\n"
            "   Check your score and qualify for counselling as per DTE MP norms.\n\n"
            "2️⃣ **Register on DTE MP Portal**\n"
            "   Visit dte.mponline.gov.in and create your counselling profile.\n\n"
            "3️⃣ **Document Verification**\n"
            "   Keep 10th, 12th, category, and JEE documents ready.\n\n"
            "4️⃣ **Choice Filling**\n"
            "   Add ITM Gwalior, choose branch preferences, and lock choices.\n\n"
            "5️⃣ **Seat Allotment**\n"
            "   Seats are allotted through counselling rounds based on merit.\n\n"
            "6️⃣ **Admission at College**\n"
            "   Report to ITM Gwalior, submit originals, pay fees, and confirm seat.\n\n"
            "📞 Help: **+91-7773005065**\n"
            f"🌐 Apply: {self.kb.get('college', {}).get('apply_online', 'http://itmgoi.in/OnlineApply_ITMGOI')}"
        )
 
    def _handle_last_date(self, entities, context, extra):
        dates = self.kb.get("important_dates", {})
        return (
            f"📅 **Important Dates — {dates.get('academic_year', '2026-27')} Admissions:**\n\n"
            f"• 📝 Form Start: **{dates.get('form_start_date', 'March 2026')}**\n"
            f"• ⏰ Last Date: **{dates.get('form_last_date', 'May 31, 2026')}**\n"
            f"• 💳 Application Fee: ₹{dates.get('application_fee', 500):,}\n"
            f"• 🎓 JEE Mains: **{dates.get('entrance_exam_date', 'Jan & Apr 2026')}**\n"
            f"• 📊 Result: {dates.get('result_declaration', 'April/May 2026')}\n"
            f"• 🗣 Counselling: {dates.get('counselling_start', 'June 2026')} – {dates.get('counselling_end', 'July 2026')}\n"
            f"• 🏫 Classes Begin: **{dates.get('classes_begin', 'August 2026')}**\n\n"
            f"⚠️ Apply early — seats are limited!\n"
            f"🌐 **http://itmgoi.in/OnlineApply_ITMGOI**\n"
            f"📞 **+91-7773005065**"
        )
 
    def _handle_documents_needed(self, entities, context, extra):
        docs = self.kb.get("documents_required", [])
        if isinstance(docs, dict):
            docs = docs.get("mandatory", []) + docs.get("conditional", [])
        mandatory = docs[:7]
        conditional = docs[7:]
        mandatory_text = "\n".join(f"{i+1}. {doc}" for i, doc in enumerate(mandatory))
        conditional_text = "\n".join(f"  • {doc}" for doc in conditional)
        return (
            f"📄 **Documents Required for Admission:**\n\n"
            f"✅ **Mandatory:**\n{mandatory_text}\n\n"
            f"📎 **If Applicable:**\n{conditional_text}\n\n"
            f"⚠️ All documents must be **self-attested**.\n"
            f"Bring originals + 2 sets of photocopies."
        )
 
    def _handle_hostel_info(self, entities, context, extra):
        h = self.kb.get("hostel", {})
        bh = h.get("boys_hostel", {})
        gh = h.get("girls_hostel", {})
        return (
            f"🏠 **Hostel at ITM Gwalior:**\n\n"
            f"👦 **Boys Hostel:**\n"
            f"  • Capacity: {bh.get('capacity', 500)} students\n"
            f"  • Fee: **₹{bh.get('fees_per_year', 68000):,}/year** (mess included)\n"
            f"  • Rooms: {', '.join(bh.get('room_types', ['2-sharing', '3-sharing']))}\n"
            f"  • Facilities: 24/7 Security, WiFi, Hot Water, Mess, Indoor Sports\n\n"
            f"👧 **Girls Hostel:**\n"
            f"  • Capacity: {gh.get('capacity', 300)} students\n"
            f"  • Fee: **₹{gh.get('fees_per_year', 72000):,}/year** (mess included)\n"
            f"  • Female wardens 24/7\n"
            f"  • Facilities: Security, WiFi, Hot Water, Mess, Common Room\n\n"
            f"📧 Contact: **{h.get('contact', 'hostel@itmgoi.in')}**\n"
            f"📞 Warden: {h.get('warden_phone', '+91-751-2440056')}"
        )
 
    def _handle_contact_info(self, entities, context, extra):
        c = self.kb.get("college", {})
        phones = " / ".join(c.get("phone", ["+91-751-2440056"]))
        adm_phones = " / ".join(c.get("admission_phone", ["+91-7773005065"]))
        return (
            f"📞 **Contact ITM Gwalior:**\n\n"
            f"🏫 **Main Office:**\n"
            f"  📱 {phones}\n"
            f"  📧 {c.get('email', 'info@itmgoi.in')}\n\n"
            f"🎓 **Admission Helpline:**\n"
            f"  📱 **{adm_phones}**\n"
            f"  📧 **{c.get('admissions_email', 'admission@itmgoi.in')}**\n\n"
            f"🌐 Website: **{c.get('website', 'www.itmgoi.in')}**\n"
            f"📍 Address: {c.get('address', 'ITM Campus, NH-75 Sithouli, Gwalior - 475001')}\n"
            f"⏰ {c.get('office_hours', 'Mon–Sat, 9 AM – 5 PM')}\n"
            f"🗺 Maps: {c.get('google_maps', 'https://bit.ly/itm-gwalior')}"
        )
 
    def _handle_scholarship(self, entities, context, extra):
        scholarships = self.kb.get("scholarships", [])
        lines = []
        for i, s in enumerate(scholarships, 1):
            lines.append(
                f"{i}. **{s['name']}:**\n"
                f"   💰 {s['benefit']}\n"
                f"   ✅ Eligibility: {s['eligibility']}"
            )
        return (
            f"🏆 **Scholarships at ITM Gwalior:**\n\n"
            + "\n\n".join(lines)
            + "\n\n📝 Apply within **30 days of admission**.\n"
            "📧 **admission@itmgoi.in** | 📞 **+91-7773005065**"
        )
 
    def _handle_facilities(self, entities, context, extra):
        f = self.kb.get("facilities", {})
        academic = "\n  ".join(f"• {x}" for x in f.get("academic", []))
        sports = "\n  ".join(f"• {x}" for x in f.get("sports", []))
        other = "\n  ".join(f"• {x}" for x in f.get("other", []))
        return (
            f"🏛️ **Campus Facilities at ITM Gwalior:**\n\n"
            f"📚 **Academic:**\n  {academic}\n\n"
            f"⚽ **Sports:**\n  {sports}\n\n"
            f"🏥 **Other Amenities:**\n  {other}\n\n"
            f"🌐 Green, WiFi-enabled, secure campus!"
        )
 
    def _handle_internship(self, entities, context, extra):
        p = self.kb.get("placement", {})
        return (
            "💼 **Internship Program at ITM Gwalior:**\n\n"
            "🔑 **Mandatory Summer Internship:**\n"
            "  • 45-day internship after 2nd/3rd year\n"
            "  • Industry exposure for all students\n\n"
            "🌐 **Virtual Internship (EduSkills + AICTE):**\n"
            "  • AWS, Microsoft, Cisco, Google certifications\n"
            f"  • {p.get('internship_record', '5 Lakh+ internships (World Record!)')}\n"
            "  • Ranked #35 All India (EduSkills 2024)\n\n"
            "🏢 **Partner Companies:**\n"
            "  TCS, Infosys, Wipro, AWS, Microsoft & 100+ more\n\n"
            "📞 TAP Cell: **+91-9691973919**\n"
            "📧 arpit.chauhan@itmuniversity.ac.in"
        )
 
    def _handle_exam_schedule(self, entities, context, extra):
        dates = self.kb.get("important_dates", {})
        centers = ", ".join(dates.get("exam_centers", ["Gwalior", "Bhopal", "Indore"]))
        return (
            f"📝 **Entrance Exam Details — {dates.get('academic_year', '2026-27')}:**\n\n"
            f"🔧 **For B.Tech (RGPV Affiliated):**\n"
            f"  • Exam: **JEE Mains** (Jan & Apr sessions)\n"
            f"  • Admission via: RGPV / DTE MP Counselling\n"
            f"  • Pattern: MCQ | Physics + Chemistry + Maths\n"
            f"  • Duration: 3 hours | Syllabus: NCERT 11th & 12th\n"
            f"  • Centers: {centers}\n\n"
            f"💻 **BCA / BBA / B.Com / B.Sc:**\n"
            f"  • No entrance exam! Direct merit-based admission\n\n"
            f"💼 **MBA:** CAT / MAT / XAT / MP-MAT score required\n"
            f"🎓 **M.Tech:** GATE score preferred\n\n"
            f"📞 More details: **+91-7773005065**"
        )
 
    def _handle_result_status(self, entities, context, extra):
        dates = self.kb.get("important_dates", {})
        return (
            f"📊 **Result & Merit List — ITM Gwalior:**\n\n"
            f"📅 **Tentative Timeline ({dates.get('academic_year', '2026-27')}):**\n"
            f"  • JEE Result: {dates.get('result_declaration', 'April/May 2026')}\n"
            f"  • 1st Merit List: {dates.get('first_merit_list', 'July 2026')}\n"
            f"  • 2nd Merit List: {dates.get('second_merit_list', 'July 2026 (if required)')}\n"
            f"  • Counselling: {dates.get('counselling_start', 'June')} – {dates.get('counselling_end', 'July 2026')}\n\n"
            f"🔍 **How to Check:**\n"
            f"  • Visit **www.itmgoi.in** → Admission section\n"
            f"  • DTE MP: dte.mponline.gov.in\n\n"
            f"📞 Result queries: **+91-7773005065**"
        )
 
    def _handle_clubs(self, entities, context, extra):
        clubs = self.kb.get("clubs_cells", [])
        clubs_text = "\n  ".join(f"• {c}" for c in clubs)
        return (
            f"🎉 **Student Life at ITM Gwalior:**\n\n"
            f"🎭 **Clubs & Cells:**\n  {clubs_text}\n\n"
            f"🏆 **Annual Events:**\n"
            f"  • DiversITM — Cultural & Technical Fest\n"
            f"  • Pratibha Samman — Merit Award Ceremony\n"
            f"  • ITM International Conference\n"
            f"  • Sports Tournaments\n\n"
            f"💻 IEEE Student Chapter | AWS Cloud Club | Coding Club\n"
            f"🌱 NSS | UBA Cell | Women Empowerment Cell\n\n"
            f"Life at ITM = Academics + Activities = Complete Development! 🌟"
        )

    def _handle_course_recommendation(self, entities, context, extra):
        return (
            "🎯 **Course Recommendation Guide:**\n\n"
            "• Coding, software, AI, data, security -> **B.Tech CSE**\n"
            "• Web/app development, IT support -> **B.Tech IT** or **BCA**\n"
            "• Hardware, electronics, telecom -> **B.Tech ECE**\n"
            "• Machines, production, automobiles -> **B.Tech ME**\n"
            "• Civil works, construction, infrastructure -> **B.Tech Civil**\n"
            "• Business, management, entrepreneurship -> **BBA** or **MBA**\n\n"
            "If you share your interest, I can suggest the best branch for you."
        )

    def _handle_career_scope(self, entities, context, extra):
        course_name = (
            entities.get("course")
            or context.get("active_course")
            or context.get("entities_so_far", {}).get("course")
        )
        if course_name:
            course_info = self._find_course(course_name)
            if course_info:
                career_options = course_info.get("career_prospects", [])
                return (
                    f"🚀 **Career Scope for {course_info['short']}:**\n\n"
                    f"• Career Roles: {', '.join(career_options) if career_options else 'N/A'}\n"
                    f"• Typical Salary: {course_info.get('avg_salary', 'Depends on role and skills')}\n"
                    f"• Higher Studies: M.Tech / MBA / MCA / MS (as applicable)\n"
                    f"• Govt Jobs: GATE, PSU, SSC, state exams where relevant\n"
                )
        return (
            "🚀 **Career Scope at ITM Gwalior:**\n\n"
            "• B.Tech CSE/IT -> software, product, AI, cloud, cybersecurity jobs\n"
            "• B.Tech ECE -> electronics, telecom, embedded, VLSI roles\n"
            "• B.Tech ME -> core engineering, production, design, automobile roles\n"
            "• B.Tech Civil -> construction, design, infrastructure, govt projects\n"
            "• BCA/MCA -> software development, web/app, IT support\n"
            "• BBA/MBA -> management, marketing, finance, HR, operations\n\n"
            "Share a branch name and I’ll narrow it down."
        )

    def _handle_total_branches(self, entities, context, extra):
        courses = self.kb.get("courses", {})
        ug = courses.get("ug", [])
        pg = courses.get("pg", [])
        btech = [course for course in ug if course.get("short", "").startswith("B.Tech")]
        specializations = sum(len(course.get("specializations", [])) for course in btech)
        ug_text = ", ".join(course.get("short", "") for course in ug if course.get("short"))
        pg_text = ", ".join(course.get("short", "") for course in pg if course.get("short"))
        return (
            f"📚 **Total Programs at ITM Gwalior:**\n\n"
            f"• B.Tech Branches: {len(btech)}\n"
            f"• CSE Specializations: {specializations}\n"
            f"• Other UG Programs: {ug_text}\n"
            f"• PG Programs: {pg_text}\n\n"
            "Ask me about any branch and I’ll give the full details."
        )
 
    def _handle_how_to_reach(self, entities, context, extra):
        c = self.kb.get("college", {})
        return (
            f"🗺️ **How to Reach ITM Gwalior:**\n\n"
            f"📍 **Address:**\n"
            f"  {c.get('address', 'ITM Campus, Opp. Sithouli Railway Station, NH-75, Gwalior - 475001')}\n\n"
            f"🚂 **By Train (Easiest!):**\n"
            f"  Nearest: **Sithouli Railway Station** — college is right opposite!\n"
            f"  From Gwalior Junction: ~15 km on NH-75 Jhansi Road\n\n"
            f"🚌 **By Road:**\n"
            f"  ~25-30 mins from Gwalior city on NH-75 towards Jhansi\n"
            f"  Auto/cab easily available from Gwalior station\n\n"
            f"✈️ **By Air:**\n"
            f"  Gwalior Airport (~20 km) — cab available\n\n"
            f"🗺 Google Maps: {c.get('google_maps', 'https://bit.ly/itm-gwalior')}"
        )
 
    def _handle_slot_booking(self, entities, context, extra):
        return "📅 I'll help you book a counselling appointment at ITM Gwalior! Let me collect your details."
 
    def _handle_angry(self, entities, context, extra):
        return ANGRY_RESPONSE
 
    def _handle_fallback(self, entities, context, extra):
        return random.choice(FALLBACK_RESPONSES)
 
    # ── Helpers ───────────────────────────────────────────────────────────────
 
    def _load_kb(self):
        try:
            with open(KB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error("Failed to load knowledge base: %s", exc)
            return {}
 
    def _find_course(self, course_name):
        course_lower = course_name.lower().strip()
        candidates = []
        mapping = {}
        for level in ("ug", "pg"):
            for course in self.kb.get("courses", {}).get(level, []):
                name = course.get("name", "").lower()
                short = course.get("short", "").lower()
                candidates.extend([name, short])
                mapping[name] = course
                mapping[short] = course
                for s in course.get("specializations", []) or []:
                    sval = s.lower()
                    candidates.append(sval)
                    mapping[sval] = course

        # direct substring match
        for key, course in mapping.items():
            if course_lower in key or key in course_lower:
                return course

        # fuzzy match as fallback
        match = get_close_matches(course_lower, candidates, n=1, cutoff=0.7)
        if match:
            return mapping.get(match[0])
        return None
 