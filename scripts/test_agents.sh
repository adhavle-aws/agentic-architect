#!/bin/bash

# Quick test script for deployed agents

export ONBOARDING_AGENT_ARN="arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/onboarding_agent-5fR28m8l3W"
export PROVISIONING_AGENT_ARN="arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/provisioning_agent-xv8yuv4bVd"

echo "🧪 Testing Deployed Agents"
echo "=========================="
echo ""

echo "1️⃣ Testing Onboarding Agent..."
echo "Input: 'Design a simple S3 bucket'"
echo ""

agentcore invoke --input "Design a simple S3 bucket for storing logs"

echo ""
echo "✅ Test complete!"
