import torch
import clip

class ConceptEraser:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model, _ = clip.load("ViT-B/32", device=self.device)
    
    def remove_concepts(self, gradients, bad_concepts):
        """Remove prohibited concepts from gradients"""
        if not bad_concepts:
            return gradients
            
        # Convert concepts to CLIP embeddings
        text_inputs = clip.tokenize(bad_concepts).to(self.device)
        with torch.no_grad():
            text_features = self.clip_model.encode_text(text_inputs)
        
        # Create projection matrix
        C = text_features.T
        P = torch.eye(C.shape[0]).to(self.device) - C @ torch.linalg.pinv(C.T @ C) @ C.T
        
        # Filter gradients
        return P @ gradients