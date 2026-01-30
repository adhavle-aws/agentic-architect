"""
Onboarding Agent - Strands A2A Implementation

AWS Architecture design agent that uses its own LLM for design decisions
and can collaborate with Provisioning Agent via A2A.
"""

import logging
import os
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer
import uvicorn
from fastapi import FastAPI
import boto3
import yaml
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROVISIONING_AGENT_URL = os.environ.get('PROVISIONING_AGENT_URL')
AGENTCORE_RUNTIME_URL = os.environ.get('AGENTCORE_RUNTIME_URL', 'http://0.0.0.0:9000/')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')


# Simple deterministic tools (no LLM)
@tool
def validate_cfn_template(template_body: str) -> dict:
    """
    Validate CloudFormation template using AWS API.
    
    Args:
        template_body: CloudFormation template (YAML or JSON string)
        
    Returns:
        Validation result with capabilities required
    """
    try:
        cfn = boto3.client('cloudformation', region_name=AWS_REGION)
        response = cfn.validate_template(TemplateBody=template_body)
        
        return {
            "success": True,
            "valid": True,
            "capabilities": response.get('Capabilities', []),
            "parameters": response.get('Parameters', [])
        }
    except Exception as e:
        return {
            "success": False,
            "valid": False,
            "error": str(e)
        }


@tool
async def deploy_with_provisioning_agent(template_body: str, stack_name: str) -> dict:
    """
    Deploy CloudFormation template using the Provisioning Agent via A2A.
    
    Use this tool when user approves deployment.
    
    Args:
        template_body: Validated CloudFormation template
        stack_name: Name for the CloudFormation stack
        
    Returns:
        Deployment result from Provisioning Agent
    """
    if not PROVISIONING_AGENT_URL:
        return {
            "success": False,
            "error": "Provisioning Agent not configured. Deploy Provisioning Agent first."
        }
    
    try:
        logger.info(f"🤝 Calling Provisioning Agent via A2A: {stack_name}")
        
        async with httpx.AsyncClient(timeout=600) as httpx_client:
            # Get Provisioning Agent card
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=PROVISIONING_AGENT_URL)
            agent_card = await resolver.get_agent_card()
            
            # Create A2A client
            config = ClientConfig(httpx_client=httpx_client, streaming=False)
            factory = ClientFactory(config)
            client = factory.create(agent_card)
            
            # Create message for Provisioning Agent
            message_text = f"""Deploy this CloudFormation template to AWS:

Stack Name: {stack_name}

Template:
{template_body}

Please validate, deploy, monitor progress, and report the results with stack outputs."""
            
            msg = Message(
                kind="message",
                role=Role.user,
                parts=[Part(TextPart(kind="text", text=message_text))],
                message_id=uuid4().hex,
            )
            
            # Send message and get response
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
            
            return {"success": False, "error": "No response from Provisioning Agent"}
            
    except Exception as e:
        logger.error(f"❌ Error calling Provisioning Agent: {e}")
        return {"success": False, "error": str(e)}


# Create Strands Agent
# The agent's LLM will handle all design decisions
onboarding_agent = Agent(
    name="AWS Onboarding Agent",
    description="AWS Solutions Architect that designs cloud architectures and generates CloudFormation templates",
    tools=[
        validate_cfn_template,
        deploy_with_provisioning_agent
    ],
    system_prompt="""You are an AWS Solutions Architect AI assistant helping customers design cloud architectures.

Your responsibilities:

1. REQUIREMENTS GATHERING
   - Ask clarifying questions to understand needs
   - Identify scale, availability, compliance, budget requirements
   - Be conversational and guide users through decisions

2. ARCHITECTURE DESIGN (You decide!)
   - Design AWS architectures based on requirements
   - Follow AWS Well-Architected Framework principles
   - Consider cost, performance, security, reliability
   - Explain your design decisions and trade-offs
   - YOU generate the architecture overview and reasoning

3. CLOUDFORMATION GENERATION (You write it!)
   - YOU write the CloudFormation template in YAML format
   - Include proper resource types and properties
   - Follow AWS best practices
   - Add appropriate resource names and tags

4. VALIDATION & DEPLOYMENT
   - Use validate_cfn_template tool to validate your template
   - When user approves, use deploy_with_provisioning_agent tool
   - The Provisioning Agent will handle deployment via A2A

5. REVIEWS & OPTIMIZATION (You analyze!)
   - YOU perform Well-Architected reviews
   - YOU analyze cost optimization opportunities
   - Provide specific, actionable recommendations

Example workflow:
User: "I need a web application"
You: "I'll help design that. Let me ask a few questions..."
[Gather requirements]
You: "Based on your needs, I'll design a 3-tier architecture with..."
[YOU design and explain]
You: "Here's the CloudFormation template I've created..."
[YOU generate the template]
You: "Let me validate this template..."
[Use validate_cfn_template tool]
You: "Template is valid! Would you like me to deploy it?"
User: "Yes"
You: [Use deploy_with_provisioning_agent tool]

Remember: YOU are the architect. YOU design, YOU generate templates, YOU analyze.
Tools are only for validation and deployment handoff."""
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
    return {"status": "healthy", "agent": "onboarding"}

# Mount A2A server at root
app.mount("/", a2a_server.to_fastapi_app())


if __name__ == "__main__":
    logger.info("🏗️  Starting Onboarding Agent (Strands A2A)")
    logger.info(f"Runtime URL: {AGENTCORE_RUNTIME_URL}")
    logger.info(f"Provisioning Agent: {PROVISIONING_AGENT_URL or 'Not configured yet'}")
    uvicorn.run(app, host="0.0.0.0", port=9000)
