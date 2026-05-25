# Custom styling tokens and CSS rules for modern premium white/light-mode UI
GLOBAL_CSS = """
<style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;600;700&display=swap');

    /* Global Body modifications for bright theme */
    .stApp {
        background-color: #ffffff;
        font-family: 'Outfit', sans-serif;
        color: #0f172a;
    }

    /* Override headers styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        letter-spacing: -0.02em;
    }

    /* Custom main title styling with gradient */
    .main-title {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .subtitle {
        color: #475569;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 2.5rem;
    }

    /* Glassmorphism Light Cards */
    .glass-card {
        background: rgba(248, 250, 252, 0.9);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.05);
        color: #0f172a;
    }
    
    .glass-metric {
        background: rgba(241, 245, 249, 0.95);
        border: 1px solid rgba(15, 23, 42, 0.06);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        color: #0f172a;
    }

    /* Severity badges */
    .badge {
        padding: 6px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-high {
        background-color: rgba(239, 68, 68, 0.15);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .badge-medium {
        background-color: rgba(245, 158, 11, 0.15);
        color: #d97706;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .badge-low {
        background-color: rgba(234, 179, 8, 0.15);
        color: #ca8a04;
        border: 1px solid rgba(234, 179, 8, 0.3);
    }
    
    .badge-info {
        background-color: rgba(59, 130, 246, 0.15);
        color: #2563eb;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* Custom table styling */
    table {
        width: 100% !important;
        border-collapse: collapse !important;
        margin: 15px 0 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    th {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        text-align: left !important;
        padding: 12px 16px !important;
        border-bottom: 2px solid #cbd5e1 !important;
    }
    
    td {
        padding: 12px 16px !important;
        border-bottom: 1px solid #e2e8f0 !important;
        color: #334155 !important;
    }
    
    tr:nth-child(even) {
        background-color: rgba(241, 245, 249, 0.5) !important;
    }

    /* Streamlit widgets modifications */
    .stTextInput>div>div>input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    
    .stTextArea>div>div>textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    /* Button overrides */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
    }

    /* Sidebar styles */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid rgba(15, 23, 42, 0.08) !important;
    }
    
    /* Make sidebar text dark */
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label {
        color: #0f172a !important;
    }

    /* Custom visual separator line */
    .gradient-hr {
        height: 2px;
        background: linear-gradient(to right, transparent, #2563eb, #db2777, transparent);
        border: none;
        margin: 30px 0;
    }
    
    /* Codeblock block styling */
    pre {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        color: #0f172a !important;
    }
    code {
        color: #b91c1c !important;
    }
</style>
"""

def get_severity_badge(severity: str) -> str:
    """Returns HTML markup for color-coded severity pill badges."""
    sev = severity.lower().strip()
    if "high" in sev:
        return '<span class="badge badge-high">High</span>'
    elif "medium" in sev:
        return '<span class="badge badge-medium">Medium</span>'
    elif "low" in sev:
        return '<span class="badge badge-low">Low</span>'
    else:
        return '<span class="badge badge-info">Info</span>'
