"""
Provisioning Agent - Strands A2A Implementation

CloudFormation deployment agent with simple deterministic tools.
Can request design help from Onboarding Agent via A2A.
"""

import logging
import os
import time
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer
import uvicorn
from fastapi import FastAPI
import boto3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
ONBOARDING_AGENT_URL = os.environ.get('ONBOARDING_AGENT_URL')
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
        Validation result
    """
    try:
        cfn = boto3.client('cloudformation', region_name=AWS_REGION)
        response = cfn.validate_template(TemplateBody=template_body)
        
        return {
            "success": True,
            "valid": True,
            "capabilities": response.get('Capabilities', [])
        }
    except Exception as e:
        return {
            "success": False,
            "valid": False,
            "error": str(e)
        }


@tool
def deploy_cfn_stack(stack_name: str, template_body: str, capabilities: list = None) -> dict:
    """
    Deploy CloudFormation stack to AWS.
    
    Args:
        stack_name: Name for the CloudFormation stack
        template_body: CloudFormation template
        capabilities: IAM capabilities (optional)
        
    Returns:
        Deployment result with stack ID
    """
    try:
        cfn = boto3.client('cloudformation', region_name=AWS_REGION)
        
        # Check if stack exists
        try:
            cfn.describe_stacks(StackName=stack_name)
            stack_exists = True
        except:
            stack_exists = False
        
        params = {
            'StackName': stack_name,
            'TemplateBody': template_body
        }
        
        if capabilities:
            params['Capabilities'] = capabilities
        else:
            params['Capabilities'] = ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        
        if stack_exists:
            response = cfn.update_stack(**params)
            action = 'updated'
        else:
            response = cfn.create_stack(**params)
            action = 'created'
        
        return {
            "success": True,
            "action": action,
            "stack_id": response['StackId'],
            "stack_name": stack_name
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool
def get_stack_status(stack_name: str) -> dict:
    """
    Get CloudFormation stack status and outputs.
    
    Args:
        stack_name: Name of the CloudFormation stack
        
    Returns:
        Stack status, outputs, and details
    """
    try:
        cfn = boto3.client('cloudformation', region_name=AWS_REGION)
        response = cfn.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        
        outputs = []
        for output in stack.get('Outputs', []):
            outputs.append({
                "key": output['OutputKey'],
                "value": output['OutputValue'],
                "description": output.get('Description', '')
            })
        
        return {
            "success": True,
            "stack_name": stack_name,
            "status": stack['StackStatus'],
            "status_reason": stack.get('StackStatusReason', ''),
            "outputs": outputs,
            "creation_time": str(stack['CreationTime'])
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool
async def request_design_from_onboarding_agent(requirements: str) -> dict:
    """
    Request architecture design from Onboarding Agent via A2A.
    
    Use this when user needs architecture design or template generation.
    
    Args:
        requirements: Architecture requirements description
        
    Returns:
        Design response with CloudFormation template from Onboarding Agent
    """
    if not ONBOARDING_AGENT_URL:
        return {
            "success": False,
            "error": "Onboarding Agent not configured. Deploy Onboarding Agent first."
        }
    
    try:
        logger.info(f"🤝 Calling Onboarding Agent via A2A for design")
        
        async with httpx.AsyncClient(timeout=300) as httpx_client:
            # Get Onboarding Agent card
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=ONBOARDING_AGENT_URL)
            agent_card = await resolver.get_agent_card()
            
            # Create A2A client
            config = ClientConfig(httpx_client=httpx_client, streaming=False)
            factory = ClientFactory(config)
            client = factory.create(agent_card)
            
            # Create message
            message_text = f"""Design an AWS architecture and generate a CloudFormation template for:

{requirements}

Please provide:
1. Architecture overview with reasoning
2. CloudFormation template in YAML format
3. Validation confirmation

I'll handle the deployment once you provide the template."""
            
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
                    
                    logger.info(f"✅ Received design from Onboarding Agent")
                    return {
                        "success": True,
                        "design_response": response_text
                    }
            
            return {"success": False, "error": "No response from Onboarding Agent"}
            
    except Exception as e:
        logger.error(f"❌ Error calling Onboarding Agent: {e}")
        return {"success": False, "error": str(e)}


# Create Strands Agent
# The agent's LLM handles deployment logic and monitoring
provisioning_agent = Agent(
    name="AWS Provisioning Agent",
    description="Deploys CloudFormation templates to AWS and monitors deployment progress",
    tools=[
        validate_cfn_template,
        deploy_cfn_stack,
        get_stack_status,
        request_design_from_onboarding_agent
    ],
    system_prompt="""You are an AWS deployment specialist responsible for deploying CloudFormation templates.

Your workflow:

1. IF USER NEEDS DESIGN:
   - Use request_design_from_onboarding_agent tool (A2A collaboration)
   - Extract the template from the response
   - Proceed to deployment

2. IF USER PROVIDES TEMPLATE:
   - Validate using validate_cfn_template tool
   - If valid, proceed to deployment
   - If invalid, report errors and suggest fixes

3. DEPLOYMENT:
   - Use deploy_cfn_stack tool with stack name and template
   - Monitor by checking get_stack_status tool every 10-15 seconds
   - Report progress: CREATE_IN_PROGRESS → CREATE_COMPLETE
   - Handle failures: report errors, suggest rollback

4. RESULTS:
   - Use get_stack_status to get final outputs
   - Report stack outputs (URLs, endpoints, resource IDs)
   - Explain how to access deployed resources

Available tools:
- validate_cfn_template: Validate templates (AWS API call)
- deploy_cfn_stack: Deploy stacks (AWS API call)
- get_stack_status: Check status and outputs (AWS API call)
- request_design_from_onboarding_agent: Get design help (A2A collaboration)

Communication style:
- Use status emojis: 🚀 ⏳ ✅ ❌ 📊
- Be clear about deployment status
- Proactive about issues
- Provide actionable next steps

Remember: YOU monitor and decide when to check status. Tools just execute AWS API calls."""
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
    return {"status": "healthy", "agent": "provisioning"}

# Mount A2A server at root
app.mount("/", a2a_server.to_fastapi_app())


if __name__ == "__main__":
    logger.info("🚀 Starting Provisioning Agent (Strands A2A)")
    logger.info(f"Runtime URL: {AGENTCORE_RUNTIME_URL}")
    logger.info(f"Onboarding Agent: {ONBOARDING_AGENT_URL or 'Not configured yet'}")
    uvicorn.run(app, host="0.0.0.0", port=9000)
