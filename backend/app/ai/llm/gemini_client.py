import google.generativeai as genai
from app.core.config import settings
from typing import Optional, List, Dict, Any

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY environment variable.")

        genai.configure(api_key=self.api_key)
        # For production, consider more robust error handling and logging for configuration.

        # Model names can be constants or configurable
        self.generative_model_name = "gemini-pro" # For text generation, explanations
        self.embedding_model_name = "text-embedding-004" # If using Gemini for embeddings too (though plan specifies Google Text-Embedding-004)

        self._generative_model = None
        # self._embedding_model = None # If using Gemini embeddings

    @property
    def generative_model(self):
        if self._generative_model is None:
            # Add safety settings and generation config as needed
            # safety_settings = [
            #     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            #     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            # ]
            # generation_config = genai.types.GenerationConfig(temperature=0.7, top_p=1, top_k=1, max_output_tokens=2048)
            self._generative_model = genai.GenerativeModel(
                self.generative_model_name,
                # safety_settings=safety_settings,
                # generation_config=generation_config
            )
        return self._generative_model

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generates text based on a given prompt.
        kwargs can include: temperature, top_p, top_k, max_output_tokens, etc.
        """
        try:
            # For more complex scenarios, might involve constructing parts for chat history
            # response = await self.generative_model.generate_content_async(prompt, **kwargs)
            response = self.generative_model.generate_content(prompt, **kwargs) # Using sync for now, adjust if service layer is async
            # Consider error handling for response.prompt_feedback (e.g., safety blocks)
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                 raise ValueError(f"Prompt blocked due to: {response.prompt_feedback.block_reason_message}")
            return response.text
        except Exception as e:
            # Log error: logging.error(f"Error generating text with Gemini: {e}")
            # Consider more specific exception handling
            raise RuntimeError(f"Gemini API request failed: {e}")


    async def generate_explanation(self, question_content: str, answer_content: Optional[str] = None) -> str:
        """
        Generates a step-by-step explanation for a given question (and optionally its answer).
        """
        # This is a placeholder for a more sophisticated prompt engineering step
        prompt = f"Provide a detailed, step-by-step explanation for the following question:\n\nQuestion: {question_content}\n"
        if answer_content:
            prompt += f"\nAnswer: {answer_content}\n"
        prompt += "\nExplanation:"

        return await self.generate_text(prompt)

    async def generate_similar_questions(self, question_content: str, num_variations: int = 3) -> List[str]:
        """
        Generates variations of a given question.
        """
        prompt = f"Generate {num_variations} variations of the following question. Ensure the variations maintain the original difficulty and topic, but are distinct questions.\n\nOriginal Question: {question_content}\n\nVariations:"
        # This might require parsing a structured response from the LLM
        response_text = await self.generate_text(prompt)
        # Naive parsing, assuming one question per line. Needs improvement.
        variations = [q.strip() for q in response_text.split('\n') if q.strip()]
        return variations[:num_variations]

    # If Gemini is also used for embeddings (alternative to dedicated Google Text-Embedding-004 service)
    # async def get_text_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
    #     """
    #     Generates embedding for a given text using Gemini embedding model.
    #     task_type can be: "RETRIEVAL_DOCUMENT", "SEMANTIC_SIMILARITY", "CLASSIFICATION", etc.
    #     """
    #     try:
    #         # result = await genai.embed_content_async(model=self.embedding_model_name, content=text, task_type=task_type)
    #         result = genai.embed_content(model=self.embedding_model_name, content=text, task_type=task_type) # Sync version
    #         return result['embedding']
    #     except Exception as e:
    #         # Log error
    #         raise RuntimeError(f"Gemini embedding API request failed: {e}")

# Global instance (optional, depends on usage pattern - could be managed by DI)
# gemini_client = GeminiClient()
