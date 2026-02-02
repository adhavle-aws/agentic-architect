# Using AWS Labs CFN MCP Server

## Decision

Use the official AWS Labs CloudFormation MCP Server instead of custom tools.

## Why?

✅ **Official AWS package** - Maintained by AWS Labs  
✅ **Deterministic tools** - No LLMs, just Cloud Control API  
✅ **1,100+ resources** - Supports all AWS CloudFormation resources  
✅ **Best practices** - IaC Generator with AWS best practices  
✅ **Well-tested** - Production-ready  

## Tools Available

- `create_resource` - Create AWS resources
- `get_resource` - Get resource details
- `update_resource` - Update resources
- `delete_resource` - Delete resources
- `list_resources` - List resources by type
- `get_resource_schema_information` - Get CloudFormation schemas
- `create_template` - Generate CloudFormation templates

## Agent Integration

Agents use MCP tools from AWS Labs server:

```python
from strands import Agent
from strands_tools.mcp import MCPClient

# Connect to AWS Labs CFN MCP server
mcp_client = MCPClient("awslabs.cfn-mcp-server")

agent = Agent(
    tools=mcp_client.get_tools(),
    system_prompt="You design AWS architectures using CloudFormation..."
)
```

## Benefits

- Agents make decisions
- MCP tools execute Cloud Control API calls
- No custom tool maintenance
- Always up-to-date with AWS resources

## References

- [AWS Labs MCP Server](https://awslabs.github.io/mcp/servers/cfn-mcp-server)
- [Cloud Control API](https://docs.aws.amazon.com/cloudcontrolapi/latest/userguide/what-is-cloudcontrolapi.html)
