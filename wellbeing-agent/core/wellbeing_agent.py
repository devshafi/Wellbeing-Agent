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
        conversation_model_path = "/home/jovyan/Works/MSc_Thesis/mh_conversation/finetuned_model/llama3.2_3b_mh_conversation_v3"
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
        print("\n" + "="*60)
        print(f"� WELLBEING AGENT - COGNITIVE PROCESSING")
        print("="*60)
        print(f"👤 Patient: {patient_id}")
        print(f"� Query: '{query}'")
        
        # Step 1: Initial Analysis & Planning
        print(f"\n🔍 PHASE 1: QUERY ANALYSIS & PLANNING")
        print(f"├── Analyzing query complexity and intent...")
        print(f"├── Identifying potential health concerns...")
        print(f"└── Determining optimal processing strategy...")
        
        # Step 2: Route the query
        print(f"\n🎯 PHASE 2: INTELLIGENT ROUTING")
        route_decision = self.query_router.route_query(patient_id, query)
        print(f"✅ ROUTING DECISION: {route_decision.upper()}")
        
        # Step 3: Execution Planning
        print(f"\n⚡ PHASE 3: EXECUTION PLANNING")
        raw_data = None
        
        if route_decision == "hybrid":
            print(f"🎭 STRATEGY: HYBRID (Data + Conversation)")
            print(f"├── Plan: Retrieve relevant health data")
            print(f"├── Plan: Analyze patterns in data")
            print(f"├── Plan: Provide empathetic data-informed response")
            print(f"└── Executing hybrid processing pipeline...")
            hybrid_result = self.hybrid_processor.process_query(patient_id, query)
            
            # Handle structured response from hybrid processor
            if isinstance(hybrid_result, dict):
                response = hybrid_result.get("response", "")
                raw_data = hybrid_result.get("raw_data")
            else:
                response = hybrid_result  # Fallback for backwards compatibility
            
        elif route_decision == "function_calling":
            print(f"🔧 STRATEGY: FUNCTION CALLING (Pure Data)")
            print(f"├── Plan: Execute health data retrieval")
            print(f"├── Plan: Format data for presentation")
            print(f"└── Executing function calling pipeline...")
            response = self.function_calling_processor.process_query(patient_id, query)
            
        else:  # conversation
            print(f"💬 STRATEGY: CONVERSATION (Emotional Support)")
            print(f"├── Plan: Provide empathetic response")
            print(f"├── Plan: Draw on mental health expertise")
            print(f"└── Executing conversation pipeline...")
            response = self.conversation_processor.generate_response(patient_id, query)
        
        # Step 4: Completion
        print(f"\n✨ PROCESSING COMPLETE")
        print(f"📋 Response generated successfully")
        print("="*60)
        
        # Step 5: Return structured result
        result = {
            "route": route_decision,
            "response": response,
            "patient_id": patient_id,
            "query": query
        }
        
        # Add raw data if available
        if raw_data:
            result["raw_data"] = raw_data
            
        return result
    
    def clear_history(self, patient_id):
        """Clear conversation history for a patient"""
        self.history_manager.clear_conversation_history(patient_id)
    
    def get_history_summary(self, patient_id):
        """Get conversation history summary"""
        return self.history_manager.get_conversation_summary(patient_id)

# Global instance
wellbeing_agent = WellbeingAgent()
