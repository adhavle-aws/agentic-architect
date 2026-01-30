# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records documenting key decisions made during the development of the Agentic-Architect project.

## What are ADRs?

ADRs document important architectural decisions, including:
- The context and problem
- The decision made
- Rationale and alternatives considered
- Consequences and trade-offs

## ADR Index

### [001: Agent vs MCP Server Architecture](001-agent-vs-mcp-server.md)
**Decision:** Use agents with simple tools instead of MCP server with LLM-powered tools

**Key Points:**
- Agents make decisions, tools execute actions
- No LLMs inside tools (anti-pattern)
- Single LLM call per interaction
- Better cost and observability

**Date:** 2026-01-30

---

### [002: Strands A2A for Agent Collaboration](002-strands-a2a-for-agent-collaboration.md)
**Decision:** Use Strands A2A protocol for inter-agent communication

**Key Points:**
- Standard A2A protocol for agent collaboration
- Agents discover each other via Agent Cards
- Seamless handoff with context preservation
- Deployed on AgentCore Runtime

**Date:** 2026-01-30

---

### [003: Two Specialized Agents](003-two-specialized-agents.md)
**Decision:** Build two specialized agents (Onboarding + Provisioning) instead of one or many

**Key Points:**
- Onboarding Agent: Design and documentation
- Provisioning Agent: Deployment and monitoring
- Clear separation of concerns
- Natural workflow boundary

**Date:** 2026-01-30

---

### [004: AgentCore Runtime Deployment](004-agentcore-runtime-deployment.md)
**Decision:** Deploy agents to Amazon Bedrock AgentCore Runtime

**Key Points:**
- Serverless, auto-scaling infrastructure
- Native A2A protocol support
- Built-in observability and session management
- Direct code deploy (no Docker)

**Date:** 2026-01-30

---

### [005: Deterministic Tools Only](003-deterministic-tools-only.md)
**Decision:** All tools must be deterministic (no LLMs inside tools)

**Key Points:**
- Tools execute AWS API calls only
- No decision-making in tools
- Agent's LLM handles all reasoning
- Clear separation of concerns

**Date:** 2026-01-30

---

## ADR Template

When creating new ADRs, use this template:

```markdown
# ADR XXX: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Date
YYYY-MM-DD

## Context
What is the issue we're facing? What factors are at play?

## Decision
What decision did we make?

## Rationale
Why did we make this decision? What alternatives did we consider?

## Consequences
What are the positive, negative, and neutral consequences?

## References
Links to relevant documentation, code, or resources
```

## Contributing

When making significant architectural decisions:
1. Create a new ADR with the next number
2. Use the template above
3. Document context, decision, and rationale
4. Update this README with the new ADR
5. Commit the ADR with the related code changes
