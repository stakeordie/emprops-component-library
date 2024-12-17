#!/usr/bin/env python3
import json
import os
import hashlib
import shutil
from typing import Dict, List

def read_json_config(config_path: str) -> Dict:
    with open(config_path, 'r') as f:
        return json.load(f)

def generate_download_stage(model: Dict, index: int) -> str:
    stage_name = f"download_{index}"
    path = model['path']
    name = model.get('name', f'model_{index}')
    
    # If path ends with /, append the name to create full path
    if path.endswith('/'):
        path_dir = path.rstrip('/')
        full_path = os.path.join(path_dir, name)
    else:
        full_path = path
        path_dir = os.path.dirname(path)
    
    # Prepend ComfyUI to the path
    comfy_path = os.path.join("ComfyUI", full_path)
    comfy_dir = os.path.dirname(comfy_path)
    
    return f"""RUN echo "Downloading {name}..."
RUN mkdir -p ${{ROOT}}/{comfy_dir}
RUN wget -O "${{ROOT}}/{comfy_path}" "{model['url']}"
""", comfy_path

def generate_node_stage(node: Dict, index: int) -> str:
    """Generate a Dockerfile stage for installing a node."""
    name = node.get('name', f'node_{index}')
    url = node.get('url', '')
    commit = node.get('commit', None)
    
    # Extract repo name from URL
    repo_name = url.split('/')[-1].replace('.git', '')
    
    # Build the clone commands only
    commands = [f"""FROM middle-comfy-install AS node_{index}
RUN echo "Installing node: {name}..."
RUN mkdir -p ${{ROOT}}/ComfyUI/custom_nodes && \\
    cd ${{ROOT}}/ComfyUI/custom_nodes && \\
    git clone {url}"""]
    
    if commit:
        commands.append(f'RUN cd ${{ROOT}}/ComfyUI/custom_nodes/{repo_name} && git checkout {commit}')
    
    return "\n".join(commands), repo_name

def generate_dockerfile_content(models_config: str, nodes_config: str = None) -> str:
    # First, generate the startup script
    script_content = ["#!/bin/bash", ""]
    
    # Add model download function
    script_content.extend([
        "check_and_download_models() {",
        '    echo "Checking and downloading models if needed..."',
        ""
    ])
    
    # Add model download commands
    if models_config:
        models = read_json_config(models_config).get('models', [])
        for model in models:
            url = model.get('url', '')
            path = model.get('path', '')
            name = model.get('name', '')
            
            full_path = os.path.join("${ROOT}/ComfyUI", path)
            script_content.extend([
                f'    if [ ! -f "{full_path}/{name}" ]; then',
                f'        echo "Downloading {name}..."',
                f'        mkdir -p "{full_path}"',
                f'        wget -q --header="Authorization: Bearer $HF_TOKEN" "{url}" -O "{full_path}/{name}"',
                '    fi',
                ''
            ])
    
    # Add node installation function
    script_content.extend([
        "}",
        "",
        "install_nodes() {",
        '    cd ${ROOT}/ComfyUI/custom_nodes',
        ""
    ])
    
    # Add node installation commands
    if nodes_config:
        nodes = read_json_config(nodes_config).get('nodes', [])
        for node in nodes:
            url = node.get('url', '')
            name = node.get('name', '')
            commit = node.get('commit', None)
            repo_name = url.split('/')[-1].replace('.git', '')
            
            script_content.extend([
                f'    if [ ! -d "{repo_name}" ]; then',
                f'        echo "Installing node: {name}"',
                f'        git clone {url}',
            ])
            
            if commit:
                script_content.append(f'        cd {repo_name} && git checkout {commit} && cd ..')
            
            script_content.extend([
                f'        if [ -f "{repo_name}/requirements.txt" ]; then',
                f'            pip install -r "{repo_name}/requirements.txt"',
                '        fi',
                '    fi',
                ''
            ])
    
    # Add script execution
    script_content.extend([
        "}",
        "",
        "# Run setup functions",
        "check_and_download_models",
        "install_nodes",
        "",
        "# Start ComfyUI",
        "cd ${ROOT}/ComfyUI",
        "python main.py"
    ])
    
    # Write the startup script to a file
    script_path = os.path.join(os.path.dirname(os.path.dirname(models_config)), "scripts")
    os.makedirs(script_path, exist_ok=True)
    with open(os.path.join(script_path, "start.sh"), "w") as f:
        f.write("\n".join(script_content))
    
    # Generate the Dockerfile content
    content = []
    content.append("# [GENERATED_CONTENT]\n")
    
    # Setup environment variables
    content.append("# Setup environment variables")
    content.append('ARG HF_TOKEN')
    content.append('ARG OPENAI_API_KEY')
    content.append('ENV HF_TOKEN=$HF_TOKEN')
    content.append('ENV OPENAI_API_KEY=$OPENAI_API_KEY')
    content.append('ENV ROOT=/home/ubuntu')
    content.append('ENV PATH="${ROOT}/.local/bin:${PATH}"\n')
    
    # Create directories for volumes
    content.append("# Create directories for volumes")
    content.append("""RUN mkdir -p ${ROOT}/ComfyUI/models && \\
    mkdir -p ${ROOT}/ComfyUI/custom_nodes && \\
    chown -R ubuntu:ubuntu ${ROOT}/ComfyUI""")
    
    # Copy and setup the startup script
    content.extend([
        "",
        "# Copy startup script",
        "COPY scripts/start.sh /start.sh",
        "RUN chmod +x /start.sh",
        "",
        "# Set working directory",
        "WORKDIR ${ROOT}/ComfyUI",
        "",
        "# Start the application",
        'CMD ["/start.sh"]',
        "",
        "# [END_GENERATED_CONTENT]"
    ])
    
    return "\n".join(content)

def merge_with_dockerfile(dockerfile_path: str, generated_content: str, marker: str = "# [GENERATED_CONTENT]") -> None:
    # Create a new Dockerfile in the current directory
    current_dir = os.getcwd()
    new_dockerfile = os.path.join(current_dir, "Dockerfile")
    
    # Copy the original Dockerfile
    shutil.copy2(dockerfile_path, new_dockerfile)
    
    # Read the contents of the new Dockerfile
    with open(new_dockerfile, 'r') as f:
        content = f.read()
    
    # Split content at marker and reconstruct
    if marker in content:
        parts = content.split(marker)
        if len(parts) >= 2:
            # Construct new content with marker, generated content, and final stages
            new_content = parts[0] + marker + "\n" + generated_content.split(marker)[1].split("# [END_GENERATED_CONTENT]")[0] + "\n\n" + "# [END_GENERATED_CONTENT]" + "\n\n" + parts[1].split("# [END_GENERATED_CONTENT]")[1]
            
            # Write back to the new Dockerfile
            with open(new_dockerfile, 'w') as f:
                f.write(new_content)
            
            print(f"Generated new Dockerfile at: {new_dockerfile}")
        else:
            print(f"Error: Marker found but content format unexpected")
    else:
        print(f"Error: Marker '{marker}' not found in Dockerfile")

if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) < 3:
        print("Usage: generate_dockerfile.py <dockerfile_path> <models_config_path> [nodes_config_path]")
        sys.exit(1)
    
    dockerfile_path = sys.argv[1]
    models_config_path = sys.argv[2]
    nodes_config_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(dockerfile_path):
        print(f"Dockerfile not found: {dockerfile_path}")
        sys.exit(1)
    
    if not os.path.exists(models_config_path):
        print(f"Models config not found: {models_config_path}")
        sys.exit(1)
    
    if nodes_config_path and not os.path.exists(nodes_config_path):
        print(f"Nodes config not found: {nodes_config_path}")
        sys.exit(1)
    
    content = generate_dockerfile_content(models_config_path, nodes_config_path)
    merge_with_dockerfile(dockerfile_path, content)