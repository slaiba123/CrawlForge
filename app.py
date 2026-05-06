"""
CrawlForge — Multi-Agent Research System
Streamlit UI with editorial terminal aesthetic.
"""

import streamlit as st
import time
import re

from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="CrawlForge",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;1,300&family=Bebas+Neue&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp {
    background-color: #080808 !important;
    color: #d4c9b0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.block-container { padding: 0 !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 9999;
    opacity: 0.35;
}
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 3rem; border-bottom: 1px solid #1e1e1e;
    background: #080808; position: sticky; top: 0; z-index: 100;
}
.topbar-logo { font-family: 'Bebas Neue', sans-serif; font-size: 1.6rem; letter-spacing: 0.12em; color: #f0e6c8; }
.topbar-logo span { color: #d4820a; }
.topbar-meta { font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; color: #333; letter-spacing: 0.15em; text-transform: uppercase; }
.hero { padding: 5rem 3rem 3.5rem; border-bottom: 1px solid #141414; position: relative; overflow: hidden; }
.hero::after {
    content: 'CRAWLFORGE'; position: absolute; right: -1rem; top: 50%; transform: translateY(-50%);
    font-family: 'Bebas Neue', sans-serif; font-size: 12rem; color: rgba(255,255,255,0.015);
    letter-spacing: 0.05em; pointer-events: none; white-space: nowrap;
}
.hero-kicker {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; letter-spacing: 0.3em;
    text-transform: uppercase; color: #d4820a; margin-bottom: 1.2rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.hero-kicker::before { content: ''; display: inline-block; width: 24px; height: 1px; background: #d4820a; }
.hero-title { font-family: 'Bebas Neue', sans-serif; font-size: clamp(3.5rem, 8vw, 7rem); line-height: 0.9; letter-spacing: 0.04em; color: #f0e6c8; margin-bottom: 1.4rem; }
.hero-title em { color: #d4820a; font-style: normal; }
.hero-desc { font-size: 0.95rem; font-weight: 300; color: #5a5040; max-width: 480px; line-height: 1.7; }
.input-section { padding: 2rem 3rem 0.75rem; background: #080808; }
.input-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; letter-spacing: 0.25em; text-transform: uppercase; color: #d4820a; margin-bottom: 0.8rem; }
[data-testid="column"] { padding-left: 0 !important; padding-right: 0 !important; }
[data-testid="stHorizontalBlock"] {
    padding-left: 3rem !important; padding-right: 3rem !important; padding-bottom: 2rem !important;
    gap: 1rem !important; border-bottom: 1px solid #141414; background: #080808;
}
.results-section [data-testid="stHorizontalBlock"] {
    padding-left: 0 !important; padding-right: 0 !important; padding-bottom: 0 !important;
    border-bottom: none !important; background: transparent !important;
}
.stTextInput > div > div > input {
    background: #0d0d0d !important; border: 1px solid #1e1e1e !important; border-radius: 0 !important;
    color: #f0e6c8 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 1rem !important;
    padding: 0.85rem 1.2rem !important; transition: border-color 0.2s, background 0.2s !important;
    caret-color: #d4820a !important; width: 100% !important;
}
.stTextInput > div > div > input:focus {
    border-color: #d4820a !important; background: #111 !important;
    box-shadow: 0 0 0 1px rgba(212,130,10,0.15) !important; outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #333 !important; font-style: italic; }
.stTextInput > label { display: none !important; }
.stTextInput, .stTextInput > div, .stTextInput > div > div { width: 100% !important; }
.stButton > button {
    background: #d4820a !important; color: #080808 !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.72rem !important;
    font-weight: 600 !important; letter-spacing: 0.2em !important; text-transform: uppercase !important;
    border: none !important; border-radius: 0 !important; padding: 0.75rem 2.5rem !important;
    transition: background 0.15s !important; width: auto !important;
}
.stButton > button:hover { background: #e8920e !important; }
.pipeline-grid { display: grid; grid-template-columns: repeat(4, 1fr); border-bottom: 1px solid #141414; }
.pipeline-cell { padding: 1.5rem 2rem; border-right: 1px solid #141414; position: relative; transition: background 0.3s; }
.pipeline-cell:last-child { border-right: none; }
.pipeline-cell.active { background: rgba(212,130,10,0.04); }
.pipeline-cell.done { background: rgba(80,160,100,0.03); }
.pipeline-cell-num { font-family: 'IBM Plex Mono', monospace; font-size: 0.55rem; letter-spacing: 0.2em; color: #222; margin-bottom: 0.5rem; }
.pipeline-cell-name { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #3a3028; margin-bottom: 0.2rem; transition: color 0.3s; }
.pipeline-cell.active .pipeline-cell-name { color: #d4820a; }
.pipeline-cell.done .pipeline-cell-name { color: #50a064; }
.pipeline-cell-desc { font-size: 0.72rem; font-weight: 300; color: #2a2a2a; }
.pipeline-cell-status { position: absolute; top: 1.5rem; right: 1.5rem; font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; letter-spacing: 0.1em; }
.status-waiting { color: #222; } .status-running { color: #d4820a; } .status-done { color: #50a064; }
.pipeline-cell-bar { position: absolute; bottom: 0; left: 0; height: 2px; width: 0%; background: #d4820a; transition: width 0.6s ease; }
.pipeline-cell.active .pipeline-cell-bar { width: 60%; }
.pipeline-cell.done .pipeline-cell-bar { width: 100%; background: #50a064; }
.agent-step { background: #0d0d0d; border: 1px solid #1e1e1e; border-left: 3px solid #d4820a; padding: 1.2rem 1.6rem; margin-bottom: 0.75rem; animation: fadeIn 0.4s ease; }
.agent-step.done { border-left-color: #50a064; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.agent-step-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.5rem; }
.agent-step-icon { font-size: 0.75rem; color: #d4820a; }
.agent-step.done .agent-step-icon { color: #50a064; }
.agent-step-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: #d4820a; }
.agent-step.done .agent-step-label { color: #50a064; }
.agent-step-content { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; line-height: 1.7; color: #b0a898; white-space: pre-wrap; word-break: break-word; max-height: 220px; overflow-y: auto; padding-right: 0.5rem; }
.results-section { padding: 3rem; }
.section-header { display: flex; align-items: baseline; gap: 1rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #141414; }
.section-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; letter-spacing: 0.25em; text-transform: uppercase; color: #d4820a; }
.section-title { font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem; letter-spacing: 0.08em; color: #f0e6c8; }
.report-card { background: #0d0d0d; border: 1px solid #1a1a1a; padding: 2.5rem; margin-bottom: 1.5rem; position: relative; }
.report-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: #d4820a; }
.report-content { font-size: 0.92rem; line-height: 1.85; color: #a09880; white-space: pre-wrap; font-family: 'IBM Plex Sans', sans-serif; font-weight: 300; }
.critic-card { background: #0d0d0d; border: 1px solid #1a1a1a; padding: 2rem 2.5rem; position: relative; }
.critic-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: #50a064; }
.critic-score { font-family: 'Bebas Neue', sans-serif; font-size: 3.5rem; color: #d4820a; line-height: 1; margin-bottom: 0.2rem; }
.critic-score-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem; letter-spacing: 0.2em; text-transform: uppercase; color: #333; margin-bottom: 1.5rem; }
.critic-content { font-size: 0.88rem; line-height: 1.8; color: #8a7e6e; white-space: pre-wrap; font-weight: 300; }
details { border: 1px solid #1e1e1e; margin-bottom: 0.75rem; }
details summary {
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.65rem !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important; color: #8a7e6e !important;
    padding: 0.9rem 1.2rem !important; cursor: pointer !important; list-style: none !important;
    display: flex !important; align-items: center !important; gap: 0.5rem !important;
    background: #0d0d0d; transition: color 0.2s;
}
details summary:hover { color: #d4820a !important; }
details[open] summary { color: #d4820a !important; border-bottom: 1px solid #1e1e1e; }
.raw-content {
    padding: 1.4rem; border-top: 1px solid #1e1e1e; font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem; line-height: 1.8; color: #b0a898; white-space: pre-wrap;
    word-break: break-word; background: #0a0a0a; max-height: 400px; overflow-y: auto;
}
.stDownloadButton > button {
    background: transparent !important; color: #d4820a !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.65rem !important;
    font-weight: 500 !important; letter-spacing: 0.2em !important; text-transform: uppercase !important;
    border: 1px solid #2a2018 !important; border-radius: 0 !important; padding: 0.6rem 1.5rem !important;
    transition: all 0.15s !important; margin-right: 0.5rem !important;
}
.stDownloadButton > button:hover { background: rgba(212,130,10,0.08) !important; border-color: #d4820a !important; }
.app-footer { padding: 1.5rem 3rem; border-top: 1px solid #101010; display: flex; justify-content: space-between; align-items: center; }
.footer-left { font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem; letter-spacing: 0.15em; text-transform: uppercase; color: #5a5040; }
.stSpinner > div { color: #d4820a !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080808; }
::-webkit-scrollbar-thumb { background: #2a2a2a; }
::-webkit-scrollbar-thumb:hover { background: #d4820a; }
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────
for k in ("results", "running", "done", "stages"):
    if k not in st.session_state:
        st.session_state[k] = {} if k == "results" else ([] if k == "stages" else False)


# ── Helpers ───────────────────────────────────────────────────
COMPONENT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=Bebas+Neue&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: transparent; font-family: 'IBM Plex Mono', monospace; }
.pipeline-grid { display: grid; grid-template-columns: repeat(4, 1fr); border-bottom: 1px solid #141414; background: #080808; }
.pipeline-cell { padding: 1.5rem 2rem; border-right: 1px solid #141414; position: relative; transition: background 0.3s; }
.pipeline-cell:last-child { border-right: none; }
.pipeline-cell.active { background: rgba(212,130,10,0.04); }
.pipeline-cell.done { background: rgba(80,160,100,0.03); }
.pipeline-cell-num { font-size: 0.55rem; letter-spacing: 0.2em; color: #333; margin-bottom: 0.5rem; }
.pipeline-cell-name { font-size: 0.78rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #3a3028; margin-bottom: 0.2rem; }
.pipeline-cell.active .pipeline-cell-name { color: #d4820a; }
.pipeline-cell.done .pipeline-cell-name { color: #50a064; }
.pipeline-cell-desc { font-size: 0.72rem; color: #2a2a2a; }
.pipeline-cell-status { position: absolute; top: 1.5rem; right: 1.5rem; font-size: 0.6rem; letter-spacing: 0.1em; }
.status-waiting { color: #333; } .status-running { color: #d4820a; } .status-done { color: #50a064; }
.pipeline-cell-bar { position: absolute; bottom: 0; left: 0; height: 2px; width: 0%; background: #d4820a; transition: width 0.6s ease; }
.pipeline-cell.active .pipeline-cell-bar { width: 60%; }
.pipeline-cell.done .pipeline-cell-bar { width: 100%; background: #50a064; }
</style>
"""


def render_pipeline(stages: list):
    steps = [("01","SEARCH","web retrieval"),("02","READER","deep scraping"),
              ("03","WRITER","synthesizing"),("04","CRITIC","quality review")]
    cells = ""
    for i, (num, name, desc) in enumerate(steps):
        if i < len(stages) and stages[i] == "done":
            state, status, status_cls = "done", "✓ DONE", "status-done"
        elif i == len(stages):
            state, status, status_cls = "active", "● RUNNING", "status-running"
        else:
            state, status, status_cls = "", "— IDLE", "status-waiting"
        cells += f"""<div class="pipeline-cell {state}">
            <div class="pipeline-cell-num">{num}</div>
            <div class="pipeline-cell-name">{name}</div>
            <div class="pipeline-cell-desc">{desc}</div>
            <div class="pipeline-cell-status {status_cls}">{status}</div>
            <div class="pipeline-cell-bar"></div>
        </div>"""
    st.iframe(COMPONENT_CSS + f'<div class="pipeline-grid">{cells}</div>', height=120)


def extract_score(feedback: str) -> str:
    m = re.search(r'Score[:\s]+(\d+(?:\.\d+)?)\s*/\s*10', feedback, re.IGNORECASE)
    return f"{m.group(1)}/10" if m else "—/10"


# ── PDF Generator (editorial magazine style) ──────────────────
def report_to_pdf_bytes(report_text: str, topic: str) -> bytes:
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        HRFlowable, PageBreak
    )
    from reportlab.platypus.flowables import Flowable
    from reportlab.pdfgen import canvas as pdfcanvas
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT

    # ── Palette ──────────────────────────────────────────────
    AMBER      = colors.HexColor("#d4820a")
    DARK_BG    = colors.HexColor("#080808")
    CHARCOAL   = colors.HexColor("#1e1e1e")
    WARM_OFF   = colors.HexColor("#f0e6c8")
    BODY_GRAY  = colors.HexColor("#2e2a22")
    MUTED      = colors.HexColor("#7a6e5e")
    GREEN_DOT  = colors.HexColor("#50a064")
    PAGE_W, PAGE_H = letter

    # ── Custom Flowables ─────────────────────────────────────
    class SidebarParagraph(Flowable):
        def __init__(self, text, style, bar_color=AMBER, bar_width=3, padding=10):
            super().__init__()
            self._para = Paragraph(text, style)
            self._bar_color = bar_color
            self._bar_width = bar_width
            self._padding = padding

        def wrap(self, availWidth, availHeight):
            _, h = self._para.wrap(availWidth - self._bar_width - self._padding, availHeight)
            self.width = availWidth
            self.height = h + 8
            return self.width, self.height

        def draw(self):
            self.canv.setFillColor(self._bar_color)
            self.canv.rect(0, 4, self._bar_width, self.height - 8, fill=1, stroke=0)
            self.canv.saveState()
            self.canv.translate(self._bar_width + self._padding, 4)
            self._para.drawOn(self.canv, 0, 0)
            self.canv.restoreState()

    class SectionBadge(Flowable):
        def __init__(self, num, label, avail_w):
            super().__init__()
            self._num = str(num).zfill(2)
            self._label = label.upper()
            self.height = 30
            self.width = avail_w

        def draw(self):
            c = self.canv
            badge_w = 30
            c.setFillColor(AMBER)
            c.rect(0, 4, badge_w, 22, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(DARK_BG)
            c.drawCentredString(badge_w / 2, 11, self._num)
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(WARM_OFF)
            c.drawString(badge_w + 10, 10, self._label)
            c.setStrokeColor(CHARCOAL)
            c.setLineWidth(0.5)
            c.line(0, 3, self.width, 3)

    class BulletItem(Flowable):
        def __init__(self, text, style, avail_w):
            super().__init__()
            self._para = Paragraph(text, style)
            self._avail_w = avail_w

        def wrap(self, availWidth, availHeight):
            _, h = self._para.wrap(self._avail_w - 20, availHeight)
            self.width = self._avail_w
            self.height = h
            return self.width, self.height

        def draw(self):
            c = self.canv
            c.setFillColor(AMBER)
            c.saveState()
            c.translate(5, self.height / 2 + 1)
            c.rotate(45)
            c.rect(-3, -3, 6, 6, fill=1, stroke=0)
            c.restoreState()
            c.saveState()
            c.translate(20, 0)
            self._para.drawOn(c, 0, 0)
            c.restoreState()

    # ── Page number canvas ────────────────────────────────────
    class PageNumCanvas(pdfcanvas.Canvas):
        def __init__(self, *args, _topic="", **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []
            self.__topic = _topic

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self._draw_footer(self._pageNumber, total)
                pdfcanvas.Canvas.showPage(self)
            pdfcanvas.Canvas.save(self)

        def _draw_footer(self, page_num, total):
            if page_num == 1:
                return
            w = PAGE_W
            self.setStrokeColor(CHARCOAL)
            self.setLineWidth(0.5)
            self.line(0.75 * inch, 0.58 * inch, w - 0.75 * inch, 0.58 * inch)
            self.setFont("Helvetica", 6.5)
            self.setFillColor(MUTED)
            self.drawString(0.75 * inch, 0.38 * inch, "CRAWLFORGE  ·  RESEARCH INTELLIGENCE SYSTEM  ·  LANGCHAIN + GROQ")
            self.setFillColor(AMBER)
            self.setFont("Helvetica-Bold", 7)
            self.drawRightString(w - 0.75 * inch, 0.38 * inch, f"{page_num} / {total}")
            self.setFillColor(AMBER)
            self.circle(w / 2, 0.42 * inch, 1.5, fill=1, stroke=0)

    # ── Cover painter ─────────────────────────────────────────
    generated = time.strftime("%B %d, %Y  %H:%M")

    def draw_cover(canvas, doc):
        canvas.saveState()
        w, h = PAGE_W, PAGE_H
        canvas.setFillColor(DARK_BG)
        canvas.rect(0, 0, w, h, fill=1, stroke=0)
        canvas.setFillColor(AMBER)
        canvas.rect(0, 0, 7, h, fill=1, stroke=0)
        # Ghost watermark
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 88)
        canvas.setFillColor(colors.HexColor("#111111"))
        canvas.translate(w * 0.72, h * 0.5)
        canvas.rotate(90)
        canvas.drawCentredString(0, 0, "CRAWLFORGE")
        canvas.restoreState()
        # Top accent lines
        for y_frac, col, lw in [(0.88, "#d4820a", 1.5), (0.875, "#2a1808", 0.5), (0.87, "#1a1208", 0.3)]:
            canvas.setStrokeColor(colors.HexColor(col))
            canvas.setLineWidth(lw)
            canvas.line(0.9 * inch, h * y_frac, w - 0.6 * inch, h * y_frac)
        # Kicker
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(AMBER)
        canvas.drawString(0.9 * inch, h * 0.90, "AUTONOMOUS RESEARCH INTELLIGENCE SYSTEM")
        # Title
        canvas.setFont("Helvetica-Bold", 72)
        canvas.setFillColor(WARM_OFF)
        canvas.drawString(0.88 * inch, h * 0.74, "RESEARCH")
        canvas.setFillColor(AMBER)
        canvas.drawString(0.88 * inch, h * 0.64, "REPORT")
        canvas.setFillColor(AMBER)
        canvas.rect(0.88 * inch, h * 0.625, 90, 5, fill=1, stroke=0)
        # Topic box
        box_y = h * 0.46
        box_h = 90
        canvas.setFillColor(colors.HexColor("#0d0d0d"))
        canvas.rect(0.88 * inch, box_y, w - 1.5 * inch, box_h, fill=1, stroke=0)
        canvas.setStrokeColor(AMBER)
        canvas.setLineWidth(0.8)
        canvas.rect(0.88 * inch, box_y, w - 1.5 * inch, box_h, fill=0, stroke=1)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(AMBER)
        canvas.drawString(0.94 * inch, box_y + box_h - 14, "TOPIC")
        canvas.setFont("Helvetica-Bold", 13)
        canvas.setFillColor(WARM_OFF)
        avail = w - 1.7 * inch
        words = topic.upper().split()
        lines_buf, buf = [], []
        for wd in words:
            test = " ".join(buf + [wd])
            if canvas.stringWidth(test, "Helvetica-Bold", 13) < avail:
                buf.append(wd)
            else:
                lines_buf.append(" ".join(buf)); buf = [wd]
        if buf: lines_buf.append(" ".join(buf))
        ty = box_y + box_h - 30
        for ln in lines_buf:
            canvas.drawString(0.94 * inch, ty, ln)
            ty -= 18
        # Meta
        meta_y = h * 0.38
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.9 * inch, meta_y, f"Generated   {generated}")
        canvas.setFillColor(GREEN_DOT)
        canvas.circle(0.82 * inch, meta_y + 4, 3, fill=1, stroke=0)
        # Bottom bar
        canvas.setFillColor(colors.HexColor("#0a0a0a"))
        canvas.rect(0, 0, w, 0.9 * inch, fill=1, stroke=0)
        canvas.setFillColor(AMBER)
        canvas.rect(0, 0.9 * inch, w, 2, fill=1, stroke=0)
        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.9 * inch, 0.38 * inch, "MULTI-AGENT AI RESEARCH  ·  LANGCHAIN + GROQ  ·  NED UNIVERSITY")
        canvas.setFillColor(WARM_OFF)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.drawRightString(w - 0.75 * inch, 0.38 * inch, "LAIBA MUSHTAQ")
        canvas.restoreState()

    # ── Doc setup ─────────────────────────────────────────────
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        leftMargin=0.9 * inch, rightMargin=0.75 * inch,
        topMargin=0.85 * inch, bottomMargin=0.85 * inch,
        title=f"CrawlForge — {topic}",
        author="CrawlForge / Laiba Mushtaq",
    )
    AVAIL_W = PAGE_W - 0.9 * inch - 0.75 * inch

    # ── Styles ────────────────────────────────────────────────
    s_h1   = ParagraphStyle("h1",   fontSize=20, textColor=WARM_OFF, fontName="Helvetica-Bold", leading=26, spaceBefore=16, spaceAfter=6)
    s_h2   = ParagraphStyle("h2",   fontSize=13, textColor=AMBER,    fontName="Helvetica-Bold", leading=19, spaceBefore=14, spaceAfter=4)
    s_h3   = ParagraphStyle("h3",   fontSize=11, textColor=WARM_OFF, fontName="Helvetica-Bold", leading=16, spaceBefore=10, spaceAfter=3)
    s_body = ParagraphStyle("body", fontSize=10.5, textColor=BODY_GRAY, fontName="Helvetica",   leading=18, spaceAfter=6, alignment=TA_JUSTIFY)
    s_bull = ParagraphStyle("bull", fontSize=10.5, textColor=BODY_GRAY, fontName="Helvetica",   leading=18, spaceAfter=4)
    s_bold = ParagraphStyle("bold", fontSize=10.5, textColor=WARM_OFF,  fontName="Helvetica-Bold", leading=18, spaceAfter=4)

    # ── Story ─────────────────────────────────────────────────
    story = [PageBreak()]  # page 1 = cover (drawn via onFirstPage)
    section_idx = 0

    for raw in report_text.split("\n"):
        stripped = raw.strip()
        if not stripped:
            story.append(Spacer(1, 5)); continue
        clean = stripped.replace("**", "")

        if stripped.startswith("### "):
            story.append(Spacer(1, 4))
            story.append(Paragraph(clean[4:], s_h3))
        elif stripped.startswith("## "):
            section_idx += 1
            story.append(Spacer(1, 10))
            story.append(SectionBadge(section_idx, clean[3:], AVAIL_W))
            story.append(Spacer(1, 8))
        elif stripped.startswith("# "):
            story.append(Spacer(1, 8))
            story.append(SidebarParagraph(clean[2:], s_h1, bar_width=5, padding=12))
            story.append(HRFlowable(width="100%", thickness=0.5, color=CHARCOAL, spaceAfter=6))
        elif stripped.startswith(("- ", "* ")):
            story.append(BulletItem(clean[2:], s_bull, AVAIL_W))
        elif stripped.startswith("**") and stripped.endswith("**"):
            story.append(SidebarParagraph(clean, s_bold, bar_color=AMBER, bar_width=3, padding=10))
        else:
            story.append(Paragraph(clean, s_body))

    # ── Canvas factory ────────────────────────────────────────
    def canvas_factory(*args, **kwargs):
        return PageNumCanvas(*args, _topic=topic, **kwargs)

    doc.build(story, onFirstPage=draw_cover, onLaterPages=lambda c, d: None, canvasmaker=canvas_factory)
    return buffer.getvalue()


# ── Top bar ───────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-logo">Crawl<span>Forge</span></div>
    <div class="topbar-meta">Multi-Agent Research Intelligence System</div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-kicker">Autonomous Research System</div>
    <div class="hero-title">Research,<br><em>Forged.</em></div>
    <div class="hero-desc">
        Four specialized AI agents collaborate — searching the live web,
        extracting deep content, writing structured reports, and critiquing
        quality — to deliver intelligence on any topic.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────
st.markdown('<div class="input-section"><div class="input-label">Research Topic</div></div>', unsafe_allow_html=True)

col_input, col_gap, col_btn = st.columns([14, 1, 3])
with col_input:
    topic = st.text_input("topic", placeholder="e.g. LLM inference optimization trends 2025",
                          label_visibility="collapsed", key="topic_input")
with col_btn:
    run = st.button("EXECUTE →", use_container_width=True)

# ── Pipeline status ───────────────────────────────────────────
pipeline_slot = st.empty()
with pipeline_slot:
    render_pipeline(st.session_state.stages)

# ── Run pipeline ──────────────────────────────────────────────
if run:
    if not topic.strip():
        st.warning("Enter a research topic to begin.")
    else:
        st.session_state.results = {}
        st.session_state.stages = []
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

def update_pipeline(stages):
    with pipeline_slot:
        render_pipeline(stages)

if st.session_state.running and not st.session_state.done:
    results = {}
    t = st.session_state.topic_input

    st.session_state.stages = []
    update_pipeline([])
    with st.spinner("Search Agent — scanning the web..."):
        sa = build_search_agent()
        sr = sa.invoke({"messages": [("user", f"Find recent, reliable and detailed information about: {t}")]})
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)

    st.session_state.stages = ["done"]
    update_pipeline(["done"])
    with st.spinner("Reader Agent — extracting deep content..."):
        ra = build_reader_agent()
        rr = ra.invoke({"messages": [("user",
            f"Based on the following search results about '{t}', "
            f"pick the TOP 3 most relevant URLs and scrape each one for deeper content. "
            f"Return all extracted content combined.\n\n"
            f"Search Results:\n{results['search'][:800]}")]})
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    st.session_state.stages = ["done", "done"]
    update_pipeline(["done", "done"])
    with st.spinner("Writer Chain — forging the report..."):
        combined = f"SEARCH RESULTS:\n{results['search']}\n\nDETAILED SCRAPED CONTENT:\n{results['reader']}"
        results["writer"] = writer_chain.invoke({"topic": t, "research": combined})
        st.session_state.results = dict(results)

    st.session_state.stages = ["done", "done", "done"]
    update_pipeline(["done", "done", "done"])
    with st.spinner("Critic Chain — reviewing quality..."):
        results["critic"] = critic_chain.invoke({"report": results["writer"]})
        st.session_state.results = dict(results)

    st.session_state.stages = ["done", "done", "done", "done"]
    st.session_state.running = False
    st.session_state.done = True
    st.rerun()

if st.session_state.done:
    with pipeline_slot:
        render_pipeline(st.session_state.stages)

# ── Results ───────────────────────────────────────────────────
r = st.session_state.results

if r and st.session_state.done:
    st.markdown('<div class="results-section">', unsafe_allow_html=True)
    col_report, col_critic = st.columns([3, 2])

    with col_report:
        st.markdown("""
        <div class="section-header">
            <span class="section-label">Output</span>
            <span class="section-title">Research Report</span>
        </div>""", unsafe_allow_html=True)

        if "writer" in r:
            st.markdown(f"""
            <div class="report-card">
                <div class="report-content">{r['writer']}</div>
            </div>""", unsafe_allow_html=True)

            dl_col1, dl_col2 = st.columns([1, 1])
            with dl_col1:
                st.download_button(
                    label="⬇  DOWNLOAD REPORT (.md)",
                    data=r["writer"],
                    file_name=f"crawlforge_report_{int(time.time())}.md",
                    mime="text/markdown",
                )
            with dl_col2:
                try:
                    pdf_bytes = report_to_pdf_bytes(r["writer"], st.session_state.topic_input)
                    st.download_button(
                        label="⬇  DOWNLOAD REPORT (.pdf)",
                        data=pdf_bytes,
                        file_name=f"crawlforge_report_{int(time.time())}.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.caption(f"PDF unavailable: {e}")

    with col_critic:
        st.markdown("""
        <div class="section-header">
            <span class="section-label">Evaluation</span>
            <span class="section-title">Critic Review</span>
        </div>""", unsafe_allow_html=True)

        if "critic" in r:
            score = extract_score(r["critic"])
            st.markdown(f"""
            <div class="critic-card">
                <div class="critic-score">{score}</div>
                <div class="critic-score-label">Quality Score</div>
                <div class="critic-content">{r['critic']}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
        <span class="section-label">Debug</span>
        <span class="section-title">Raw Agent Outputs</span>
    </div>""", unsafe_allow_html=True)

    for key, label in [("search","Search Agent Output"),("reader","Reader Agent Output"),
                        ("writer","Writer Chain Output"),("critic","Critic Chain Output")]:
        if key in r:
            preview = r[key][:2000] + "..." if key == "reader" and len(r[key]) > 2000 else r[key]
            safe = preview.replace("<","&lt;").replace(">","&gt;")
            st.markdown(f"""
            <details>
                <summary>⬡ &nbsp; {label}</summary>
                <div class="raw-content">{safe}</div>
            </details>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    <div class="footer-left">CrawlForge · Multi-Agent AI Research System · LangChain + Groq</div>
    <div class="footer-left">Built by <span>Laiba Mushtaq</span> · NED University</div>
</div>
""", unsafe_allow_html=True)