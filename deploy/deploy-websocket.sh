#!/bin/bash

# Deploy WebSocket infrastructure for A2A agents

set -e

echo "🚀 Deploying WebSocket Infrastructure for A2A Agents"
echo "====================================================="
echo ""

STACK_NAME="agentic-architect-websocket"
REGION="${AWS_REGION:-us-east-1}"

# Get agent ARNs
ONBOARDING_ARN="${ONBOARDING_AGENT_ARN:-arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/onboarding_agent-j6Y9CIGVDj}"
PROVISIONING_ARN="${PROVISIONING_AGENT_ARN:-arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/provisioning_agent-lZECd14iTW}"

echo "Configuration:"
echo "  Stack: $STACK_NAME"
echo "  Region: $REGION"
echo "  Onboarding Agent: $ONBOARDING_ARN"
echo "  Provisioning Agent: $PROVISIONING_ARN"
echo ""

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
  --template-file websocket-infrastructure.yaml \
  --stack-name "$STACK_NAME" \
  --parameter-overrides \
    OnboardingAgentArn="$ONBOARDING_ARN" \
    ProvisioningAgentArn="$PROVISIONING_ARN" \
  --capabilities CAPABILITY_IAM \
  --region "$REGION"

echo ""
echo "✅ Deployment complete!"
echo ""

# Get WebSocket URL
WS_URL=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --query 'Stacks[0].Outputs[?OutputKey==`WebSocketUrl`].OutputValue' \
  --output text)

echo "🔗 WebSocket URL: $WS_URL"
echo ""
echo "📝 Update your frontend with:"
echo "  const WS_URL = '$WS_URL';"
echo ""
echo "💾 Saving to SSM Parameter Store..."
aws ssm put-parameter \
  --name "/agentic-architect/websocket-url" \
  --value "$WS_URL" \
  --type String \
  --overwrite \
  --region "$REGION" 2>/dev/null || echo "Note: Could not save to SSM"

echo ""
echo "✅ WebSocket infrastructure ready!"
echo ""
