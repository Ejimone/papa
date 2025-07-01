

class ContentQualityScorer:
    def __init__(self):
        self.gemini_client = GoogleGeminiClient()
        self.quality_thresholds = {
            "completeness": 0.8,
            "clarity": 0.7,
            "accuracy": 0.9
        }
    
    async def score_content_quality(self, content: ProcessedContent) -> QualityScore:
        # AI-powered quality assessment
        quality_analysis = await self.gemini_client.analyze_content(
            content=content.cleaned_content,
            task="quality_assessment",
            criteria=[
                "completeness",  # Has question and answer
                "clarity",       # Clear and understandable
                "accuracy",      # Factually correct
                "relevance",     # Relevant to academic context
                "difficulty_appropriateness"
            ]
        )
        
        # Duplicate detection
        duplicate_score = await self.check_for_duplicates(content)
        
        # Calculate composite quality score
        composite_score = self.calculate_composite_score(
            quality_analysis, 
            duplicate_score
        )
        
        return QualityScore(
            overall_score=composite_score,
            completeness=quality_analysis.completeness,
            clarity=quality_analysis.clarity,
            accuracy=quality_analysis.accuracy,
            is_duplicate=duplicate_score > 0.9,
            processing_confidence=content.text_confidence if hasattr(content, 'text_confidence') else 1.0
        )