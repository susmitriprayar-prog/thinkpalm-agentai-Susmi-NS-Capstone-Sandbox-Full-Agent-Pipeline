import os
import sys
import streamlit as st
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Adjust Python path to include the parent workspace directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import styles and memory database functions
from ui.styles import GLOBAL_CSS, get_severity_badge
from memory.database import (
    get_all_scans, 
    get_scan_details, 
    clear_scan_history, 
    create_scan_history,
    save_agent_interaction,
    update_scan_status
)
from main import run_agentic_pipeline
from agents.extended_features_agent import ExtendedFeaturesAgent

# Configure Streamlit page parameters
st.set_page_config(
    page_title="Autonomous Agentic QA & Security Pipeline",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global dark mode glassmorphic styling
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Configuration Panel
# ---------------------------------------------------------
st.sidebar.markdown("### 🛠️ Configuration Console")

# 1. API Keys & Models Configuration
st.sidebar.subheader("LLM Parameters")
openai_key = os.getenv("Groq_API_KEY") or os.getenv("OPENAI_API_KEY", "")
if not openai_key:
    st.sidebar.error("⚠️ API Key not found in .env file (Groq_API_KEY or OPENAI_API_KEY)")
selected_model = st.sidebar.selectbox(
    "LLM Model Engine",
    options=["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gpt-4o", "gpt-3.5-turbo"],
    index=0
)

# 2. Target Configuration
st.sidebar.subheader("Target Settings")
target_url = st.sidebar.text_input(
    "Application URL",
    value="http://localhost:5000",
    help="Target web application URL under test. Start the demo target app locally to run tests on http://localhost:5000"
)

# 3. Demo Helper Action
st.sidebar.subheader("Local Testing Tools")
if st.sidebar.button("🚀 Initialize SQLite Memory"):
    from memory.database import init_db
    init_db()
    st.sidebar.success("Database tables initialized!")

if st.sidebar.button("🧹 Clear All Scan Histories"):
    clear_scan_history()
    st.sidebar.warning("Scan database logs cleared successfully!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size:0.8rem; color:#64748b; text-align:center;'>"
    "Agentic QA & Security Pipeline v1.0.0<br>"
    "Developed with Antigravity Core"
    "</div>", 
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Main Page Dashboard Title Header
# ---------------------------------------------------------
st.markdown("<div class='main-title'>🛡️ Autonomous QA & Security Pipeline</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Multi-Agent Orchestration for Intelligent Functional Validation and Vulnerability Assessments</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Tabs Layout
# ---------------------------------------------------------
tab_pipeline, tab_bdd, tab_playwright, tab_coverage, tab_vulns, tab_interactions = st.tabs([
    "⚡ Run Agentic Pipeline",
    "🥒 BDD Test Cases",
    "🎭 Playwright Scripts",
    "📊 Coverage Gap Analysis",
    "🚨 Security Vulnerability Portal",
    "🤝 Multi-Agent Audit Log"
])

# Retrieve all history scans for visualization and selection
scans = get_all_scans()

# ---------------------------------------------------------
# TAB 1: Pipeline Execution Trigger
# ---------------------------------------------------------
with tab_pipeline:
    st.markdown("### ⚡ Launch Multi-Agent QA & Security Assessment")
    st.markdown(
        "Enter optional feature guidelines, requirements, or specifications below to guide the QA Test Case Agent. "
        "The orchestrator will activate agents sequentially, executing real testing and scanning tools under-the-hood."
    )
    
    # Text input for feature specification guidance
    spec_input = st.text_area(
        "Feature Specifications or User Stories (Optional)",
        placeholder=(
            "Example: As a user, I want to log in using an email. "
            "I should see errors for blank passwords. "
            "I can search products and look up product reviews by index."
        ),
        height=120
    )
    
    # Trigger Pipeline Run Button
    if st.button("🚀 Trigger Full Multi-Agent Audit"):
        if not openai_key:
            st.error("❌ OpenAI API Key is missing! Please set OPENAI_API_KEY in the .env file.")
        else:
            # Set up visual log streams in Streamlit UI
            st.markdown("<div class='gradient-hr'></div>", unsafe_allow_html=True)
            st.markdown("### 🔄 Autonomous Pipeline Live Stream")
            
            # UI log container
            status_box = st.empty()
            progress_bar = st.progress(0)
            
            with st.spinner("Collaborating agents spinning up..."):
                try:
                    # Simulation / Loading status helper updates to make execution look engaging and interactive
                    status_box.markdown(
                        "<div class='glass-card'>"
                        "🤖 <b>Pipeline Orchestrator:</b> Setting up SQLite memory logs and spawning agents...<br>"
                        "</div>",
                        unsafe_allow_html=True
                    )
                    progress_bar.progress(10)
                    
                    # 1. Trigger pipeline execution backend
                    results = run_agentic_pipeline(
                        target_url=target_url,
                        feature_desc=spec_input,
                        zap_url=None,
                        zap_key=None,
                        api_key=openai_key or None,
                        model=selected_model
                    )
                    
                    progress_bar.progress(100)
                    status_box.markdown(
                        "<div class='glass-card' style='border-color: #10b981;'>"
                        "✅ <b>Orchestrator:</b> Continuous integration pipeline executed successfully!<br>"
                        "📂 Word DOCX and database archives are now compiled and finalized."
                        "</div>",
                        unsafe_allow_html=True
                    )
                    
                    st.success("🎉 Multi-agent audit cycle completed successfully!")
                    
                    # Set the new scan ID in state and refresh to show on Dashboard
                    st.session_state["current_scan_id"] = results["id"]
                    
                    st.markdown("#### Summary of Results:")
                    st.write(f"- **Designed Test Cases:** `{len(results['test_cases'])}` scenarios designed")
                    st.write(f"- **Vulnerabilities Discovered:** `{len(results['vulnerabilities'])}` issues logged")
                    
                    # Read compiled file path for download option
                    if os.path.exists(results["docx_path"]):
                        with open(results["docx_path"], "rb") as f:
                            st.download_button(
                                label="📥 Download Consolidated DOCX Audit Report",
                                data=f,
                                file_name=os.path.basename(results["docx_path"]),
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                            
                except Exception as run_err:
                    st.error(f"❌ Pipeline Execution Failed: {str(run_err)}")
                    st.info("💡 Tip: Verify target web server is running and accessible (or start test_app.py locally).")



# ---------------------------------------------------------
# TAB 3: BDD Testcase Generator
# ---------------------------------------------------------
with tab_bdd:
    st.markdown("### 🥒 BDD Test Case Scenario Suite")
    st.markdown("Convert designed functional test cases into Cucumber/Gherkin specifications for cross-functional alignment.")
    
    current_scan_id = st.session_state.get("current_scan_id")
    if not current_scan_id:
        st.warning("Please run a new scan or load a past run in the Dashboard tab first.")
    else:
        loaded_data = get_scan_details(current_scan_id)
        if loaded_data:
            tcs = loaded_data.get("test_cases", [])
            if not tcs:
                st.info("No test cases found. Run a scan to capture elements and generate scenarios first.")
            else:
                if st.button("🥒 Generate Gherkin BDD Feature Suite"):
                    if not openai_key:
                        st.error("❌ OpenAI/Groq API Key is missing! Please set it in the sidebar or .env file.")
                    else:
                        with st.spinner("Generating beautiful BDD Gherkin files..."):
                            try:
                                agent = ExtendedFeaturesAgent(api_key=openai_key, model=selected_model)
                                bdd_output = agent.generate_bdd_scenarios(target_url, tcs)
                                st.session_state["bdd_scenarios"] = bdd_output
                                st.success("🎉 BDD Gherkin scenarios generated successfully!")
                            except Exception as e:
                                st.error(f"Failed to generate BDD scenarios: {e}")
                                
                if "bdd_scenarios" in st.session_state:
                    st.markdown("#### 📝 Compiled Gherkin Feature Specifications")
                    st.code(st.session_state["bdd_scenarios"], language="gherkin")
                    st.download_button(
                        label="📥 Download BDD Feature File",
                        data=st.session_state["bdd_scenarios"],
                        file_name="features_suite.feature",
                        mime="text/plain"
                    )

# ---------------------------------------------------------
# TAB 4: Playwright Script Generator
# ---------------------------------------------------------
with tab_playwright:
    st.markdown("### 🎭 Playwright Automation Script Compiler")
    st.markdown("Instantly compile functional test scenarios into executable asynchronous Python Playwright script blocks.")
    
    current_scan_id = st.session_state.get("current_scan_id")
    if not current_scan_id:
        st.warning("Please run a new scan or load a past run in the Dashboard tab first.")
    else:
        loaded_data = get_scan_details(current_scan_id)
        if loaded_data:
            tcs = loaded_data.get("test_cases", [])
            if not tcs:
                st.info("No test cases found. Run a scan to capture elements and generate scripts first.")
            else:
                if st.button("🎭 Compile Playwright Automation Script"):
                    if not openai_key:
                        st.error("❌ OpenAI/Groq API Key is missing! Please set it in the sidebar or .env file.")
                    else:
                        with st.spinner("Compiling high-fidelity automated Playwright code..."):
                            try:
                                agent = ExtendedFeaturesAgent(api_key=openai_key, model=selected_model)
                                playwright_code = agent.generate_playwright_script(target_url, tcs)
                                st.session_state["playwright_script"] = playwright_code
                                st.success("🎉 Playwright automation script compiled successfully!")
                            except Exception as e:
                                st.error(f"Failed to compile script: {e}")
                                
                if "playwright_script" in st.session_state:
                    st.markdown("#### 💻 Executable Python Playwright Script")
                    st.code(st.session_state["playwright_script"], language="python")
                    st.download_button(
                        label="📥 Download Playwright Script",
                        data=st.session_state["playwright_script"],
                        file_name="test_automation.py",
                        mime="text/plain"
                    )

# ---------------------------------------------------------
# TAB 5: Coverage Gap Analysis
# ---------------------------------------------------------
with tab_coverage:
    st.markdown("### 📊 QA & Security Coverage Gap Analyzer")
    st.markdown("Evaluate testing depth by auditing the scraped site architecture against designed test cases and discovered security vulnerabilities.")
    
    current_scan_id = st.session_state.get("current_scan_id")
    if not current_scan_id:
        st.warning("Please run a new scan or load a past run in the Dashboard tab first.")
    else:
        loaded_data = get_scan_details(current_scan_id)
        if loaded_data:
            tcs = loaded_data.get("test_cases", [])
            vulns = loaded_data.get("vulnerabilities", [])
            
            if st.button("📊 Perform QA & Security Coverage Audit"):
                if not openai_key:
                    st.error("❌ OpenAI/Groq API Key is missing! Please set it in the sidebar or .env file.")
                else:
                    with st.spinner("Analyzing coverage depth and mapping gaps..."):
                        try:
                            agent = ExtendedFeaturesAgent(api_key=openai_key, model=selected_model)
                            analysis_report = agent.perform_coverage_gap_analysis(target_url, tcs, vulns)
                            st.session_state["coverage_analysis"] = analysis_report
                            st.success("🎉 Coverage Gap Analysis completed successfully!")
                        except Exception as e:
                            st.error(f"Failed to perform coverage gap analysis: {e}")
                            
            if "coverage_analysis" in st.session_state:
                st.markdown("#### 📋 Quality Assurance & Security Audit Report")
                st.markdown(
                    f"<div class='glass-card' style='padding: 24px; font-size:0.95rem; border-left: 4px solid #8b5cf6;'>",
                    unsafe_allow_html=True
                )
                st.markdown(st.session_state["coverage_analysis"])
                st.markdown("</div>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download Gap Analysis Report",
                    data=st.session_state["coverage_analysis"],
                    file_name="coverage_gap_analysis.md",
                    mime="text/markdown"
                )

# ---------------------------------------------------------
# TAB 6: Security Vulnerabilities Portal
# ---------------------------------------------------------
with tab_vulns:
    st.markdown("### 🚨 Discovered Application Security Vulnerabilities")
    st.markdown("Penetration testing results compiled by the **Security Scan Agent**, enriched with OWASP descriptions and code remediations.")
    
    current_scan_id = st.session_state.get("current_scan_id")
    
    if not current_scan_id:
        st.warning("Please run a new scan or load a past run in the Dashboard tab first.")
    else:
        loaded_data = get_scan_details(current_scan_id)
        if loaded_data:
            vulns_list = loaded_data.get("vulnerabilities", [])
            
            if not vulns_list:
                st.success("🛡️ Excellent! Zero security issues detected. Your target meets recommended security postures.")
            else:
                for idx, vuln in enumerate(vulns_list, start=1):
                    badge_html = get_severity_badge(vuln["severity"])
                    
                    st.markdown(
                        f"<div class='glass-card'>"
                        f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                        f"<h4>VULN-{idx}: {vuln['name']}</h4>"
                        f"<div>{badge_html}</div>"
                        f"</div>"
                        f"<hr style='border:0.5px solid rgba(255,255,255,0.05); margin: 10px 0;'>"
                        f"<p><b>Location / Path:</b> <code>{vuln.get('url_path', 'Global')}</code></p>"
                        f"<p><b>Threat Description:</b> {vuln.get('description', '')}</p>"
                        f"<div style='background-color:rgba(37,99,235,0.08); border-left:3px solid #2563eb; padding: 12px; border-radius: 6px; font-size:0.95rem;'>"
                        f"<b>⚡ Secure Coding Remediation Strategy:</b><br>{vuln.get('remediation', '')}"
                        f"</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

# ---------------------------------------------------------
# TAB 5: Multi-Agent Collaboration Logs (Short-term context)
# ---------------------------------------------------------
with tab_interactions:
    st.markdown("### 🤝 Autonomous Multi-Agent Handoff and Audit Trail")
    st.markdown("This records the sequence of actions and handoffs executed by collaborating agents in short-term context.")
    
    current_scan_id = st.session_state.get("current_scan_id")
    
    if not current_scan_id:
        st.warning("Please run a new scan or load a past run in the Dashboard tab first.")
    else:
        loaded_data = get_scan_details(current_scan_id)
        if loaded_data:
            logs = loaded_data.get("agent_interactions", [])
            
            if not logs:
                st.info("No audit transactions logged for this scan run.")
            else:
                for log in logs:
                    # Format timestamp
                    time_val = log["timestamp"]
                    try:
                        time_val = datetime.fromisoformat(time_val).strftime("%H:%M:%S")
                    except Exception:
                        pass
                        
                    agent_name = log["agent_name"]
                    message = log["message"]
                    
                    # Style based on agent name
                    bg_color = "rgba(30, 41, 59, 0.4)"
                    border_color = "rgba(255, 255, 255, 0.08)"
                    
                    if "QA" in agent_name or "Test" in agent_name:
                        bg_color = "rgba(16, 185, 129, 0.05)"
                        border_color = "rgba(16, 185, 129, 0.2)"
                    elif "Security" in agent_name:
                        bg_color = "rgba(239, 68, 68, 0.05)"
                        border_color = "rgba(239, 68, 68, 0.2)"
                    elif "Report" in agent_name:
                        bg_color = "rgba(139, 92, 246, 0.05)"
                        border_color = "rgba(139, 92, 246, 0.2)"
                        
                    st.markdown(
                        f"<div style='background-color:{bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 20px; margin-bottom: 15px;'>"
                        f"<div style='display:flex; justify-content:space-between; margin-bottom: 8px;'>"
                        f"<b>👤 {agent_name}</b>"
                        f"<span style='color:#64748b; font-size:0.85rem;'>⏱️ {time_val}</span>"
                        f"</div>"
                        f"<div style='font-size:0.95rem; color:#e2e8f0; white-space: pre-wrap;'>{message}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
