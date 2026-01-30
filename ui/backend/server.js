/**
 * Backend proxy for both MCP Server and A2A Agents
 * Supports Quick Generate (MCP wrapper) and A2A Agents modes
 */
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { SignatureV4 } = require('@smithy/signature-v4');
const { Sha256 } = require('@aws-crypto/sha256-js');
const { HttpRequest } = require('@smithy/protocol-http');
const { defaultProvider } = require('@aws-sdk/credential-provider-node');

const app = express();
const PORT = process.env.PORT || 3001;

// Configuration
const MCP_SERVER_ARN = process.env.MCP_SERVER_ARN;
const ONBOARDING_AGENT_URL = process.env.ONBOARDING_AGENT_URL;
const PROVISIONING_AGENT_URL = process.env.PROVISIONING_AGENT_URL;
const REGION = process.env.AWS_REGION || 'us-east-1';

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Encode ARN for URL
function encodeArn(arn) {
  return arn.replace(/:/g, '%3A').replace(/\//g, '%2F');
}

// Get MCP endpoint URL
function getMcpUrl() {
  const encodedArn = encodeArn(MCP_SERVER_ARN);
  return `https://bedrock-agentcore.${REGION}.amazonaws.com/runtimes/${encodedArn}/invocations?qualifier=DEFAULT`;
}

// MCP Proxy (Quick Generate mode)
app.post('/api/mcp', async (req, res) => {
  try {
    const mcpRequest = req.body;
    const sessionId = req.headers['x-session-id'];
    
    console.log('📡 MCP Request:', mcpRequest.method);
    
    // Get AWS credentials
    const credentials = await defaultProvider()();
    
    // Prepare request
    const url = new URL(getMcpUrl());
    const body = JSON.stringify(mcpRequest);
    
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json, text/event-stream',
      'Host': url.host,
    };
    
    if (sessionId) {
      headers['Mcp-Session-Id'] = sessionId;
    }
    
    // Create HTTP request for signing
    const request = new HttpRequest({
      method: 'POST',
      protocol: url.protocol,
      hostname: url.hostname,
      path: url.pathname + url.search,
      headers,
      body,
    });
    
    // Sign request with SigV4
    const signer = new SignatureV4({
      credentials,
      region: REGION,
      service: 'bedrock-agentcore',
      sha256: Sha256,
    });
    
    const signedRequest = await signer.sign(request);
    
    // Make request to AgentCore
    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: signedRequest.headers,
      body: signedRequest.body,
    });
    
    // Extract new session ID
    const newSessionId = response.headers.get('Mcp-Session-Id');
    if (newSessionId) {
      res.setHeader('X-Session-Id', newSessionId);
    }
    
    const data = await response.json();
    res.json(data);
    
  } catch (error) {
    console.error('❌ MCP Proxy error:', error);
    res.status(500).json({
      error: error.message,
      details: error.stack,
    });
  }
});

// A2A Agent Proxy
app.post('/api/agent/:agentType', async (req, res) => {
  try {
    const { agentType } = req.params;
    const { message, sessionId } = req.body;
    
    console.log(`🤖 A2A Request to ${agentType}:`, message.substring(0, 100));
    
    // Get agent URL
    const agentUrl = agentType === 'onboarding' 
      ? ONBOARDING_AGENT_URL 
      : PROVISIONING_AGENT_URL;
    
    if (!agentUrl) {
      throw new Error(`${agentType} agent URL not configured`);
    }
    
    // Get AWS credentials
    const credentials = await defaultProvider()();
    
    // Prepare A2A message
    const a2aMessage = {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'message/send',
      params: {
        message: {
          role: 'user',
          parts: [{ kind: 'text', text: message }],
          messageId: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        }
      }
    };
    
    const url = new URL(agentUrl);
    const body = JSON.stringify(a2aMessage);
    
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Host': url.host,
      'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id': sessionId || `session-${Date.now()}-${Math.random().toString(36).substr(2, 20)}`
    };
    
    // Create HTTP request for signing
    const request = new HttpRequest({
      method: 'POST',
      protocol: url.protocol,
      hostname: url.hostname,
      path: url.pathname,
      headers,
      body,
    });
    
    // Sign request with SigV4
    const signer = new SignatureV4({
      credentials,
      region: REGION,
      service: 'bedrock-agentcore',
      sha256: Sha256,
    });
    
    const signedRequest = await signer.sign(request);
    
    // Make request to agent
    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: signedRequest.headers,
      body: signedRequest.body,
    });
    
    const data = await response.json();
    
    // Extract text from A2A response
    let responseText = '';
    
    // Check for artifacts (AgentCore format)
    if (data.result?.artifacts) {
      for (const artifact of data.result.artifacts) {
        if (artifact.parts) {
          responseText += artifact.parts
            .filter(p => p.kind === 'text')
            .map(p => p.text)
            .join('');
        }
      }
    }
    // Fallback: Check for message format
    else if (data.result?.message?.parts) {
      responseText = data.result.message.parts
        .filter(p => p.kind === 'text')
        .map(p => p.text)
        .join('\n');
    }
    
    res.json({
      success: true,
      response: responseText,
      raw: data
    });
    
  } catch (error) {
    console.error('❌ A2A Proxy error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    modes: {
      quickGenerate: {
        available: !!MCP_SERVER_ARN,
        mcpServerArn: MCP_SERVER_ARN
      },
      a2aAgents: {
        available: !!(ONBOARDING_AGENT_URL && PROVISIONING_AGENT_URL),
        onboardingUrl: ONBOARDING_AGENT_URL ? 'configured' : 'missing',
        provisioningUrl: PROVISIONING_AGENT_URL ? 'configured' : 'missing'
      }
    },
    region: REGION
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Backend proxy running on http://localhost:${PORT}`);
  console.log(`\n📡 Available modes:`);
  console.log(`   Quick Generate: ${MCP_SERVER_ARN ? '✅' : '❌'}`);
  console.log(`   A2A Agents: ${(ONBOARDING_AGENT_URL && PROVISIONING_AGENT_URL) ? '✅' : '❌'}`);
  console.log(`\n🔐 Using AWS credentials from environment`);
});
