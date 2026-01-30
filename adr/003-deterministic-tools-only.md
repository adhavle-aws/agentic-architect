# ADR 003: Deterministic Tools Only (No LLMs in Tools)

## Status
Accepted

## Date
2026-01-30

## Context

Original MCP server had tools that called LLMs:
- `build_cfn_template()` - called Claude to generate templates
- `generate_architecture_overview()` - called Claude for design
- `well_architected_review()` - called Claude for analysis
- `analyze_cost_optimization()` - called Claude for recommendations

This created an anti-pattern where tools made decisions instead of agents.

## Decision

**Tools Must Be Deterministic - No LLMs Inside Tools**

All tools must:
- Execute deterministic operations only
- Call AWS APIs directly
- Return structured data
- Not make decisions or call LLMs

## Rationale

### The Anti-Pattern

```python
# BAD: Tool calls LLM
@tool
def build_cfn_template(prompt: str) -> dict:
    response = bedrock.invoke_model(...)  # ❌ LLM inside tool
    return {"template": response}

# Agent calls tool
agent = Agent(tools=[build_cfn_template])
response = agent("Create an S3 bucket")
# Result: Agent → Tool → LLM (hidden decision-making)
```

**Problems:**
- ❌ Agent can't see LLM's reasoning
- ❌ Can't interrupt or guide the process
- ❌ Double LLM invocation (agent + tool)
- ❌ Expensive (two model calls)
- ❌ Poor observability

### The Correct Pattern

```python
# GOOD: Tool just executes
@tool
def validate_cfn_template(template: str) -> dict:
    cfn = boto3.client('cloudformation')
    return cfn.validate_template(TemplateBody=template)  # ✅ AWS API only

# Agent makes decisions
agent = Agent(
    tools=[validate_cfn_template],
    system_prompt="You design architectures and generate CloudFormation templates..."
)
response = agent("Create an S3 bucket")
# Result: Agent (LLM) → Tool (AWS API) - clear separation
```

**Benefits:**
- ✅ Agent sees everything
- ✅ Single LLM call
- ✅ Cheaper and faster
- ✅ Better observability
- ✅ Agent can chain tools intelligently

## Implementation

### Allowed in Tools

✅ AWS API calls (boto3)
```python
@tool
def deploy_stack(stack_name: str, template: str) -> dict:
    cfn = boto3.client('cloudformation')
    return cfn.create_stack(StackName=stack_name, TemplateBody=template)
```

✅ Data transformations
```python
@tool
def parse_yaml_template(template: str) -> dict:
    return yaml.safe_load(template)
```

✅ External API calls (deterministic)
```python
@tool
def get_aws_pricing(service: str) -> dict:
    pricing = boto3.client('pricing')
    return pricing.get_products(ServiceCode=service)
```

✅ A2A agent calls (for collaboration)
```python
@tool
async def call_other_agent(message: str) -> dict:
    client = A2AClient(agent_url)
    return await client.send_message(message)
```

### NOT Allowed in Tools

❌ LLM calls
```python
@tool
def generate_template(prompt: str) -> dict:
    # ❌ NO! Agent should do this
    response = bedrock.invoke_model(...)
    return response
```

❌ Decision-making logic
```python
@tool
def decide_architecture(requirements: str) -> dict:
    # ❌ NO! Agent should decide
    if "high traffic" in requirements:
        return {"architecture": "multi-az"}
```

❌ Complex reasoning
```python
@tool
def analyze_costs(template: str) -> dict:
    # ❌ NO! Agent should analyze
    # Complex cost analysis logic...
```

## Consequences

### Positive
- Clear separation: agents think, tools execute
- Single source of reasoning (agent's LLM)
- Better cost efficiency
- Improved observability
- Easier to test tools independently

### Negative
- Agents need more detailed system prompts
- Agent must have knowledge to make decisions
- Can't offload complex logic to tools

### Migration Impact

**Before (MCP Server):**
- Tools: `build_cfn_template`, `generate_overview`, `well_architected_review`, `analyze_costs` (all with LLMs)
- Simple: `validate_template`, `provision_stack`

**After (Agents):**
- Agent handles: design, template generation, reviews, cost analysis
- Tools: `validate_cfn_template`, `deploy_cfn_stack`, `get_stack_status` (AWS API only)
- A2A tools: `deploy_with_provisioning_agent`, `request_design_from_onboarding_agent`

## Validation

Tools are deterministic if:
1. Same input → Same output (no randomness)
2. No LLM calls
3. No complex decision logic
4. Just data retrieval or API calls

## References
- Original MCP server: `cfn-mcp-server/mcp_server.py`
- New agents: `Agentic-Architect/agents/`
- [Strands Tools Documentation](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/)
