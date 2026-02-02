# ADR 006: Use AWS Labs CFN MCP Server

## Status
Accepted

## Date
2026-01-30

## Context

We need deterministic CloudFormation tools for our agents. Options:
1. Custom boto3 tools (current)
2. AWS Labs CFN MCP Server (official)
3. Custom MCP server with LLMs (anti-pattern)

## Decision

**Use AWS Labs CFN MCP Server for all CloudFormation operations**

## Rationale

### Why AWS Labs CFN MCP Server?

✅ **Official AWS package** - Maintained by AWS Labs team  
✅ **Deterministic** - Uses Cloud Control API, no LLMs  
✅ **Comprehensive** - Supports 1,100+ AWS resources  
✅ **Best practices** - IaC Generator with AWS standards  
✅ **Well-tested** - Production-ready  
✅ **Always current** - Updated with new AWS resources  

### Why Not Custom Tools?

❌ Maintenance burden  
❌ Limited resource coverage  
❌ Need to keep up with AWS changes  
❌ Reinventing the wheel  

### Why Not Custom MCP with LLMs?

❌ Anti-pattern (LLMs in tools)  
❌ Already covered in ADR 001  

## Implementation

### Agent Integration

```python
from strands import Agent
from strands_tools.mcp import MCPClient

# Connect to AWS Labs CFN MCP server
mcp_client = MCPClient("awslabs.cfn-mcp-server")
cfn_tools = mcp_client.get_tools()

agent = Agent(
    tools=[*cfn_tools, custom_a2a_tool],
    system_prompt="You design architectures using CFN MCP tools..."
)
```

### Available Tools

From AWS Labs CFN MCP Server:
- `create_resource` - Create AWS resources via Cloud Control API
- `get_resource` - Get resource details
- `update_resource` - Update resources
- `delete_resource` - Delete resources
- `list_resources` - List resources by type
- `get_resource_schema_information` - Get CloudFormation schemas
- `create_template` - Generate CloudFormation templates from resources

## Consequences

### Positive
- Official AWS support
- Comprehensive resource coverage
- No maintenance burden
- Always up-to-date
- Best practices built-in
- Deterministic operations

### Negative
- External dependency
- Need to run MCP server
- Agents must connect to MCP server

### Neutral
- MCP server can run locally or deployed
- Can use readonly mode for safety

## Migration

### Before (Custom Tools)

```python
@tool
def validate_cfn_template(template: str):
    cfn = boto3.client('cloudformation')
    return cfn.validate_template(TemplateBody=template)
```

### After (AWS Labs MCP)

```python
# Agent automatically gets these tools from MCP server:
# - create_resource
# - get_resource_schema_information
# - create_template
# - etc.

agent = Agent(tools=mcp_client.get_tools())
```

## Deployment

Agents deployed with MCP client will connect to AWS Labs CFN MCP server at runtime.

## References
- [AWS Labs CFN MCP Server](https://awslabs.github.io/mcp/servers/cfn-mcp-server)
- [Cloud Control API](https://docs.aws.amazon.com/cloudcontrolapi/latest/userguide/)
- [Strands MCP Integration](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/mcp/)
