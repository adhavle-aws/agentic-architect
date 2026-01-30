# Deployment Information - Strands A2A Agents

## Agent ARNs

### Onboarding Agent
```
arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/onboarding_agent-j6Y9CIGVDj
```

### Provisioning Agent
```
arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/provisioning_agent-lZECd14iTW
```

## Runtime URLs (for A2A)

### Onboarding Agent
```
https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A905767016260%3Aruntime%2Fonboarding_agent-j6Y9CIGVDj/invocations/
```

### Provisioning Agent
```
https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A905767016260%3Aruntime%2Fprovisioning_agent-lZECd14iTW/invocations/
```

## Architecture

```
User
 ↓
Onboarding Agent (Strands)
 - LLM designs architecture
 - LLM generates CloudFormation
 - LLM performs reviews
 - Tools: validate_template, deploy_with_provisioning_agent (A2A)
 ↓ A2A Handoff
Provisioning Agent (Strands)
 - LLM monitors deployment
 - Tools: validate, deploy, get_status (AWS API only)
 - Tool: request_design_from_onboarding_agent (A2A)
```

## Key Features

✅ **Agents make decisions** - LLMs do the thinking  
✅ **Tools execute actions** - Just AWS API calls  
✅ **A2A collaboration** - Agents can call each other  
✅ **No anti-pattern** - No LLMs inside tools

## Environment Variables

```bash
export ONBOARDING_AGENT_ARN="arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/onboarding_agent-j6Y9CIGVDj"
export PROVISIONING_AGENT_ARN="arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/provisioning_agent-lZECd14iTW"

export ONBOARDING_AGENT_URL="https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A905767016260%3Aruntime%2Fonboarding_agent-j6Y9CIGVDj/invocations/"
export PROVISIONING_AGENT_URL="https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A905767016260%3Aruntime%2Fprovisioning_agent-lZECd14iTW/invocations/"

export AWS_REGION="us-east-1"
```

## Testing

```bash
# Test Onboarding Agent
agentcore invoke --input "Design a simple S3 bucket architecture"

# Test Provisioning Agent
agentcore invoke --input "I need help designing a web application first"
```

## CloudWatch Logs

```bash
# Onboarding Agent
aws logs tail /aws/bedrock-agentcore/runtimes/onboarding_agent-j6Y9CIGVDj-DEFAULT \
  --log-stream-name-prefix "2026/01/30/[runtime-logs" --follow

# Provisioning Agent
aws logs tail /aws/bedrock-agentcore/runtimes/provisioning_agent-lZECd14iTW-DEFAULT \
  --log-stream-name-prefix "2026/01/30/[runtime-logs" --follow
```

## Deployment Date
January 30, 2026 - 4:42 PM EST

## Status
✅ Both agents deployed with Strands A2A  
✅ Simple deterministic tools (no LLM in tools)  
✅ A2A collaboration configured  
⚠️  Need to set agent URLs as environment variables for A2A to work
