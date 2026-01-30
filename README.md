# Agentic-Architect

AI-powered AWS architecture design and deployment using Amazon Bedrock AgentCore Runtime with Strands A2A protocol.

## Overview

Two specialized AI agents that collaborate to design and deploy AWS infrastructure:

- **Onboarding Agent**: Conversational architecture design, CloudFormation generation, Well-Architected reviews
- **Provisioning Agent**: CloudFormation deployment, monitoring, and reporting

## Architecture

```
User Interface
     ↓
┌────────────────────┐      ┌─────────────────────┐
│ Onboarding Agent   │─────▶│ Provisioning Agent  │
│ (Design & Review)  │ A2A  │ (Deploy & Monitor)  │
└────────────────────┘      └─────────────────────┘
         │                           │
         └───────────┬───────────────┘
                     │
              Simple Tools
           (AWS API calls only)
```

### Key Principles

✅ **Agents make decisions** - LLMs handle all reasoning  
✅ **Tools execute actions** - Deterministic AWS API calls only  
✅ **A2A collaboration** - Agents communicate via standard protocol  
✅ **No anti-patterns** - No LLMs hidden inside tools  

## Features

### Onboarding Agent
- Conversational requirements gathering
- AWS architecture design with reasoning
- CloudFormation template generation
- Well-Architected Framework reviews
- Cost optimization analysis
- Template validation
- Handoff to Provisioning Agent via A2A

### Provisioning Agent
- CloudFormation stack deployment
- Deployment progress monitoring
- Error handling and troubleshooting
- Stack output reporting
- Request design help from Onboarding Agent via A2A

### Enhanced UI
- **Quick Generate**: Fast MCP wrapper for prototypes
- **A2A Agents**: Conversational interface for production
- Side-by-side comparison
- No breaking changes to existing functionality

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- AWS credentials configured
- Amazon Bedrock access

### Installation

```bash
# Clone repository
git clone <repo-url>
cd Agentic-Architect

# Install Python dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your agent ARNs

# Install UI backend
cd ui/backend
npm install
cp .env.example .env
# Edit .env with agent URLs
```

### Deployment

```bash
# Deploy agents to AgentCore Runtime
bash scripts/deploy_strands_agents.sh

# Start UI backend
cd ui/backend
npm start

# Open UI
open ui/frontend/index.html
```

## Project Structure

```
Agentic-Architect/
├── agents/              # Strands A2A agent implementations
├── adr/                 # Architecture Decision Records
├── config/              # Agent configurations (YAML)
├── docs/                # Documentation
├── scripts/             # Deployment and utility scripts
├── tests/               # Test files
├── ui/                  # Enhanced web UI
│   ├── backend/         # Node.js proxy server
│   └── frontend/        # HTML/JS interface
├── requirements.txt
├── .env.example
└── README.md
```

## Documentation

- **[ADRs](adr/README.md)** - Architecture decisions
- **[Deployment Info](docs/DEPLOYMENT_INFO.md)** - Agent ARNs and URLs
- **[Environment Setup](docs/ENVIRONMENT_SETUP.md)** - Configuration guide
- **[A2A Documentation](docs/README_A2A.md)** - Agent collaboration
- **[UI Enhancement Guide](docs/UI_ENHANCEMENT_GUIDE.md)** - UI implementation

## Deployed Agents

### Onboarding Agent
```
ARN: arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/onboarding_agent-j6Y9CIGVDj
```

### Provisioning Agent
```
ARN: arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/provisioning_agent-lZECd14iTW
```

## Usage

### CLI

```bash
# Invoke Onboarding Agent
agentcore invoke --input "Design a 3-tier web application"

# Invoke Provisioning Agent
agentcore invoke --input "Deploy this CloudFormation template: ..."
```

### UI

1. Open `ui/frontend/index.html`
2. Choose mode:
   - **Quick Generate**: Fast, one-shot generation
   - **A2A Agents**: Conversational, collaborative
3. Enter requirements or chat with agents
4. Review generated architecture
5. Deploy to AWS

## Testing

```bash
# Validate environment
bash scripts/validate_env.sh

# Test agent URLs
bash scripts/test_agent_urls.sh

# Test A2A communication
python3 tests/test_a2a.py

# Run all tests
pytest tests/
```

## Monitoring

### CloudWatch Logs

```bash
# Onboarding Agent
aws logs tail /aws/bedrock-agentcore/runtimes/onboarding_agent-j6Y9CIGVDj-DEFAULT \
  --log-stream-name-prefix "2026/01/30/[runtime-logs" --follow

# Provisioning Agent
aws logs tail /aws/bedrock-agentcore/runtimes/provisioning_agent-lZECd14iTW-DEFAULT \
  --log-stream-name-prefix "2026/01/30/[runtime-logs" --follow
```

### GenAI Observability Dashboard

https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#gen-ai-observability/agent-core

## Architecture Decisions

See [adr/README.md](adr/README.md) for all Architecture Decision Records:

1. **Agent vs MCP Server** - Why agents with simple tools
2. **Strands A2A** - Why A2A protocol for collaboration
3. **Deterministic Tools** - Why no LLMs in tools
4. **AgentCore Runtime** - Why this deployment platform
5. **UI Enhancement** - Why separate sidebar sections

## Contributing

1. Create feature branch
2. Make changes
3. Add tests
4. Update ADRs if architectural decisions made
5. Submit pull request

## License

[Your License]

## Contact

[Your Contact Info]
# Trigger rebuild
