#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from ai.processing.text_processor import TextProcessor

async def test_direct():
    processor = TextProcessor()
    result = await processor.process_text("What is the derivative of x^2 + 3x + 5?")
    print("TextAnalysisResult attributes:")
    for attr in dir(result):
        if not attr.startswith('_'):
            print(f"  {attr}: {getattr(result, attr)}")
    
    print(f"\nResult type: {type(result)}")
    print(f"Has estimated_time_seconds: {hasattr(result, 'estimated_time_seconds')}")

if __name__ == "__main__":
    asyncio.run(test_direct())
