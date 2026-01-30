# ADR 001: Agent vs MCP Server Architecture

## Status
Accepted

## Date
2026-01-30

## Context

We needed to decide whether to build CloudFormation automation as:
1. MCP Server (tool provider)
2. Agent (decision maker)
3. Hybrid approach

Initial implementation had MCP server tools that called LLMs internally, creating an anti-pattern where tools made decisions instead of agents.

## Decision

**Use Agents with Simple Tools**

We decided to:
- Build two specialized Strands agents (Onboarding, Provisioning)
- Agents use their own LLMs for all decision-making
- Tools are simple, deterministic AWS API calls only
- No LLMs inside tools

## Rationale

### Why Not Pure MCP Server?

MCP servers are tool providers, not decision makers:
- ❌ Can't have conversations
- ❌ Can't maintain context across interactions
- ❌ Can't make multi-step decisions
- ❌ Just execute predefined operations

### Why Not MCP Server with LLM Tools?

Original implementation had tools like:
```python
@mcp.tool()
def build_cfn_template(prompt: str) -> dict:
    # Calls Claude to generate template
    bedrock.invoke_model(...)
```

**Problems:**
- ❌ Anti-pattern: Tools making decisions
- ❌ Outer agent can't see reasoning
- ❌ Double LLM calls (agent + tool's LLM)
- ❌ Expensive and slow
- ❌ Can't chain tools effectively

### Why Agents with Simple Tools? ✅

```python
# Agent makes decisions
agent = Agent(
    tools=[validate_template, deploy_stack],  # Simple AWS API calls
    system_prompt="You design architectures and generate templates..."
)

# Tools just execute
@tool
def validate_template(template: str) -> dict:
    return cfn.validate_template(TemplateBody=template)  # AWS API only
```

**Benefits:**
- ✅ Single LLM makes all decisions
- ✅ Agent sees full context
- ✅ Tools are deterministic
- ✅ Cheaper (one LLM call)
- ✅ Faster execution
- ✅ Better observability

## Consequences

### Positive
- Clear separation of concerns
- Agents handle reasoning, tools handle execution
- Better cost efficiency
- Improved debugging and observability
- Agents can chain tools intelligently

### Negative
- Need to deploy agents (more infrastructure)
- Agents require more careful prompt engineering
- Can't reuse MCP server's LLM-powered tools

### Neutral
- MCP server still useful for other use cases
- Can keep MCP server for UI/other clients
- Agents and MCP server can coexist

## Implementation

**Onboarding Agent:**
- LLM designs architectures
- LLM generates CloudFormation templates
- LLM performs Well-Architected reviews
- Tools: `validate_cfn_template` (AWS API), `deploy_with_provisioning_agent` (A2A)

**Provisioning Agent:**
- LLM monitors deployment progress
- LLM decides when to check status
- Tools: `validate_cfn_template`, `deploy_cfn_stack`, `get_stack_status` (all AWS API)
- Tool: `request_design_from_onboarding_agent` (A2A)

## References
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Strands Agents Documentation](https://strandsagents.com/)
- [AgentCore Runtime A2A Support](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-a2a.html)
