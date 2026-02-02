"""
Onboarding Agent v2 - Using AWS Labs CFN MCP Server

AWS Architecture design agent that uses AWS Labs CFN MCP server for deterministic tools.
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
PROVISIONING_AGENT_URL = os.environ.get('PROVISIONING_AGENT_URL')
AGENTCORE_RUNTIME_URL = os.environ.get('AGENTCORE_RUNTIME_URL', 'http://0.0.0.0:9000/')

# Connect to AWS Labs CFN MCP Server
logger.info("Connecting to AWS Labs CFN MCP Server...")
mcp_client = MCPClient("awslabs.cfn-mcp-server")
cfn_tools = mcp_client.get_tools()

logger.info(f"Loaded {len(cfn_tools)} tools from AWS Labs CFN MCP Server")

# A2A collaboration tool
@tool
async def deploy_with_provisioning_agent(template_body: str, stack_name: str) -> dict:
    """
    Deploy CloudFormation template using the Provisioning Agent via A2A.
    
    Args:
        template_body: CloudFormation template to deploy
        stack_name: Name for the CloudFormation stack
        
    Returns:
        Deployment result from Provisioning Agent
    """
    if not PROVISIONING_AGENT_URL:
        return {
            "success": False,
            "error": "Provisioning Agent not configured"
        }
    
    try:
        logger.info(f"🤝 Calling Provisioning Agent via A2A: {stack_name}")
        
        async with httpx.AsyncClient(timeout=600) as httpx_client:
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=PROVISIONING_AGENT_URL)
            agent_card = await resolver.get_agent_card()
            
            config = ClientConfig(httpx_client=httpx_client, streaming=False)
            factory = ClientFactory(config)
            client = factory.create(agent_card)
            
            message_text = f"""Deploy this CloudFormation template:

Stack Name: {stack_name}

Template:
{template_body}

Please deploy, monitor progress, and report results."""
            
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
                    
                    logger.info(f"✅ Received response from Provisioning Agent")
                    return {
                        "success": True,
                        "deployment_response": response_text
                    }
            
            return {"success": False, "error": "No response"}
            
    except Exception as e:
        logger.error(f"❌ Error calling Provisioning Agent: {e}")
        return {"success": False, "error": str(e)}


# Create Strands Agent with AWS Labs MCP tools
onboarding_agent = Agent(
    name="AWS Onboarding Agent",
    description="AWS Solutions Architect using AWS Labs CFN MCP server for CloudFormation operations",
    tools=[*cfn_tools, deploy_with_provisioning_agent],
    system_prompt="""You are an AWS Solutions Architect AI assistant.

Your workflow:
1. Gather requirements through conversation
2. Design AWS architectures following Well-Architected Framework
3. Use AWS Labs CFN MCP tools to:
   - create_resource: Create AWS resources
   - get_resource_schema_information: Understand resource schemas
   - create_template: Generate CloudFormation templates
   - list_resources: Check existing resources
4. When user approves deployment, use deploy_with_provisioning_agent tool

Available MCP tools from AWS Labs:
- create_resource, get_resource, update_resource, delete_resource
- list_resources, get_resource_schema_information
- create_template

YOU design the architecture and decide what resources to create.
The MCP tools execute the Cloud Control API calls.

Be conversational, ask clarifying questions, and explain your design decisions."""
)

# Create A2A server
a2a_server = A2AServer(
    agent=onboarding_agent,
    http_url=AGENTCORE_RUNTIME_URL,
    serve_at_root=True
)

# Create FastAPI app
app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "healthy", "agent": "onboarding", "mcp": "aws-labs-cfn"}

app.mount("/", a2a_server.to_fastapi_app())


if __name__ == "__main__":
    logger.info("🏗️  Starting Onboarding Agent v2 (AWS Labs CFN MCP)")
    logger.info(f"Runtime URL: {AGENTCORE_RUNTIME_URL}")
    logger.info(f"MCP Tools: {len(cfn_tools)}")
    uvicorn.run(app, host="0.0.0.0", port=9000)
