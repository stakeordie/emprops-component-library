# Environment Variables & Security

This guide outlines best practices for managing environment variables securely with our Docker containers.

## Environment Variables Overview

Our Docker containers support many environment variables to configure services including:

- AWS credentials for model syncing
- API keys for various services (OpenAI, HuggingFace)
- Port mappings
- Service-specific configurations (LangFlow, etc.)

## Secure Environment Variable Management

### Method 1: Using `.env` Files (Recommended)

1. Copy the template file:
   ```bash
   cp docker/.env.example docker/.env.local
   ```

2. Edit `docker/.env.local` with your actual credentials
3. Ensure `.env.local` is in your `.gitignore` (already configured)
4. Pass the file to Docker:
   ```bash
   docker run --env-file docker/.env.local emprops-hybrid
   ```

### Method 2: Command Line Variables

For one-off runs or CI/CD pipelines:

```bash
docker run \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e OPENAI_API_KEY=your_api_key \
  emprops-hybrid
```

### Method 3: Using Docker Secrets (For Swarm Mode)

For production deployments using Docker Swarm:

```yaml
version: '3.8'
services:
  hybrid:
    image: emprops-hybrid
    secrets:
      - aws_access_key
      - aws_secret_key
      - openai_api_key
    environment:
      - AWS_ACCESS_KEY_ID_FILE=/run/secrets/aws_access_key
      - AWS_SECRET_ACCESS_KEY_FILE=/run/secrets/aws_secret_key
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key

secrets:
  aws_access_key:
    external: true
  aws_secret_key:
    external: true
  openai_api_key:
    external: true
```

## Security Best Practices

1. **Never commit real credentials to version control**
   - Use `.env.example` with placeholder values
   - Add all `.env.local*` files to `.gitignore`

2. **Rotate credentials regularly**
   - Update AWS IAM keys every 90 days
   - Refresh API keys regularly

3. **Use credential validation**
   - The container verifies required credentials on startup
   - Error messages indicate missing or invalid credentials

4. **Limit permission scope**
   - For AWS credentials, use IAM policies with minimal permissions
   - Only allow read access to necessary S3 buckets

5. **Secure SSH keys**
   - Mount SSH keys using Docker volumes instead of environment variables
   - Use SSH key passphrase protection

## Environment Variable Reference

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `AWS_ACCESS_KEY_ID` | AWS authentication | Yes (for S3) | `AKIAXXXXXXXXXXXXXXXX` |
| `AWS_SECRET_ACCESS_KEY` | AWS authentication | Yes (for S3) | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `AWS_DEFAULT_REGION` | AWS region | Yes (for S3) | `us-east-1` |
| `OPENAI_API_KEY` | OpenAI API access | Optional | `sk-xxxxxxxxxxxx` |
| `HF_TOKEN` | HuggingFace API access | Optional | `hf_xxxxxxxxxxxx` |
| `LANGFLOW_*` | LangFlow configuration | Optional | Various values |

## Example Docker Run Command

Here's a complete example using environment variables:

```bash
docker run \
  -p 3188:3188 -p 3130:3130 \
  --gpus all \
  -v /path/to/models:/workspace/shared \
  --env-file docker/.env.local \
  emprops-hybrid
```
