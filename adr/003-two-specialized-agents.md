# ADR 003: Two Specialized Agents vs Single Agent

## Status
Accepted

## Date
2026-01-30

## Context

We needed to decide whether to build:
1. Single agent handling both design and deployment
2. Two specialized agents (Onboarding + Provisioning)
3. Multiple fine-grained agents (Design, Review, Cost, Deploy, Monitor)

## Decision

**Build Two Specialized Agents**

- **Onboarding Agent**: Architecture design, template generation, reviews
- **Provisioning Agent**: CloudFormation deployment, monitoring, reporting

## Rationale

### Why Not Single Agent?

```python
# Single agent doing everything
agent = Agent(
    tools=[design, generate, validate, deploy, monitor, review, analyze],
    system_prompt="You do everything..."
)
```

**Problems:**
- ❌ Too many responsibilities
- ❌ Complex system prompt
- ❌ Harder to test
- ❌ Can't scale independently
- ❌ Difficult to maintain

### Why Not Many Fine-Grained Agents?

```python
# Too many agents
design_agent = Agent(...)
review_agent = Agent(...)
cost_agent = Agent(...)
deploy_agent = Agent(...)
monitor_agent = Agent(...)
```

**Problems:**
- ❌ Over-engineered
- ❌ Too many handoffs
- ❌ Complex orchestration
- ❌ Higher latency
- ❌ More expensive

### Why Two Specialized Agents? ✅

```python
# Onboarding Agent: Design phase
onboarding_agent = Agent(
    tools=[validate_template, deploy_with_provisioning_agent],
    system_prompt="You design architectures..."
)

# Provisioning Agent: Deployment phase
provisioning_agent = Agent(
    tools=[validate, deploy, get_status, request_design],
    system_prompt="You deploy and monitor..."
)
```

**Benefits:**
- ✅ Clear separation of concerns
- ✅ Each agent has focused responsibility
- ✅ Easier to test and maintain
- ✅ Can scale independently
- ✅ Natural workflow boundary (design → deploy)

## Agent Responsibilities

### Onboarding Agent

**Primary Role:** Architecture design and documentation

**Responsibilities:**
1. Gather requirements through conversation
2. Design AWS architectures
3. Generate CloudFormation templates
4. Perform Well-Architected reviews
5. Analyze cost optimization
6. Validate templates
7. Hand off to Provisioning Agent when ready

**Tools:**
- `validate_cfn_template` (AWS API)
- `deploy_with_provisioning_agent` (A2A)

**Why This Scope?**
- Natural conversation flow
- All design-related tasks together
- Clear handoff point (approval)

### Provisioning Agent

**Primary Role:** CloudFormation deployment and monitoring

**Responsibilities:**
1. Validate templates before deployment
2. Deploy CloudFormation stacks
3. Monitor deployment progress
4. Handle errors and rollbacks
5. Report results with outputs
6. Request design help when needed

**Tools:**
- `validate_cfn_template` (AWS API)
- `deploy_cfn_stack` (AWS API)
- `get_stack_status` (AWS API)
- `request_design_from_onboarding_agent` (A2A)

**Why This Scope?**
- Focused on execution
- Deployment expertise
- Can work independently with provided templates

## Workflow

```
User: "I need a web application"
  ↓
Onboarding Agent:
  ├─ Gathers requirements
  ├─ Designs architecture
  ├─ Generates template
  ├─ Validates template
  └─ "Ready to deploy?"
  ↓
User: "Yes, deploy it"
  ↓
Onboarding Agent:
  └─ Calls deploy_with_provisioning_agent (A2A)
  ↓
Provisioning Agent:
  ├─ Validates template
  ├─ Deploys to AWS
  ├─ Monitors progress
  └─ Reports results
```

## Consequences

### Positive
- Clear boundaries between design and deployment
- Each agent can be improved independently
- Easier to test (focused scope)
- Natural conversation flow
- Can reuse agents separately

### Negative
- Need to deploy two agents (more infrastructure)
- A2A handoff adds latency
- Need to configure agent URLs

### Neutral
- Could add more agents later (e.g., Cost Optimization Agent)
- Agents can work independently if needed
- Handoff is optional (can use agents separately)

## Future Considerations

Could add more specialized agents:
- **Security Agent**: Security reviews, compliance checks
- **Cost Agent**: Detailed cost analysis and optimization
- **Monitoring Agent**: Post-deployment monitoring and alerts

But two agents are sufficient for MVP.

## Validation

Each agent should:
1. Have a clear, focused purpose
2. Be usable independently
3. Have 3-7 tools (not too many)
4. Have a clear handoff mechanism

## References
- Onboarding Agent: `agents/onboarding_agent.py`
- Provisioning Agent: `agents/provisioning_agent.py`
- [Strands Multi-Agent Patterns](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/multi-agent-patterns/)
