#!/bin/bash

# Test agent URLs and connectivity

set -e

echo "🧪 Testing Agent URLs and Connectivity"
echo "======================================="
echo ""

# Load environment
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "✅ Loaded .env file"
else
    echo "⚠️  No .env file found, using environment variables"
fi

echo ""

# Validate ARNs
echo "📋 Agent ARNs:"
echo "  Onboarding:   ${ONBOARDING_AGENT_ARN:-NOT SET}"
echo "  Provisioning: ${PROVISIONING_AGENT_ARN:-NOT SET}"
echo ""

# Validate URLs
echo "🔗 Agent URLs:"
echo "  Onboarding:   ${ONBOARDING_AGENT_URL:-NOT SET}"
echo "  Provisioning: ${PROVISIONING_AGENT_URL:-NOT SET}"
echo ""

# Test Onboarding Agent Card
if [ ! -z "$ONBOARDING_AGENT_URL" ]; then
    echo "🔍 Testing Onboarding Agent Card..."
    
    CARD_URL="${ONBOARDING_AGENT_URL}.well-known/agent-card.json"
    
    if curl -s -f -H "Accept: application/json" "$CARD_URL" >/dev/null 2>&1; then
        echo "✅ Onboarding Agent Card accessible"
        echo "   URL: $CARD_URL"
    else
        echo "❌ Onboarding Agent Card not accessible"
        echo "   URL: $CARD_URL"
        echo "   Note: May need authentication"
    fi
else
    echo "⚠️  ONBOARDING_AGENT_URL not set"
fi

echo ""

# Test Provisioning Agent Card
if [ ! -z "$PROVISIONING_AGENT_URL" ]; then
    echo "🔍 Testing Provisioning Agent Card..."
    
    CARD_URL="${PROVISIONING_AGENT_URL}.well-known/agent-card.json"
    
    if curl -s -f -H "Accept: application/json" "$CARD_URL" >/dev/null 2>&1; then
        echo "✅ Provisioning Agent Card accessible"
        echo "   URL: $CARD_URL"
    else
        echo "❌ Provisioning Agent Card not accessible"
        echo "   URL: $CARD_URL"
        echo "   Note: May need authentication"
    fi
else
    echo "⚠️  PROVISIONING_AGENT_URL not set"
fi

echo ""
echo "======================================="
echo "✅ Validation complete!"
echo ""
echo "💡 Next steps:"
echo "  1. If URLs not accessible, check authentication"
echo "  2. Test with: agentcore invoke --input 'Hello'"
echo "  3. View logs: aws logs tail /aws/bedrock-agentcore/runtimes/AGENT_ID-DEFAULT --follow"
echo ""
