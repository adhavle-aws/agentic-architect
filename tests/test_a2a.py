"""
Test Agent-to-Agent (A2A) Communication

This script tests the A2A capability between Onboarding and Provisioning agents.
"""

import boto3
import json
import os
import sys


def test_onboarding_to_provisioning():
    """Test Onboarding Agent handing off to Provisioning Agent."""
    
    onboarding_arn = os.environ.get('ONBOARDING_AGENT_ARN')
    provisioning_arn = os.environ.get('PROVISIONING_AGENT_ARN')
    
    if not onboarding_arn or not provisioning_arn:
        print("❌ Error: Agent ARNs not set")
        print("Please set:")
        print("  export ONBOARDING_AGENT_ARN='arn:aws:bedrock-agentcore:...'")
        print("  export PROVISIONING_AGENT_ARN='arn:aws:bedrock-agentcore:...'")
        sys.exit(1)
    
    print("🧪 Testing A2A Communication")
    print("=" * 60)
    print(f"Onboarding Agent:   {onboarding_arn}")
    print(f"Provisioning Agent: {provisioning_arn}")
    print()
    
    # Test 1: Onboarding Agent with deployment request
    print("Test 1: Design + Deploy Request")
    print("-" * 60)
    
    bedrock_agent = boto3.client('bedrock-agent-runtime')
    
    # Start with Onboarding Agent
    print("📋 Sending to Onboarding Agent: 'Create a simple S3 bucket and deploy it'")
    
    try:
        response = bedrock_agent.invoke_agent(
            agentId=onboarding_arn.split('/')[-1],
            agentAliasId='DEFAULT',
            sessionId='test-session-1',
            inputText='Create a simple S3 bucket CloudFormation template and deploy it to AWS'
        )
        
        # Process response
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    print(f"Response: {text}")
        
        print("\n✅ Test 1 Complete")
        
    except Exception as e:
        print(f"❌ Test 1 Failed: {e}")
    
    # Test 2: Provisioning Agent requesting design help
    print("\n\nTest 2: Deployment with Design Request")
    print("-" * 60)
    
    print("🚀 Sending to Provisioning Agent: 'I need help designing a template first'")
    
    try:
        response = bedrock_agent.invoke_agent(
            agentId=provisioning_arn.split('/')[-1],
            agentAliasId='DEFAULT',
            sessionId='test-session-2',
            inputText='I want to deploy a web application but need help designing the architecture first'
        )
        
        # Process response
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    print(f"Response: {text}")
        
        print("\n✅ Test 2 Complete")
        
    except Exception as e:
        print(f"❌ Test 2 Failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 A2A Testing Complete")


def test_agent_collaboration_config():
    """Test that agents have proper A2A configuration."""
    
    print("\n🔍 Checking A2A Configuration")
    print("=" * 60)
    
    onboarding_arn = os.environ.get('ONBOARDING_AGENT_ARN')
    provisioning_arn = os.environ.get('PROVISIONING_AGENT_ARN')
    
    if not onboarding_arn or not provisioning_arn:
        print("❌ Agent ARNs not set")
        return
    
    bedrock_agent = boto3.client('bedrock-agent')
    
    # Check Onboarding Agent
    print("\n1. Onboarding Agent Configuration:")
    try:
        agent_id = onboarding_arn.split('/')[-1].split('-')[0]
        response = bedrock_agent.get_agent(agentId=agent_id)
        
        if 'agentCollaboration' in response:
            print("  ✅ A2A enabled")
            print(f"  Collaborators: {len(response.get('agentCollaborators', []))}")
        else:
            print("  ⚠️  A2A not configured")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Check Provisioning Agent
    print("\n2. Provisioning Agent Configuration:")
    try:
        agent_id = provisioning_arn.split('/')[-1].split('-')[0]
        response = bedrock_agent.get_agent(agentId=agent_id)
        
        if 'agentCollaboration' in response:
            print("  ✅ A2A enabled")
            print(f"  Collaborators: {len(response.get('agentCollaborators', []))}")
        else:
            print("  ⚠️  A2A not configured")
    except Exception as e:
        print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    print("🤝 Agent-to-Agent (A2A) Communication Test")
    print("=" * 60)
    print()
    
    # Check configuration first
    test_agent_collaboration_config()
    
    # Run A2A tests
    print("\n")
    proceed = input("Proceed with A2A tests? (yes/no): ")
    
    if proceed.lower() == 'yes':
        test_onboarding_to_provisioning()
    else:
        print("Cancelled.")
