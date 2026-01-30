"""
Tests for Onboarding Agent
"""

import pytest
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.onboarding_agent import OnboardingAgent


@pytest.fixture
def agent():
    """Create onboarding agent instance."""
    return OnboardingAgent()


@pytest.mark.asyncio
async def test_start_conversation(agent):
    """Test starting a conversation."""
    response = await agent.start_conversation("I need a web application")
    
    assert 'message' in response
    assert 'next_steps' in response
    assert 'conversation_id' in response
    assert len(agent.conversation_history) > 0


@pytest.mark.asyncio
async def test_extract_requirements(agent):
    """Test requirements extraction."""
    await agent.start_conversation("I need a serverless API")
    await agent.continue_conversation("With DynamoDB")
    await agent.continue_conversation("And Lambda functions")
    
    requirements = agent._extract_requirements()
    
    assert "serverless" in requirements.lower()
    assert "dynamodb" in requirements.lower()
    assert "lambda" in requirements.lower()


def test_determine_intent(agent):
    """Test intent determination."""
    assert agent._determine_intent("generate template") == "generate_template"
    assert agent._determine_intent("create diagram") == "create_diagram"
    assert agent._determine_intent("review architecture") == "review_architecture"
    assert agent._determine_intent("analyze costs") == "analyze_costs"


def test_suggest_next_steps(agent):
    """Test next steps suggestion."""
    # No template yet
    steps = agent._suggest_next_steps()
    assert "Generate CloudFormation template" in steps
    
    # With template
    agent.current_design['template'] = "test"
    steps = agent._suggest_next_steps()
    assert "Deploy to AWS" in steps


@pytest.mark.asyncio
async def test_get_current_design(agent):
    """Test getting current design state."""
    design = agent.get_current_design()
    assert isinstance(design, dict)
    
    # Add some design elements
    agent.current_design['template'] = "test template"
    agent.current_design['overview'] = "test overview"
    
    design = agent.get_current_design()
    assert 'template' in design
    assert 'overview' in design


def test_conversation_history(agent):
    """Test conversation history tracking."""
    assert len(agent.conversation_history) == 0
    
    agent.conversation_history.append({
        "role": "user",
        "content": "test message"
    })
    
    assert len(agent.conversation_history) == 1
    assert agent.conversation_history[0]['role'] == 'user'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
