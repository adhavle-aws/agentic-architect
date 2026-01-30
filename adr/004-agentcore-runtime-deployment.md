# ADR 004: AgentCore Runtime for Agent Deployment

## Status
Accepted

## Date
2026-01-30

## Context

We needed to deploy Strands agents and had several options:
1. EC2 instances
2. ECS/Fargate containers
3. Lambda functions
4. Amazon Bedrock AgentCore Runtime

## Decision

**Deploy agents to Amazon Bedrock AgentCore Runtime**

Use AgentCore Runtime with A2A protocol support for hosting both agents.

## Rationale

### Why AgentCore Runtime?

**Built for Agents:**
- ✅ Designed specifically for AI agents
- ✅ Native A2A protocol support
- ✅ Automatic scaling
- ✅ Session management built-in
- ✅ Memory management (STM)
- ✅ Observability (CloudWatch, X-Ray)

**Deployment Benefits:**
- ✅ Direct code deploy (no Docker required)
- ✅ Python 3.13 runtime
- ✅ Auto-creates IAM roles
- ✅ Auto-creates S3 buckets
- ✅ Built-in authentication (IAM/OAuth)

**Cost Efficiency:**
- ✅ Pay per invocation
- ✅ No idle costs
- ✅ Automatic scaling

### Why Not EC2?

- ❌ Manual scaling
- ❌ Always-on costs
- ❌ Infrastructure management
- ❌ No built-in session management

### Why Not ECS/Fargate?

- ❌ Container management overhead
- ❌ More complex deployment
- ❌ Higher baseline costs
- ❌ Manual A2A setup

### Why Not Lambda?

- ❌ 15-minute timeout (too short for deployments)
- ❌ Cold starts
- ❌ Complex A2A setup
- ❌ No built-in agent features

## Implementation

### Deployment Configuration

```yaml
# .bedrock_agentcore.yaml
agents:
  onboarding_agent:
    deployment_type: direct_code_deploy
    runtime_type: PYTHON_3_13
    protocol: A2A
    memory:
      mode: STM_ONLY
      event_expiry_days: 30
  
  provisioning_agent:
    deployment_type: direct_code_deploy
    runtime_type: PYTHON_3_13
    protocol: A2A
    memory:
      mode: STM_ONLY
      event_expiry_days: 30
```

### Deployment Process

```bash
# Configure
agentcore configure -e agents/onboarding_agent.py --protocol A2A

# Deploy
agentcore launch

# Result: Agent ARN
arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/onboarding_agent-xyz
```

## Consequences

### Positive
- Serverless architecture
- Auto-scaling
- Built-in observability
- Native A2A support
- Simple deployment (one command)
- No infrastructure management

### Negative
- Vendor lock-in to AWS
- AgentCore Runtime is relatively new
- Limited to supported runtimes (Python 3.13)
- Requires AgentCore CLI

### Operational
- CloudWatch logs automatically configured
- X-Ray tracing enabled
- GenAI Observability dashboard available
- Memory managed automatically (30-day retention)

## Monitoring

**CloudWatch Logs:**
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/AGENT_ID-DEFAULT \
  --log-stream-name-prefix "2026/01/30/[runtime-logs" --follow
```

**GenAI Observability:**
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#gen-ai-observability/agent-core

**X-Ray Traces:**
- Automatic tracing of all invocations
- A2A handoffs traced
- Tool calls traced

## Cost Considerations

**Pricing Model:**
- Pay per invocation
- No idle costs
- Memory storage: $0.10/GB-month (STM)
- Data transfer: Standard AWS rates

**Estimated Costs:**
- 1000 invocations/month: ~$5-10
- Memory (2 agents): ~$0.20/month
- Much cheaper than always-on EC2/ECS

## Alternatives Considered

1. **Self-hosted on EC2**: More control, but higher cost and management overhead
2. **Kubernetes (EKS)**: Overkill for two agents
3. **Lambda**: Timeout limitations for long deployments
4. **Bedrock Agents**: Different service, would require rebuild

## References
- [AgentCore Runtime Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AgentCore Starter Toolkit](https://aws.github.io/bedrock-agentcore-starter-toolkit/)
- Deployment: `scripts/deploy_strands_agents.sh`
