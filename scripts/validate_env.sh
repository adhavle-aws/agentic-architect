#!/bin/bash

# Validate environment variables for Agentic-Architect

echo "🔍 Validating Environment Variables"
echo "===================================="
echo ""

# Check required variables
REQUIRED_VARS=(
    "AWS_REGION"
    "ONBOARDING_AGENT_ARN"
    "PROVISIONING_AGENT_ARN"
    "ONBOARDING_AGENT_URL"
    "PROVISIONING_AGENT_URL"
)

MISSING_VARS=()
INVALID_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    value="${!var}"
    
    if [ -z "$value" ]; then
        MISSING_VARS+=("$var")
    else
        echo "✅ $var is set"
        
        # Validate format
        case $var in
            *_ARN)
                if [[ ! $value =~ ^arn:aws:bedrock-agentcore: ]]; then
                    INVALID_VARS+=("$var (invalid ARN format)")
                fi
                ;;
            *_URL)
                if [[ ! $value =~ ^https?:// ]]; then
                    INVALID_VARS+=("$var (invalid URL format)")
                fi
                ;;
        esac
    fi
done

echo ""

# Report missing variables
if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "❌ Missing required variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "💡 Copy .env.example to .env and update with your values"
    echo "   cp .env.example .env"
    echo ""
    exit 1
fi

# Report invalid variables
if [ ${#INVALID_VARS[@]} -gt 0 ]; then
    echo "⚠️  Invalid variable formats:"
    for var in "${INVALID_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    exit 1
fi

# Test agent connectivity
echo "🌐 Testing Agent Connectivity"
echo "------------------------------"

# Test Onboarding Agent
echo "Testing Onboarding Agent..."
ONBOARDING_ID=$(echo "$ONBOARDING_AGENT_ARN" | awk -F'/' '{print $2}')
if aws bedrock-agentcore get-runtime \
    --runtime-identifier "$ONBOARDING_ID" \
    --region "$AWS_REGION" \
    --no-cli-pager >/dev/null 2>&1; then
    echo "✅ Onboarding Agent is accessible"
else
    echo "⚠️  Could not verify Onboarding Agent (may need permissions)"
fi

# Test Provisioning Agent
echo "Testing Provisioning Agent..."
PROVISIONING_ID=$(echo "$PROVISIONING_AGENT_ARN" | awk -F'/' '{print $2}')
if aws bedrock-agentcore get-runtime \
    --runtime-identifier "$PROVISIONING_ID" \
    --region "$AWS_REGION" \
    --no-cli-pager >/dev/null 2>&1; then
    echo "✅ Provisioning Agent is accessible"
else
    echo "⚠️  Could not verify Provisioning Agent (may need permissions)"
fi

echo ""
echo "===================================="
echo "✅ Environment validation complete!"
echo "===================================="
echo ""
echo "📝 Current configuration:"
echo "  Region: $AWS_REGION"
echo "  Onboarding Agent: $ONBOARDING_ID"
echo "  Provisioning Agent: $PROVISIONING_ID"
echo ""
echo "🚀 Ready to invoke agents!"
echo ""
