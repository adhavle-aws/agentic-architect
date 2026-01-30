"""
Tests for Provisioning Agent
"""

import pytest
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.provisioning_agent import ProvisioningAgent


@pytest.fixture
def agent():
    """Create provisioning agent instance."""
    return ProvisioningAgent()


@pytest.fixture
def sample_template():
    """Sample CloudFormation template."""
    return """
AWSTemplateFormatVersion: '2010-09-09'
Description: Test template

Resources:
  TestBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: test-bucket-12345

Outputs:
  BucketName:
    Value: !Ref TestBucket
"""


def test_agent_initialization(agent):
    """Test agent initialization."""
    assert agent.mcp_url is not None
    assert agent.region is not None
    assert agent.cfn_client is not None
    assert isinstance(agent.deployment_history, list)


def test_extract_text(agent):
    """Test text extraction from MCP result."""
    # Mock MCP result
    class MockContent:
        def __init__(self, text):
            self.type = "text"
            self.text = text
    
    class MockResult:
        def __init__(self, text):
            self.content = [MockContent(text)]
    
    result = MockResult('{"success": true}')
    text = agent._extract_text(result)
    
    assert text == '{"success": true}'


def test_check_stack_exists(agent):
    """Test stack existence check."""
    # This will fail for non-existent stack
    exists = agent._check_stack_exists("non-existent-stack-12345")
    assert exists == False


def test_get_stack_outputs(agent):
    """Test getting stack outputs."""
    # This will return empty for non-existent stack
    outputs = agent._get_stack_outputs("non-existent-stack-12345")
    assert isinstance(outputs, list)


@pytest.mark.asyncio
async def test_get_stack_status_nonexistent(agent):
    """Test getting status of non-existent stack."""
    status = await agent.get_stack_status("non-existent-stack-12345")
    
    assert status['success'] == False
    assert 'error' in status


def test_print_deployment_summary(agent, capsys):
    """Test deployment summary printing."""
    result = {
        'status': 'CREATE_COMPLETE',
        'outputs': [
            {
                'OutputKey': 'BucketName',
                'OutputValue': 'test-bucket',
                'Description': 'Test bucket'
            }
        ]
    }
    
    agent._print_deployment_summary("test-stack", result)
    
    captured = capsys.readouterr()
    assert "test-stack" in captured.out
    assert "CREATE_COMPLETE" in captured.out
    assert "BucketName" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
