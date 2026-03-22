"""
Example test file - tests/test_ai_router.py
"""

import pytest
import asyncio
from backend.providers.ai_router import AIRouter, GroqProvider


@pytest.fixture
def ai_router():
    """Create AI router instance for testing"""
    return AIRouter()


@pytest.mark.asyncio
async def test_ai_router_generation(ai_router):
    """Test AI text generation"""
    prompt = "What is machine learning?"
    response = await ai_router.generate(prompt)
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0


def test_get_available_providers(ai_router):
    """Test getting available providers"""
    providers = ai_router.get_available_providers()
    
    assert isinstance(providers, list)
    # At least one provider should be available
    assert len(providers) > 0


def test_groq_provider_initialization():
    """Test Groq provider initialization"""
    import os
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        pytest.skip("GROQ_API_KEY not set")
    
    provider = GroqProvider(groq_key)
    assert provider.is_available()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
