from PyPDF2 import PdfReader
class DocumentProcessor:
    def __init__(self):
        self.document_ai_client = DocumentAIClient()
        self.pdf_parser = PyPDF2Parser()
    
    async def process_pdf_content(self, pdf_path: str) -> List[ProcessedContent]:
        # Extract pages and convert to images
        pages = await self.pdf_parser.extract_pages(pdf_path)
        processed_pages = []
        
        for page_num, page_image in enumerate(pages):
            # Process each page as image
            page_content = await self.process_page_content(
                page_image=page_image,
                page_number=page_num
            )
            processed_pages.append(page_content)
        
        # Combine pages into coherent questions
        questions = await self.extract_questions_from_pages(processed_pages)
        
        return questions