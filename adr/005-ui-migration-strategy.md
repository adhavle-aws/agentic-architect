# ADR 005: UI Enhancement Strategy - Adding A2A Agents

## Status
Accepted

## Date
2026-01-30

## Context

Existing UI uses MCP server with WebSocket connection. We want to add A2A agents without breaking existing functionality.

Options considered:
1. Replace MCP with agents (breaking change)
2. Dual-mode backend with toggle (complex)
3. Add A2A agents as new sidebar section (non-breaking)

## Decision

**Add A2A Agents as New Sidebar Section**

Keep existing MCP functionality and add A2A agents as a separate section in the sidebar.

## UI Structure

```
Sidebar:
├── Quick Generate (existing - MCP wrapper with LLM)
│   ├── Design
│   └── Deploy
│
└── A2A Agents (new - true agents)
    ├── Onboarding Agent (conversational)
    └── Provisioning Agent (deployment)
```

## Migration Strategy

### Phase 1: Add Agent Support (Non-Breaking)

**Backend Changes:**
```javascript
// backend/server.js - Add agent endpoints

// New: A2A agent proxy
app.post('/api/agent/:agentName', async (req, res) => {
  const { agentName } = req.params;
  const { message } = req.body;
  
  // Call A2A agent
  const agentUrl = getAgentUrl(agentName);
  const result = await callA2AAgent(agentUrl, message);
  
  res.json(result);
});

// Keep existing: MCP proxy
app.post('/api/mcp', async (req, res) => {
  // Existing MCP logic
});
```

**Frontend Changes:**
```javascript
// frontend/index.html - Add agent mode toggle

// Configuration
const USE_AGENTS = true;  // Toggle between MCP and Agents

async function generateInfrastructure() {
  if (USE_AGENTS) {
    await generateWithAgents();  // New
  } else {
    await generateWithMCP();     // Existing
  }
}
```

### Phase 2: Enable Agent Mode (Opt-In)

Add UI toggle to switch between modes:

```html
<div class="mode-selector">
  <label>
    <input type="radio" name="mode" value="mcp" checked> MCP Server (Fast)
  </label>
  <label>
    <input type="radio" name="mode" value="agents"> A2A Agents (Conversational)
  </label>
</div>
```

### Phase 3: Make Agents Default (Deprecate MCP)

Once agents are stable:
1. Make agents the default
2. Keep MCP as fallback
3. Eventually remove MCP option

## Implementation Plan

### Step 1: Backend Abstraction Layer

Create `backend/agent_proxy.js`:

```javascript
const { A2AClient } = require('a2a-client');

class AgentProxy {
  constructor(agentUrls) {
    this.onboardingUrl = agentUrls.onboarding;
    this.provisioningUrl = agentUrls.provisioning;
  }
  
  async callOnboardingAgent(message) {
    const client = new A2AClient(this.onboardingUrl);
    return await client.sendMessage(message);
  }
  
  async callProvisioningAgent(message) {
    const client = new A2AClient(this.provisioningUrl);
    return await client.sendMessage(message);
  }
  
  // Wrapper methods matching MCP tool names
  async generateArchitectureOverview(prompt) {
    return await this.callOnboardingAgent(
      `Generate architecture overview for: ${prompt}`
    );
  }
  
  async buildCfnTemplate(prompt) {
    return await this.callOnboardingAgent(
      `Generate CloudFormation template for: ${prompt}`
    );
  }
  
  async validateCfnTemplate(template) {
    return await this.callOnboardingAgent(
      `Validate this template: ${template}`
    );
  }
  
  async wellArchitectedReview(prompt) {
    return await this.callOnboardingAgent(
      `Perform Well-Architected review for: ${prompt}`
    );
  }
  
  async analyzeCostOptimization(prompt) {
    return await this.callOnboardingAgent(
      `Analyze cost optimization for: ${prompt}`
    );
  }
  
  async provisionCfnStack(stackName, template) {
    return await this.callProvisioningAgent(
      `Deploy stack ${stackName} with template: ${template}`
    );
  }
}

module.exports = AgentProxy;
```

### Step 2: Update Backend Router

```javascript
// backend/server.js

const AgentProxy = require('./agent_proxy');
const McpProxy = require('./mcp_proxy');  // Existing

// Configuration
const USE_AGENTS = process.env.USE_AGENTS === 'true';

const agentProxy = new AgentProxy({
  onboarding: process.env.ONBOARDING_AGENT_URL,
  provisioning: process.env.PROVISIONING_AGENT_URL
});

const mcpProxy = new McpProxy(process.env.MCP_SERVER_ARN);

// Unified endpoint
app.post('/api/generate', async (req, res) => {
  const { operation, args } = req.body;
  
  try {
    let result;
    
    if (USE_AGENTS) {
      // Route to appropriate agent
      switch (operation) {
        case 'architecture_overview':
        case 'build_template':
        case 'validate_template':
        case 'well_architected_review':
        case 'cost_optimization':
          result = await agentProxy[operation](args);
          break;
        case 'provision_stack':
          result = await agentProxy.provisionCfnStack(args.stackName, args.template);
          break;
      }
    } else {
      // Use MCP server
      result = await mcpProxy.callTool(operation, args);
    }
    
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Step 3: Update Frontend (Minimal Changes)

```javascript
// frontend/index.html

// Replace callMcpToolWs with unified API call
async function callBackend(operation, args) {
  const response = await fetch('http://localhost:3001/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ operation, args })
  });
  
  return await response.json();
}

// Update existing functions to use new API
async function generateInfrastructure() {
  const prompt = document.getElementById('promptInput').value;
  
  // Architecture overview
  const overview = await callBackend('architecture_overview', { prompt });
  displayArchitecture(overview);
  
  // Template
  const template = await callBackend('build_template', { prompt });
  displayTemplate(template);
  
  // Review
  const review = await callBackend('well_architected_review', { prompt });
  displayReview(review);
  
  // Cost
  const cost = await callBackend('cost_optimization', { prompt });
  displayCost(cost);
}
```

## UI Enhancements for Agents

### Add Conversational Mode

```html
<div class="conversation-mode" style="display: none;">
  <div id="chatHistory"></div>
  <div class="chat-input">
    <input type="text" placeholder="Ask follow-up questions..." />
    <button>Send</button>
  </div>
</div>
```

### Enable Provisioning Agent

```javascript
// Enable provisioning menu item when template is ready
function enableProvisioning() {
  const provisioningMenu = document.getElementById('provisioningMenu');
  provisioningMenu.classList.remove('disabled');
  provisioningMenu.onclick = () => switchToProvisioning();
}

function switchToProvisioning() {
  // Switch to provisioning agent view
  // Show deployment options
  // Enable deploy button
}
```

## Backward Compatibility

### Keep MCP Server Running

- UI can toggle between MCP and Agents
- MCP server remains available for quick operations
- Gradual migration path

### Feature Parity

Ensure agents provide same features as MCP:
- ✅ Architecture overview
- ✅ CloudFormation template generation
- ✅ Template validation
- ✅ Well-Architected review
- ✅ Cost optimization
- ✅ Diagram generation (add to agents if needed)
- ✅ Stack deployment

## Consequences

### Positive
- No breaking changes to existing UI
- Gradual migration path
- Can A/B test MCP vs Agents
- Users can choose mode
- Backward compatible

### Negative
- Need to maintain both backends temporarily
- More complex backend routing
- Duplicate functionality during migration

### Neutral
- Can remove MCP mode after agents proven stable
- Backend abstraction useful for future changes

## Rollout Plan

1. **Week 1**: Deploy backend abstraction layer (both modes)
2. **Week 2**: Test agent mode internally
3. **Week 3**: Enable agent mode for beta users
4. **Week 4**: Make agents default, keep MCP as fallback
5. **Week 5+**: Monitor, then deprecate MCP mode

## Success Criteria

- ✅ UI works with both MCP and Agents
- ✅ No functionality regression
- ✅ Agent mode provides same features
- ✅ Smooth handoff between agents
- ✅ Performance acceptable (< 5s for design)

## References
- Existing UI: `cfn-mcp-server/ui/frontend/index.html`
- Existing backend: `cfn-mcp-server/ui/backend/server.js`
- New agents: `Agentic-Architect/agents/`
- Migration guide: `docs/UI_MIGRATION_GUIDE.md` (to be created)
