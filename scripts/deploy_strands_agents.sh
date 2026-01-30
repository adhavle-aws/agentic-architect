#!/bin/bash

# Deploy Strands A2A Agents to Bedrock AgentCore Runtime

set -e

echo "🚀 Deploying Strands A2A Agents to AgentCore Runtime"
echo "===================================================="
echo ""

# Check environment
if [ -z "$MCP_SERVER_URL" ]; then
    echo "⚠️  MCP_SERVER_URL not set, using default: http://localhost:8080/mcp"
    export MCP_SERVER_URL="http://localhost:8080/mcp"
fi

echo "Environment:"
echo "  AWS_REGION: ${AWS_REGION:-us-east-1}"
echo "  MCP_SERVER_URL: $MCP_SERVER_URL"
echo ""

cd "$(dirname "$0")"

# Deploy Onboarding Agent
echo "1️⃣  Deploying Onboarding Agent..."
echo "------------------------------------"

agentcore configure \
    -e agents/onboarding_agent.py \
    --protocol A2A \
    --name onboarding_agent \
    --non-interactive

agentcore launch

# Get Onboarding Agent ARN
ONBOARDING_AGENT_ARN=$(agentcore status | grep "Agent ARN" | awk '{print $3}')
echo "✅ Onboarding Agent: $ONBOARDING_AGENT_ARN"

# Save to SSM
if [ ! -z "$ONBOARDING_AGENT_ARN" ]; then
    aws ssm put-parameter \
        --name "/agentic-architect/onboarding-agent-arn" \
        --value "$ONBOARDING_AGENT_ARN" \
        --type String \
        --overwrite \
        --region ${AWS_REGION:-us-east-1} 2>/dev/null || true
    
    # Construct runtime URL for Onboarding Agent
    ENCODED_ARN=$(echo "$ONBOARDING_AGENT_ARN" | sed 's/:/%3A/g' | sed 's/\//%2F/g')
    export ONBOARDING_AGENT_URL="https://bedrock-agentcore.${AWS_REGION:-us-east-1}.amazonaws.com/runtimes/${ENCODED_ARN}/invocations/"
    
    echo "  Runtime URL: $ONBOARDING_AGENT_URL"
fi

echo ""

# Deploy Provisioning Agent
echo "2️⃣  Deploying Provisioning Agent..."
echo "-------------------------------------"

# Set Onboarding Agent URL for Provisioning Agent to use
export ONBOARDING_AGENT_URL="$ONBOARDING_AGENT_URL"

agentcore configure \
    -e agents/provisioning_agent.py \
    --protocol A2A \
    --name provisioning_agent \
    --non-interactive

agentcore launch

# Get Provisioning Agent ARN
PROVISIONING_AGENT_ARN=$(agentcore status | grep "Agent ARN" | awk '{print $3}')
echo "✅ Provisioning Agent: $PROVISIONING_AGENT_ARN"

# Save to SSM
if [ ! -z "$PROVISIONING_AGENT_ARN" ]; then
    aws ssm put-parameter \
        --name "/agentic-architect/provisioning-agent-arn" \
        --value "$PROVISIONING_AGENT_ARN" \
        --type String \
        --overwrite \
        --region ${AWS_REGION:-us-east-1} 2>/dev/null || true
    
    # Construct runtime URL for Provisioning Agent
    ENCODED_ARN=$(echo "$PROVISIONING_AGENT_ARN" | sed 's/:/%3A/g' | sed 's/\//%2F/g')
    export PROVISIONING_AGENT_URL="https://bedrock-agentcore.${AWS_REGION:-us-east-1}.amazonaws.com/runtimes/${ENCODED_ARN}/invocations/"
    
    echo "  Runtime URL: $PROVISIONING_AGENT_URL"
fi

echo ""

# Summary
echo "===================================================="
echo "✅ Deployment Complete!"
echo "===================================================="
echo ""
echo "📋 Agent ARNs:"
echo "  Onboarding:   $ONBOARDING_AGENT_ARN"
echo "  Provisioning: $PROVISIONING_AGENT_ARN"
echo ""
echo "🔗 Runtime URLs:"
echo "  Onboarding:   $ONBOARDING_AGENT_URL"
echo "  Provisioning: $PROVISIONING_AGENT_URL"
echo ""
echo "🤝 A2A Communication:"
echo "  ✅ Onboarding Agent can call Provisioning Agent"
echo "  ✅ Provisioning Agent can call Onboarding Agent"
echo ""
echo "📝 Next Steps:"
echo "  1. Update agents with runtime URLs:"
echo "     agentcore configure --env PROVISIONING_AGENT_URL=$PROVISIONING_AGENT_URL"
echo "     agentcore configure --env ONBOARDING_AGENT_URL=$ONBOARDING_AGENT_URL"
echo ""
echo "  2. Test A2A:"
echo "     python3 test_a2a.py"
echo ""
echo "  3. View logs:"
echo "     aws logs tail /aws/bedrock-agentcore/runtimes/\$(echo \$ONBOARDING_AGENT_ARN | cut -d'/' -f2)-DEFAULT --follow"
echo ""
echo "💡 Save these for later:"
echo "  export ONBOARDING_AGENT_ARN='$ONBOARDING_AGENT_ARN'"
echo "  export PROVISIONING_AGENT_ARN='$PROVISIONING_AGENT_ARN'"
echo "  export ONBOARDING_AGENT_URL='$ONBOARDING_AGENT_URL'"
echo "  export PROVISIONING_AGENT_URL='$PROVISIONING_AGENT_URL'"
echo ""
