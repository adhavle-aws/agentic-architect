"""
Provisioning Agent v2 - Using AWS Labs CFN MCP Server

CloudFormation deployment agent using AWS Labs CFN MCP server for operations.
"""

import logging
import os
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer
from strands_tools.mcp import MCPClient
import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ONBOARDING_AGENT_URL = os.environ.get('ONBOARDING_AGENT_URL')
AGENTCORE_RUNTIME_URL = os.environ.get('AGENTCORE_RUNTIME_URL', 'http://0.0.0.0:9000/')

# Connect to AWS Labs CFN MCP Server
logger.info("Connecting to AWS Labs CFN MCP Server...")
mcp_client = MCPClient("awslabs.cfn-mcp-server")
cfn_tools = mcp_client.get_tools()

logger.info(f"Loaded {len(cfn_tools)} tools from AWS Labs CFN MCP Server")

# A2A collaboration tool
@tool
async def request_design_from_onboarding_agent(requirements: str) -> dict:
    """
    Request architecture design from Onboarding Agent via A2A.
    
    Args:
        requirements: Architecture requirements
        
    Returns:
        Design response with CloudFormation template
    """
    if not ONBOARDING_AGENT_URL:
        return {
            "success": False,
            "error": "Onboarding Agent not configured"
        }
    
    try:
        logger.info(f"🤝 Calling Onboarding Agent via A2A")
        
        async with httpx.AsyncClient(timeout=300) as httpx_client:
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=ONBOARDING_AGENT_URL)
            agent_card = await resolver.get_agent_card()
            
            config = ClientConfig(httpx_client=httpx_client, streaming=False)
            factory = ClientFactory(config)
            client = factory.create(agent_card)
            
            message_text = f"""Design an AWS architecture for:

{requirements}

Please generate a CloudFormation template."""
            
            msg = Message(
                kind="message",
                role=Role.user,
                parts=[Part(TextPart(kind="text", text=message_text))],
                message_id=uuid4().hex,
            )
            
            async for event in client.send_message(msg):
                if isinstance(event, Message):
                    response_text = ""
                    for part in event.parts:
                        if hasattr(part, 'text'):
                            response_text += part.text
                    
                    logger.info(f"✅ Received design from Onboarding Agent")
                    return {
                        "success": True,
                        "design_response": response_text
                    }
            
            return {"success": False, "error": "No response"}
            
    except Exception as e:
        logger.error(f"❌ Error calling Onboarding Agent: {e}")
        return {"success": False, "error": str(e)}


# Create Strands Agent with AWS Labs MCP tools
provisioning_agent = Agent(
    name="AWS Provisioning Agent",
    description="CloudFormation deployment specialist using AWS Labs CFN MCP server",
    tools=[*cfn_tools, request_design_from_onboarding_agent],
    system_prompt="""You are an AWS deployment specialist.

Your workflow:
1. If user needs design help: use request_design_from_onboarding_agent tool
2. If user provides template: deploy using AWS Labs CFN MCP tools
3. Use MCP tools to:
   - create_resource: Deploy CloudFormation resources
   - get_resource: Check resource status
   - list_resources: Monitor deployments
   - create_template: Generate templates if needed

Available MCP tools from AWS Labs:
- create_resource, get_resource, update_resource, delete_resource
- list_resources, get_resource_schema_information
- create_template

YOU monitor deployment and make decisions about when to check status.
The MCP tools execute the Cloud Control API calls.

Be clear about deployment status and provide actionable next steps."""
)

# Create A2A server
a2a_server = A2AServer(
    agent=provisioning_agent,
    http_url=AGENTCORE_RUNTIME_URL,
    serve_at_root=True
)

# Create FastAPI app
app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "healthy", "agent": "provisioning", "mcp": "aws-labs-cfn"}

app.mount("/", a2a_server.to_fastapi_app())


if __name__ == "__main__":
    logger.info("🚀 Starting Provisioning Agent v2 (AWS Labs CFN MCP)")
    logger.info(f"Runtime URL: {AGENTCORE_RUNTIME_URL}")
    logger.info(f"MCP Tools: {len(cfn_tools)}")
    uvicorn.run(app, host="0.0.0.0", port=9000)
