# UI Enhancement Guide: Adding A2A Agents Section

## Overview

Add A2A agents as a new section in the sidebar WITHOUT changing existing MCP functionality.

## Current UI

```
Sidebar:
├── Design Agent (MCP)
└── Deployment Agent (disabled)
```

## Enhanced UI

```
Sidebar:
├── Quick Generate (existing - MCP wrapper with LLM)
│   ├── Design
│   └── Deploy
│
└── A2A Agents (new - true agents)
    ├── Onboarding Agent
    └── Provisioning Agent
```

## Benefits

✅ **Zero Breaking Changes** - Existing MCP functionality untouched  
✅ **Side-by-Side Comparison** - Users can try both  
✅ **Clear Separation** - MCP vs A2A clearly labeled  
✅ **Gradual Adoption** - Users choose when to switch  
✅ **A/B Testing** - Compare MCP vs A2A performance  

## Implementation

### Step 1: Update Sidebar HTML

```html
<div class="sidebar">
    <div class="sidebar-header">
        <h2>Architect AI</h2>
        <p>AI-Powered Infrastructure Design</p>
    </div>
    
    <div class="sidebar-menu">
        <!-- Quick Generate Section (MCP wrapper with LLM) -->
        <div class="menu-section-header">Quick Generate</div>
        <div class="menu-section-note">Fast, one-shot generation</div>
        
        <div class="menu-item active" id="quickDesignMenu" onclick="switchMode('quick-design')">
            <div class="menu-item-title">⚡ Design</div>
            <div class="menu-item-desc">Instant architecture generation</div>
        </div>
        
        <div class="menu-item disabled" id="quickDeployMenu">
            <div class="menu-item-title">🚀 Deploy</div>
            <div class="menu-item-desc">One-click deployment</div>
        </div>
        
        <!-- A2A Agents Section (True agents) -->
        <div class="menu-section-header">A2A Agents</div>
        <div class="menu-section-note">Conversational, collaborative</div>
        
        <div class="menu-item" id="a2aOnboardingMenu" onclick="switchMode('a2a-onboarding')">
            <div class="menu-item-title">🤖 Onboarding Agent</div>
            <div class="menu-item-desc">Conversational design & reviews</div>
        </div>
        
        <div class="menu-item" id="a2aProvisioningMenu" onclick="switchMode('a2a-provisioning')">
            <div class="menu-item-title">🚀 Provisioning Agent</div>
            <div class="menu-item-desc">Intelligent deployment</div>
        </div>
    </div>
</div>
```

### Step 2: Add CSS for Section Headers

```css
.menu-section-header {
    padding: 1rem 1rem 0.5rem 1rem;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: rgba(255, 255, 255, 0.5);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    margin-top: 0.5rem;
}

.menu-section-header:first-child {
    border-top: none;
    margin-top: 0;
}

.menu-item-title {
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
```

### Step 3: Add Mode Switching Logic

```javascript
let currentMode = 'mcp-design';  // mcp-design, mcp-provisioning, a2a-onboarding, a2a-provisioning
let conversationHistory = [];

function switchMode(mode) {
    currentMode = mode;
    
    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const menuMap = {
        'mcp-design': 'mcpDesignMenu',
        'mcp-provisioning': 'mcpProvisioningMenu',
        'a2a-onboarding': 'a2aOnboardingMenu',
        'a2a-provisioning': 'a2aProvisioningMenu'
    };
    
    document.getElementById(menuMap[mode]).classList.add('active');
    
    // Update UI based on mode
    if (mode.startsWith('a2a')) {
        showConversationalUI();
    } else {
        showStandardUI();
    }
    
    // Clear content
    clearAllContent();
    
    // Show mode-specific welcome message
    showWelcomeMessage(mode);
}

function showConversationalUI() {
    // Show chat interface for A2A agents
    document.getElementById('chatInterface').style.display = 'block';
    document.getElementById('standardInterface').style.display = 'none';
}

function showStandardUI() {
    // Show standard interface for MCP
    document.getElementById('chatInterface').style.display = 'none';
    document.getElementById('standardInterface').style.display = 'block';
}
```

### Step 4: Add Conversational Interface for A2A

```html
<!-- Add after existing tab-content divs -->
<div id="chatInterface" style="display: none;">
    <div class="chat-container">
        <div class="chat-header">
            <h3 id="chatAgentName">Onboarding Agent</h3>
            <span class="chat-status">🟢 Connected</span>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <!-- Messages appear here -->
        </div>
        
        <div class="chat-input-area">
            <textarea 
                id="chatInput" 
                placeholder="Ask me anything about AWS architecture..."
                rows="3"
            ></textarea>
            <button class="aws-button aws-button-primary" onclick="sendChatMessage()">
                Send
            </button>
        </div>
    </div>
    
    <!-- Results panel (shows generated content) -->
    <div class="results-panel">
        <div class="tabs">
            <button class="tab active" onclick="switchResultTab('overview')">Overview</button>
            <button class="tab" onclick="switchResultTab('template')">Template</button>
            <button class="tab" onclick="switchResultTab('review')">Review</button>
            <button class="tab" onclick="switchResultTab('cost')">Cost</button>
        </div>
        
        <div id="resultContent" class="result-content">
            <!-- Generated content appears here -->
        </div>
    </div>
</div>
```

### Step 5: Add Chat Functions

```javascript
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage('user', message);
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Call appropriate agent based on current mode
        const agentType = currentMode === 'a2a-onboarding' ? 'onboarding' : 'provisioning';
        
        const response = await fetch('http://localhost:3001/api/agent/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                agent: agentType,
                message: message,
                history: conversationHistory
            })
        });
        
        const result = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add agent response to chat
        addChatMessage('agent', result.response);
        
        // Update conversation history
        conversationHistory.push(
            { role: 'user', content: message },
            { role: 'assistant', content: result.response }
        );
        
        // If agent generated content, show in results panel
        if (result.template) {
            displayTemplate(result.template);
        }
        if (result.overview) {
            displayArchitecture(result.overview);
        }
        
    } catch (error) {
        removeTypingIndicator();
        addChatMessage('error', `Error: ${error.message}`);
    }
}

function addChatMessage(role, content) {
    const chatMessages = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message chat-message-${role}`;
    
    if (role === 'user') {
        messageDiv.innerHTML = `
            <div class="message-avatar">👤</div>
            <div class="message-content">${escapeHtml(content)}</div>
        `;
    } else if (role === 'agent') {
        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content markdown-content">${marked.parse(content)}</div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-content error">${escapeHtml(content)}</div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const indicator = document.createElement('div');
    indicator.id = 'typingIndicator';
    indicator.className = 'chat-message chat-message-agent';
    indicator.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <span class="typing-dots">
                <span>.</span><span>.</span><span>.</span>
            </span>
        </div>
    `;
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}
```

### Step 6: Add Chat Styles

```css
/* Chat Interface */
#chatInterface {
    display: flex;
    height: 100%;
    gap: 1rem;
}

.chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: white;
    border: 1px solid var(--aws-border-gray);
    border-radius: 4px;
}

.chat-header {
    padding: 1rem;
    border-bottom: 1px solid var(--aws-border-gray);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--aws-bg-secondary);
}

.chat-status {
    font-size: 0.85rem;
    color: var(--aws-success-green);
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.chat-message {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
}

.chat-message-user {
    flex-direction: row-reverse;
}

.message-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--aws-smile-orange);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
}

.chat-message-user .message-avatar {
    background: var(--aws-link-blue);
}

.message-content {
    flex: 1;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    background: var(--aws-bg-secondary);
    max-width: 70%;
}

.chat-message-user .message-content {
    background: var(--aws-link-blue);
    color: white;
}

.chat-input-area {
    padding: 1rem;
    border-top: 1px solid var(--aws-border-gray);
    display: flex;
    gap: 1rem;
}

.chat-input-area textarea {
    flex: 1;
    min-height: 60px;
}

.results-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: white;
    border: 1px solid var(--aws-border-gray);
    border-radius: 4px;
}

.result-content {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
}

.typing-dots span {
    animation: typing 1.4s infinite;
    opacity: 0;
}

.typing-dots span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% { opacity: 0; }
    30% { opacity: 1; }
}
```

### Step 7: Backend Agent Chat Endpoint

```javascript
// backend/server.js

const AgentProxy = require('./agent_proxy');

const agentProxy = new AgentProxy({
  onboardingUrl: process.env.ONBOARDING_AGENT_URL,
  provisioningUrl: process.env.PROVISIONING_AGENT_URL
});

// New: Agent chat endpoint
app.post('/api/agent/chat', async (req, res) => {
  const { agent, message, history } = req.body;
  
  try {
    let response;
    
    if (agent === 'onboarding') {
      response = await agentProxy.callOnboardingAgent(message, history);
    } else if (agent === 'provisioning') {
      response = await agentProxy.callProvisioningAgent(message, history);
    } else {
      throw new Error(`Unknown agent: ${agent}`);
    }
    
    // Parse response to extract structured data
    const parsed = parseAgentResponse(response);
    
    res.json({
      success: true,
      response: parsed.text,
      template: parsed.template,
      overview: parsed.overview,
      review: parsed.review,
      cost: parsed.cost
    });
    
  } catch (error) {
    console.error('Agent chat error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

function parseAgentResponse(response) {
  // Extract structured data from agent response
  const result = {
    text: response,
    template: null,
    overview: null,
    review: null,
    cost: null
  };
  
  // Look for YAML template blocks
  const yamlMatch = response.match(/```yaml\n([\s\S]+?)\n```/);
  if (yamlMatch) {
    result.template = yamlMatch[1];
  }
  
  // Look for specific sections
  if (response.includes('## Architecture Overview')) {
    result.overview = response;
  }
  
  if (response.includes('## Well-Architected Review')) {
    result.review = response;
  }
  
  if (response.includes('## Cost Analysis')) {
    result.cost = response;
  }
  
  return result;
}

// Keep existing MCP endpoint
app.post('/api/mcp', async (req, res) => {
  // Existing MCP logic unchanged
});
```

## UI Layout

### Split View for A2A Agents

```
┌─────────────────────────────────────────────────────────┐
│  Header: AWS Architect AI                               │
├──────────────┬──────────────────────────────────────────┤
│              │  Chat with Agent                         │
│  Sidebar     │  ┌────────────────────────────────────┐  │
│              │  │ 🤖 Agent: Thinking...              │  │
│  MCP Tools   │  │ 👤 User: Design a web app         │  │
│  - Design    │  │ 🤖 Agent: I'll help with that...  │  │
│  - Deploy    │  └────────────────────────────────────┘  │
│              │  [Type message...]              [Send]   │
│  A2A Agents  ├──────────────────────────────────────────┤
│  - Onboarding│  Results Panel                           │
│  - Provision │  [Overview] [Template] [Review] [Cost]   │
│              │  ┌────────────────────────────────────┐  │
│              │  │ Generated content appears here     │  │
│              │  └────────────────────────────────────┘  │
└──────────────┴──────────────────────────────────────────┘
```

## User Experience

### Quick Generate Mode (Existing - MCP Wrapper)

**What it is:** MCP server with LLM-powered tools (fast but opaque)

1. User enters requirements
2. Clicks "Generate"
3. All tabs populate instantly
4. No conversation
5. ⚠️ Decision-making hidden in tools

**Best for:** Quick prototypes, simple architectures

### A2A Agent Mode (New - True Agents)

**What it is:** Strands agents with transparent reasoning

1. User selects "Onboarding Agent"
2. Chat interface appears
3. User: "I need a web application"
4. Agent: "Let me ask a few questions..." (reasoning visible)
5. Conversational back-and-forth
6. Agent generates template (you see the thinking)
7. Results appear in right panel
8. User can switch to "Provisioning Agent" to deploy
9. ✅ All decision-making visible

**Best for:** Complex requirements, production architectures

## Feature Comparison

| Feature | Quick Generate (MCP Wrapper) | A2A Agents |
|---------|------------------------------|------------|
| Architecture | MCP wrapper with LLM inside | True agents with LLM |
| Speed | ⚡ Fast (single call) | 🐢 Slower (conversational) |
| Interaction | One-shot | Multi-turn conversation |
| Customization | Limited | High (ask questions) |
| Context | None | Maintains history |
| Handoff | Manual | Automatic (A2A) |
| Decision Making | Hidden in tools | Visible in agent |
| Best For | Quick prototypes | Production architectures |
| Transparency | Low (LLM in tools) | High (agent reasoning visible) |

## Implementation Checklist

- [ ] Add sidebar section headers
- [ ] Add A2A agent menu items
- [ ] Create chat interface HTML
- [ ] Add chat CSS styles
- [ ] Implement mode switching
- [ ] Add agent chat endpoint to backend
- [ ] Implement A2A client in backend
- [ ] Add conversation history management
- [ ] Parse agent responses for structured data
- [ ] Test both modes work independently
- [ ] Add mode indicator in UI
- [ ] Document for users

## Backend Environment Variables

```bash
# Existing (keep)
MCP_SERVER_ARN=arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/mcp_server-xyz

# New (add)
ONBOARDING_AGENT_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3A.../invocations/
PROVISIONING_AGENT_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3A.../invocations/
```

## Deployment

1. **Deploy A2A agents** (already done ✅)
2. **Update backend** with agent proxy
3. **Update frontend** with new sidebar section
4. **Test both modes** work independently
5. **Deploy to production**
6. **Monitor usage** (MCP vs A2A)

## Success Metrics

- ✅ Both MCP and A2A modes work
- ✅ No regression in MCP functionality
- ✅ A2A agents provide conversational experience
- ✅ Users can switch between modes seamlessly
- ✅ Performance acceptable for both modes

## Future Enhancements

1. **Usage Analytics**: Track which mode users prefer
2. **Smart Routing**: Suggest A2A for complex requirements
3. **Hybrid Mode**: Use MCP for speed, A2A for complexity
4. **Agent Collaboration**: Show A2A handoff in UI
5. **Deployment Monitoring**: Real-time CloudFormation events in chat

## References
- Current UI: `cfn-mcp-server/ui/frontend/index.html`
- Backend: `cfn-mcp-server/ui/backend/server.js`
- A2A Agents: `Agentic-Architect/agents/`
- ADR 005: UI Migration Strategy
