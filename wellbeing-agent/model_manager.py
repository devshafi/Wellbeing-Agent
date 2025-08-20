from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class ModelManager:
    _instance = None
    _model = None
    _tokenizer = None
    _loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    def load_model(self, peft_model_id=None):
        """Load model only once"""
        if self._loaded:
            print("Model already loaded!")
            return self._model, self._tokenizer
        
        if peft_model_id is None:
            peft_model_id = "/home/jovyan/Works/MSc_Thesis/mh_function_calling/model_training/finetuned_models/llama3.2_3b_mh_function_calling_v6"
        
        print("Loading model...")
        
        # Load PEFT config to get base model info
        config = PeftConfig.from_pretrained(peft_model_id)
        print(f"Base model: {config.base_model_name_or_path}")
        
        # Load base model
        self._model = AutoModelForCausalLM.from_pretrained(
            config.base_model_name_or_path,
            device_map={"": 0},
            torch_dtype=torch.bfloat16
        )
        
        # Load tokenizer from the adapter (contains special tokens)
        self._tokenizer = AutoTokenizer.from_pretrained(peft_model_id)
        print(f"Tokenizer vocab size: {len(self._tokenizer)}")
        
        # Resize model to accommodate new tokens
        self._model.resize_token_embeddings(len(self._tokenizer))
        
        # Load the adapter weights
        self._model = PeftModel.from_pretrained(self._model, peft_model_id)
        self._model.to(torch.bfloat16)
        self._model.eval()
        
        self._loaded = True
        print("Model loaded successfully!")
        
        return self._model, self._tokenizer
    
    def get_model(self):
        """Get loaded model and tokenizer"""
        if not self._loaded:
            self.load_model()
        return self._model, self._tokenizer
    
    def test_model(self, patient_id, query, max_length=1024):
        """Test the model with inference"""
        model, tokenizer = self.get_model()
        
        # Format exactly like training data
        messages = [
            {
                "role": "system",
                "content": """You are a helpful mental health assistant. When users ask for health data, use the available functions to retrieve the information. Think through your response before choosing a function. Use <think>your reasoning</think> tags to show your thought process, then use <function>json</function> tags to call the appropriate function."""
            },
            {
                "role": "user",
                "content": f"Patient ID: {patient_id}\nQuery: {query}"
            }
        ]
        
        # Apply chat template
        prompt = tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Tokenize and generate
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        input_length = inputs['input_ids'].shape[1]
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_length,
                do_sample=True,
                temperature=0.1,              
                top_p=0.95,                 
                repetition_penalty=1.0,     
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        
        response_tokens = outputs[0][input_length:]
        response = tokenizer.decode(response_tokens, skip_special_tokens=False)
        response = response.replace(tokenizer.eos_token, "").strip()
        
        return response

# Global instance
model_manager = ModelManager()