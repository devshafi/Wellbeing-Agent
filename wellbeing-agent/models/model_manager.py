from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class MultiModelManager:
    """Singleton class to manage multiple models efficiently"""
    
    _instance = None
    _conversation_model = None
    _function_calling_model = None
    _router_model = None
    _tokenizers = {}
    _loaded_models = set()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MultiModelManager, cls).__new__(cls)
        return cls._instance
    
    def load_conversation_model(self, model_path):
        """Load the conversation model"""
        if "conversation" in self._loaded_models:
            print("Conversation model already loaded!")
            return
        
        print("🔄 Loading conversation model...")
        try:
            config = PeftConfig.from_pretrained(model_path)
            print(f"Base model: {config.base_model_name_or_path}")
            
            self._conversation_model = AutoModelForCausalLM.from_pretrained(
                config.base_model_name_or_path,
                device_map={"": 0},
                torch_dtype=torch.bfloat16
            )
            
            self._tokenizers["conversation"] = AutoTokenizer.from_pretrained(model_path)
            print(f"Conversation tokenizer vocab size: {len(self._tokenizers['conversation'])}")
            
            self._conversation_model.resize_token_embeddings(len(self._tokenizers["conversation"]))
            self._conversation_model = PeftModel.from_pretrained(self._conversation_model, model_path)
            self._conversation_model.to(torch.bfloat16)
            self._conversation_model.eval()
            self._loaded_models.add("conversation")
            print("✅ Conversation model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load conversation model: {e}")
            raise e
    
    def load_function_calling_model(self, model_path):
        """Load the function calling model"""
        if "function_calling" in self._loaded_models:
            print("Function calling model already loaded!")
            return
        
        print("🔄 Loading function calling model...")
        try:
            config = PeftConfig.from_pretrained(model_path)
            print(f"Base model: {config.base_model_name_or_path}")
            
            # Use different GPU if available, otherwise same GPU
            device_map = {"": 1} if torch.cuda.device_count() > 1 else {"": 0}
            
            self._function_calling_model = AutoModelForCausalLM.from_pretrained(
                config.base_model_name_or_path,
                device_map=device_map,
                torch_dtype=torch.bfloat16
            )
            
            self._tokenizers["function_calling"] = AutoTokenizer.from_pretrained(model_path)
            print(f"Function calling tokenizer vocab size: {len(self._tokenizers['function_calling'])}")
            
            self._function_calling_model.resize_token_embeddings(len(self._tokenizers["function_calling"]))
            self._function_calling_model = PeftModel.from_pretrained(self._function_calling_model, model_path)
            self._function_calling_model.to(torch.bfloat16)
            self._function_calling_model.eval()
            self._loaded_models.add("function_calling")
            print("✅ Function calling model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load function calling model: {e}")
            raise e
    
    def load_router_model(self, model_name="meta-llama/Llama-3.2-3B-Instruct"):
        """Load Llama 3.2 3B as router model"""
        if "router" in self._loaded_models:
            print("Router model already loaded!")
            return
        
        print("🔄 Loading Llama 3.2 3B router model...")
        try:
            # Use CPU or different GPU for router to save memory
            device_map = "cpu" if torch.cuda.device_count() <= 2 else {"": 2}
            
            self._router_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=device_map,
                torch_dtype=torch.bfloat16 if device_map != "cpu" else torch.float32
            )
            
            self._tokenizers["router"] = AutoTokenizer.from_pretrained(model_name)
            if self._tokenizers["router"].pad_token is None:
                self._tokenizers["router"].pad_token = self._tokenizers["router"].eos_token
            
            self._router_model.eval()
            self._loaded_models.add("router")
            print("✅ Llama 3.2 3B router model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Router model failed to load: {e}")
            print("Falling back to rule-based routing")
            raise e
    
    def get_model(self, model_type):
        """Get a specific model"""
        if model_type == "conversation":
            return self._conversation_model
        elif model_type == "function_calling":
            return self._function_calling_model
        elif model_type == "router":
            return self._router_model
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def get_tokenizer(self, model_type):
        """Get tokenizer for a specific model"""
        return self._tokenizers.get(model_type)
    
    def is_model_loaded(self, model_type):
        """Check if a model is loaded"""
        return model_type in self._loaded_models

# Global instance
model_manager = MultiModelManager()
