# Agent-to-Agent (A2A) Communication

## Overview

The Onboarding and Provisioning agents use Bedrock AgentCore's Agent-to-Agent (A2A) communication capability to collaborate seamlessly.

## How A2A Works

```
User: "Design and deploy a web app"
         ↓
┌────────────────────────┐
│  Onboarding Agent      │
│  - Gathers requirements│
│  - Designs architecture│
│  - Generates template  │
│  - Validates template  │
└───────────┬────────────┘
            │ A2A Handoff
            ↓
┌────────────────────────┐
│  Provisioning Agent    │
│  - Receives template   │
│  - Deploys to AWS      │
│  - Monitors progress   │
│  - Reports results     │
└────────────────────────┘
```

## Configuration

### 1. Agent Collaborators

Each agent defines its collaborators in `get_agent_collaborators()`:

**Onboarding Agent:**
```python
def get_agent_collaborators(self) -> List[Dict]:
    return [{
        "agentDescriptor": {
            "aliasArn": os.environ.get('PROVISIONING_AGENT_ARN')
        },
        "collaborationInstruction": "Use for deployment..."
    }]
```

**Provisioning Agent:**
```python
def get_agent_collaborators(self) -> List[Dict]:
    return [{
        "agentDescriptor": {
            "aliasArn": os.environ.get('ONBOARDING_AGENT_ARN')
        },
        "collaborationInstruction": "Use for design..."
    }]
```

### 2. Environment Variables

Set agent ARNs for cross-reference:

```bash
export ONBOARDING_AGENT_ARN="arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/onboarding-agent-xyz"
export PROVISIONING_AGENT_ARN="arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/provisioning-agent-xyz"
```

### 3. Collaboration Instructions

Each agent has specific instructions on when and how to collaborate:

**Onboarding → Provisioning:**
- When user approves deployment
- When user says "deploy", "provision", "create stack"
- After design is complete

**Provisioning → Onboarding:**
- When user asks for architecture design
- When template needs modification
- When reviews or cost analysis needed

## Usage Examples

### Example 1: Design and Deploy

```
User: "I need a 3-tier web application deployed to AWS"

Onboarding Agent:
  "I'll help you design that. Let me ask a few questions..."
  [Gathers requirements]
  [Generates template]
  "Template is ready! Would you like me to deploy it?"

User: "Yes, deploy it"

Onboarding Agent:
  "I'll hand you over to the Provisioning Agent to deploy this."
  [A2A handoff with template]

Provisioning Agent:
  "I've received the template. Deploying to AWS..."
  [Deploys stack]
  "✅ Deployment complete! Your application is available at..."
```

### Example 2: Deploy with Design Help

```
User: "Deploy a serverless API"

Provisioning Agent:
  "I need a CloudFormation template to deploy. Let me connect you 
   with the Onboarding Agent to design the architecture."
  [A2A handoff to Onboarding]

Onboarding Agent:
  "I'll help design your serverless API..."
  [Designs architecture]
  [Generates template]
  "Template ready! Handing back to Provisioning Agent."
  [A2A handoff back]

Provisioning Agent:
  "Deploying your serverless API..."
  [Deploys stack]
```

## Testing A2A

### Test Script

```bash
# Set agent ARNs
export ONBOARDING_AGENT_ARN="arn:aws:..."
export PROVISIONING_AGENT_ARN="arn:aws:..."

# Run A2A tests
python test_a2a.py
```

### Manual Testing

```bash
# Test Onboarding → Provisioning
agentcore invoke \
  --agent-id onboarding-agent \
  --input "Create an S3 bucket and deploy it"

# Test Provisioning → Onboarding
agentcore invoke \
  --agent-id provisioning-agent \
  --input "I need help designing a template first"
```

## A2A Benefits

1. **Seamless Handoff**: Users don't need to switch contexts
2. **Specialized Agents**: Each agent focuses on its expertise
3. **Automatic Collaboration**: Agents decide when to collaborate
4. **Context Preservation**: Session state maintained across agents
5. **Better UX**: Single conversation flow for complex workflows

## Monitoring A2A

### CloudWatch Logs

```bash
# View Onboarding Agent logs
aws logs tail /aws/bedrock-agentcore/runtimes/onboarding-agent-DEFAULT --follow

# View Provisioning Agent logs
aws logs tail /aws/bedrock-agentcore/runtimes/provisioning-agent-DEFAULT --follow
```

### X-Ray Traces

A2A handoffs are traced in AWS X-Ray:
- View agent collaboration traces
- Track handoff latency
- Debug collaboration issues

### Metrics

Key metrics to monitor:
- `AgentCollaborationCount`: Number of A2A handoffs
- `AgentCollaborationLatency`: Time for handoffs
- `AgentCollaborationErrors`: Failed handoffs

## Troubleshooting

### Issue: Agents not collaborating

**Check:**
1. Agent ARNs are set correctly
2. Agents have proper IAM permissions
3. Collaboration instructions are clear
4. Agents are in same region

**Fix:**
```bash
# Verify ARNs
echo $ONBOARDING_AGENT_ARN
echo $PROVISIONING_AGENT_ARN

# Check agent configuration
agentcore status
```

### Issue: Handoff fails

**Check:**
1. Target agent is deployed and active
2. Session state is preserved
3. CloudWatch logs for errors

**Fix:**
```bash
# Check agent status
aws bedrock-agent get-agent --agent-id <agent-id>

# View logs
aws logs tail /aws/bedrock-agentcore/runtimes/<agent-id>-DEFAULT
```

## Best Practices

1. **Clear Collaboration Instructions**: Be specific about when to collaborate
2. **Preserve Context**: Pass relevant information during handoff
3. **Handle Failures**: Gracefully handle collaboration failures
4. **Monitor Performance**: Track A2A latency and success rates
5. **Test Thoroughly**: Test all collaboration scenarios

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼─────────┐
│  Onboarding    │◄────►│  Provisioning    │
│     Agent      │ A2A  │     Agent        │
│                │      │                  │
│ - Design       │      │ - Deploy         │
│ - Generate     │      │ - Monitor        │
│ - Review       │      │ - Report         │
└────────┬───────┘      └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼────────────┐
         │   CFN MCP Server       │
         │   (Shared Tools)       │
         └────────────────────────┘
```

## Resources

- [Bedrock AgentCore A2A Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/userguide/agent-collaboration.html)
- [Agent Collaboration Best Practices](https://docs.aws.amazon.com/bedrock-agentcore/latest/userguide/collaboration-best-practices.html)
