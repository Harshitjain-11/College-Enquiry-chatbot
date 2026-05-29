"""
Response Generator for ITM Gwalior College Enquiry Chatbot.
Branch-aware, specialization-aware, context-aware responses.
"""
 
import json
import random
import logging
from pathlib import Path
 
logger = logging.getLogger(__name__)
 
BASE_DIR = Path(__file__).resolve().parent.parent
KB_PATH   = BASE_DIR / "data" / "knowledge_base.json"
 
# ── Quick replies ──────────────────────────────────────────────────────────────
QUICK_REPLIES: dict[str, list[str]] = {
    "greeting":             ["Admission Process", "Courses Offered", "Fee Structure", "Book Appointment"],
    "college_overview":     ["Courses Offered", "Placement Info", "Admission Process", "Contact Us"],
    "about_college":        ["Courses Offered", "Placement Info", "Admission Process", "Contact Us"],
    "admission_process":    ["Documents Needed", "Last Date to Apply", "Eligibility Criteria", "Fee Structure"],
    "courses_offered":      ["Fee Structure", "Eligibility Criteria", "Placement Info", "Scholarship Info"],
    "specializations":      ["Fee Structure", "Eligibility Criteria", "Admission Process", "Placement Info"],
    "eligibility":          ["Courses Offered", "Fee Structure", "Admission Process", "Contact Us"],
    "eligibility_check":    ["Courses Offered", "Fee Structure", "Admission Process", "Contact Us"],
    "fees_structure":       ["Scholarship Info", "Apply Now", "Documents Needed", "Contact Us"],
    "placement":            ["Companies List", "Courses Offered", "Book Appointment", "Contact Us"],
    "companies_recruiters": ["Placement Info", "Courses Offered", "Fee Structure", "Book Appointment"],
    "campus_timing":        ["Contact Us", "Book Appointment", "Admission Process", "How to Reach"],
    "counselling_info":     ["Documents Needed", "Fee Structure", "Book Appointment", "Contact Us"],
    "course_recommendation":["Fee Structure", "Eligibility Criteria", "Admission Process", "Book Appointment"],
    "course_details":       ["Fee Structure", "Eligibility Criteria", "Placement Info", "Book Appointment"],
    "career_scope":         ["Courses Offered", "Placement Info", "Fee Structure", "Book Appointment"],
    "total_branches":       ["Fee Structure", "Eligibility Criteria", "Placement Info", "Book Appointment"],
    "last_date":            ["Admission Process", "Documents Needed", "Contact Us", "Book Appointment"],
    "documents_needed":     ["Admission Process", "Fee Structure", "Contact Us", "Book Appointment"],
    "hostel_info":          ["Fee Structure", "Contact Us", "Admission Process", "Book Appointment"],
    "contact_info":         ["Admission Process", "Book Appointment", "Courses Offered", "Fee Structure"],
    "scholarship":          ["Eligibility Criteria", "Fee Structure", "Admission Process", "Contact Us"],
    "facilities":           ["Hostel Info", "Courses Offered", "Contact Us", "Book Appointment"],
    "internship":           ["Placement Info", "Courses Offered", "Contact Us", "Book Appointment"],
    "exam_schedule":        ["Admission Process", "Last Date to Apply", "Eligibility Criteria", "Contact Us"],
    "result_status":        ["Documents Needed", "Contact Us", "Fee Structure", "Book Appointment"],
    "clubs_activities":     ["Facilities", "Courses Offered", "Contact Us", "Book Appointment"],
    "how_to_reach":         ["Contact Us", "Book Appointment", "Hostel Info", "Admission Process"],
    "slot_booking":         ["Fee Structure", "Courses Offered", "Contact Us"],
    "goodbye":              [],
    "angry_user":           ["Contact Us", "Book Appointment"],
    "fallback":             ["Admission Process", "Courses Offered", "Fee Structure", "Contact Us"],
}
 
FALLBACK_RESPONSES = [
    "🤔 Mujhe samajh nahi aaya. Main in topics mein help kar sakta hoon:\n\n"
    "📚 Courses & Specializations (AIML, CSE, IT, ECE, ME, Civil...)\n"
    "💰 Fees & Scholarships\n📋 Admission Process (B.Tech/MBA/BCA)\n"
    "🏆 Placement & Companies\n🏠 Hostel\n📅 Book Campus Visit\n\n"
    "Kripya apna sawaal dobara puchein! 😊",
    "Hmm, could you rephrase? Try asking about:\n"
    "Courses | Fees | Admission | Placement | AIML | Hostel\n\n"
    "Or call: +91-7773005065 for direct help!",
]
 
ANGRY_RESPONSE = (
    "I sincerely apologize for the inconvenience! 🙏 "
    "Please call us directly at **+91-7773005065** or email **admission@itmgoi.in** — "
    "our counsellors will be happy to assist you personally."
)
 
# ── Specialization keyword map ─────────────────────────────────────────────────
SPEC_MAP = {
    "aiml":             ("CSE-AIML", "B.Tech CSE", "Artificial Intelligence & Machine Learning"),
    "ai ml":            ("CSE-AIML", "B.Tech CSE", "Artificial Intelligence & Machine Learning"),
    "artificial intelligence": ("CSE-AIML", "B.Tech CSE", "Artificial Intelligence & Machine Learning"),
    "machine learning": ("CSE-AIML", "B.Tech CSE", "Artificial Intelligence & Machine Learning"),
    "data science":     ("CSE-DS",   "B.Tech CSE", "Data Science"),
    "ds":               ("CSE-DS",   "B.Tech CSE", "Data Science"),
    "cybersecurity":    ("CSE-Cyber","B.Tech CSE", "Cyber Security"),
    "cyber security":   ("CSE-Cyber","B.Tech CSE", "Cyber Security"),
    "cyber":            ("CSE-Cyber","B.Tech CSE", "Cyber Security"),
    "iot":              ("CSE-IoT",  "B.Tech CSE", "Internet of Things"),
    "internet of things":("CSE-IoT","B.Tech CSE", "Internet of Things"),
    "cloud":            ("CSE-Cloud","B.Tech CSE", "Cloud Computing"),
    "cloud computing":  ("CSE-Cloud","B.Tech CSE", "Cloud Computing"),
    "vlsi":             ("ECE-VLSI", "B.Tech ECE", "VLSI Design"),
    "embedded":         ("ECE-ES",   "B.Tech ECE", "Embedded Systems"),
    "automobile":       ("ME-Auto",  "B.Tech ME",  "Automobile Engineering"),
    "mechanical":       ("ME",       "B.Tech ME",  "Mechanical Engineering"),
    "structural":       ("Civil-SE", "B.Tech Civil","Structural Engineering"),
    "civil":            ("Civil",    "B.Tech Civil","Civil Engineering"),
    "cse":              ("CSE",      "B.Tech CSE", "Computer Science Engineering"),
    "computer science": ("CSE",      "B.Tech CSE", "Computer Science Engineering"),
    "information technology": ("IT", "B.Tech IT",  "Information Technology"),
    "btech it":         ("IT",       "B.Tech IT",  "Information Technology"),
    "ece":              ("ECE",      "B.Tech ECE", "Electronics & Communication"),
    "electronics":      ("ECE",      "B.Tech ECE", "Electronics & Communication"),
    "ec":               ("ECE",      "B.Tech ECE", "Electronics & Communication"),
}
 
 
def _detect_specialization(text: str) -> tuple | None:
    """Return (spec_code, branch, full_name) if a specialization keyword is found."""
    t = text.lower()
    # longer keywords first for specificity
    for kw in sorted(SPEC_MAP.keys(), key=len, reverse=True):
        if kw in t:
            return SPEC_MAP[kw]
    return None
 
 
class ResponseGenerator:
    def __init__(self):
        self.kb = self._load_kb()
        logger.info("ResponseGenerator initialized.")
 
    # ── Public API ─────────────────────────────────────────────────────────────
 
    def generate(self, intent, entities, context, slot_state="IDLE", extra_data=None):
        extra_data = extra_data or {}
        if slot_state not in ("IDLE", "COMPLETED", "CANCELLED") and extra_data.get("slot_prompt"):
            return extra_data["slot_prompt"], []
        handler = self._get_handler(intent)
        response = handler(entities, context, extra_data)
        quick_replies = QUICK_REPLIES.get(intent, QUICK_REPLIES["fallback"])
        return response, quick_replies
 
    # ── Handler registry ───────────────────────────────────────────────────────
 
    def _get_handler(self, intent):
        return {
            "greeting":             self._handle_greeting,
            "goodbye":              self._handle_goodbye,
            "college_overview":     self._handle_about_college,
            "about_college":        self._handle_about_college,
            "admission_process":    self._handle_admission_process,
            "courses_offered":      self._handle_courses_offered,
            "specializations":      self._handle_specializations,
            "eligibility":          self._handle_eligibility,
            "eligibility_check":    self._handle_eligibility_check,
            "fees_structure":       self._handle_fees_structure,
            "placement":            self._handle_placement,
            "companies_recruiters": self._handle_companies,
            "campus_timing":        self._handle_campus_timing,
            "counselling_info":     self._handle_counselling_info,
            "course_recommendation":self._handle_course_recommendation,
            "course_details":       self._handle_course_details,
            "career_scope":         self._handle_career_scope,
            "total_branches":       self._handle_total_branches,
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
        }.get(intent, self._handle_fallback)
 
    # ── Handlers ───────────────────────────────────────────────────────────────
 
    def _handle_greeting(self, entities, context, extra):
        return random.choice([
            "Hello! 👋 Welcome to **Institute of Technology & Management, Gwalior**!\n"
            "I'm your virtual admission counsellor. Ask me about admissions, courses, fees, placement, or scholarships! 😊",
            "Hi there! 🎓 I'm the ITM Gwalior chatbot.\nWhat would you like to know? Admissions | Fees | Courses | AIML | Placement?",
            "Namaste! 🙏 Welcome to ITM Gwalior — **NAAC 'A' Grade Institute**.\nI'm here to guide you through your admission journey. What's on your mind?",
        ])
 
    def _handle_goodbye(self, entities, context, extra):
        return random.choice([
            "Thank you for chatting! 🎓 Best of luck with your admission.\nVisit **www.itmgoi.in** or call **+91-7773005065** anytime!",
            "Goodbye! 👋 Hope to see you on campus soon.\nFor info: **www.itmgoi.in** | **+91-7773005065**",
        ])
 
    def _handle_about_college(self, entities, context, extra):
        c = self.kb.get("college", {})
        awards = c.get("awards", [])
        awards_text = "\n  ".join(f"🏅 {a}" for a in awards[:4])
        return (
            f"🎓 **About Institute of Technology & Management, Gwalior:**\n\n"
            f"📍 Established: **{c.get('established', 1997)}** (29+ years of excellence)\n"
            f"🏆 NAAC Grade: **'A'** (CGPA {c.get('naac_cgpa', 3.01)}, valid till Nov 2030)\n"
            f"🎖️ NBA Accredited | AICTE Approved | RGPV Affiliated\n"
            f"🌐 Website: **{c.get('website', 'www.itmgoi.in')}**\n\n"
            f"✨ Key Achievements:\n  {awards_text}\n\n"
            f"📞 Admission: **+91-7773005065** | 📧 **admission@itmgoi.in**"
        )
 
    def _handle_admission_process(self, entities, context, extra):
        """Branch/specialization-aware admission process."""
        # Detect from entities + context message
        raw = extra.get("user_message", "") or ""
        ctx_course = (entities.get("course") or
                      context.get("entities_so_far", {}).get("course") or "")
        combined = (raw + " " + ctx_course).lower()
 
        spec = _detect_specialization(combined)
 
        # MBA specific
        if "mba" in combined:
            return (
                "📋 **MBA Admission Process at ITM Gwalior:**\n\n"
                "✅ **Eligibility:** Any graduation with 50% marks\n"
                "📝 **Entrance:** CAT / MAT / XAT / MP-MAT score required\n\n"
                "**Steps:**\n"
                "1. Appear in CAT/MAT/XAT/MP-MAT exam\n"
                "2. Visit www.itmgoi.in → Online Apply\n"
                "3. Fill form & pay ₹500 application fee\n"
                "4. Submit score card + academic documents\n"
                "5. Attend GD/PI (Group Discussion + Personal Interview)\n"
                "6. Merit list → Pay fees → Confirm seat\n\n"
                "💼 Specializations: Marketing | Finance | HR | Operations | Analytics\n"
                "💰 Fee: ₹88,000/year | Duration: 2 years\n"
                "📞 **+91-7773005065** | 📧 admission@itmgoi.in"
            )
 
        # MCA specific
        if "mca" in combined:
            return (
                "📋 **MCA Admission at ITM Gwalior:**\n\n"
                "✅ **Eligibility:** BCA/B.Sc CS/IT with 55% + Maths\n"
                "📝 **Direct merit-based admission** — No entrance exam!\n\n"
                "**Steps:**\n"
                "1. Visit www.itmgoi.in → Online Apply\n"
                "2. Fill form & pay ₹500 fee\n"
                "3. Submit documents\n"
                "4. Merit list → Confirm seat\n\n"
                "💰 Fee: ₹58,000/year | Duration: 2 years\n"
                "📞 **+91-7773005065**"
            )
 
        # BCA/BBA/B.Com — direct admission
        for c in ["bca", "bba", "b.com", "bcom", "b.sc", "bsc"]:
            if c in combined:
                name = c.upper()
                return (
                    f"📋 **{name} Admission at ITM Gwalior:**\n\n"
                    "✅ **Direct merit-based admission** — No entrance exam needed!\n\n"
                    "**Steps:**\n"
                    "1. Visit www.itmgoi.in → Online Apply\n"
                    "2. Fill form & pay ₹500 application fee\n"
                    "3. Upload 12th marksheet & documents\n"
                    "4. Merit list published → Pay fees → Confirm seat\n\n"
                    "📞 **+91-7773005065** | 📧 admission@itmgoi.in"
                )
 
        # B.Tech specialization aware
        if spec:
            spec_code, branch, spec_name = spec
            return (
                f"📋 **Admission Process for {branch} ({spec_name}) at ITM Gwalior:**\n\n"
                f"✅ **Eligibility:** 60% in PCM (Physics, Chemistry, Maths) in 12th\n"
                f"📝 **Entrance:** JEE Mains score + RGPV DTE MP Counselling\n"
                f"💰 **Fee:** ₹87,000/year (4 years)\n\n"
                f"**Step-by-Step Process:**\n"
                f"1. 📝 JEE Mains exam (Jan or Apr session) dein\n"
                f"2. 🌐 DTE MP portal register karein: dte.mponline.gov.in\n"
                f"3. 📄 Documents verify karein (10th, 12th, JEE scorecard)\n"
                f"4. 🏫 Choice filling mein **ITM Gwalior** + **{spec_name}** select karein\n"
                f"5. 🎯 Merit-based seat allotment (multiple rounds)\n"
                f"6. 🏛️ ITM campus report karein, originals submit karein\n"
                f"7. 💳 Fees pay karein aur seat confirm karein\n\n"
                f"🌐 Apply: http://itmgoi.in/OnlineApply_ITMGOI\n"
                f"📞 **+91-7773005065** | 📧 admission@itmgoi.in"
            )
 
        # Generic B.Tech process
        steps = self.kb.get("admission_process", [])
        steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
        return (
            f"📋 **Admission Process at ITM Gwalior:**\n\n"
            f"{steps_text}\n\n"
            f"🌐 Apply: http://itmgoi.in/OnlineApply_ITMGOI\n"
            f"📞 **+91-7773005065** / +91-7773001624\n"
            f"📧 admission@itmgoi.in"
        )
 
    def _handle_courses_offered(self, entities, context, extra):
        return (
            "🎓 **Courses at ITM Gwalior (RGPV Affiliated):**\n\n"
            "**🔧 B.Tech Engineering (4 years, JEE Mains required):**\n"
            "  • B.Tech CSE — AIML ✅ | Data Science ✅ | Cyber Security ✅ | IoT | Cloud\n"
            "  • B.Tech IT  — Web Tech | Mobile App | Network Security\n"
            "  • B.Tech ECE — VLSI | Embedded Systems | Signal Processing\n"
            "  • B.Tech ME  — Automobile | Thermal | Manufacturing\n"
            "  • B.Tech Civil — Structural | Environmental | Transportation\n\n"
            "**💻 UG Programs (3 years, Direct Admission):**\n"
            "  • BCA (₹48k/yr) | BBA (₹42k/yr) | B.Sc (₹36k/yr) | B.Com (₹32k/yr)\n\n"
            "**📚 PG Programs:**\n"
            "  • M.Tech (₹92k/yr) | MBA (₹88k/yr) | MCA (₹58k/yr) | M.Sc (₹46k/yr)\n\n"
            "Kisi specific course ke baare mein poochein — fees, eligibility, career sab bataunga! 😊"
        )
 
    def _handle_specializations(self, entities, context, extra):
        raw = extra.get("user_message", "") or ""
        ctx_course = (entities.get("course") or
                      context.get("entities_so_far", {}).get("course") or "")
        combined = (raw + " " + ctx_course).lower()
        spec = _detect_specialization(combined)
 
        if spec:
            spec_code, branch, spec_name = spec
            # Return detailed info for that specific specialization
            details = {
                "CSE-AIML": (
                    "🤖 **B.Tech CSE — Artificial Intelligence & Machine Learning (AIML):**\n\n"
                    "📚 **Kya Seekhoge:**\n"
                    "  Python, Machine Learning, Deep Learning, Neural Networks,\n"
                    "  Natural Language Processing, Computer Vision, Data Analytics,\n"
                    "  TensorFlow/PyTorch, Big Data, Cloud AI\n\n"
                    "💼 **Career Options:**\n"
                    "  AI/ML Engineer, Data Scientist, NLP Engineer,\n"
                    "  Computer Vision Engineer, AI Researcher, MLOps Engineer\n\n"
                    "💰 **Fee:** ₹87,000/year | 4 years | ₹3.48 lakh total\n"
                    "✅ **Eligibility:** 60% in PCM in 12th + JEE Mains\n"
                    "🏆 **Placement:** 90%+ | Avg ₹5.5 LPA | Highest ₹18 LPA\n"
                    "🌟 ITM is **Microsoft Centre of Excellence** & **AWS Academy Member!**\n\n"
                    "📞 Admission: +91-7773005065"
                ),
                "CSE-DS": (
                    "📊 **B.Tech CSE — Data Science (DS):**\n\n"
                    "📚 **Kya Seekhoge:**\n"
                    "  Statistics, Python, R, Machine Learning, Data Visualization,\n"
                    "  SQL/NoSQL, Tableau, Power BI, Big Data (Hadoop/Spark),\n"
                    "  Predictive Analytics, Business Intelligence\n\n"
                    "💼 **Career Options:**\n"
                    "  Data Scientist, Data Analyst, Business Analyst,\n"
                    "  Data Engineer, BI Developer, Research Analyst\n\n"
                    "💰 **Fee:** ₹87,000/year | 4 years\n"
                    "✅ **Eligibility:** 60% in PCM in 12th + JEE Mains\n"
                    "🏆 **Avg Package:** ₹5.5–8 LPA\n\n"
                    "📞 Admission: +91-7773005065"
                ),
                "CSE-Cyber": (
                    "🔐 **B.Tech CSE — Cyber Security:**\n\n"
                    "📚 **Kya Seekhoge:**\n"
                    "  Network Security, Ethical Hacking, Cryptography,\n"
                    "  Penetration Testing, Digital Forensics, Firewall & IDS,\n"
                    "  Cloud Security, Malware Analysis, Security Auditing\n\n"
                    "💼 **Career Options:**\n"
                    "  Cybersecurity Analyst, Ethical Hacker, Security Engineer,\n"
                    "  Penetration Tester, SOC Analyst, CISO (future)\n\n"
                    "💰 **Fee:** ₹87,000/year | 4 years\n"
                    "✅ **Eligibility:** 60% in PCM in 12th + JEE Mains\n"
                    "🏆 **Demand:** TOP skill in 2024-2030!\n\n"
                    "📞 Admission: +91-7773005065"
                ),
                "CSE-IoT": (
                    "🌐 **B.Tech CSE — Internet of Things (IoT):**\n\n"
                    "📚 **Kya Seekhoge:**\n"
                    "  Embedded Systems, Sensors, Arduino/Raspberry Pi,\n"
                    "  Wireless Protocols (WiFi/BLE/Zigbee), Cloud IoT,\n"
                    "  Smart Home/City, Industrial IoT, Edge Computing\n\n"
                    "💼 **Career Options:**\n"
                    "  IoT Engineer, Embedded Developer, Product Engineer,\n"
                    "  Hardware+Software hybrid roles\n\n"
                    "💰 **Fee:** ₹87,000/year | 4 years\n"
                    "✅ **Eligibility:** 60% in PCM in 12th + JEE Mains\n\n"
                    "📞 Admission: +91-7773005065"
                ),
                "CSE-Cloud": (
                    "☁️ **B.Tech CSE — Cloud Computing:**\n\n"
                    "📚 **Kya Seekhoge:**\n"
                    "  AWS, Microsoft Azure, Google Cloud,\n"
                    "  DevOps, Docker, Kubernetes, CI/CD,\n"
                    "  Cloud Architecture, Serverless Computing\n\n"
                    "💼 **Career Options:**\n"
                    "  Cloud Engineer, DevOps Engineer, Cloud Architect,\n"
                    "  Site Reliability Engineer, Platform Engineer\n\n"
                    "💰 **Fee:** ₹87,000/year | 4 years\n"
                    "✅ **Eligibility:** 60% in PCM in 12th + JEE Mains\n"
                    "🌟 ITM = **AWS Academy Member** — industry certification included!\n\n"
                    "📞 Admission: +91-7773005065"
                ),
            }
            if spec_code in details:
                return details[spec_code]
 
        # Generic — show all specializations
        return (
            "🎓 **Sari Specializations at ITM Gwalior:**\n\n"
            "💻 **B.Tech CSE (₹87,000/yr) — 5 Specializations:**\n"
            "  ✅ CS-AIML (Artificial Intelligence & Machine Learning)\n"
            "  ✅ CS-Data Science\n"
            "  ✅ CS-Cyber Security\n"
            "  ✅ CS-IoT (Internet of Things)\n"
            "  ✅ CS-Cloud Computing (AWS Academy Partner)\n\n"
            "🌐 **B.Tech IT (₹85,000/yr) — 4 Specializations:**\n"
            "  • Web Technologies | Mobile App Dev | Network Security | Database Mgmt\n\n"
            "📡 **B.Tech ECE (₹84,000/yr):**\n"
            "  • VLSI Design | Embedded Systems | Signal Processing\n\n"
            "⚙️ **B.Tech ME (₹82,000/yr):**\n"
            "  • Automobile | Thermal Engineering | Manufacturing | CAD/CAM\n\n"
            "🏗️ **B.Tech Civil (₹80,000/yr):**\n"
            "  • Structural | Environmental | Transportation Engineering\n\n"
            "🌟 ITM = **Microsoft Centre of Excellence** + **AWS Academy Member!**\n"
            "📞 +91-7773005065 | Kisi bhi specialization ke baare mein poochein!"
        )
 
    def _handle_eligibility(self, entities, context, extra):
        raw = extra.get("user_message", "") or ""
        ctx_course = (entities.get("course") or
                      context.get("entities_so_far", {}).get("course") or "")
        combined = (raw + " " + ctx_course).lower()
 
        spec = _detect_specialization(combined)
 
        # MBA
        if "mba" in combined:
            return (
                "📋 **MBA Eligibility at ITM Gwalior:**\n\n"
                "✅ Any graduation with minimum **50% marks**\n"
                "📝 Entrance: CAT / MAT / XAT / MP-MAT score required\n"
                "⏱ Duration: 2 years\n"
                "💰 Fee: ₹88,000/year\n\n"
                "📞 More info: +91-7773005065"
            )
 
        # MCA
        if "mca" in combined:
            return (
                "📋 **MCA Eligibility at ITM Gwalior:**\n\n"
                "✅ BCA / B.Sc (CS/IT) with minimum **55% marks**\n"
                "📝 Mathematics compulsory in qualifying exam\n"
                "📝 Direct merit-based admission — No entrance exam!\n"
                "⏱ Duration: 2 years | 💰 Fee: ₹58,000/year\n\n"
                "📞 More info: +91-7773005065"
            )
 
        # BCA
        if "bca" in combined:
            return (
                "📋 **BCA Eligibility at ITM Gwalior:**\n\n"
                "✅ 12th pass with minimum **55% marks**\n"
                "📝 Mathematics as a subject in 12th compulsory\n"
                "📝 Direct merit-based admission — No JEE required!\n"
                "⏱ Duration: 3 years | 💰 Fee: ₹48,000/year\n\n"
                "📞 More info: +91-7773005065"
            )
 
        # BBA/B.Com
        if "bba" in combined or "b.com" in combined or "bcom" in combined:
            return (
                "📋 **BBA/B.Com Eligibility at ITM Gwalior:**\n\n"
                "✅ 12th pass with minimum **50% marks** (any stream)\n"
                "📝 No entrance exam — Direct merit-based admission!\n"
                "⏱ Duration: 3 years\n"
                "💰 BBA: ₹42,000/year | B.Com: ₹32,000/year\n\n"
                "📞 More info: +91-7773005065"
            )
 
        # B.Tech specialization
        if spec:
            spec_code, branch, spec_name = spec
            return (
                f"📋 **Eligibility for {branch} — {spec_name}:**\n\n"
                f"✅ Minimum **60% marks in PCM** (Physics, Chemistry, Maths) in 12th\n"
                f"📝 **JEE Mains** score required\n"
                f"🎯 Admission via **RGPV DTE MP Counselling** (dte.mponline.gov.in)\n"
                f"⏱ Duration: 4 years\n"
                f"💰 Fee: ₹87,000/year\n"
                f"💺 Seats: 120 (CSE total)\n\n"
                f"💡 **Note:** {spec_name} is a specialization within B.Tech CSE.\n"
                f"Aap 12th mein choice filling ke time yeh specialization choose kar sakte ho.\n\n"
                f"📞 +91-7773005065 | 📧 admission@itmgoi.in"
            )
 
        # Generic
        return (
            "📋 **Eligibility Criteria at ITM Gwalior:**\n\n"
            "🔧 **B.Tech (CSE/IT/ECE/ME/Civil):**\n"
            "   ✅ 60% in PCM in 12th + JEE Mains + RGPV DTE MP Counselling\n\n"
            "💻 **BCA:** 55% in 12th with Mathematics (Direct admission)\n"
            "📊 **BBA / B.Com:** 50% in 12th any stream (Direct admission)\n"
            "🔬 **B.Sc:** 55% in 12th Science stream\n"
            "📚 **M.Tech:** B.Tech with 60% + GATE (preferred)\n"
            "💼 **MBA:** Graduation 50% + CAT/MAT/XAT/MP-MAT\n"
            "🖥️ **MCA:** BCA/B.Sc CS with 55% + Maths\n\n"
            "Kisi specific branch ki eligibility jaanna chahte ho? 😊"
        )
 
    def _handle_eligibility_check(self, entities, context, extra):
        """Handle 'X% mein eligible hoon kya?' queries."""
        import re
        raw = extra.get("user_message", "") or ""
        combined = raw.lower()
        pct_match = re.search(r'(\d{1,3})\s*(?:%|percent|marks|percentage)', combined)
        pct = int(pct_match.group(1)) if pct_match else None
 
        if pct is None:
            return self._handle_eligibility(entities, context, extra)
 
        if pct >= 60:
            return (
                f"✅ **Aap B.Tech ke liye ELIGIBLE hain! ({pct}%)**\n\n"
                f"Aapke {pct}% marks B.Tech minimum 60% PCM requirement poori karte hain.\n\n"
                f"📋 **Next Steps:**\n"
                f"1. JEE Mains dein (Jan ya Apr session)\n"
                f"2. RGPV DTE MP Counselling mein register karein: dte.mponline.gov.in\n"
                f"3. ITM Gwalior + apni preferred branch choose karein\n\n"
                f"🌐 Apply: http://itmgoi.in/OnlineApply_ITMGOI\n"
                f"📞 **+91-7773005065**"
            )
        elif pct >= 55:
            return (
                f"⚠️ **B.Tech ke liye eligible NAHI hain ({pct}%)**\n\n"
                f"B.Tech minimum: **60% in PCM** required hai.\n\n"
                f"✅ **Aap in courses ke liye eligible hain ({pct}%):**\n"
                f"  • **BCA** — 55% in 12th with Maths → ₹48,000/year\n"
                f"  • **B.Sc** — 55% in 12th Science → ₹36,000/year\n\n"
                f"💡 **BCA + MCA** = Strong software career — B.Tech jaisa hi profile!\n"
                f"📞 Guidance: **+91-7773005065**"
            )
        elif pct >= 50:
            return (
                f"⚠️ **B.Tech ke liye eligible NAHI hain ({pct}%)**\n\n"
                f"B.Tech minimum: **60% in PCM** required.\n\n"
                f"✅ **Aap in courses ke liye eligible hain ({pct}%):**\n"
                f"  • **BBA** — 50% in 12th any stream → ₹42,000/year\n"
                f"  • **B.Com** — 50% in 12th any stream → ₹32,000/year\n\n"
                f"💡 BBA + MBA = Strong management career!\n"
                f"📞 Guidance: **+91-7773005065**"
            )
        else:
            return (
                f"❌ **Abhi eligible nahi hain ({pct}%)**\n\n"
                f"Minimum marks required:\n"
                f"  • B.Tech: 60% in PCM\n"
                f"  • BCA/B.Sc: 55% in 12th\n"
                f"  • BBA/B.Com: 50% in 12th\n\n"
                f"📞 Personal guidance ke liye: **+91-7773005065**"
            )
 
    def _handle_fees_structure(self, entities, context, extra):
        raw = extra.get("user_message", "") or ""
        ctx_course = (entities.get("course") or
                      context.get("entities_so_far", {}).get("course") or "")
        combined = (raw + " " + ctx_course).lower()
        spec = _detect_specialization(combined)
 
        course_info = None
        if ctx_course:
            course_info = self._find_course(ctx_course)
 
        if course_info:
            total = course_info['fees_per_year'] * int(course_info['duration'].split()[0])
            return (
                f"💰 **Fee for {course_info['short']}:**\n\n"
                f"• Annual Fee: **₹{course_info['fees_per_year']:,}**/year\n"
                f"• Duration: {course_info['duration']}\n"
                f"• Total Course Fee: **₹{total:,}** (approx.)\n\n"
                f"💡 Merit students (>90%) get **50% fee waiver!**\n"
                f"📞 Call: +91-7773005065"
            )
 
        ug = self.kb["courses"]["ug"]
        pg = self.kb["courses"]["pg"]
        ug_fees = "\n".join(f"  • {c['short']}: ₹{c['fees_per_year']:,}/year" for c in ug)
        pg_fees = "\n".join(f"  • {c['short']}: ₹{c['fees_per_year']:,}/year" for c in pg)
        return (
            f"💰 **Fee Structure at ITM Gwalior:**\n\n"
            f"**🔧 B.Tech & UG Programs:**\n{ug_fees}\n\n"
            f"**📚 PG Programs:**\n{pg_fees}\n\n"
            f"💡 Scholarships: Merit (50%) | EWS (30%) | SC/ST | Sports (20%)\n"
            f"📞 More info: +91-7773005065"
        )
 
    def _handle_placement(self, entities, context, extra):
        p = self.kb.get("placement", {})
        it  = p.get("top_recruiters", {}).get("IT_software", [])
        fin = p.get("top_recruiters", {}).get("banking_finance", [])
        cor = p.get("top_recruiters", {}).get("core_engineering", [])
        return (
            f"🏆 **Placement at ITM Gwalior:**\n\n"
            f"📊 **Key Stats:**\n"
            f"  • Placement Rate: **{p.get('placement_rate','90%+')}**\n"
            f"  • Average Package: **{p.get('average_package','₹5.5 LPA')}**\n"
            f"  • Highest Package: **{p.get('highest_package','₹18 LPA')}**\n"
            f"  • Companies Visiting: **{p.get('companies_count','300+')} annually**\n\n"
            f"🏢 **Top Recruiters:**\n"
            f"  💻 IT: {', '.join(it[:6])}\n"
            f"  🏦 Finance: {', '.join(fin)}\n"
            f"  🏭 Core: {', '.join(cor[:3])}\n\n"
            f"🎯 **TAP Cell Services:**\n"
            f"  • Pre-placement personal training\n"
            f"  • Mock interviews & GD practice\n"
            f"  • 45-day mandatory internship\n"
            f"  • AWS & Microsoft certifications\n\n"
            f"📧 {p.get('tap_email','placement@itmgoi.in')}\n"
            f"🏅 Best Placement Award — Indian Education Excellence Awards 2022!"
        )
 
    def _handle_companies(self, entities, context, extra):
        p = self.kb.get("placement", {}).get("top_recruiters", {})
        return (
            f"🏢 **Companies Recruiting from ITM Gwalior:**\n\n"
            f"💻 **IT & Software:**\n"
            f"  {', '.join(p.get('IT_software', []))}\n\n"
            f"🌐 **Tech Companies:**\n"
            f"  {', '.join(p.get('tech_companies', []))}\n\n"
            f"🏦 **Banking & Finance:**\n"
            f"  {', '.join(p.get('banking_finance', []))}\n\n"
            f"🏭 **Core Engineering:**\n"
            f"  {', '.join(p.get('core_engineering', []))}\n\n"
            f"📊 **300+ companies** visit annually!\n"
            f"Avg: ₹5.5 LPA | Highest: ₹18 LPA\n\n"
            f"Placement process ya internship ke baare mein jaanna chahte ho?"
        )
 
    def _handle_campus_timing(self, entities, context, extra):
        c = self.kb.get("college", {})
        return (
            f"⏰ **ITM Gwalior Timings:**\n\n"
            f"🏫 **College & Office:**\n"
            f"  Monday to Saturday: **9:00 AM – 5:00 PM**\n"
            f"  Sunday: Closed\n\n"
            f"📚 **Class Timings:**\n"
            f"  Morning: 9:00 AM – 1:00 PM\n"
            f"  Afternoon: 1:30 PM – 5:00 PM\n\n"
            f"📖 **Library:** Mon–Sat, 8:00 AM – 8:00 PM\n\n"
            f"🏢 **Admission Office:** Mon–Sat, 9 AM – 5 PM\n"
            f"📞 {c.get('admission_phone', ['+91-7773005065'])[0]}"
        )
 
    def _handle_counselling_info(self, entities, context, extra):
        return (
            "📋 **RGPV / DTE MP B.Tech Counselling Process:**\n\n"
            "1️⃣ **JEE Mains Score** — Jan ya Apr session dein\n\n"
            "2️⃣ **DTE MP Portal Register** — dte.mponline.gov.in\n"
            "   JEE Roll No. + personal details se register karein\n\n"
            "3️⃣ **Document Verification**\n"
            "   10th, 12th, category certificate, JEE scorecard\n\n"
            "4️⃣ **Online Choice Filling**\n"
            "   ITM Gwalior select karein + branch preference dein\n"
            "   (CSE → AIML/DS/Cyber/IoT/Cloud specialization choose karein)\n\n"
            "5️⃣ **Seat Allotment** — Merit + category based\n"
            "   Round 1 → Round 2 → Mop-up Round\n\n"
            "6️⃣ **Report to ITM Gwalior**\n"
            "   Original documents + fees payment = seat confirm!\n\n"
            "📞 Help: **+91-7773005065**\n"
            "🌐 Apply: http://itmgoi.in/OnlineApply_ITMGOI"
        )
 
    def _handle_course_recommendation(self, entities, context, extra):
        return (
            "🎓 **ITM Gwalior Course Guide — Apna Course Choose Karein:**\n\n"
            "💻 **Coding/Software/AI mein interest hai?**\n"
            "  → **B.Tech CSE** (Best choice!)\n"
            "     AIML ✅ | Data Science ✅ | Cybersecurity ✅ | IoT | Cloud\n"
            "     Fee: ₹87,000/yr | 92% placement\n\n"
            "🌐 **Web/Networking/Apps pasand hai?**\n"
            "  → **B.Tech IT**\n"
            "     Web Tech | Mobile Apps | Network Security\n"
            "     Fee: ₹85,000/yr\n\n"
            "📡 **Electronics/Hardware/Circuits mein interest?**\n"
            "  → **B.Tech ECE**\n"
            "     VLSI | Embedded Systems | Signal Processing\n"
            "     Fee: ₹84,000/yr | ISRO/DRDO/Telecom scope\n\n"
            "⚙️ **Machines/Automobile/Manufacturing?**\n"
            "  → **B.Tech ME**\n"
            "     Automobile | Thermal | Manufacturing\n"
            "     Fee: ₹82,000/yr | PSU/Govt job scope excellent\n\n"
            "🏗️ **Construction/Infrastructure mein interest?**\n"
            "  → **B.Tech Civil**\n"
            "     Fee: ₹80,000/yr | PWD/NHAI/Railways jobs\n\n"
            "💻 **Computer career chahiye, JEE nahi dena?**\n"
            "  → **BCA** (55% in 12th with Maths only)\n"
            "     Fee: ₹48,000/yr | BCA + MCA = B.Tech jaisa profile!\n\n"
            "📊 **Business/Management mein interest?**\n"
            "  → **BBA** → then **MBA**\n"
            "     Fee: ₹42,000/yr | Marketing | Finance | HR\n\n"
            "Apna interest batao — main best course suggest karunga! 😊"
        )
 
    def _handle_course_details(self, entities, context, extra):
        raw = extra.get("user_message", "") or ""
        ctx_course = (entities.get("course") or
                      context.get("entities_so_far", {}).get("course") or "")
        combined = (raw + " " + ctx_course).lower()
        spec = _detect_specialization(combined)
        if spec:
            return self._handle_specializations(entities, context, extra)
        return self._handle_courses_offered(entities, context, extra)
 
    def _handle_career_scope(self, entities, context, extra):
        raw = extra.get("user_message", "") or ""
        ctx_course = (entities.get("course") or
                      context.get("entities_so_far", {}).get("course") or "")
        combined = (raw + " " + ctx_course).lower()
 
        if "aiml" in combined or "ai" in combined or "machine" in combined:
            return (
                "🚀 **Career Scope — AI/ML (CSE-AIML):**\n\n"
                "💼 **Job Roles:** AI Engineer, ML Engineer, Data Scientist,\n"
                "   NLP Engineer, Computer Vision Engineer, MLOps\n\n"
                "💰 **Salary:** Fresher ₹5–12 LPA | Experienced ₹15–40 LPA\n"
                "🏢 **Companies:** Google, Amazon, Microsoft, TCS, Infosys,\n"
                "   startups, research labs\n\n"
                "📈 **Future Scope:** HIGHEST demand 2024–2030\n"
                "   Every industry needs AI — Finance, Healthcare, Automobiles!\n\n"
                "🎓 **Higher Studies:** M.Tech AI, MS Abroad, PhD\n"
                "📞 +91-7773005065"
            )
        if "data science" in combined or "ds" in combined:
            return (
                "📊 **Career Scope — Data Science:**\n\n"
                "💼 **Job Roles:** Data Scientist, Data Analyst,\n"
                "   Business Analyst, BI Developer, Data Engineer\n\n"
                "💰 **Salary:** Fresher ₹4–8 LPA | Senior ₹12–25 LPA\n"
                "🏢 **Companies:** Flipkart, Amazon, TCS, Accenture,\n"
                "   Banks, Consulting firms\n\n"
                "📈 **Future Scope:** Very high demand — data is the new oil!\n"
                "📞 +91-7773005065"
            )
        if "cse" in combined or "computer" in combined or "software" in combined:
            return (
                "💻 **Career Scope — B.Tech CSE:**\n\n"
                "💼 **Job Roles:** Software Engineer, Full Stack Developer,\n"
                "   AI/ML Engineer, Cloud Architect, Cybersecurity Analyst\n\n"
                "💰 **Salary:** Fresher ₹3.6–8 LPA (TCS, Wipro, IBM)\n"
                "   Good startups: ₹8–15 LPA\n\n"
                "🏢 **Top Hiring:** TCS, Infosys, Wipro, IBM, Accenture,\n"
                "   Microsoft, Google, Amazon\n\n"
                "📈 **ITM Placement:** 92% CSE students placed!\n"
                "🎓 **Higher Studies:** M.Tech, MS Abroad, MBA\n"
                "📞 +91-7773005065"
            )
        if "mechanical" in combined or "me" in combined:
            return (
                "⚙️ **Career Scope — B.Tech ME:**\n\n"
                "💼 **Job Roles:** Mechanical Engineer, Automobile Engineer,\n"
                "   Production Manager, Design Engineer, HVAC Engineer\n\n"
                "💰 **Salary:** Fresher ₹2.5–5 LPA | Core companies ₹4–8 LPA\n\n"
                "🏛️ **Govt Jobs:** EXCELLENT scope!\n"
                "   UPSC IES, PSU (ONGC, BHEL, SAIL, BPCL, NTPC)\n"
                "   GATE score se PSU mein direct entry!\n\n"
                "🎓 **Higher Studies:** M.Tech ME, MBA Operations\n"
                "📞 +91-7773005065"
            )
        if "civil" in combined:
            return (
                "🏗️ **Career Scope — B.Tech Civil:**\n\n"
                "💼 **Job Roles:** Civil Engineer, Structural Engineer,\n"
                "   Site Engineer, Urban Planner, Construction Manager\n\n"
                "💰 **Salary:** Fresher ₹2.5–4.5 LPA | Senior ₹8–15 LPA\n\n"
                "🏛️ **Govt Jobs:** Very good scope!\n"
                "   PWD, NHAI, Railways, Municipal Corp, UPSC IES\n\n"
                "📈 **Future:** Smart cities, infrastructure boom in India!\n"
                "📞 +91-7773005065"
            )
        return (
            "🚀 **Career Scope — ITM Gwalior ke Baad:**\n\n"
            "💻 **CSE/IT:** Software Engineer, AI/ML, Data Scientist → ₹5–15 LPA\n"
            "📡 **ECE:** VLSI, Embedded, Telecom → ₹3.5–8 LPA\n"
            "⚙️ **ME:** Automobile, Manufacturing, PSU → ₹3–7 LPA\n"
            "🏗️ **Civil:** PWD, NHAI, Construction → ₹2.5–6 LPA\n"
            "💼 **MBA:** Management roles → ₹4–10 LPA\n\n"
            "🏆 ITM Placement: **90%+ students placed!**\n"
            "Avg: ₹5.5 LPA | Highest: ₹18 LPA\n\n"
            "Kisi specific branch ka career scope jaanna hai? 😊"
        )
 
    def _handle_total_branches(self, entities, context, extra):
        return (
            "🎓 **Complete Courses & Specializations at ITM Gwalior:**\n\n"
            "**🔧 B.Tech Engineering (4 years, JEE + RGPV):**\n"
            "1. **CSE** — 5 Specs: AIML | Data Science | Cyber Security | IoT | Cloud\n"
            "2. **IT**  — 4 Specs: Web Tech | Mobile App | Network Security | Database\n"
            "3. **ECE** — 3 Specs: VLSI | Embedded Systems | Signal Processing\n"
            "4. **ME**  — 4 Specs: Automobile | Thermal | Manufacturing | CAD/CAM\n"
            "5. **Civil** — 3 Specs: Structural | Environmental | Transportation\n\n"
            "**💻 UG Programs (3 years, Direct Admission):**\n"
            "6. BCA (₹48k) | 7. BBA (₹42k) | 8. B.Sc (₹36k) | 9. B.Com (₹32k)\n\n"
            "**📚 PG Programs:**\n"
            "10. M.Tech (₹92k) | 11. MBA (₹88k) | 12. MCA (₹58k) | 13. M.Sc (₹46k)\n\n"
            "**Total: 5 B.Tech branches | 19 specializations | 13 programs**\n\n"
            "Kisi bhi course ke baare mein poochein — full details dunga! 😊"
        )
 
    def _handle_last_date(self, entities, context, extra):
        dates = self.kb.get("important_dates", {})
        return (
            f"📅 **Important Dates — {dates.get('academic_year', '2026-27')} Admissions:**\n\n"
            f"• 📝 Form Start: **{dates.get('form_start_date', 'March 2026')}**\n"
            f"• ⏰ Last Date: **{dates.get('form_last_date', 'May 31, 2026')}**\n"
            f"• 💳 Application Fee: ₹{dates.get('application_fee', 500)}\n"
            f"• 🎓 JEE Mains: **{dates.get('entrance_exam_date', 'Jan & Apr 2026')}**\n"
            f"• 📊 Result: {dates.get('result_declaration', 'April/May 2026')}\n"
            f"• 🗣 Counselling: {dates.get('counselling_start','June 2026')} – {dates.get('counselling_end','July 2026')}\n"
            f"• 🏫 Classes Begin: **{dates.get('classes_begin', 'August 2026')}**\n\n"
            f"⚠️ Apply early — seats limited!\n"
            f"🌐 http://itmgoi.in/OnlineApply_ITMGOI\n"
            f"📞 **+91-7773005065**"
        )
 
    def _handle_documents_needed(self, entities, context, extra):
        docs = self.kb.get("documents_required", [])
        if isinstance(docs, dict):
            docs = docs.get("mandatory", []) + docs.get("conditional", [])
        mandatory = docs[:7]
        conditional = docs[7:]
        m_text = "\n".join(f"{i+1}. {d}" for i, d in enumerate(mandatory))
        c_text = "\n".join(f"  • {d}" for d in conditional)
        return (
            f"📄 **Documents Required for Admission:**\n\n"
            f"✅ **Mandatory:**\n{m_text}\n\n"
            f"📎 **If Applicable:**\n{c_text}\n\n"
            f"⚠️ All documents **self-attested** honaye chahiye.\n"
            f"Originals + 2 sets of photocopies laana."
        )
 
    def _handle_hostel_info(self, entities, context, extra):
        h  = self.kb.get("hostel", {})
        bh = h.get("boys_hostel", {})
        gh = h.get("girls_hostel", {})
        return (
            f"🏠 **Hostel at ITM Gwalior:**\n\n"
            f"👦 **Boys Hostel:**\n"
            f"  • Capacity: {bh.get('capacity',500)} students\n"
            f"  • Fee: **₹{bh.get('fees_per_year',68000):,}/year** (mess included)\n"
            f"  • Rooms: {', '.join(bh.get('room_types',['2-sharing','3-sharing']))}\n"
            f"  • Facilities: 24/7 Security, WiFi, Hot Water, Mess, Indoor Sports\n\n"
            f"👧 **Girls Hostel:**\n"
            f"  • Capacity: {gh.get('capacity',300)} students\n"
            f"  • Fee: **₹{gh.get('fees_per_year',72000):,}/year** (mess included)\n"
            f"  • Female wardens 24/7 | Very safe environment\n"
            f"  • Facilities: Security, WiFi, Hot Water, Mess, Common Room\n\n"
            f"📧 {h.get('contact','hostel@itmgoi.in')}\n"
            f"📞 Warden: {h.get('warden_phone','+91-751-2440056')}"
        )
 
    def _handle_contact_info(self, entities, context, extra):
        c = self.kb.get("college", {})
        phones     = " / ".join(c.get("phone", ["+91-751-2440056"]))
        adm_phones = " / ".join(c.get("admission_phone", ["+91-7773005065"]))
        return (
            f"📞 **Contact ITM Gwalior:**\n\n"
            f"🏫 **Main Office:**\n"
            f"  📱 {phones}\n"
            f"  📧 {c.get('email','info@itmgoi.in')}\n\n"
            f"🎓 **Admission Helpline:**\n"
            f"  📱 **{adm_phones}**\n"
            f"  📧 **{c.get('admissions_email','admission@itmgoi.in')}**\n\n"
            f"🌐 **{c.get('website','www.itmgoi.in')}**\n"
            f"📍 {c.get('address','ITM Campus, Opp. Sithouli Station, NH-75, Gwalior - 475001')}\n"
            f"⏰ {c.get('office_hours','Mon–Sat, 9 AM – 5 PM')}\n"
            f"🗺 {c.get('google_maps','https://bit.ly/itm-gwalior')}"
        )
 
    def _handle_scholarship(self, entities, context, extra):
        scholarships = self.kb.get("scholarships", [])
        lines = []
        for i, s in enumerate(scholarships, 1):
            desc = s.get("description", s.get("eligibility", ""))
            lines.append(
                f"{i}. **{s['name']}:** {desc}\n"
                f"   💰 {s['benefit']}\n"
                f"   ✅ Eligibility: {s['eligibility']}"
            )
        return (
            "🏆 **Scholarships at ITM Gwalior:**\n\n"
            + "\n\n".join(lines)
            + "\n\n📝 Apply within **30 days of admission**.\n"
            "📧 admission@itmgoi.in | 📞 +91-7773005065"
        )
 
    def _handle_facilities(self, entities, context, extra):
        f = self.kb.get("facilities", {})
        acad   = "\n  ".join(f"• {x}" for x in f.get("academic", []))
        sports = "\n  ".join(f"• {x}" for x in f.get("sports", []))
        other  = "\n  ".join(f"• {x}" for x in f.get("other", []))
        return (
            f"🏛️ **Campus Facilities at ITM Gwalior:**\n\n"
            f"📚 **Academic:**\n  {acad}\n\n"
            f"⚽ **Sports:**\n  {sports}\n\n"
            f"🏥 **Other:**\n  {other}\n\n"
            f"🌐 WiFi-enabled, green, secure campus!"
        )
 
    def _handle_internship(self, entities, context, extra):
        p = self.kb.get("placement", {})
        return (
            "💼 **Internship Program at ITM Gwalior:**\n\n"
            "🔑 **Mandatory Summer Internship:**\n"
            "  • 45-day internship after 2nd/3rd year\n"
            "  • Industry exposure for ALL students\n\n"
            "🌐 **Virtual Internship (EduSkills + AICTE):**\n"
            "  • AWS, Microsoft, Cisco, Google certifications\n"
            f"  • {p.get('internship_record','5 Lakh+ internships — World Record!')}\n"
            "  • Ranked #35 All India (EduSkills 2024)\n\n"
            "🏢 **Partner Companies:**\n"
            "  TCS, Infosys, Wipro, AWS, Microsoft & 100+ more\n\n"
            "📞 TAP Cell: **+91-9691973919**\n"
            "📧 arpit.chauhan@itmuniversity.ac.in"
        )
 
    def _handle_exam_schedule(self, entities, context, extra):
        dates   = self.kb.get("important_dates", {})
        centers = ", ".join(dates.get("exam_centers", ["Gwalior", "Bhopal", "Indore"]))
        return (
            f"📝 **Entrance Exam — {dates.get('academic_year','2026-27')}:**\n\n"
            f"🔧 **B.Tech (RGPV Affiliated):**\n"
            f"  • Exam: **JEE Mains** (Jan & Apr sessions)\n"
            f"  • Admission via: RGPV / DTE MP Counselling\n"
            f"  • Pattern: MCQ | PCM | 3 hours | NCERT 11th & 12th\n"
            f"  • Centers: {centers}\n\n"
            f"💻 **BCA/BBA/B.Com/B.Sc:** No entrance — direct merit admission!\n"
            f"💼 **MBA:** CAT/MAT/XAT/MP-MAT\n"
            f"🎓 **M.Tech:** GATE (preferred)\n\n"
            f"📞 +91-7773005065"
        )
 
    def _handle_result_status(self, entities, context, extra):
        dates = self.kb.get("important_dates", {})
        return (
            f"📊 **Result & Merit List — ITM Gwalior:**\n\n"
            f"• JEE Result: {dates.get('result_declaration','April/May 2026')}\n"
            f"• 1st Merit List: {dates.get('first_merit_list','July 2026')}\n"
            f"• 2nd Merit List: {dates.get('second_merit_list','July 2026 (if required)')}\n"
            f"• Counselling: {dates.get('counselling_start','June')} – {dates.get('counselling_end','July 2026')}\n\n"
            f"🔍 Check at: **www.itmgoi.in** → Admission section\n"
            f"DTE MP: dte.mponline.gov.in\n\n"
            f"📞 +91-7773005065"
        )
 
    def _handle_clubs(self, entities, context, extra):
        clubs = self.kb.get("clubs_cells", [
            "Performing Arts Club (PAC)", "IEEE Student Chapter",
            "NSS Cell", "UBA Cell", "Women Empowerment Cell",
            "Coding Club", "AWS Cloud Club"
        ])
        clubs_text = "\n  ".join(f"• {c}" for c in clubs)
        return (
            f"🎉 **Student Life at ITM Gwalior:**\n\n"
            f"🏆 **Clubs & Cells:**\n  {clubs_text}\n\n"
            f"🎭 **Annual Events:**\n"
            f"  • **DiversITM** — Cultural & Technical Fest\n"
            f"  • **Pratibha Samman** — Merit Award Ceremony\n"
            f"  • ITM International Conference\n"
            f"  • Sports Tournaments\n\n"
            f"ITM mein life = Academics + Activities = Complete Development! 🌟"
        )
 
    def _handle_how_to_reach(self, entities, context, extra):
        c = self.kb.get("college", {})
        return (
            f"🗺️ **How to Reach ITM Gwalior:**\n\n"
            f"📍 **Address:**\n"
            f"  {c.get('address','ITM Campus, Opp. Sithouli Rly Station, NH-75, Gwalior - 475001')}\n\n"
            f"🚂 **By Train (Easiest!):**\n"
            f"  Nearest: **Sithouli Railway Station** — college is right opposite!\n"
            f"  Gwalior Junction se ~15 km NH-75 Jhansi Road pe\n\n"
            f"🚌 **By Road:**\n"
            f"  ~25-30 min from Gwalior city on NH-75 towards Jhansi\n"
            f"  Auto/cab easily available from Gwalior station\n\n"
            f"✈️ **By Air:** Gwalior Airport (~20 km)\n\n"
            f"🗺 Google Maps: {c.get('google_maps','https://bit.ly/itm-gwalior')}"
        )
 
    def _handle_slot_booking(self, entities, context, extra):
        return "📅 I'll help you book a counselling appointment at ITM Gwalior! Let me collect your details."
 
    def _handle_angry(self, entities, context, extra):
        return ANGRY_RESPONSE
 
    def _handle_fallback(self, entities, context, extra):
        return random.choice(FALLBACK_RESPONSES)
 
    # ── Helpers ────────────────────────────────────────────────────────────────
 
    def _load_kb(self):
        try:
            with open(KB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error("Failed to load knowledge base: %s", exc)
            return {}
 
    def _find_course(self, course_name):
        cl = course_name.lower()
        for level in ("ug", "pg"):
            for c in self.kb.get("courses", {}).get(level, []):
                if (cl in c["short"].lower() or cl in c["name"].lower()
                        or c["short"].lower() in cl):
                    return c
        return None