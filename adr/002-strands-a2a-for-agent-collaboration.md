# ADR 002: Strands A2A for Agent Collaboration

## Status
Accepted

## Date
2026-01-30

## Context

We needed agents to collaborate (Onboarding → Provisioning) and had to choose between:
1. Manual orchestrator pattern
2. Bedrock Agents with native A2A collaboration
3. AgentCore Runtime with Strands A2A protocol

Initial confusion: AgentCore Runtime "A2A protocol" means agents expose A2A-compliant APIs, not that they automatically collaborate.

## Decision

**Use Strands A2A Protocol for Inter-Agent Communication**

Deploy agents with Strands framework using A2A protocol for agent-to-agent communication.

## Rationale

### Why Not Manual Orchestrator?

```python
# Orchestrator pattern
onboarding_result = call_onboarding_agent(requirements)
provisioning_result = call_provisioning_agent(onboarding_result['template'])
```

**Problems:**
- ❌ Requires separate orchestrator service
- ❌ Not truly conversational
- ❌ Agents can't decide when to collaborate
- ❌ User has to switch contexts

### Why Not Bedrock Agents?

Bedrock Agents (different from AgentCore Runtime) support native collaboration but:
- ❌ Our agents are on AgentCore Runtime, not Bedrock Agents
- ❌ Different service with different APIs
- ❌ Would require complete rebuild
- ❌ Less flexibility

### Why Strands A2A? ✅

```python
# Onboarding Agent
@tool
async def deploy_with_provisioning_agent(template: str, stack_name: str):
    # Call Provisioning Agent via A2A
    client = A2AClient(provisioning_agent_url)
    response = await client.send_message(f"Deploy: {template}")
    return response
```

**Benefits:**
- ✅ Standard protocol (A2A specification)
- ✅ Agents decide when to collaborate
- ✅ Seamless handoff with context
- ✅ Works across platforms
- ✅ Native to Strands framework
- ✅ Deployed on AgentCore Runtime

## Implementation Details

### A2A Protocol Support

Each agent exposes:
- Agent Card at `/.well-known/agent-card.json`
- JSON-RPC endpoint for messages
- Runs on port 9000
- Stateless HTTP server

### Agent Collaboration Tools

**Onboarding Agent:**
```python
@tool
async def deploy_with_provisioning_agent(template_body: str, stack_name: str):
    """Deploy via Provisioning Agent (A2A)"""
    # Discovers Provisioning Agent via Agent Card
    # Sends message with template
    # Receives deployment result
```

**Provisioning Agent:**
```python
@tool
async def request_design_from_onboarding_agent(requirements: str):
    """Request design via Onboarding Agent (A2A)"""
    # Discovers Onboarding Agent via Agent Card
    # Sends requirements
    # Receives template
```

### Workflow

```
User: "Design and deploy a web app"
  ↓
Onboarding Agent:
  - Gathers requirements
  - Designs architecture (LLM)
  - Generates template (LLM)
  - Validates template (tool)
  - Calls deploy_with_provisioning_agent (A2A tool)
  ↓ A2A Protocol
Provisioning Agent:
  - Receives template via A2A
  - Validates (tool)
  - Deploys (tool)
  - Monitors status (tool + LLM)
  - Reports results
```

## Consequences

### Positive
- Seamless agent collaboration
- Standard protocol (interoperable)
- Agents maintain autonomy
- Context preserved across handoff
- Can add more agents easily

### Negative
- Requires both agents to be deployed
- Need to configure agent URLs
- A2A protocol adds complexity
- Requires network connectivity between agents

### Neutral
- Agents can work independently too
- A2A is optional (can use direct invocation)
- Protocol overhead is minimal

## Configuration Required

Agents need each other's runtime URLs:

```bash
export ONBOARDING_AGENT_URL="https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3A.../invocations/"
export PROVISIONING_AGENT_URL="https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3A.../invocations/"
```

## Alternatives Considered

1. **Agents as Tools Pattern**: Wrap one agent as a tool in another
   - Rejected: Less flexible than A2A
   
2. **Shared Memory**: Agents communicate via shared state
   - Rejected: Not conversational, complex state management

3. **Event-Driven**: Agents communicate via events/queues
   - Rejected: Asynchronous, harder to debug

## References
- [A2A Protocol Specification](https://a2a-protocol.org/)
- [Strands A2A Documentation](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/)
- [AgentCore Runtime A2A Support](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-a2a.html)
