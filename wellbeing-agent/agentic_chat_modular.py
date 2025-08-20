import gradio as gr
import time
from core.wellbeing_agent import wellbeing_agent

# Initialize the system
print("🚀 Setting up Modular Wellbeing Agent...")

# Setup models
try:
    wellbeing_agent.setup_models()
    print("✅ Modular system ready!")
except Exception as e:
    print(f"❌ Failed to initialize system: {e}")
    exit(1)

def chat_response(message, history, patient_id="UID_123"):
    """Process user message and return response"""
    if not message.strip():
        return "", history
    
    try:
        # Process the query using the modular system
        result = wellbeing_agent.process_query(patient_id, message)
        
        route = result["route"].upper()
        response = result["response"]
        
        # Add route indicator
        route_indicators = {
            "CONVERSATION": "💬 **Conversation Mode**",
            "FUNCTION_CALLING": "🔧 **Data Retrieval Mode**", 
            "HYBRID": "🎭 **Hybrid Response** (Data + Conversation)"
        }
        
        route_indicator = route_indicators.get(route, f"🤖 **{route} Mode**")
        formatted_response = f"{route_indicator}\n\n{response}"
        
        # Update history
        history.append([message, formatted_response])
        
        return "", history
        
    except Exception as e:
        error_response = f"❌ I apologize, but I encountered an error: {str(e)}"
        history.append([message, error_response])
        return "", history

def clear_chat():
    """Clear chat history"""
    wellbeing_agent.clear_history("UID_123")
    return []

# Create Gradio interface
with gr.Blocks(
    title="🧠 Wellbeing Agent - Modular Mental Health Assistant",
    theme=gr.themes.Soft(),
    css="""
    :root, body, #root, .gradio-container {
        width: 100% !important;
        max-width: none !important;
        margin: 0 !important;
    }
    """
) as demo:
    
    gr.Markdown("# 🧠 Wellbeing Agent - Modular System")
    gr.Markdown("### 🎯 Intelligent Mental Health Assistant with Multi-Model Architecture")
    
    with gr.Row():
        with gr.Column(scale=4):  # Made chat area bigger
            chatbot = gr.Chatbot(
                height=500,  # Increased height
                show_label=False,
                container=True,
                bubble_full_width=True,
                show_copy_button=True,
                avatar_images=None,
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Type your message here... (e.g., 'I can't sleep for two days')",
                    show_label=False,
                    scale=5,  # Made input box bigger
                    container=False,
                    lines=2,  # Allow multi-line input
                    max_lines=4
                )
                send_btn = gr.Button("Send", scale=1, variant="primary", size="lg")
            
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear Chat", scale=1, variant="secondary")
                patient_id = gr.Textbox(
                    value="UID_123",
                    placeholder="Patient ID",
                    label="Patient ID",
                    scale=2
                )
        
        with gr.Column(scale=2):  # Made sidebar smaller to give more space to chat
            gr.Markdown("### 🏗️ Modular Architecture")
            gr.HTML("""
            <div style="font-size: 0.9em; color: #6b7280;">
                <p><strong>🧠 Model Manager:</strong><br>
                Handles 3 specialized models</p>
                <p><strong>🎯 Query Router:</strong><br>
                LLM-based intelligent routing</p>
                <p><strong>⚙️ Processors:</strong><br>
                • Conversation<br>
                • Function Calling<br>
                • Hybrid (Data + Chat)</p>
                <p><strong>💾 History Manager:</strong><br>
                Context-aware conversations</p>
            </div>
            """)
            
            gr.Markdown("### 📊 Routing Examples")
            gr.HTML("""
            <div style="font-size: 0.9em; color: #6b7280;">
                <p><strong>🔧 → Function Calling:</strong><br>
                "Show me my exercise data"<br>
                "Get my sleep history"</p>
                <p><strong>💬 → Conversation:</strong><br>
                "I feel anxious today"<br>
                "Help me cope with stress"</p>
                <p><strong>🎭 → Hybrid (NEW!):</strong><br>
                "I can't sleep for two days"<br>
                "My heart rate feels high, I'm worried"</p>
            </div>
            """)
            
            gr.Markdown("### 💡 Test Queries")
            
            test_queries = [
                ("💬 I'm feeling really stressed about work", "conversation"),
                ("🔧 Show me my heart rate data", "function_calling"),
                ("🎭 I can't sleep for two days", "hybrid"),
                ("🔧 Get my medication history", "function_calling"),
                ("🎭 My heart rate feels high, should I worry?", "hybrid"),
                ("💬 How can I manage anxiety?", "conversation")
            ]
            
            for query_text, expected_route in test_queries:
                test_btn = gr.Button(
                    query_text, 
                    size="sm",
                    variant="secondary",
                    scale=1
                )
                test_btn.click(
                    lambda q=query_text.split(' ', 1)[1]: chat_response(q, [], "UID_123")[1],
                    outputs=[chatbot],
                    show_progress=False
                )
    
    # Event handlers
    def submit_message(message, history, patient_id):
        return chat_response(message, history, patient_id)
    
    msg.submit(submit_message, [msg, chatbot, patient_id], [msg, chatbot])
    send_btn.click(submit_message, [msg, chatbot, patient_id], [msg, chatbot])
    clear_btn.click(clear_chat, outputs=[chatbot])
    
    gr.Markdown("""
    ---
    ### 🔧 System Status: **Modular Architecture Active**
    - **Models**: Conversation, Function Calling, Router
    - **Architecture**: Clean separation of concerns
    - **Routing**: LLM-based with rule-based fallback
    - **Processing**: Specialized processors for each mode
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )
