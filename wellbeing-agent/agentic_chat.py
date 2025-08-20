import gradio as gr
from agentic_system import agentic_system
import re
import time

def chat_response(message, history, patient_id):
    """Enhanced chat function using agentic system with LLM routing"""
    print(f"🔍 Received: '{message}' for patient: '{patient_id}'")
    
    if not message or not message.strip():
        return history, ""
    
    try:
        # Process through agentic system
        result = agentic_system.process_query(patient_id or "UID_123", message)
        
        raw_response = result["response"]
        route_decision = result["route"]
        
        print(f"✅ Route: {route_decision}, Response length: {len(raw_response)}")
        
        # Clean the response
        cleaned_response = clean_model_response(raw_response, route_decision)
        
        # Add route indicator with LLM info
        if route_decision == "function_calling":
            route_indicator = "🔧 **Data Retrieval** (LLM Routed)"
        elif route_decision == "hybrid":
            route_indicator = "🎭 **Hybrid Response** (Data + Conversation)"
        else:
            route_indicator = "💬 **Conversation** (LLM Routed)"
            
        final_response = f"{route_indicator}\n\n{cleaned_response}"
        
        # Create new history entry
        history = history + [[message, final_response]]
        print(f"📊 History length: {len(history)}")
        
        return history, ""
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        history = history + [[message, f"❌ **System Error**: {str(e)}\n\nPlease try again or contact support."]]
        return history, ""

def clean_model_response(response, route_type):
    """Clean response based on route type"""
    if not response:
        return "No response generated."
    
    response = str(response).strip()
    
    if route_type == "function_calling":
        # Handle function calling format
        if "<think>" in response and "</think>" in response:
            think_pattern = r'<think>(.*?)</think>'
            think_match = re.search(think_pattern, response, re.DOTALL)
            if think_match:
                thinking = think_match.group(1).strip()
                response = re.sub(think_pattern, '', response, flags=re.DOTALL).strip()
                response = f"**🤔 Analysis:** {thinking}\n\n**📊 Result:** {response}"
        
        if "<function>" in response and "</function>" in response:
            func_pattern = r'<function>(.*?)</function>'
            func_match = re.search(func_pattern, response, re.DOTALL)
            if func_match:
                function_call = func_match.group(1).strip()
                response = re.sub(func_pattern, '', response, flags=re.DOTALL).strip()
                response = f"**⚙️ Function Call:**\n```json\n{function_call}\n```\n\n**📋 Response:** {response}"
    
    # Remove any remaining HTML-like tags
    response = re.sub(r'<[^>]+>', '', response)
    response = re.sub(r'\n\s*\n', '\n\n', response).strip()
    
    if not response.strip():
        return "I processed your message but the response was empty. Please try rephrasing your question."
    
    return response

def initialize_system():
    """Initialize the agentic system with loading indicator"""
    try:
        print("🚀 Initializing Agentic Mental Health System with LLM Router...")
        agentic_system.setup_models()
        return "🟢 **System Status**: All models loaded (Conversation + Function Calling + LLM Router)!", True
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return f"🔴 **System Error**: Failed to load models - {str(e)}", False

# Initialize system
print("Starting system initialization...")
status_message, system_ready = initialize_system()

# Create enhanced Gradio interface
with gr.Blocks(
    title="Agentic Mental Health Assistant with LLM Router", 
    theme=gr.themes.Base(),
    css="""
    .system-status { 
        padding: 10px; 
        border-radius: 8px; 
        margin: 10px 0; 
    }
    .route-indicator { 
        font-weight: bold; 
        color: #2563eb; 
    }
    """
) as demo:
    
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
        <h1 style="margin: 0; font-size: 2.5em;">🧠 Agentic Mental Health Assistant</h1>
        <p style="margin: 10px 0 5px 0; font-size: 1.2em;">Multi-Model AI with Intelligent Hybrid Routing</p>
        <p style="margin: 0; opacity: 0.9;">Llama 3.2 3B router can use BOTH conversation + data models for comprehensive responses</p>
    </div>
    """)
    
    # System status
    system_status = gr.HTML(
        f'<div class="system-status" style="background: {"#d4edda" if system_ready else "#f8d7da"}; color: {"#155724" if system_ready else "#721c24"}; border: 1px solid {"#c3e6cb" if system_ready else "#f5c6cb"};">{status_message}</div>',
        visible=True
    )
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                height=600,
                show_copy_button=True,
                label="🤖 Intelligent Assistant (LLM-Routed)",
                avatar_images=("👤", "🧠"),
                bubble_full_width=False,
                show_share_button=False
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Ask me anything - the LLM router will intelligently choose the best model...", 
                    scale=4,
                    show_label=False,
                    lines=2,
                    max_lines=4
                )
                send = gr.Button("Send 🚀", scale=1, variant="primary")
        
        with gr.Column(scale=1):
            patient_id = gr.Textbox(
                label="👤 Patient ID",
                value="UID_123",
                placeholder="Enter patient ID..."
            )
            
            gr.Markdown("### 🎛️ System Architecture")
            gr.HTML("""
            <div style="font-size: 0.85em; color: #4b5563; background: #f9fafb; padding: 10px; border-radius: 6px;">
                <strong>🧠 LLM Router:</strong> Llama 3.2 3B<br>
                <strong>💬 Conversation:</strong> Fine-tuned Llama 3.2 3B<br>
                <strong>🔧 Function Calling:</strong> Fine-tuned Llama 3.2 3B
            </div>
            """)
            
            clear = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")
            
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
                ("� How can I manage anxiety?", "conversation")
            ]
            
            for query_text, expected_route in test_queries:
                test_btn = gr.Button(f"{query_text}", size="sm", variant="secondary")
                test_btn.click(lambda x=query_text.split(" ", 1)[1]: x, outputs=msg)

    # Event handlers
    if system_ready:
        send.click(
            chat_response,
            inputs=[msg, chatbot, patient_id],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            chat_response,
            inputs=[msg, chatbot, patient_id],
            outputs=[chatbot, msg]
        )
    else:
        send.click(
            lambda m, h, p: (h + [[m, "❌ System not ready. Please restart the application."]], ""),
            inputs=[msg, chatbot, patient_id],
            outputs=[chatbot, msg]
        )
    
    clear.click(lambda: [], outputs=chatbot)
    
    gr.Markdown("""
    ---
    **🚀 Enhanced LLM-Based Routing:**
    - 🧠 **Llama 3.2 3B Router**: Uses few-shot examples to classify queries
    - 🎯 **Intelligent Classification**: Better understanding of context and intent  
    - 🔧 **Function Calls**: Automatically triggered for data requests
    - 💬 **Conversations**: Seamlessly handles emotional support needs
    - 🔄 **Fallback**: Rule-based backup if LLM routing fails
    """)

if __name__ == "__main__":
    if system_ready:
        print("🎉 Starting LLM-Routed Agentic Chat Interface...")
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            debug=True,
            share=True,
            show_error=True,
        )
    else:
        print("❌ Cannot start interface - system initialization failed")