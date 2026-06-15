#!/usr/bin/env python3
"""
Foundry Agent Deployment Script

This script guides you through deploying the Retail AI Agents to Azure AI Foundry.
It will help you:
1. Set up a Foundry project (if needed)
2. Deploy model endpoints
3. Build and deploy agent containers
4. Get agent invocation endpoints
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich import print as rprint
except ImportError:
    print("Installing rich for better output...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich import print as rprint

console = Console()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_azure_login() -> Tuple[bool, Optional[Dict]]:
    """Check if user is logged into Azure CLI."""
    try:
        result = subprocess.run(
            ["az", "account", "show", "--query", "{subscription:id,tenant:tenantId}", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        account = json.loads(result.stdout)
        return True, account
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, None


def check_foundry_extension() -> bool:
    """Check if Azure ML extension is installed."""
    try:
        result = subprocess.run(
            ["az", "extension", "list", "--query", "[?name=='ml'].name", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        extensions = json.loads(result.stdout)
        return "ml" in extensions
    except:
        return False


def list_foundry_projects(subscription_id: str) -> list:
    """List available Foundry (AI Services) projects."""
    try:
        result = subprocess.run(
            ["az", "cognitiveservices", "account", "list", 
             "--subscription", subscription_id,
             "--query", "[?kind=='AIServices' || kind=='OpenAI'].{name:name,resourceGroup:resourceGroup,location:location,endpoint:properties.endpoint}",
             "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except:
        return []


def create_env_file(config: Dict) -> None:
    """Create or update .env file with Foundry configuration."""
    env_path = Path(__file__).parent.parent / ".env"
    
    env_content = f"""# Azure AI Foundry Configuration
FOUNDRY_PROJECT_ENDPOINT={config['endpoint']}
FOUNDRY_SUBSCRIPTION_ID={config['subscription_id']}
FOUNDRY_RESOURCE_GROUP={config['resource_group']}
FOUNDRY_PROJECT_NAME={config['project_name']}

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT={config['endpoint']}
AZURE_OPENAI_API_KEY={config.get('api_key', 'use-managed-identity')}
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Model Configuration
MODEL_NAME={config.get('model_name', 'gpt-4o')}
MODEL_DEPLOYMENT_NAME={config.get('deployment_name', 'gpt-4o')}

# OPA Configuration
OPA_URL=http://localhost:8181
OPA_POLICY_PATH=/v1/data

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=production

# Mock Data Configuration (set to false for production)
USE_MOCK_DATA=false
MOCK_DATA_PATH=./data/mock

# Agent Configuration
ENABLE_TELEMETRY=true
ENABLE_POLICY_AUDIT=true
POLICY_AUDIT_LOG_PATH=./logs/policy-audit.jsonl
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    console.print(f"[green]✓ Created .env file at {env_path}[/green]")


def get_api_key(resource_group: str, account_name: str, subscription_id: str) -> Optional[str]:
    """Get API key for the Foundry account."""
    try:
        result = subprocess.run(
            ["az", "cognitiveservices", "account", "keys", "list",
             "--name", account_name,
             "--resource-group", resource_group,
             "--subscription", subscription_id,
             "--query", "key1",
             "-o", "tsv"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return None


def main():
    """Main deployment workflow."""
    console.print(Panel.fit(
        "[bold cyan]Azure AI Foundry Deployment[/bold cyan]\n"
        "[white]Retail AI Agent Policy Workshop[/white]",
        border_style="cyan"
    ))
    
    # Step 1: Check Azure login
    console.print("\n[bold cyan]Step 1: Checking Azure Authentication[/bold cyan]")
    is_logged_in, account = check_azure_login()
    
    if not is_logged_in:
        console.print("[red]✗ Not logged into Azure CLI[/red]")
        console.print("[yellow]Please run: az login[/yellow]")
        sys.exit(1)
    
    console.print(f"[green]✓ Logged into Azure[/green]")
    console.print(f"  Subscription: {account['subscription']}")
    console.print(f"  Tenant: {account['tenant']}")
    
    # Step 2: Check for existing Foundry projects
    console.print("\n[bold cyan]Step 2: Finding Foundry Projects[/bold cyan]")
    projects = list_foundry_projects(account['subscription'])
    
    if projects:
        console.print(f"[green]✓ Found {len(projects)} AI Services project(s)[/green]\n")
        
        table = Table(title="Available Projects")
        table.add_column("#", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Resource Group", style="yellow")
        table.add_column("Location", style="magenta")
        
        for idx, project in enumerate(projects, 1):
            table.add_row(
                str(idx),
                project['name'],
                project['resourceGroup'],
                project['location']
            )
        
        console.print(table)
        
        # Let user select a project
        selection = Prompt.ask(
            "\nSelect project number (or 'n' for new)",
            default="1"
        )
        
        if selection.lower() == 'n':
            console.print("[yellow]Please create an AI Services resource in Azure Portal first.[/yellow]")
            console.print("[cyan]https://portal.azure.com -> Create Resource -> Azure AI Services[/cyan]")
            sys.exit(0)
        
        try:
            selected_project = projects[int(selection) - 1]
        except (ValueError, IndexError):
            console.print("[red]Invalid selection[/red]")
            sys.exit(1)
        
        # Get API key
        console.print(f"\n[cyan]Getting API key for {selected_project['name']}...[/cyan]")
        api_key = get_api_key(
            selected_project['resourceGroup'],
            selected_project['name'],
            account['subscription']
        )
        
        if not api_key:
            console.print("[yellow]⚠ Could not retrieve API key, will use managed identity[/yellow]")
        
        # Create configuration
        config = {
            'subscription_id': account['subscription'],
            'resource_group': selected_project['resourceGroup'],
            'project_name': selected_project['name'],
            'endpoint': selected_project['endpoint'],
            'api_key': api_key or 'use-managed-identity',
            'model_name': 'gpt-4o',
            'deployment_name': 'gpt-4o'
        }
        
    else:
        console.print("[yellow]⚠ No Foundry projects found[/yellow]\n")
        console.print("You have two options:\n")
        console.print("1. [cyan]Test locally[/cyan] - Run agents with mock data (no Foundry needed)")
        console.print("2. [cyan]Create project[/cyan] - Set up Azure AI Services in Azure Portal\n")
        
        choice = Prompt.ask("Choose option", choices=["1", "2"], default="1")
        
        if choice == "1":
            # Local testing mode
            console.print("\n[bold green]Setting up for local testing[/bold green]")
            config = {
                'subscription_id': account['subscription'],
                'resource_group': 'local-testing',
                'project_name': 'local-agents',
                'endpoint': 'http://localhost:8000',
                'api_key': 'mock-key-for-local-testing',
                'model_name': 'gpt-4o',
                'deployment_name': 'mock'
            }
            
            # Update .env for local mode
            env_path = Path(__file__).parent.parent / ".env"
            with open(env_path, 'w') as f:
                f.write(f"""# Local Testing Configuration
FOUNDRY_PROJECT_ENDPOINT=http://localhost:8000
FOUNDRY_SUBSCRIPTION_ID={account['subscription']}
FOUNDRY_RESOURCE_GROUP=local-testing
FOUNDRY_PROJECT_NAME=local-agents

# Azure OpenAI Configuration (mock for local)
AZURE_OPENAI_ENDPOINT=http://localhost:8000
AZURE_OPENAI_API_KEY=mock-key-for-local-testing
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Model Configuration
MODEL_NAME=gpt-4o
MODEL_DEPLOYMENT_NAME=mock

# OPA Configuration
OPA_URL=http://localhost:8181
OPA_POLICY_PATH=/v1/data

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development

# Mock Data Configuration
USE_MOCK_DATA=true
MOCK_DATA_PATH=./data/mock

# Agent Configuration
ENABLE_TELEMETRY=true
ENABLE_POLICY_AUDIT=true
POLICY_AUDIT_LOG_PATH=./logs/policy-audit.jsonl
""")
            
            console.print("\n[bold green]✓ Local testing mode configured![/bold green]\n")
            console.print("[cyan]Your agents are running locally. To test:[/cyan]\n")
            console.print("  1. Make sure OPA is running: [yellow]docker-compose up -d[/yellow]")
            console.print("  2. Run a demo: [yellow]python scripts/demo_ai_agent.py[/yellow]")
            console.print("  3. Start agent server: [yellow]python src/agents/agent_server.py[/yellow]\n")
            console.print("[cyan]Agent endpoint:[/cyan] [green]http://localhost:8000[/green]\n")
            console.print("To deploy to Azure Foundry:")
            console.print("  1. Create AI Services in Azure Portal")
            console.print("  2. Run this script again and select your project\n")
            
            return
            
        else:
            console.print("\n[cyan]To create an Azure AI Services resource:[/cyan]")
            console.print("1. Go to https://portal.azure.com")
            console.print("2. Click 'Create a resource'")
            console.print("3. Search for 'Azure AI Services'")
            console.print("4. Fill in the form:")
            console.print("   - Subscription: [yellow]Current subscription[/yellow]")
            console.print("   - Resource Group: [yellow]Create new or use existing[/yellow]")
            console.print("   - Region: [yellow]Choose nearest region[/yellow]")
            console.print("   - Name: [yellow]retail-agent-policy-workshop[/yellow]")
            console.print("   - Pricing tier: [yellow]Standard S0[/yellow]")
            console.print("5. Click 'Review + Create'")
            console.print("\n[cyan]After creation, run this script again![/cyan]\n")
            sys.exit(0)
    
    # Step 3: Create .env file
    console.print("\n[bold cyan]Step 3: Creating Environment Configuration[/bold cyan]")
    create_env_file(config)
    
    # Step 4: Show deployment endpoints
    console.print("\n[bold green]✓ Configuration Complete![/bold green]\n")
    
    console.print(Panel.fit(
        f"[bold cyan]Foundry Agent Endpoints[/bold cyan]\n\n"
        f"[yellow]Project Endpoint:[/yellow]\n"
        f"  {config['endpoint']}\n\n"
        f"[yellow]Subscription:[/yellow] {config['subscription_id']}\n"
        f"[yellow]Resource Group:[/yellow] {config['resource_group']}\n"
        f"[yellow]Project Name:[/yellow] {config['project_name']}\n\n"
        f"[green]To test locally first:[/green]\n"
        f"  1. docker-compose up -d\n"
        f"  2. python scripts/demo_ai_agent.py\n\n"
        f"[green]To deploy to Foundry:[/green]\n"
        f"  See notebooks/06-foundry-deployment.ipynb",
        border_style="green"
    ))
    
    # Step 5: Offer to test locally
    if Confirm.ask("\nWould you like to test agents locally now?", default=True):
        console.print("\n[cyan]Starting local agent server...[/cyan]")
        console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")
        
        try:
            # Start OPA if not running
            subprocess.run(["docker-compose", "up", "-d"], cwd=Path(__file__).parent.parent, check=False)
            
            # Run demo
            subprocess.run([sys.executable, "scripts/demo_ai_agent.py"], cwd=Path(__file__).parent.parent)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped[/yellow]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)
