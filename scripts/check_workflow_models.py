#!/usr/bin/env python3
import json
import os
from collections import defaultdict
from typing import Dict, Set, List, Any, Tuple

def load_json_file(filepath: str) -> dict:
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {filepath}: {e}")
        return {}

def get_model_from_node(node: Dict[str, Any], inputs_override: Dict[str, Any]) -> Tuple[str, bool]:
    """Extract model name from a node based on its class type and check if it's overridden"""
    class_type = node.get('class_type', '')
    node_inputs = node.get('inputs', {})
    
    # Map class types to their input field names
    model_fields = {
        'CheckpointLoaderSimple': 'ckpt_name',
        'ControlNetLoader': 'control_net_name',
        'CLIPLoader': 'clip_name',
        'UpscaleModelLoader': 'model_name',
        'VAELoader': 'vae_name',
        'IPAdapterModelLoader': 'ipadapter_name'
    }
    
    if class_type not in model_fields:
        return '', False
        
    field_name = model_fields[class_type]
    model = node_inputs.get(field_name, '')
    
    # Check if this input is overridden
    is_overridden = any(field_name in override for override in inputs_override.values())
    
    # Handle case where model is a list
    if isinstance(model, list):
        return str(model), is_overridden
    return str(model) if model else '', is_overridden

def load_form_conf_models(components_dir: str) -> Set[str]:
    """Load all models specified in form configuration files"""
    form_conf_dir = os.path.join(components_dir, '_form_confs')
    model_files = ['sd_models.json', 'upscale-models.json']
    
    allowed_models = set()
    for file in model_files:
        filepath = os.path.join(form_conf_dir, file)
        config = load_json_file(filepath)
        for item in config:
            if isinstance(item, dict):
                if 'value' in item:  # For upscale-models.json format
                    allowed_models.add(item['value'])
                elif file == 'sd_models.json' and 'meta' in item:  # For sd_models.json format
                    allowed_models.add(item.get('value', ''))
    
    return allowed_models

def scan_workflow_for_models(workflow: Dict[str, Any], inputs_override: Dict[str, Any]) -> Tuple[Set[str], Set[str]]:
    """Scan a workflow JSON and extract all model requirements, separating static and dynamic models"""
    static_models = set()
    dynamic_models = set()
    
    for node_id, node in workflow.items():
        if isinstance(node, dict):
            model_name, is_overridden = get_model_from_node(node, inputs_override)
            if model_name:
                if is_overridden:
                    dynamic_models.add(model_name)
                else:
                    static_models.add(model_name)
    
    return static_models, dynamic_models

def get_s3_models(config_dir: str) -> Dict[str, List[str]]:
    """Get mapping of model types to available models in S3"""
    s3_models = defaultdict(list)
    
    config_files = ['basic/config.json', 'flux/config.json']
    for config_file in config_files:
        config_path = os.path.join(config_dir, config_file)
        config = load_json_file(config_path)
        
        for model in config.get('models', []):
            name = model.get('name', '')
            path = model.get('path', '')
            if name and path:
                if isinstance(path, list):
                    path = str(path[0]) if path else ''
                elif not isinstance(path, str):
                    continue
                    
                try:
                    model_type = path.split('/')[-2]
                    s3_models[model_type].append(str(name))
                except (IndexError, AttributeError):
                    print(f"Warning: Invalid path format for model {name}: {path}")
                    continue
    
    return s3_models

def main():
    components_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Components')
    config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docker/config')
    
    # Load models from form configurations
    allowed_models = load_form_conf_models(components_dir)
    
    # Get all workflow and input files
    workflow_files = []
    for root, _, files in os.walk(components_dir):
        if 'workflow.json' in files:
            workflow_path = os.path.join(root, 'workflow.json')
            input_path = os.path.join(root, 'inputs.json')
            workflow_files.append((workflow_path, input_path))
    
    # Collect required models from all workflows
    static_models = set()
    dynamic_models = set()
    workflow_models = {}
    
    for workflow_path, input_path in workflow_files:
        component_name = os.path.basename(os.path.dirname(workflow_path))
        workflow = load_json_file(workflow_path)
        inputs_override = load_json_file(input_path)
        
        static, dynamic = scan_workflow_for_models(workflow, inputs_override)
        if static or dynamic:
            workflow_models[component_name] = {'static': static, 'dynamic': dynamic}
            static_models.update(static)
            dynamic_models.update(dynamic)
    
    # Get available models from S3
    s3_models = get_s3_models(config_dir)
    all_s3_models = set()
    for models in s3_models.values():
        all_s3_models.update(models)
    
    # Print analysis
    print("\n=== Model Usage Analysis ===")
    print("\nStatic Models (hardcoded in workflows):")
    for model in sorted(static_models):
        components = [name for name, info in workflow_models.items() if model in info['static']]
        status = "✓" if model in all_s3_models else "✗"
        print(f"\n  {status} {model}")
        print(f"    Used in: {', '.join(components)}")
    
    print("\nDynamic Models (configurable via inputs):")
    for model in sorted(dynamic_models):
        components = [name for name, info in workflow_models.items() if model in info['dynamic']]
        status = "✓" if model in all_s3_models else "✗"
        print(f"\n  {status} {model}")
        print(f"    Used in: {', '.join(components)}")
    
    print("\n=== Unused S3 Models ===")
    used_models = static_models | dynamic_models | allowed_models
    for model_type, models in sorted(s3_models.items()):
        unused = [m for m in models if m not in used_models]
        if unused:
            print(f"\n{model_type}:")
            for model in sorted(unused):
                print(f"  - {model}")

if __name__ == '__main__':
    main()
