# UI Migration Guide: Adding A2A Agents

## Overview

This guide explains how to add A2A agent support to your existing UI without breaking current functionality.

## Current Architecture

```
Browser → WebSocket → Lambda → MCP Server (with LLM tools)
```

## Target Architecture

```
Browser → Backend Proxy → A2A Agents (Strands)
                ↓
         (Optional: MCP Server fallback)
```

## Migration Strategy

### Option 1: Dual-Mode Backend (Recommended)

Keep both MCP and Agents, let users choose:

```
Browser
   ↓
Backend Proxy
   ├─→ MCP Server (fast, existing)
   └─→ A2A Agents (conversational, new)
```

### Option 2: Agent-Only (Clean Break)

Replace MCP with agents completely:

```
Browser → Backend Proxy → A2A Agents only
```

## Implementation Steps

### Step 1: Add A2A Client to Backend

```bash
cd cfn-mcp-server/ui/backend
npm install a2a-client httpx
```

Update `package.json`:
```json
{
  "dependencies": {
    "a2a-client": "^0.1.0",
    "httpx": "^0.25.0",
    "express": "^4.18.0",
    "@smithy/signature-v4": "^2.0.0",
    "@aws-sdk/credential-provider-node": "^3.0.0"
  }
}
```

### Step 2: Create Agent Proxy Module

Create `cfn-mcp-server/ui/backend/agent_proxy.js`:

```javascript
const httpx = require('httpx');

class AgentProxy {
  constructor(config) {
    this.onboardingUrl = config.onboardingUrl;
    this.provisioningUrl = config.provisioningUrl;
    this.region = config.region || 'us-east-1';
  }
  
  async callAgent(agentUrl, message) {
    // Get agent card
    const cardUrl = `${agentUrl}.well-known/agent-card.json`;
    const cardResponse = await fetch(cardUrl, {
      headers: {
        'Authorization': `Bearer ${await this.getAuthToken()}`,
        'Accept': 'application/json'
      }
    });
    
    const agentCard = await cardResponse.json();
    
    // Send message to agent
    const response = await fetch(agentUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await this.getAuthToken()}`,
        'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id': this.generateSessionId()
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'message/send',
        params: {
          message: {
            role: 'user',
            parts: [{ kind: 'text', text: message }],
            messageId: this.generateMessageId()
          }
        }
      })
    });
    
    return await response.json();
  }
  
  async getAuthToken() {
    // Get AWS credentials and sign request
    // Or use Cognito token
    // Implementation depends on auth method
    return 'token';
  }
  
  generateSessionId() {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  generateMessageId() {
    return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  // Wrapper methods matching UI expectations
  async generateArchitectureOverview(prompt) {
    const response = await this.callAgent(
      this.onboardingUrl,
      `Generate a comprehensive architecture overview for: ${prompt}`
    );
    return this.extractTextFromA2AResponse(response);
  }
  
  async buildCfnTemplate(prompt) {
    const response = await this.callAgent(
      this.onboardingUrl,
      `Generate a CloudFormation template in YAML format for: ${prompt}`
    );
    return this.extractTextFromA2AResponse(response);
  }
  
  async validateCfnTemplate(template) {
    const response = await this.callAgent(
      this.onboardingUrl,
      `Validate this CloudFormation template: ${template}`
    );
    return this.extractTextFromA2AResponse(response);
  }
  
  async wellArchitectedReview(prompt) {
    const response = await this.callAgent(
      this.onboardingUrl,
      `Perform a Well-Architected Framework review for: ${prompt}`
    );
    return this.extractTextFromA2AResponse(response);
  }
  
  async analyzeCostOptimization(prompt) {
    const response = await this.callAgent(
      this.onboardingUrl,
      `Analyze cost optimization opportunities for: ${prompt}`
    );
    return this.extractTextFromA2AResponse(response);
  }
  
  async provisionCfnStack(stackName, template) {
    const response = await this.callAgent(
      this.provisioningUrl,
      `Deploy CloudFormation stack named "${stackName}" with this template: ${template}`
    );
    return this.extractTextFromA2AResponse(response);
  }
  
  extractTextFromA2AResponse(response) {
    // Extract text from A2A message format
    if (response.result?.message?.parts) {
      return response.result.message.parts
        .filter(p => p.kind === 'text')
        .map(p => p.text)
        .join('\n');
    }
    return '';
  }
}

module.exports = AgentProxy;
```

### Step 3: Update Backend Router

```javascript
// backend/server.js

const AgentProxy = require('./agent_proxy');
const McpProxy = require('./mcp_proxy');  // Existing

// Configuration from environment
const USE_AGENTS = process.env.USE_AGENTS === 'true';

const agentProxy = new AgentProxy({
  onboardingUrl: process.env.ONBOARDING_AGENT_URL,
  provisioningUrl: process.env.PROVISIONING_AGENT_URL,
  region: process.env.AWS_REGION
});

// Existing MCP proxy
const mcpProxy = new McpProxy(process.env.MCP_SERVER_ARN);

// Unified endpoint - works with both MCP and Agents
app.post('/api/generate', async (req, res) => {
  const { operation, args } = req.body;
  
  try {
    let result;
    
    if (USE_AGENTS) {
      // Use A2A agents
      switch (operation) {
        case 'architecture_overview':
          result = await agentProxy.generateArchitectureOverview(args.prompt);
          break;
        case 'build_template':
          result = await agentProxy.buildCfnTemplate(args.prompt);
          break;
        case 'validate_template':
          result = await agentProxy.validateCfnTemplate(args.template);
          break;
        case 'well_architected_review':
          result = await agentProxy.wellArchitectedReview(args.prompt);
          break;
        case 'cost_optimization':
          result = await agentProxy.analyzeCostOptimization(args.prompt);
          break;
        case 'provision_stack':
          result = await agentProxy.provisionCfnStack(args.stackName, args.template);
          break;
      }
    } else {
      // Use MCP server (existing)
      result = await mcpProxy.callTool(operation, args);
    }
    
    res.json({ success: true, data: result });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Health check shows current mode
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    mode: USE_AGENTS ? 'agents' : 'mcp',
    onboardingAgent: USE_AGENTS ? process.env.ONBOARDING_AGENT_URL : null,
    provisioningAgent: USE_AGENTS ? process.env.PROVISIONING_AGENT_URL : null,
    mcpServer: !USE_AGENTS ? process.env.MCP_SERVER_ARN : null
  });
});
```

### Step 4: Update Frontend (Minimal Changes)

```javascript
// frontend/index.html

// Replace WebSocket calls with HTTP API calls
async function generateInfrastructure() {
  const prompt = document.getElementById('promptInput').value;
  
  try {
    // Show loading
    showLoading();
    
    // Call unified backend API
    const results = await Promise.all([
      callBackend('architecture_overview', { prompt }),
      callBackend('build_template', { prompt }),
      callBackend('well_architected_review', { prompt }),
      callBackend('cost_optimization', { prompt })
    ]);
    
    // Display results
    displayArchitecture(results[0].data);
    displayTemplate(results[1].data);
    displayReview(results[2].data);
    displayCost(results[3].data);
    
    // Enable provisioning
    enableProvisioningAgent();
    
  } catch (error) {
    showError(error.message);
  }
}

async function callBackend(operation, args) {
  const response = await fetch('http://localhost:3001/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ operation, args })
  });
  
  if (!response.ok) {
    throw new Error(`Backend error: ${response.statusText}`);
  }
  
  return await response.json();
}

// No other changes needed!
// All existing display functions work as-is
```

## Key Benefits

### 1. Zero Breaking Changes

- Existing UI code mostly unchanged
- Same API contract
- Same data format
- Same user experience

### 2. Easy Toggle

```bash
# Use MCP server
USE_AGENTS=false npm start

# Use A2A agents
USE_AGENTS=true npm start
```

### 3. Gradual Migration

- Test agents without affecting users
- Roll back easily if issues
- A/B test performance

### 4. Future-Proof

- Backend abstraction allows easy changes
- Can add more agents later
- Can switch protocols without UI changes

## Testing Plan

### 1. Test MCP Mode (Existing)

```bash
USE_AGENTS=false npm start
# Verify all features work
```

### 2. Test Agent Mode (New)

```bash
USE_AGENTS=true \
ONBOARDING_AGENT_URL="https://..." \
PROVISIONING_AGENT_URL="https://..." \
npm start
# Verify all features work
```

### 3. Compare Results

- Same prompt should produce similar results
- Agent mode may be more conversational
- Performance should be comparable

## Deployment

### Environment Variables

```bash
# Backend .env
USE_AGENTS=true
ONBOARDING_AGENT_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3A.../invocations/
PROVISIONING_AGENT_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3A.../invocations/
AWS_REGION=us-east-1

# Fallback (optional)
MCP_SERVER_ARN=arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/mcp_server-xyz
```

### Deployment Steps

1. Deploy A2A agents (already done)
2. Update backend with agent proxy
3. Set USE_AGENTS=true
4. Test thoroughly
5. Deploy to production
6. Monitor for issues
7. Gradually deprecate MCP mode

## Rollback Plan

If issues occur:
```bash
# Instant rollback
USE_AGENTS=false

# Restart backend
npm restart
```

## Next Steps

1. Create `agent_proxy.js` module
2. Update `server.js` with dual-mode support
3. Test with existing UI
4. Add conversational features (optional)
5. Deploy and monitor

## References
- ADR 001: Agent vs MCP Server
- ADR 002: Strands A2A
- Existing UI: `cfn-mcp-server/ui/`
- New agents: `Agentic-Architect/agents/`
