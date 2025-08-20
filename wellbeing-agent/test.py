import gradio as gr
from model_manager import model_manager
import re

def chat_response(message, history, patient_id):
    """Simple chat function that should work"""
    print(f"🔍 Received: '{message}' for patient: '{patient_id}'")
    
    if not message or not message.strip():
        return history, ""
    
    try:
        # Get model response
        raw_response = model_manager.test_model(patient_id or "UID_123", message)
        print(f"✅ Raw response length: {len(raw_response)}")
        print(f"📝 Raw response preview: {raw_response[:100]}...")
        
        # Clean the response - this is the key fix!
        cleaned_response = clean_model_response(raw_response)
        print(f"🧹 Cleaned response: {cleaned_response[:100]}...")
        
        # Make sure response is visible
        if not cleaned_response.strip():
            cleaned_response = "I received your message but generated an empty response. Please try rephrasing."
        
        # Create new history entry
        history = history + [[message, cleaned_response]]
        print(f"📊 History length: {len(history)}")
        
        return history, ""  # Clear input box
        
    except Exception as e:
        print(f"❌ Error: {e}")
        history = history + [[message, f"Error: {str(e)}"]]
        return history, ""

def clean_model_response(response):
    """Clean model response for better display in Gradio"""
    if not response:
        return "No response generated."
    
    # Remove HTML-like tags that might interfere with rendering
    response = str(response).strip()
    
    # Extract content from <think> tags and format nicely
    if "<think>" in response and "</think>" in response:
        think_pattern = r'<think>(.*?)</think>'
        think_match = re.search(think_pattern, response, re.DOTALL)
        if think_match:
            thinking = think_match.group(1).strip()
            # Remove the think tags from response
            response = re.sub(think_pattern, '', response, flags=re.DOTALL).strip()
            # Add thinking as formatted text
            response = f"**Thinking:** {thinking}\n\n**Response:** {response}"
    
    # Extract function calls and format nicely
    if "<function>" in response and "</function>" in response:
        func_pattern = r'<function>(.*?)</function>'
        func_match = re.search(func_pattern, response, re.DOTALL)
        if func_match:
            function_call = func_match.group(1).strip()
            # Remove function tags from response
            response = re.sub(func_pattern, '', response, flags=re.DOTALL).strip()
            # Add function call as formatted text
            response = f"**Function Call:**\n```json\n{function_call}\n```\n\n**Response:** {response}"
    
    # Remove any remaining HTML-like tags
    response = re.sub(r'<[^>]+>', '', response)
    
    # Clean up extra whitespace
    response = re.sub(r'\n\s*\n', '\n\n', response).strip()
    
    # Ensure we have some content
    if not response.strip():
        return "I processed your message but the response was empty after cleaning. Please try rephrasing."
    
    return response

# Simple interface with better styling
with gr.Blocks(theme=gr.themes.Default()) as demo:  # Changed to Default theme
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="margin: 0;">🤖 Mental Health Assistant</h1>
        <p style="margin: 5px 0 0 0;">AI-powered mental health conversation assistant</p>
    </div>
    """)
    
    with gr.Row():
        # Chat area
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                height=500,
                show_copy_button=True,
                container=True,
                show_label=True,
                label="💬 Conversation",
                bubble_full_width=False,
                avatar_images=("👤", "🤖")  # Add avatars for better visibility
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Type your message here...", 
                    scale=4,
                    show_label=False,
                    lines=2
                )
                send = gr.Button("Send 📤", scale=1, variant="primary")
        
        # Controls
        with gr.Column(scale=1):
            patient_id = gr.Textbox(
                label="👤 Patient ID",
                value="UID_123"
            )
            
            gr.Markdown("### 🎛️ Controls")
            clear = gr.Button("🗑️ Clear Chat", variant="secondary")
            
            # Test button
            test_btn = gr.Button("🧪 Test Model", variant="secondary")
            test_result = gr.Textbox(
                label="Test Result",
                interactive=False,
                visible=True,  # Make visible by default
                lines=3
            )
            
            gr.Markdown("### 💡 Sample Messages")
            samples = [
                "I feel stressed about work",
                "I need help with anxiety",
                "I'm having trouble sleeping"
            ]
            
            for sample in samples:
                sample_btn = gr.Button(sample, size="sm", variant="secondary")
                sample_btn.click(lambda x=sample: x, outputs=msg)

    # Event handlers
    def test_model():
        try:
            response = model_manager.test_model("TEST", "Hello test")
            cleaned = clean_model_response(response)
            return f"✅ Working! Length: {len(response)}\n\nCleaned preview:\n{cleaned[:200]}..."
        except Exception as e:
            return f"❌ Error: {e}"

    # Wire events
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
    
    clear.click(lambda: [], outputs=chatbot)
    test_btn.click(test_model, outputs=test_result)

if __name__ == "__main__":
    print("🚀 Starting Enhanced Chat Interface...")
    demo.launch(
        server_port=7860,
        debug=True,
        share=True,
        show_error=True
    )