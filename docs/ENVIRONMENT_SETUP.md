# Environment Setup Guide

## Quick Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` with your deployment values:**
   - Get agent ARNs from `docs/DEPLOYMENT_INFO.md`
   - Update agent URLs with your deployed agent ARNs
   - Set AWS region

3. **Load environment variables:**
   ```bash
   source .env  # or use direnv, dotenv, etc.
   ```

## Required Environment Variables

### AWS Configuration

```bash
AWS_REGION=us-east-1
```

**Purpose:** AWS region for CloudFormation operations  
**Default:** us-east-1  
**Required:** Yes

### Agent Runtime URLs (for A2A)

```bash
ONBOARDING_AGENT_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3A.../invocations/
PROVISIONING_AGENT_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3A.../invocations/
```

**Purpose:** URLs for A2A agent-to-agent communication  
**Required:** Yes (for A2A collaboration)  
**How to get:** See `docs/DEPLOYMENT_INFO.md` after deployment

**URL Format:**
```
https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations/
```

**Encoding ARN:**
- Replace `:` with `%3A`
- Replace `/` with `%2F`

Example:
```
ARN: arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/agent-xyz
Encoded: arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A123456789012%3Aruntime%2Fagent-xyz
```

### AgentCore Runtime URL

```bash
# AGENTCORE_RUNTIME_URL - DO NOT SET MANUALLY
```

**Purpose:** Base URL for the agent's A2A server  
**Default:** Set automatically by AgentCore Runtime during deployment  
**Required:** No - AgentCore sets this automatically  
**Note:** Only set this for local development (http://0.0.0.0:9000/)

⚠️ **Important:** When deployed to AgentCore Runtime, this variable is automatically set by the platform. Do not override it in production.

## Optional Environment Variables

### AWS Credentials

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

**Purpose:** AWS credentials for API calls  
**Required:** Only if not using IAM role  
**Note:** AgentCore Runtime uses execution role by default

### Bedrock API Key

```bash
AWS_BEDROCK_API_KEY=your_bedrock_api_key
```

**Purpose:** Bedrock API key for development/testing  
**Required:** No (agents use IAM role in production)  
**Note:** Only for local testing with Bedrock

## Environment Variable Loading

### Option 1: Manual Export

```bash
export AWS_REGION=us-east-1
export ONBOARDING_AGENT_URL="https://..."
export PROVISIONING_AGENT_URL="https://..."
```

### Option 2: Source .env File

```bash
# Load all variables
set -a
source .env
set +a
```

### Option 3: Use direnv

```bash
# Install direnv
brew install direnv  # macOS

# Create .envrc
echo "dotenv" > .envrc

# Allow direnv
direnv allow
```

### Option 4: Python dotenv

```python
from dotenv import load_dotenv
load_dotenv()

# Now os.environ.get() will work
```

## Deployment-Specific Setup

### After Deploying Agents

1. Get agent ARNs from deployment output
2. Construct runtime URLs (see format above)
3. Update `.env` file
4. Reload environment variables

### Script to Generate URLs

```bash
# scripts/generate_env.sh
ONBOARDING_ARN="arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/onboarding_agent-j6Y9CIGVDj"
PROVISIONING_ARN="arn:aws:bedrock-agentcore:us-east-1:905767016260:runtime/provisioning_agent-lZECd14iTW"

# URL encode
ONBOARDING_ENCODED=$(echo "$ONBOARDING_ARN" | sed 's/:/%3A/g' | sed 's/\//%2F/g')
PROVISIONING_ENCODED=$(echo "$PROVISIONING_ARN" | sed 's/:/%3A/g' | sed 's/\//%2F/g')

echo "ONBOARDING_AGENT_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/${ONBOARDING_ENCODED}/invocations/"
echo "PROVISIONING_AGENT_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/${PROVISIONING_ENCODED}/invocations/"
```

## Verification

Check if environment variables are set:

```bash
echo "AWS Region: $AWS_REGION"
echo "Onboarding URL: $ONBOARDING_AGENT_URL"
echo "Provisioning URL: $PROVISIONING_AGENT_URL"
```

## Troubleshooting

### Issue: "PROVISIONING_AGENT_URL not configured"

**Cause:** Environment variable not set  
**Solution:** 
1. Check `.env` file exists
2. Verify variable is set: `echo $PROVISIONING_AGENT_URL`
3. Source the file: `source .env`

### Issue: "Agent not found" or 404 errors

**Cause:** Incorrect agent URL  
**Solution:**
1. Verify ARN is correct
2. Check URL encoding (: → %3A, / → %2F)
3. Ensure `/invocations/` suffix is present

### Issue: "Access denied"

**Cause:** Missing AWS credentials or IAM permissions  
**Solution:**
1. Check AWS credentials: `aws sts get-caller-identity`
2. Verify IAM role has bedrock-agentcore permissions
3. Check execution role in AgentCore

## Security Notes

- ⚠️ Never commit `.env` file to git
- ⚠️ Use IAM roles in production (not API keys)
- ⚠️ Rotate API keys regularly
- ⚠️ Use AWS Secrets Manager for sensitive values in production

## References
- Deployment info: `docs/DEPLOYMENT_INFO.md`
- Agent code: `agents/onboarding_agent.py`, `agents/provisioning_agent.py`
