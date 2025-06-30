
import spacy


class TextContentProcessor:
    def __init__(self):
        self.gemini_client = GoogleGeminiClient()
        self.nlp_processor = spacy.load("en_core_web_sm")
    
    async def process_text_question(self, content: str) -> ProcessedContent:
        # Content cleaning and normalization
        cleaned_content = self.clean_text(content)
        
        # Extract metadata using NLP
        doc = self.nlp_processor(cleaned_content)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # AI-powered content analysis
        analysis = await self.gemini_client.analyze_content(
            content=cleaned_content,
            task="extract_metadata",
            schema={
                "subject": "string",
                "topic": "string", 
                "difficulty": "integer",
                "question_type": "string",
                "keywords": "list[string]"
            }
        )
        
        return ProcessedContent(
            original_content=content,
            cleaned_content=cleaned_content,
            entities=entities,
            ai_metadata=analysis,
            content_type="text"
        )