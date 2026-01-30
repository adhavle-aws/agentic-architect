"""
WebSocket Lambda handler for A2A Agents
Uses boto3 bedrock-agent-runtime client for proper IAM permissions
"""
import json
import os
import boto3

ONBOARDING_AGENT_ARN = os.environ['ONBOARDING_AGENT_ARN']
PROVISIONING_AGENT_ARN = os.environ['PROVISIONING_AGENT_ARN']
REGION = os.environ.get('REGION', 'us-east-1')

lambda_client = boto3.client('lambda')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=REGION)
apigw = None

def get_apigw_client(event):
    global apigw
    if apigw is None:
        domain = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        endpoint = f"https://{domain}/{stage}"
        apigw = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint)
    return apigw

def send_message(connection_id, message, event):
    try:
        client = get_apigw_client(event)
        client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message)
        )
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def call_a2a_agent(agent_arn, message, session_id):
    """Call A2A agent using bedrock-agent-runtime client"""
    print(f"Calling agent: {agent_arn}")
    print(f"Session: {session_id}")
    print(f"Message: {message[:100]}")
    
    # Extract agent ID from ARN
    agent_id = agent_arn.split('/')[-1]
    
    try:
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId='DEFAULT',
            sessionId=session_id,
            inputText=message
        )
        
        # Collect streaming response
        response_text = ''
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    response_text += chunk['bytes'].decode('utf-8')
        
        print(f"Response length: {len(response_text)}")
        
        return {
            'response': response_text,
            'sessionId': session_id
        }
        
    except Exception as e:
        print(f"Error calling agent: {e}")
        raise

def lambda_handler(event, context):
    route_key = event.get('requestContext', {}).get('routeKey')
    connection_id = event.get('requestContext', {}).get('connectionId')
    
    # Async processing
    if 'async_processing' in event:
        async_event = event['async_processing']
        agent_type = async_event['agentType']
        message = async_event['message']
        request_id = async_event['requestId']
        session_id = async_event['sessionId']
        connection_id = async_event['connectionId']
        original_event = async_event['event']
        
        print(f"Async processing: {agent_type}")
        
        try:
            send_message(connection_id, {
                'type': 'progress',
                'requestId': request_id,
                'message': 'Agent is thinking...'
            }, original_event)
            
            agent_arn = ONBOARDING_AGENT_ARN if agent_type == 'onboarding' else PROVISIONING_AGENT_ARN
            result = call_a2a_agent(agent_arn, message, session_id)
            
            send_message(connection_id, {
                'type': 'response',
                'requestId': request_id,
                'agentType': agent_type,
                'response': result['response'],
                'sessionId': result['sessionId']
            }, original_event)
        
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            send_message(connection_id, {
                'type': 'error',
                'requestId': request_id,
                'error': str(e)
            }, original_event)
        
        return {'statusCode': 200}
    
    # WebSocket routes
    try:
        if route_key == '$connect':
            send_message(connection_id, {
                'type': 'connected',
                'message': 'Connected to Agentic-Architect'
            }, event)
            return {'statusCode': 200}
        
        elif route_key == '$disconnect':
            print(f"Disconnected: {connection_id}")
            return {'statusCode': 200}
        
        elif route_key == '$default':
            body = json.loads(event.get('body', '{}'))
            request_id = body.get('id')
            agent_type = body.get('agentType', 'onboarding')
            message = body.get('message')
            session_id = body.get('sessionId', f"session-{request_id}")
            
            print(f"Agent: {agent_type}, Request: {request_id}")
            
            send_message(connection_id, {
                'type': 'acknowledged',
                'requestId': request_id,
                'agentType': agent_type
            }, event)
            
            # Invoke async
            lambda_client.invoke(
                FunctionName=context.function_name,
                InvocationType='Event',
                Payload=json.dumps({
                    'async_processing': {
                        'agentType': agent_type,
                        'message': message,
                        'requestId': request_id,
                        'sessionId': session_id,
                        'connectionId': connection_id,
                        'event': event
                    }
                })
            )
            
            return {'statusCode': 200}
        
        return {'statusCode': 400}
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        if route_key == '$default':
            try:
                send_message(connection_id, {
                    'type': 'error',
                    'requestId': body.get('id'),
                    'error': str(e)
                }, event)
            except:
                pass
        
        return {'statusCode': 500}
