#!/usr/bin/env node

import { Command } from "commander";
import chalk from "chalk";
import fs from "fs-extra";
import path from "path";
import { input, select, number, expand } from "@inquirer/prompts";
import crypto from 'crypto';
import { validateComponent } from './schemas.js';

const configPath = path.join(process.env.HOME, ".ecli", "config.json");
const componentsDir = path.join(process.cwd(), "Components");
const stateFilePath = path.join(componentsDir, ".ecli-state.json");

// File path constants for the new architecture
const getComponentPaths = (componentName) => ({
  form: path.join(componentsDir, componentName, "form.json"),
  inputs: path.join(componentsDir, componentName, "inputs.json"),
  workflow: path.join(componentsDir, componentName, "workflow.json"),
  test: path.join(componentsDir, componentName, "test.json"),
  credits: path.join(componentsDir, componentName, "credits.js"),
  api: path.join(componentsDir, componentName, "api.json"),
  body: path.join(componentsDir, componentName, "body.json"),
});

async function fetchGetComponent(config, name) {
  try {
    const url = `${config.apiUrl}/workflows/name/${name}`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // API already returns { data, error } structure
  } catch (error) {
    return { data: null, error: `Failed to fetch component: ${error.message}` };
  }
}

async function fetchGetServers(config) {
  try {
    const url = `${config.apiUrl}/servers`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // API already returns { data, error } structure
  } catch (error) {
    return { data: null, error: `Failed to fetch servers: ${error.message}` };
  }
}

async function fetchCreateComponent(config, data) {
  try {
    const url = `${config.apiUrl}/workflows`;
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // API already returns { data, error } structure
  } catch (error) {
    return { data: null, error: `Failed to create component: ${error.message}` };
  }
}

async function fetchRemoveComponent(config, id) {
  try {
    const url = `${config.apiUrl}/workflows/${id}`;
    const response = await fetch(url, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // API already returns { data, error } structure
  } catch (error) {
    return { data: null, error: `Failed to remove component: ${error.message}` };
  }
}

async function fetchUpdateComponent(config, id, data) {
  try {
    const url = `${config.apiUrl}/workflows/${id}`;
    const response = await fetch(url, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // API already returns { data, error } structure
  } catch (error) {
    return { data: null, error: `Failed to update component: ${error.message}` };
  }
}

async function fetchGetFormConfig(config, name) {
  try {
    const url = name 
      ? `${config.apiUrl}/form-configs/name/${name}`
      : `${config.apiUrl}/form-configs`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    return { data: null, error: `Failed to fetch form config: ${error.message}` };
  }
}

async function fetchCreateFormConfig(config, name, data) {
  try {
    const url = `${config.apiUrl}/form-configs`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name,
        data
      }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    return { data: null, error: `Failed to create form config: ${error.message}` };
  }
}

async function fetchDeleteFormConfig(config, id) {
  try {
    const url = `${config.apiUrl}/form-configs/${id}`;
    const response = await fetch(url, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    return { data: null, error: `Failed to delete form config: ${error.message}` };
  }
}

async function initConfig() {
  try {
    const defaultConfig = {
      currentEnv: "dev",
      environments: {
        dev: {
          apiUrl: "https://cycle-16-dev-api-openstudio.emprops.ai"
        }
      }
    };
    await fs.ensureDir(path.dirname(configPath));
    await fs.writeJson(configPath, defaultConfig, { spaces: 2 });
    console.log(chalk.green("Configuration file created successfully!"));
  } catch (error) {
    console.error(chalk.red(`Failed to initialize configuration: ${error.message}`));
  }
}

async function getCurrentEnvironment() {
  try {
    const config = await fs.readJson(configPath);
    return {
      name: config.currentEnv,
      ...config.environments[config.currentEnv]
    };
  } catch (error) {
    console.error(chalk.red(`Failed to get current environment: ${error.message}`));
    process.exit(1);
  }
}

async function addEnvironment(name, apiUrl) {
  try {
    const config = await fs.readJson(configPath);
    if (config.environments[name]) {
      console.error(chalk.red(`Environment "${name}" already exists`));
      return;
    }
    
    config.environments[name] = { apiUrl };
    await fs.writeJson(configPath, config, { spaces: 2 });
    console.log(chalk.green(`Environment "${name}" added successfully`));
  } catch (error) {
    console.error(chalk.red(`Failed to add environment: ${error.message}`));
  }
}

async function removeEnvironment(name) {
  try {
    const config = await fs.readJson(configPath);
    if (!config.environments[name]) {
      console.error(chalk.red(`Environment "${name}" does not exist`));
      return;
    }
    
    if (config.currentEnv === name) {
      console.error(chalk.red(`Cannot remove current environment "${name}"`));
      return;
    }
    
    delete config.environments[name];
    await fs.writeJson(configPath, config, { spaces: 2 });
    console.log(chalk.green(`Environment "${name}" removed successfully`));
  } catch (error) {
    console.error(chalk.red(`Failed to remove environment: ${error.message}`));
  }
}

async function switchEnvironment(name) {
  try {
    const config = await fs.readJson(configPath);
    if (!config.environments[name]) {
      console.error(chalk.red(`Environment "${name}" does not exist`));
      return;
    }
    
    config.currentEnv = name;
    await fs.writeJson(configPath, config, { spaces: 2 });
    console.log(chalk.green(`Switched to environment "${name}"`));
  } catch (error) {
    console.error(chalk.red(`Failed to switch environment: ${error.message}`));
  }
}

async function listEnvironments() {
  try {
    const config = await fs.readJson(configPath);
    console.log(chalk.blue("\nAvailable Environments:"));
    Object.entries(config.environments).forEach(([name, env]) => {
      const isCurrent = name === config.currentEnv;
      const prefix = isCurrent ? chalk.green("* ") : "  ";
      console.log(`${prefix}${name}: ${env.apiUrl}`);
    });
  } catch (error) {
    console.error(chalk.red(`Failed to list environments: ${error.message}`));
  }
}

async function newComponent() {
  try {
    const config = await getCurrentEnvironment();

    const { data: servers, error: fetchServersError } = await fetchGetServers(config);
    if (fetchServersError) {
      console.error(chalk.red(fetchServersError));
      return;
    }
    
    const serverChoices = servers
      .map((server) => ({
        name: server.name,
        value: server.id,
      }))
      .concat({ name: "None", value: undefined });

    let componentData;
    try {
      componentData = {
        name: await input({
          message: "Enter the name of the component",
          required: true,
          validate: (input) => {
            if (!/^[a-z0-9-]+$/.test(input)) {
              return 'Component name must contain only lowercase letters, numbers, and hyphens';
            }
            return true;
          }
        }),
        label: await input({
          message: "Enter the label of the component",
          required: true,
        }),
        description: await input({
          message: "Enter the description of the component",
          required: true,
        }),
        server_id: await select({
          message: "Select the server",
          choices: serverChoices,
        }),
        output_mime_type: await input({
          message: "Enter the output mime type",
          initial: "image/png",
          validate: (input) => {
            if (!/^[a-z]+\/[a-z0-9.+-]+$/.test(input)) {
              return 'Invalid MIME type format (e.g., image/png, video/mp4)';
            }
            return true;
          }
        }),
        type: await select({
          message: "Select the type of the component",
          choices: [
            { title: "Basic", value: "basic" },
            { title: "Comfy Workflow", value: "comfy_workflow" },
            { title: "Fetch API", value: "fetch_api" },
          ],
        }),
        order: await number({
          message: "Enter the order of the component",
          default: 0,
        }),
        display: false,
      };
    } catch (error) {
      return;
    }

    // Check if the component already exists
    const componentPath = path.join(componentsDir, componentData.name);
    const { error: componentCreationError } = await fetchCreateComponent(config, componentData);
    
    if (componentCreationError) {
      console.error(chalk.red(componentCreationError));
      return;
    }

    if (!(await fs.pathExists(componentPath))) {
      const paths = getComponentPaths(componentData.name);
      
      try {
        // Create component directory
        await fs.ensureDir(componentPath);
        
        // Create ref directory only for comfy_workflow type
        if (componentData.type === "comfy_workflow") {
          await fs.mkdir(path.join(componentPath, "ref"));
        }
        
        if (componentData.type === "comfy_workflow") {
          // Create all required files with empty objects/default content
          await fs.writeJson(paths.form, { main: [], advanced: [] }, { spaces: 2 });
          await fs.writeJson(paths.inputs, {}, { spaces: 2 });
          await fs.writeJson(paths.workflow, {}, { spaces: 2 });
          await fs.writeJson(paths.test, {}, { spaces: 2 });
          await fs.writeFile(
            paths.credits,
            `function computeCost(context) {\n  return { cost: 1 };\n}`
          );
        } else if (componentData.type === "fetch_api") {
          // For fetch_api, create credits.js, form.json, inputs.json, body.json and api.json
          await fs.writeJson(paths.form, { main: [], advanced: [] }, { spaces: 2 });
          await fs.writeJson(paths.api, {}, { spaces: 2 });
          await fs.writeJson(paths.inputs, {}, { spaces: 2 });
          await fs.writeJson(paths.body, {}, { spaces: 2 });
          await fs.writeFile(
            paths.credits,
            `function computeCost(context) {\n  return { cost: 1 };\n}`
          );
        } else if (componentData.type === "basic") {
          // For basic, only create credits.js
          await fs.writeFile(
            paths.credits,
            `function computeCost(context) {\n  return { cost: 1 };\n}`
          );
        }
        
        console.log(chalk.green(`Component "${componentData.name}" added successfully!`));
      } catch (fsError) {
        console.error(chalk.red(`Failed to create component files: ${fsError.message}`));
        // Attempt to rollback the API creation
        const { data: component } = await fetchGetComponent(config, componentData.name);
        if (component?.id) {
          await fetchRemoveComponent(config, component.id);
        }
      }
    }
  } catch (error) {
    console.error(chalk.red(`Unexpected error: ${error.message}`));
  }
}

async function removeComponent(componentName) {
  try {
    const config = await getCurrentEnvironment();
    const { data: component, error: getComponentError } = await fetchGetComponent(
      config,
      componentName
    );
    if (getComponentError) {
      console.error(chalk.red(getComponentError));
      return;
    }
    const { error: removeComponentError } = await fetchRemoveComponent(
      config,
      component.id
    );
    if (removeComponentError) {
      console.error(chalk.red(removeComponentError));
      return;
    }
    
    const componentPath = path.join(componentsDir, componentName);
    if (!(await fs.pathExists(componentPath))) {
      console.error(chalk.red(`Component "${componentName}" does not exist!`));
      return;
    }
    
    await fs.remove(componentPath);
    console.log(chalk.green(`Component "${componentName}" removed successfully!`));
  } catch (error) {
    console.error(chalk.red(`Unexpected error: ${error.message}`));
  }
}

async function applyComponents(componentName, options = { verbose: false }) {
  try {
    const config = await getCurrentEnvironment();
    const paths = getComponentPaths(componentName);

    const { error: componentError, data: component } = await fetchGetComponent(
      config,
      componentName
    );
    if (componentError) {
      console.error(chalk.red(componentError));
      return;
    }

    // Validate component files
    const validationResult = await validateComponent(path.join(componentsDir, componentName), component.type);
    if (!validationResult.valid) {
      console.error(chalk.red('Validation errors:'));
      validationResult.errors.forEach(error => {
        console.error(chalk.red(`- ${error}`));
      });
      return;
    }

    // Check for required files based on component type
    let requiredFiles = [];
    
    if (component.type === "fetch_api") {
      requiredFiles = [
        { path: paths.form, name: "Form" },
        { path: paths.api, name: "API" },
        { path: paths.credits, name: "Credits" }
      ];
    } else if (component.type === "basic") {
      requiredFiles = [
        { path: paths.credits, name: "Credits" }
      ];
    } else if (component.type === "comfy_workflow") {
      requiredFiles = [
        { path: paths.form, name: "Form" },
        { path: paths.inputs, name: "Inputs" },
        { path: paths.workflow, name: "Workflow" },
        { path: paths.test, name: "Test" },
        { path: paths.credits, name: "Credits" }
      ];
    }

    for (const file of requiredFiles) {
      if (!(await fs.pathExists(file.path))) {
        console.error(chalk.red(`${file.name} file not found for component "${componentName}"!`));
        return;
      }
    }

    // Read files based on component type
    let form = undefined;
    let inputs = undefined;
    let workflow = undefined;
    let test = undefined;
    let api = undefined;
    let body = undefined;
    let credits = undefined;

    if (component.type === "comfy_workflow") {
      form = await fs.readJson(paths.form);
      inputs = await fs.readJson(paths.inputs);
      workflow = await fs.readJson(paths.workflow);
      if (await fs.pathExists(paths.test)) {
        test = await fs.readJson(paths.test);
      }
      credits = await fs.readFile(paths.credits, "utf8");
    } else if (component.type === "fetch_api") {
      form = await fs.readJson(paths.form);
      api = await fs.readJson(paths.api);
      if (await fs.pathExists(paths.inputs)) {
        inputs = await fs.readJson(paths.inputs);
      }
      if (await fs.pathExists(paths.body)) {
        body = await fs.readJson(paths.body);
      }
      credits = await fs.readFile(paths.credits, "utf8");
    } else if (component.type === "basic") {
      credits = await fs.readFile(paths.credits, "utf8");
    }

    console.log(chalk.green(`Applying component "${componentName}"...`));

    const data = {
      form,
      inputs,
      workflow,
      test,
      api,
      body,
      credits_script: credits,
      output_node_id: workflow?.output_node_id || null,
    };

    if (options.verbose) {
      console.log(chalk.blue("\nSubmitting data:"));
      console.log(JSON.stringify(data, null, 2));
    }

    const { error: updateError } = await fetchUpdateComponent(config, component.id, {
      data,
    });

    if (updateError) {
      console.error(chalk.red(`Failed to update component: ${updateError}`));
      return;
    }

    console.log(chalk.green(`Component "${componentName}" applied successfully!`));
  } catch (error) {
    console.error(chalk.red(`Unexpected error: ${error.message}`));
  }
}

async function getComponent(componentName, options) {
  try {
    console.log(`Getting details of component "${componentName}"...`);
    const config = await getCurrentEnvironment();
    const paths = getComponentPaths(componentName);

    if (options.form) {
      if (await fs.pathExists(paths.form)) {
        const form = await fs.readJson(paths.form);
        console.log(chalk.magentaBright(JSON.stringify(form, null, 2)));
      } else {
        console.log(chalk.yellow("Form not found"));
      }
    } else if (options.input) {
      if (await fs.pathExists(paths.inputs)) {
        const inputs = await fs.readJson(paths.inputs);
        console.log(chalk.magentaBright(JSON.stringify(inputs, null, 2)));
      } else {
        console.log(chalk.yellow("Inputs not found"));
      }
    } else if (options.workflow) {
      if (await fs.pathExists(paths.workflow)) {
        const workflow = await fs.readJson(paths.workflow);
        console.log(chalk.magentaBright(JSON.stringify(workflow, null, 2)));
      } else {
        console.log(chalk.yellow("Workflow not found"));
      }
    } else if (options.credits) {
      if (await fs.pathExists(paths.credits)) {
        const credits = await fs.readFile(paths.credits, "utf8");
        console.log(chalk.magenta(credits));
      } else {
        console.log(chalk.yellow("Credits not found"));
      }
    } else {
      // Fetch and display all component data
      const { data: component, error } = await fetchGetComponent(config, componentName);
      if (error) {
        console.error(chalk.red(error));
        return;
      }
      console.log(JSON.stringify(component, null, 2));
    }
  } catch (error) {
    console.error(chalk.red(`Unexpected error: ${error.message}`));
  }
}

async function displayComponents(componentName) {
  try {
    const config = await getCurrentEnvironment();
    const { data: components, error: getComponentError } =
      await fetchGetComponent(config, componentName);
    if (getComponentError) {
      console.error(chalk.red(getComponentError));
      return;
    }

    const answer = await expand({
      message: `Do you want to display/hide the ${componentName}?`,
      default: "n",
      choices: [
        {
          key: "y",
          name: "Display",
          value: "yes",
        },
        {
          key: "n",
          name: "Hide",
          value: "no",
        },
        {
          key: "x",
          name: "Abort",
          value: "abort",
        },
      ],
    });

    switch (answer) {
      case "yes": {
        const { error } = await fetchUpdateComponent(config, components.id, {
          display: true,
        });
        if (error) {
          console.error(chalk.red(`Failed to update component: ${error}`));
          return;
        }
        console.log(chalk.green("Component displayed successfully!"));
        break;
      }
      case "no": {
        const { error } = await fetchUpdateComponent(config, components.id, {
          display: false,
        });
        if (error) {
          console.error(chalk.red(`Failed to update component: ${error}`));
          return;
        }
        console.log(chalk.green("Component hidden successfully!"));
        break;
      }
      case "abort":
        break;
    }
  } catch (error) {
    console.error(chalk.red(`Unexpected error: ${error.message}`));
  }
}

async function calculateFileHash(filePath) {
  try {
    const content = await fs.readFile(filePath, 'utf8');
    return crypto.createHash('sha256').update(content).digest('hex');
  } catch (error) {
    return null;
  }
}

async function getComponentHash(componentName) {
  const paths = getComponentPaths(componentName);
  
  // Get component type first
  const config = await getCurrentEnvironment();
  const { data: component } = await fetchGetComponent(config, componentName);
  
  const hashes = {
    credits: await calculateFileHash(paths.credits)
  };

  if (component.type === "comfy_workflow") {
    hashes.form = await calculateFileHash(paths.form);
    hashes.inputs = await calculateFileHash(paths.inputs);
    hashes.workflow = await calculateFileHash(paths.workflow);
    hashes.test = await calculateFileHash(paths.test);
  } else if (component.type === "fetch_api") {
    hashes.form = await calculateFileHash(paths.form);
    hashes.api = await calculateFileHash(paths.api);
  }
  
  return hashes;
}

async function loadState() {
  try {
    if (await fs.pathExists(stateFilePath)) {
      return await fs.readJson(stateFilePath);
    }
    return { components: {} };
  } catch (error) {
    console.error(chalk.yellow(`Warning: Could not load state file: ${error.message}`));
    return { components: {} };
  }
}

async function saveState(state) {
  try {
    await fs.writeJson(stateFilePath, state, { spaces: 2 });
  } catch (error) {
    console.error(chalk.yellow(`Warning: Could not save state file: ${error.message}`));
  }
}

async function getValidComponents() {
  try {
    const items = await fs.readdir(componentsDir);
    return items.filter(item => 
      !item.startsWith('_') && 
      item !== 'p52vid' && 
      item !== '.ecli-state.json' &&
      fs.statSync(path.join(componentsDir, item)).isDirectory()
    );
  } catch (error) {
    console.error(chalk.red(`Error reading components directory: ${error.message}`));
    return [];
  }
}

async function hasComponentChanged(componentName, state) {
  const currentHashes = await getComponentHash(componentName);
  const storedState = state.components[componentName];
  
  if (!storedState) {
    return true;
  }

  const storedHashes = storedState.fileHashes;
  return Object.entries(currentHashes).some(([file, hash]) => 
    hash !== storedHashes[file]
  );
}

async function applyChangedComponents(options = { force: false, dryRun: false }) {
  try {
    const state = await loadState();
    const components = await getValidComponents();
    
    if (components.length === 0) {
      console.log(chalk.yellow('No valid components found.'));
      return;
    }

    console.log(chalk.blue('Checking for changed components...'));
    
    const changedComponents = [];
    for (const component of components) {
      const changed = options.force || await hasComponentChanged(component, state);
      if (changed) {
        changedComponents.push(component);
      }
    }

    if (changedComponents.length === 0) {
      console.log(chalk.green('No components have changed.'));
      return;
    }

    console.log(chalk.blue(`\nFound ${changedComponents.length} changed components:`));
    changedComponents.forEach(component => 
      console.log(chalk.cyan(`- ${component}`))
    );

    if (options.dryRun) {
      console.log(chalk.yellow('\nDry run - no changes will be made.'));
      return;
    }

    console.log(chalk.blue('\nApplying changes...'));
    
    const results = {
      success: [],
      failure: []
    };

    for (const component of changedComponents) {
      try {
        console.log(chalk.cyan(`\nApplying ${component}...`));
        await applyComponents(component);
        
        // Update state after successful apply
        state.components[component] = {
          lastApplied: new Date().toISOString(),
          fileHashes: await getComponentHash(component)
        };
        
        results.success.push(component);
        console.log(chalk.green(`✓ ${component} applied successfully`));
      } catch (error) {
        results.failure.push({ component, error: error.message });
        console.log(chalk.red(`✗ Failed to apply ${component}: ${error.message}`));
      }
    }

    // Save state only after all successful applications
    await saveState(state);

    // Print summary
    console.log(chalk.blue('\nSummary:'));
    console.log(chalk.green(`✓ Successfully applied: ${results.success.length}`));
    if (results.failure.length > 0) {
      console.log(chalk.red(`✗ Failed to apply: ${results.failure.length}`));
      console.log(chalk.red('\nFailed components:'));
      results.failure.forEach(({ component, error }) => 
        console.log(chalk.red(`- ${component}: ${error}`))
      );
    }
  } catch (error) {
    console.error(chalk.red(`\nUnexpected error: ${error.message}`));
  }
}

async function updateComponent(componentName) {
  try {
    const config = await getCurrentEnvironment();

    // Get current component data
    const { data: component, error: componentError } = await fetchGetComponent(
      config,
      componentName
    );
    if (componentError) {
      console.error(chalk.red(componentError));
      return;
    }

    const { data: servers, error: fetchServersError } = await fetchGetServers(config);
    if (fetchServersError) {
      console.error(chalk.red(fetchServersError));
      return;
    }
    
    const serverChoices = servers
      .map((server) => ({
        name: server.name,
        value: server.id,
      }))
      .concat({ name: "None", value: undefined });

    let updatedData;
    try {
      updatedData = {
        name: await input({
          message: "Enter the new name of the component",
          default: component.name,
          required: true,
        }),
        label: await input({
          message: "Enter the new label of the component",
          default: component.label,
          required: true,
        }),
        description: await input({
          message: "Enter the new description of the component",
          default: component.description,
          required: true,
        }),
        server_id: await select({
          message: "Select the new server",
          choices: serverChoices,
          default: component.server_id,
        }),
        output_mime_type: await input({
          message: "Enter the new output mime type",
          default: component.output_mime_type || "image/png",
        }),
        type: await select({
          message: "Select the new type of the component",
          choices: [
            { title: "Basic", value: "basic" },
            { title: "Comfy Workflow", value: "comfy_workflow" },
            { title: "Fetch API", value: "fetch_api" },
          ],
          default: component.type,
        }),
        order: await number({
          message: "Enter the new order of the component",
          default: component.order || 0,
        }),
      };
    } catch (error) {
      return;
    }

    // Update the component on the server
    const { error: updateError } = await fetchUpdateComponent(config, component.id, updatedData);
    if (updateError) {
      console.error(chalk.red(updateError));
      return;
    }

    console.log(chalk.green(`✓ Component ${componentName} updated successfully`));
  } catch (error) {
    console.error(chalk.red(`Failed to update component: ${error.message}`));
  }
}

async function getFormConfig(fileName) {
  try {
    const config = await getCurrentEnvironment();
    const result = await fetchGetFormConfig(config, fileName);
    
    if (result.error) {
      console.error(chalk.red(result.error));
      return;
    }

    console.log(JSON.stringify(result.data, null, 2));
  } catch (error) {
    console.error(chalk.red(`Error: ${error.message}`));
  }
}

async function newFormConfig(fileName) {
  try {
    const config = await getCurrentEnvironment();
    const formConfigPath = path.join(componentsDir, "_form_confs", fileName);
    
    if (!fs.existsSync(formConfigPath)) {
      console.error(chalk.red(`Error: File ${fileName} not found in Components/_form_confs`));
      return;
    }

    const fileData = await fs.readJson(formConfigPath);
    const result = await fetchCreateFormConfig(config, fileName, fileData);
    
    if (result.error) {
      console.error(chalk.red(result.error));
      return;
    }

    console.log(chalk.green(`Successfully created form config: ${fileName}`));
    console.log(JSON.stringify(result.data, null, 2));
  } catch (error) {
    console.error(chalk.red(`Error: ${error.message}`));
  }
}

async function deleteFormConfig(fileName, options) {
  try {
    const config = await getCurrentEnvironment();
    const formConfigPath = path.join(componentsDir, "_form_confs", fileName);
    
    const { data: formConfig, error: getFormConfigError } = await fetchGetFormConfig(config, fileName);
    if (getFormConfigError) {
      console.error(chalk.red(getFormConfigError));
      return;
    }
    const result = await fetchDeleteFormConfig(config, formConfig.id);
    if (result.error) {
      console.error(chalk.red(result.error));
      return;
    }

    // Delete local file if --server-only flag is not set
    if (!options.serverOnly) {
      if (await fs.pathExists(formConfigPath)) {
        await fs.remove(formConfigPath);
        console.log(chalk.green(`Local file "${fileName}" deleted successfully`));
      } else {
        console.warn(chalk.yellow(`Local file "${fileName}" not found`));
      }
    }

    console.log(chalk.green(`Form config "${fileName}" deleted successfully from server`));
  } catch (error) {
    console.error(chalk.red(`Error: ${error.message}`));
  }
}

const program = new Command();

program
  .command("init")
  .description("Initialize the CLI configuration")
  .action(initConfig);

program
  .command("env")
  .description("Manage environments")
  .addCommand(
    new Command("list")
      .description("List all environments")
      .action(listEnvironments)
  )
  .addCommand(
    new Command("add")
      .argument("<name>", "Environment name")
      .argument("<apiUrl>", "API URL for the environment")
      .description("Add a new environment")
      .action(addEnvironment)
  )
  .addCommand(
    new Command("remove")
      .argument("<name>", "Environment name")
      .description("Remove an environment")
      .action(removeEnvironment)
  )
  .addCommand(
    new Command("switch")
      .argument("<name>", "Environment name")
      .description("Switch to an environment")
      .action(switchEnvironment)
  );

const componentsCommand = program
  .command("component")
  .description("Manage components");

componentsCommand
  .command("new")
  .description("Create a new component")
  .action(newComponent);

componentsCommand
  .command("update <componentName>")
  .description("Update component details (name, label, description, etc.)")
  .action(updateComponent);

componentsCommand
  .command("remove <componentName>")
  .description("Remove a component")
  .action(removeComponent);

componentsCommand
  .command("apply <componentName>")
  .description("Apply component configuration from local files")
  .option("-v, --verbose", "Print submitted data", false)
  .action((componentName, options) => applyComponents(componentName, options));

componentsCommand
  .command("apply-changed")
  .description("Apply all components that have changed since last apply")
  .option("-f, --force", "Force apply all components regardless of changes", false)
  .option("-d, --dry-run", "Show what would be applied without making changes", false)
  .action((options) => applyChangedComponents(options));

componentsCommand
  .command("display <componentName>")
  .description("Toggle component visibility")
  .action(displayComponents);

componentsCommand
  .command("get <componentName>")
  .description("Get component details")
  .option("-f, --form", "Get form configuration")
  .option("-i, --input", "Get inputs configuration")
  .option("-w, --workflow", "Get workflow configuration")
  .option("-c, --credits", "Get credits script")
  .action(getComponent);

const formConfigCommand = program
  .command("form-config")
  .description("Manage form configurations");

formConfigCommand
  .command("get [fileName]")
  .description("Get form config(s). If fileName is provided, get specific config")
  .action(getFormConfig);

formConfigCommand
  .command("apply <fileName>")
  .description("Create a new form config from file in Components/_form_confs")
  .action(newFormConfig);

formConfigCommand
  .command("delete <fileName>")
  .description("Delete a form config")
  .option("-s, --server-only", "Only delete from server, keep local file", false)
  .action((fileName, options) => deleteFormConfig(fileName, options));

program.parse(process.argv);
