#!/usr/bin/env node

import { Command } from "commander";
import chalk from "chalk";
import fs from "fs-extra";
import path from "path";
import { input, select, number, expand } from "@inquirer/prompts";

const configPath = path.join(process.env.HOME, ".ecli", "config.json");
const componentsDir = path.join(process.cwd(), "Components");

// File path constants for the new architecture
const getComponentPaths = (componentName) => ({
  form: path.join(componentsDir, componentName, "form.json"),
  inputs: path.join(componentsDir, componentName, "inputs.json"),
  workflow: path.join(componentsDir, componentName, "workflow.json"),
  test: path.join(componentsDir, componentName, "test.json"),
  credits: path.join(componentsDir, componentName, "credits.js"),
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

async function initConfig() {
  try {
    const defaultConfig = {
      apiUrl: "https://cycle-16-dev-api-openstudio.emprops.ai",
    };
    await fs.ensureDir(path.dirname(configPath));
    await fs.writeJson(configPath, defaultConfig, { spaces: 2 });
    console.log(chalk.green("Configuration file created successfully!"));
  } catch (error) {
    console.error(chalk.red(`Failed to initialize configuration: ${error.message}`));
  }
}

async function newComponent() {
  try {
    const config = await fs.readJson(configPath);

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
        }),
        type: await select({
          message: "Select the type of the component",
          choices: [
            { title: "Basic", value: "basic" },
            { title: "Comfy Workflow", value: "comfy_workflow" },
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
        // Create component directory and ref subdirectory
        await fs.ensureDir(componentPath);
        await fs.mkdir(path.join(componentPath, "ref"));
        
        // Create all required files with empty objects/default content
        await fs.writeJson(paths.form, {}, { spaces: 2 });
        await fs.writeJson(paths.inputs, {}, { spaces: 2 });
        await fs.writeJson(paths.workflow, {}, { spaces: 2 });
        await fs.writeJson(paths.test, {}, { spaces: 2 });
        await fs.writeFile(
          paths.credits,
          `function computeCost(context) {\n  return 1;\n}`
        );
        
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
    const config = await fs.readJson(configPath);
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

async function applyComponents(componentName) {
  try {
    const config = await fs.readJson(configPath);
    const paths = getComponentPaths(componentName);

    const { data: component, error: componentError } = await fetchGetComponent(
      config,
      componentName
    );
    if (componentError) {
      console.error(chalk.red(componentError));
      return;
    }

    // Check for required files
    const requiredFiles = [
      { path: paths.form, name: "Forms" },
      { path: paths.inputs, name: "Inputs" },
      { path: paths.workflow, name: "Workflow" }
    ];

    for (const file of requiredFiles) {
      if (!(await fs.pathExists(file.path))) {
        console.error(chalk.red(`${file.name} file not found for component "${componentName}"!`));
        return;
      }
    }

    // Read all component files
    const form = await fs.readJson(paths.form);
    const inputs = await fs.readJson(paths.inputs);
    const workflow = await fs.readJson(paths.workflow);
    let test = {};
    let credits;

    // Optional files
    if (await fs.pathExists(paths.test)) {
      test = await fs.readJson(paths.test);
    }
    if (await fs.pathExists(paths.credits)) {
      credits = await fs.readFile(paths.credits, "utf8");
    }

    console.log(chalk.green(`Applying component "${componentName}"...`));

    const data = {
      form,
      inputs,
      workflow,
      test,
      credits_script: credits,
      output_node_id: workflow.output_node_id || null,
    };

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
    const config = await fs.readJson(configPath);
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
    const config = await fs.readJson(configPath);
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

const program = new Command();

program
  .command("init")
  .description("Initialize the configuration file")
  .action(initConfig);

const componentsCommand = program
  .command("component")
  .arguments("<n>")
  .description("Manage components");

componentsCommand
  .command("new")
  .description("Add a new component")
  .action(newComponent);

componentsCommand
  .command("remove")
  .description("Remove a component")
  .arguments("<n>")
  .action(removeComponent);

componentsCommand
  .command("apply")
  .description("Apply component configuration from local files")
  .arguments("<n>")
  .action(applyComponents);

componentsCommand
  .command("display")
  .description("Toggle component visibility")
  .arguments("<n>")
  .action(displayComponents);

componentsCommand
  .command("get")
  .description("Get component details")
  .arguments("<n>")
  .option("-f, --form", "Get form configuration")
  .option("-i, --input", "Get inputs configuration")
  .option("-w, --workflow", "Get workflow configuration")
  .option("-c, --credits", "Get credits script")
  .action(getComponent);

program.parse(process.argv);
