import streamlit as st
from agent import HoneypotAgent
from personas import get_persona, list_personas

# Page config
st.set_page_config(
    page_title="AI Honeypot - Scam Engagement System",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .scammer-message {
        background-color: #FFE5E5;
        border-left: 4px solid #FF4B4B;
    }
    .agent-message {
        background-color: #E5F5E5;
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = HoneypotAgent()
    st.session_state.conversation = []
    st.session_state.current_persona = "Elderly Teacher"

# Header
st.markdown('<div class="main-header">🕵️ AI Honeypot System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Engage scammers. Extract intelligence. Protect citizens.</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Persona selection
    selected_persona = st.selectbox(
        "Choose AI Persona",
        list_personas(),
        index=list_personas().index(st.session_state.current_persona)
    )
    
    # Update persona if changed
    if selected_persona != st.session_state.current_persona:
        st.session_state.current_persona = selected_persona
        st.session_state.agent.set_persona(get_persona(selected_persona))
        st.success(f"✅ Persona changed to: {selected_persona}")
    
    st.divider()
    
    # Info
    st.info("""
    **How it works:**
    1. Select a persona above
    2. Enter scammer's message
    3. AI agent responds believably
    4. Continue conversation
    """)
    
    # Reset button
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.conversation = []
        st.session_state.agent.reset_conversation()
        st.rerun()
    
    st.divider()
    
    # Stats
    st.metric("Total Messages", len(st.session_state.conversation))

# Main area - 2 columns
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Live Conversation")
    
    # Display conversation history
    if st.session_state.conversation:
        for msg in st.session_state.conversation:
            if msg["role"] == "scammer":
                st.markdown(f"""
                <div class="chat-message scammer-message">
                    <strong>🔴 Scammer:</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <strong>🟢 AI Agent ({st.session_state.current_persona}):</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👆 Start the conversation by entering a scammer message below")
    
    # Input area
    st.divider()
    
    with st.form("chat_form", clear_on_submit=True):
        scammer_input = st.text_area(
            "Scammer says:",
            placeholder="Example: Hello sir, I'm calling from State Bank of India. Your account has been blocked...",
            height=100
        )
        
        col_a, col_b = st.columns([3, 1])
        with col_a:
            submit_button = st.form_submit_button("📤 Send to AI Agent", use_container_width=True)
        with col_b:
            handoff_button = st.form_submit_button("🤖 Handoff", use_container_width=True)
    
    # Process input
    if (submit_button or handoff_button) and scammer_input.strip():
        # Set persona if first message
        if not st.session_state.conversation:
            st.session_state.agent.set_persona(get_persona(st.session_state.current_persona))
        
        # Add scammer message
        st.session_state.conversation.append({
            "role": "scammer",
            "content": scammer_input
        })
        
        # Get AI response
        with st.spinner("🤔 AI Agent thinking..."):
            response = st.session_state.agent.chat(scammer_input)
        
        # Add agent response
        st.session_state.conversation.append({
            "role": "agent",
            "content": response
        })
        
        st.rerun()

with col2:
    st.header("📊 Intelligence Panel")
    
    # Quick stats
    if st.session_state.conversation:
        scammer_messages = [m for m in st.session_state.conversation if m["role"] == "scammer"]
        agent_messages = [m for m in st.session_state.conversation if m["role"] == "agent"]
        
        st.metric("Scammer Messages", len(scammer_messages))
        st.metric("Agent Responses", len(agent_messages))
        
        st.divider()
        
        # Current persona info
        st.subheader("🎭 Active Persona")
        st.write(f"**{st.session_state.current_persona}**")
        
        # Show basic extracted data placeholder
        st.divider()
        st.subheader("🔍 Extracted Data")
        st.caption("(Will be implemented in Day 2)")
        
        with st.expander("📞 Phone Numbers"):
            st.write("Coming soon...")
        
        with st.expander("💳 UPI IDs"):
            st.write("Coming soon...")
        
        with st.expander("🏦 Bank Details"):
            st.write("Coming soon...")
            
    else:
        st.info("Start a conversation to see intelligence data")

# Footer
st.divider()
st.caption("Built for AI Impact Buildathon | Fighting India's ₹60 Crore Daily Fraud Crisis")