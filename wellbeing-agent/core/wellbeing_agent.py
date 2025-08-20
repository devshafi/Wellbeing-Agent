from models.model_manager import model_manager
from routing.query_router import query_router
from processors.conversation_processor import conversation_processor
from processors.hybrid_processor import hybrid_processor
from processors.function_calling_processor import function_calling_processor
from utils.history_manager import history_manager

class WellbeingAgent:
    """Main orchestrator for the wellbeing agent system"""
    
    def __init__(self):
        self.model_manager = model_manager
        self.query_router = query_router
        self.conversation_processor = conversation_processor
        self.hybrid_processor = hybrid_processor
        self.function_calling_processor = function_calling_processor
        self.history_manager = history_manager
    
    def setup_models(self):
        """Initialize all models with specific paths"""
        conversation_model_path = "/home/jovyan/Works/MSc_Thesis/mh_conversation/finetuned_model/llama3.2_3b_mh_conversation_v7"
        function_calling_model_path = "/home/jovyan/Works/MSc_Thesis/mh_function_calling/model_training/finetuned_models/llama3.2_3b_mh_function_calling_v6"
        
        print("🚀 Initializing Agentic Mental Health System...")
        
        try:
            # Load conversation model
            self.model_manager.load_conversation_model(conversation_model_path)
            
            # Load function calling model
            self.model_manager.load_function_calling_model(function_calling_model_path)
            
            # Load Llama 3.2 3B router
            self.model_manager.load_router_model()
            
            print("🎉 All models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to setup models: {e}")
            raise e
    
    def process_query(self, patient_id, query):
        """Main processing pipeline with modular routing"""
        print(f"🤖 Processing query for patient {patient_id}")
        print(f"📝 Query: {query}")
        
        # Step 1: Route the query
        route_decision = self.query_router.route_query(patient_id, query)
        print(f"🎯 Final routing decision: {route_decision}")
        
        # Step 2: Process based on route using appropriate processor
        if route_decision == "hybrid":
            print("🎭 Using HYBRID approach (data + conversation)")
            response = self.hybrid_processor.process_query(patient_id, query)
            
        elif route_decision == "function_calling":
            print("🔧 Using FUNCTION CALLING approach")
            response = self.function_calling_processor.process_query(patient_id, query)
            
        else:  # conversation
            print("💬 Using CONVERSATION approach")
            response = self.conversation_processor.generate_response(patient_id, query)
        
        # Step 3: Return structured result
        return {
            "route": route_decision,
            "response": response,
            "patient_id": patient_id,
            "query": query
        }
    
    def clear_history(self, patient_id):
        """Clear conversation history for a patient"""
        self.history_manager.clear_conversation_history(patient_id)
    
    def get_history_summary(self, patient_id):
        """Get conversation history summary"""
        return self.history_manager.get_conversation_summary(patient_id)

# Global instance
wellbeing_agent = WellbeingAgent()
