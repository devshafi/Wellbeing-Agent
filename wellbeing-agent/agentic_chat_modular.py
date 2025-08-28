import gradio as gr
import json
import time
from core.wellbeing_agent import wellbeing_agent
from utils.history_manager import history_manager

# Initialize the system
print("🚀 Setting up Modular Wellbeing Agent...")

# Setup models
try:
    wellbeing_agent.setup_models()
    print("✅ Modular system ready!")
    
    # Display database info
    db_info = history_manager.get_database_info()
    print(f"📁 Database: {db_info['database_path']} ({db_info['database_size_mb']} MB)")
    print(f"📊 Stored: {db_info['total_messages']} messages for {db_info['unique_patients']} patients")
    
except Exception as e:
    print(f"❌ Failed to initialize system: {e}")
    exit(1)

def chat_response(message, history, patient_id="UID_123"):
    """Process user message and return response"""
    if not message.strip():
        return "", history, gr.update(visible=False, value="")
    
    try:
        # Use standard routing system
        result = wellbeing_agent.process_query(patient_id, message)
        
        route = result["route"].upper()
        response = result["response"]
        raw_data = result.get("raw_data")
        
        # Add route indicator
        route_indicators = {
            "CONVERSATION": "💬 **Conversation Mode**",
            "FUNCTION_CALLING": "🔧 **Data Retrieval Mode**", 
            "HYBRID": "🎭 **Hybrid Response** (Data + Conversation)"
        }
        
        route_indicator = route_indicators.get(route, f"🤖 **{route} Mode**")
        formatted_response = f"{route_indicator}\n\n{response}"
        
        # Store interaction in SQLite database (persistent)
        metadata = {
            "route": route,
            "has_raw_data": bool(raw_data),
            "raw_data_types": list(raw_data.keys()) if raw_data else [],
            "timestamp": time.time()
        }
        
        history_manager.add_interaction(
            patient_id=patient_id,
            user_query=message,
            agent_response=formatted_response,
            metadata=metadata
        )
        
        # Update Gradio history (temporary display)
        history.append([message, formatted_response])
        
        # Prepare raw data display if available
        raw_data_visible = False
        raw_data_content = ""
        
        if raw_data:
            raw_data_visible = True
            raw_data_content = "**📊 Raw Data Used:**\n\n"
            for data_type, result_data in raw_data.items():
                if isinstance(result_data, dict) and 'data' in result_data:
                    raw_data_content += f"**{data_type.upper()}:**\n```json\n{json.dumps(result_data['data'], indent=2)}\n```\n\n"
                else:
                    raw_data_content += f"**{data_type.upper()}:**\n```json\n{json.dumps(result_data, indent=2)}\n```\n\n"
        
        return "", history, gr.update(visible=raw_data_visible, value=raw_data_content)
        
    except Exception as e:
        error_response = f"❌ I apologize, but I encountered an error: {str(e)}"
        history.append([message, error_response])
        return "", history, gr.update(visible=False, value="")

def clear_chat():
    """Clear chat history"""
    patient_id = "UID_123"
    
    # Clear both Gradio history and SQLite database
    wellbeing_agent.clear_history(patient_id)
    
    # Show confirmation
    print(f"🗑️ Cleared conversation history for patient {patient_id}")
    
    return [], gr.update(visible=False, value="")

def load_conversation_history(patient_id="UID_123"):
    """Load conversation history from SQLite database"""
    try:
        conversations = history_manager.get_conversation_context(patient_id, max_history=40)  # Load last 20 pairs
        
        # Convert to Gradio format
        history = []
        for i in range(0, len(conversations), 2):
            if i + 1 < len(conversations):
                user_msg = conversations[i]
                agent_msg = conversations[i + 1]
                
                if user_msg["role"] == "user" and agent_msg["role"] == "assistant":
                    history.append([user_msg["content"], agent_msg["content"]])
        
        print(f"📁 Loaded {len(history)} conversation pairs from database")
        return history
        
    except Exception as e:
        print(f"❌ Error loading conversation history: {e}")
        return []

def get_database_stats():
    """Get database statistics for display"""
    try:
        db_info = history_manager.get_database_info()
        patients = history_manager.get_patients_with_history()
        
        stats = f"""
        **📊 Database Statistics:**
        - **Database Size**: {db_info['database_size_mb']} MB
        - **Total Messages**: {db_info['total_messages']}
        - **Unique Patients**: {db_info['unique_patients']}
        - **Current Patients**: {', '.join(patients) if patients else 'None'}
        - **Status**: {db_info['status'].title()}
        """
        
        return stats.strip()
        
    except Exception as e:
        return f"❌ Error getting database stats: {e}"

def export_conversation():
    """Export current patient conversation"""
    try:
        conversation_json = history_manager.export_conversation("UID_123", format="json")
        
        if conversation_json:
            # Save to file
            with open("exported_conversation.json", "w") as f:
                f.write(conversation_json)
            return "✅ Conversation exported to exported_conversation.json"
        else:
            return "❌ No conversation history to export"
            
    except Exception as e:
        return f"❌ Export failed: {e}"

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
            
            # Raw data display (initially hidden)
            raw_data_display = gr.Markdown(
                value="",
                visible=False,
                label="📊 Raw Data Details"
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
                SQLite persistent storage</p>
            </div>
            """)
            
            gr.Markdown("### 💾 Database Management")
            
            # Database stats display
            db_stats_display = gr.Markdown(
                value=get_database_stats(),
                label="Database Statistics"
            )
            
            with gr.Row():
                load_history_btn = gr.Button("📁 Load History", size="sm", variant="secondary")
                refresh_stats_btn = gr.Button("🔄 Refresh Stats", size="sm")
            
            with gr.Row(): 
                export_btn = gr.Button("💾 Export Chat", size="sm")
                # Hidden textbox to show export status
                export_status = gr.Textbox(
                    value="",
                    visible=False,
                    label="Export Status"
                )
            
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
                    lambda q=query_text.split(' ', 1)[1]: chat_response(q, [], "UID_123"),
                    outputs=[msg, chatbot, raw_data_display],
                    show_progress=False
                )
    
    # Event handlers
    def submit_message(message, history, patient_id):
        return chat_response(message, history, patient_id)
    
    # Main chat event handlers
    msg.submit(submit_message, [msg, chatbot, patient_id], [msg, chatbot, raw_data_display])
    send_btn.click(submit_message, [msg, chatbot, patient_id], [msg, chatbot, raw_data_display])
    clear_btn.click(clear_chat, outputs=[chatbot, raw_data_display])
    
    # Database management event handlers
    load_history_btn.click(
        lambda: load_conversation_history("UID_123"),
        outputs=[chatbot]
    )
    
    refresh_stats_btn.click(
        get_database_stats,
        outputs=[db_stats_display]
    )
    
    export_btn.click(
        export_conversation,
        outputs=[export_status]
    )
    
    gr.Markdown("""
    ---
    ### 🔧 System Status: **Modular Architecture with SQLite Persistence**
    - **Models**: Conversation, Function Calling, Router  
    - **Architecture**: Clean separation of concerns
    - **Routing**: LLM-based with rule-based fallback
    - **Processing**: Specialized processors for each mode
    - **Storage**: SQLite database with automatic cleanup (last 20 pairs)
    - **Features**: Persistent history, export functionality, database statistics
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=True,
        show_error=True
    )
