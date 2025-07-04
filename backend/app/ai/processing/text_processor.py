from typing import List, Dict, Any, Optional, Set, Tuple
import re
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

# Optional dependencies for advanced text processing
try:
    import spacy
    from spacy.lang.en.stop_words import STOP_WORDS
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    STOP_WORDS = set()
    SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    nltk = None
    NLTK_AVAILABLE = False

class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"
    NUMERICAL = "numerical"
    FILL_IN_BLANK = "fill_in_blank"
    MATCHING = "matching"
    UNKNOWN = "unknown"

class DifficultyLevel(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4

@dataclass
class TextAnalysisResult:
    cleaned_text: str
    question_type: QuestionType
    difficulty_score: float
    keywords: List[str]
    concepts: List[str]
    reading_level: float
    word_count: int
    sentence_count: int
    complexity_indicators: Dict[str, float]
    mathematical_expressions: List[str]
    language_detected: str = "en"

@dataclass
class TextChunk:
    text: str
    chunk_type: str
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any]

class TextProcessor:
    def __init__(self, use_advanced_nlp: bool = True):
        self.use_advanced_nlp = use_advanced_nlp and (SPACY_AVAILABLE or NLTK_AVAILABLE)
        self.nlp_model = None
        self.lemmatizer = None
        
        if self.use_advanced_nlp:
            self._initialize_nlp_models()
    
    def _initialize_nlp_models(self):
        """Initialize NLP models if available"""
        try:
            if SPACY_AVAILABLE:
                # Try to load English model
                try:
                    self.nlp_model = spacy.load("en_core_web_sm")
                    logging.info("SpaCy English model loaded successfully")
                except OSError:
                    logging.warning("SpaCy English model not found. Install with: python -m spacy download en_core_web_sm")
                    self.nlp_model = None
            
            if NLTK_AVAILABLE:
                try:
                    # Download required NLTK data if not already present
                    nltk.download('punkt', quiet=True)
                    nltk.download('stopwords', quiet=True)
                    nltk.download('wordnet', quiet=True)
                    nltk.download('averaged_perceptron_tagger', quiet=True)
                    
                    self.lemmatizer = WordNetLemmatizer()
                    logging.info("NLTK components initialized successfully")
                except Exception as e:
                    logging.warning(f"Failed to initialize NLTK: {e}")
                    
        except Exception as e:
            logging.warning(f"Failed to initialize NLP models: {e}")
            self.use_advanced_nlp = False

    async def process_text(self, text: str, context: Optional[str] = None) -> TextAnalysisResult:
        """
        Comprehensive text processing and analysis
        """
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        # Detect question type
        question_type = self.detect_question_type(cleaned_text)
        
        # Calculate difficulty score
        difficulty_score = await self.calculate_difficulty_score(cleaned_text)
        
        # Extract keywords and concepts
        keywords = await self.extract_keywords(cleaned_text)
        concepts = await self.extract_concepts(cleaned_text)
        
        # Calculate reading level
        reading_level = self.calculate_reading_level(cleaned_text)
        
        # Basic text statistics
        word_count = len(cleaned_text.split())
        sentence_count = len(self._split_sentences(cleaned_text))
        
        # Complexity indicators
        complexity_indicators = await self.analyze_complexity(cleaned_text)
        
        # Extract mathematical expressions
        mathematical_expressions = self.extract_mathematical_expressions(cleaned_text)
        
        # Language detection (basic)
        language_detected = self.detect_language(cleaned_text)
        
        return TextAnalysisResult(
            cleaned_text=cleaned_text,
            question_type=question_type,
            difficulty_score=difficulty_score,
            keywords=keywords,
            concepts=concepts,
            reading_level=reading_level,
            word_count=word_count,
            sentence_count=sentence_count,
            complexity_indicators=complexity_indicators,
            mathematical_expressions=mathematical_expressions,
            language_detected=language_detected
        )

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common OCR errors
        text = self._fix_ocr_errors(text)
        
        # Normalize quotes and dashes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'[––—]', '-', text)
        
        # Remove or replace special characters that might cause issues
        text = re.sub(r'[^\w\s\.\,\?\!\:\;\(\)\[\]\{\}\-\+\=\<\>\"\'\$\\\/@#%&\*]', '', text)
        
        return text

    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors"""
        # Common OCR replacements
        ocr_fixes = {
            r'\b0\b': 'O',  # Zero to letter O
            r'\b1\b': 'I',  # One to letter I (context dependent)
            r'\bS\b': '5',  # Letter S to number 5 (context dependent)
            r'rn': 'm',     # rn to m
            r'vv': 'w',     # vv to w
        }
        
        for pattern, replacement in ocr_fixes.items():
            text = re.sub(pattern, replacement, text)
        
        return text

    def detect_question_type(self, text: str) -> QuestionType:
        """
        Detect the type of question based on text patterns
        """
        text_lower = text.lower()
        
        # Multiple choice indicators
        if any(indicator in text for indicator in ['(a)', '(b)', '(c)', '(d)', 'A)', 'B)', 'C)', 'D)']):
            return QuestionType.MULTIPLE_CHOICE
        
        if re.search(r'\b[abcd]\)\s|\([abcd]\)', text):
            return QuestionType.MULTIPLE_CHOICE
        
        # True/False indicators
        if any(phrase in text_lower for phrase in ['true or false', 'true/false', 't/f']):
            return QuestionType.TRUE_FALSE
        
        # Fill in the blank indicators
        if '____' in text or '______' in text or re.search(r'__{3,}', text):
            return QuestionType.FILL_IN_BLANK
        
        # Numerical indicators
        if re.search(r'calculate|compute|find the value|solve for|what is \d+|how many', text_lower):
            return QuestionType.NUMERICAL
        
        # Essay indicators
        essay_words = ['explain', 'describe', 'discuss', 'analyze', 'compare', 'contrast', 'evaluate', 'critically']
        if any(word in text_lower for word in essay_words) and len(text.split()) > 10:
            return QuestionType.ESSAY
        
        # Short answer (default for questions)
        if '?' in text or text_lower.startswith(('what', 'how', 'why', 'when', 'where', 'who')):
            return QuestionType.SHORT_ANSWER
        
        return QuestionType.UNKNOWN

    async def calculate_difficulty_score(self, text: str) -> float:
        """
        Calculate difficulty score based on various factors
        """
        score = 0.0
        
        # Word length complexity
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        score += min(avg_word_length / 10, 0.3)  # Max 0.3 from word length
        
        # Sentence complexity
        sentences = self._split_sentences(text)
        if sentences:
            avg_sentence_length = sum(len(sent.split()) for sent in sentences) / len(sentences)
            score += min(avg_sentence_length / 50, 0.3)  # Max 0.3 from sentence length
        
        # Technical vocabulary
        technical_score = await self._calculate_technical_vocabulary_score(text)
        score += technical_score * 0.4  # Max 0.4 from technical vocab
        
        # Mathematical content
        math_expressions = self.extract_mathematical_expressions(text)
        if math_expressions:
            score += min(len(math_expressions) / 10, 0.2)  # Max 0.2 from math content
        
        # Complex grammatical structures
        if self.nlp_model:
            doc = self.nlp_model(text)
            complex_structures = len([sent for sent in doc.sents if len(list(sent.children)) > 5])
            score += min(complex_structures / 10, 0.2)  # Max 0.2 from grammar complexity
        
        return min(score, 1.0)

    async def _calculate_technical_vocabulary_score(self, text: str) -> float:
        """Calculate the technical vocabulary complexity"""
        words = text.lower().split()
        
        # Common technical prefixes and suffixes
        technical_patterns = [
            r'\b\w*(?:tion|sion|ment|ance|ence|ity|ism|ogy|ics)\b',
            r'\b(?:pre|post|anti|pro|sub|super|inter|trans|multi)\w*\b',
            r'\b\w{10,}\b',  # Very long words
        ]
        
        technical_count = 0
        for pattern in technical_patterns:
            technical_count += len(re.findall(pattern, text.lower()))
        
        return min(technical_count / len(words) if words else 0, 1.0)

    async def extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from text
        """
        keywords = []
        
        if self.nlp_model:
            # Use spaCy for advanced keyword extraction
            doc = self.nlp_model(text)
            
            # Extract named entities
            entities = [ent.text.lower() for ent in doc.ents]
            keywords.extend(entities)
            
            # Extract noun phrases
            noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]
            keywords.extend(noun_phrases)
            
            # Extract important words (excluding stop words)
            important_words = [
                token.lemma_.lower() for token in doc 
                if not token.is_stop and not token.is_punct and len(token.text) > 2 
                and token.pos_ in ['NOUN', 'ADJ', 'VERB']
            ]
            keywords.extend(important_words)
            
        else:
            # Fallback to simple keyword extraction
            words = text.lower().split()
            stop_words = STOP_WORDS if STOP_WORDS else {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but'}
            
            keywords = [
                word for word in words 
                if len(word) > 3 and word not in stop_words and word.isalpha()
            ]
        
        # Remove duplicates and return top keywords
        unique_keywords = list(set(keywords))
        return unique_keywords[:20]  # Return top 20 keywords

    async def extract_concepts(self, text: str) -> List[str]:
        """
        Extract higher-level concepts from text
        """
        concepts = []
        
        # Subject-specific concept patterns
        concept_patterns = {
            'mathematics': [r'\b(?:algebra|calculus|geometry|trigonometry|statistics|probability)\b'],
            'physics': [r'\b(?:mechanics|thermodynamics|electromagnetism|quantum|relativity)\b'],
            'chemistry': [r'\b(?:organic|inorganic|physical chemistry|biochemistry|molecular)\b'],
            'biology': [r'\b(?:genetics|evolution|ecology|anatomy|physiology|molecular biology)\b'],
            'computer_science': [r'\b(?:algorithm|data structure|programming|software|database)\b'],
            'economics': [r'\b(?:microeconomics|macroeconomics|supply|demand|market|inflation)\b'],
        }
        
        text_lower = text.lower()
        for domain, patterns in concept_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    concepts.append(domain)
                    break
        
        # Extract noun phrases as concepts if using spaCy
        if self.nlp_model:
            doc = self.nlp_model(text)
            noun_phrases = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) >= 2]
            concepts.extend(noun_phrases[:10])  # Add top 10 noun phrases
        
        return list(set(concepts))

    def calculate_reading_level(self, text: str) -> float:
        """
        Calculate reading level using Flesch Reading Ease score
        """
        sentences = self._split_sentences(text)
        words = text.split()
        
        if not sentences or not words:
            return 0.0
        
        # Count syllables (approximation)
        syllable_count = sum(self._count_syllables(word) for word in words)
        
        # Flesch Reading Ease formula
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllable_count / len(words)
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Convert to 0-1 scale (higher = easier to read)
        return max(0, min(flesch_score / 100, 1.0))

    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        
        if word[0] in vowels:
            count += 1
        
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        
        if word.endswith("e"):
            count -= 1
        
        if count == 0:
            count = 1
        
        return count

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if NLTK_AVAILABLE:
            try:
                return sent_tokenize(text)
            except:
                pass
        
        # Fallback to simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    async def analyze_complexity(self, text: str) -> Dict[str, float]:
        """
        Analyze various complexity indicators
        """
        indicators = {}
        
        words = text.split()
        sentences = self._split_sentences(text)
        
        # Lexical diversity
        unique_words = set(word.lower() for word in words if word.isalpha())
        indicators['lexical_diversity'] = len(unique_words) / len(words) if words else 0
        
        # Average word length
        indicators['avg_word_length'] = sum(len(word) for word in words) / len(words) if words else 0
        
        # Average sentence length
        indicators['avg_sentence_length'] = len(words) / len(sentences) if sentences else 0
        
        # Punctuation density
        punctuation_count = sum(1 for char in text if char in '.,;:!?()[]{}')
        indicators['punctuation_density'] = punctuation_count / len(text) if text else 0
        
        # Numerical content
        number_count = len(re.findall(r'\d+', text))
        indicators['numerical_density'] = number_count / len(words) if words else 0
        
        return indicators

    def extract_mathematical_expressions(self, text: str) -> List[str]:
        """
        Extract mathematical expressions from text
        """
        expressions = []
        
        # LaTeX patterns
        latex_patterns = [
            r'\$\$.*?\$\$',  # Display math
            r'\$.*?\$',      # Inline math
            r'\\begin\{.*?\}[\s\S]*?\\end\{.*?\}',  # LaTeX environments
            r'\\[a-zA-Z]+\{.*?\}',  # LaTeX commands
        ]
        
        for pattern in latex_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            expressions.extend(matches)
        
        # Mathematical symbols and expressions
        math_patterns = [
            r'[∑∏∫∂∇√π∞±≤≥≠≈∈∉⊂⊃∪∩∀∃]',  # Math symbols
            r'\b\d+\s*[+\-*/=<>]\s*\d+',  # Simple equations
            r'\b[a-zA-Z]\s*[=<>]\s*[a-zA-Z0-9+\-*/()]+',  # Variable equations
            r'\([^)]*[+\-*/][^)]*\)',  # Expressions in parentheses
        ]
        
        for pattern in math_patterns:
            matches = re.findall(pattern, text)
            expressions.extend(matches)
        
        return list(set(expressions))  # Remove duplicates

    def detect_language(self, text: str) -> str:
        """
        Basic language detection (placeholder for more sophisticated detection)
        """
        # Simple heuristic-based language detection
        english_indicators = ['the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'have', 'has']
        
        words = text.lower().split()
        english_count = sum(1 for word in words if word in english_indicators)
        
        if english_count / len(words) > 0.05 if words else False:
            return "en"
        
        return "unknown"

    async def validate_question_quality(self, text: str) -> Dict[str, Any]:
        """
        Validate the quality of a question
        """
        quality_metrics = {
            'completeness_score': 0.0,
            'clarity_score': 0.0,
            'complexity_score': 0.0,
            'issues': [],
            'suggestions': []
        }
        
        # Check completeness
        if len(text.strip()) < 10:
            quality_metrics['issues'].append("Question too short")
        else:
            quality_metrics['completeness_score'] = min(len(text.split()) / 20, 1.0)
        
        # Check for question mark or interrogative words
        if '?' not in text and not any(text.lower().startswith(word) for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            quality_metrics['issues'].append("Missing question indicator")
        
        # Check clarity (basic grammar and structure)
        if self.nlp_model:
            doc = self.nlp_model(text)
            complete_sentences = len([sent for sent in doc.sents if len(list(sent)) > 3])
            quality_metrics['clarity_score'] = min(complete_sentences / 2, 1.0)
        else:
            # Fallback clarity check
            quality_metrics['clarity_score'] = 0.8 if len(self._split_sentences(text)) > 0 else 0.3
        
        # Complexity score
        quality_metrics['complexity_score'] = await self.calculate_difficulty_score(text)
        
        # Generate suggestions
        if quality_metrics['completeness_score'] < 0.5:
            quality_metrics['suggestions'].append("Consider adding more context to the question")
        
        if quality_metrics['clarity_score'] < 0.5:
            quality_metrics['suggestions'].append("Improve question structure and grammar")
        
        return quality_metrics

    async def extract_answer_patterns(self, text: str) -> Dict[str, Any]:
        """
        Extract patterns that might indicate expected answer format
        """
        patterns = {
            'expected_format': 'text',
            'answer_length': 'medium',
            'requires_calculation': False,
            'requires_explanation': False,
            'multiple_parts': False
        }
        
        text_lower = text.lower()
        
        # Check for calculation requirements
        calc_indicators = ['calculate', 'compute', 'solve', 'find the value', 'determine']
        if any(indicator in text_lower for indicator in calc_indicators):
            patterns['requires_calculation'] = True
            patterns['expected_format'] = 'numerical'
        
        # Check for explanation requirements
        explain_indicators = ['explain', 'describe', 'justify', 'show your work', 'give reasons']
        if any(indicator in text_lower for indicator in explain_indicators):
            patterns['requires_explanation'] = True
            patterns['answer_length'] = 'long'
        
        # Check for multiple parts
        if re.search(r'\b(?:a\)|b\)|c\)|i\)|ii\)|iii\)|part\s+[abc]|question\s+\d+)', text_lower):
            patterns['multiple_parts'] = True
        
        # Estimate answer length based on question type
        if patterns['requires_explanation']:
            patterns['answer_length'] = 'long'
        elif patterns['requires_calculation']:
            patterns['answer_length'] = 'short'
        elif len(text.split()) > 30:
            patterns['answer_length'] = 'medium'
        else:
            patterns['answer_length'] = 'short'
        
        return patterns

    async def chunk_text_for_rag(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[TextChunk]:
        """
        Split text into chunks for RAG (Retrieval-Augmented Generation) processing.
        
        Args:
            text: The text to chunk
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of TextChunk objects
        """
        chunks = []
        
        # Clean the text first
        cleaned_text = self._clean_text(text)
        
        # Split into sentences for better chunk boundaries
        if self.use_advanced_nlp and self.nlp_model:
            doc = self.nlp_model(cleaned_text)
            sentences = [sent.text.strip() for sent in doc.sents]
        elif NLTK_AVAILABLE:
            sentences = sent_tokenize(cleaned_text)
        else:
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+', cleaned_text)
            sentences = [s.strip() for s in sentences if s.strip()]
        
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) + 1 > chunk_size and current_chunk:
                # Create chunk
                chunk = TextChunk(
                    text=current_chunk.strip(),
                    chunk_type="text_segment",
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk),
                    metadata={
                        "chunk_index": chunk_index,
                        "word_count": len(current_chunk.split()),
                        "sentence_count": len([s for s in current_chunk.split('.') if s.strip()])
                    }
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                if overlap > 0:
                    # Take last part of current chunk for overlap
                    overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                    current_chunk = overlap_text + " " + sentence
                    current_start = chunk.end_pos - len(overlap_text)
                else:
                    current_chunk = sentence
                    current_start = chunk.end_pos
                
                chunk_index += 1
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add final chunk if there's remaining text
        if current_chunk.strip():
            chunk = TextChunk(
                text=current_chunk.strip(),
                chunk_type="text_segment",
                start_pos=current_start,
                end_pos=current_start + len(current_chunk),
                metadata={
                    "chunk_index": chunk_index,
                    "word_count": len(current_chunk.split()),
                    "sentence_count": len([s for s in current_chunk.split('.') if s.strip()])
                }
            )
            chunks.append(chunk)
        
        return chunks

    # ...existing methods...
