#!/usr/bin/env node

import { Command } from "commander";
import chalk from "chalk";
import fs from "fs-extra";
import path from "path";
import { input, select, number, expand } from "@inquirer/prompts";

const configPath = path.join(process.env.HOME, ".ecli", "config.json");
const componentsDir = path.join(process.cwd(), "Components");

async function fetchGetComponent(config, name) {
  const url = `${config.apiUrl}/workflows/name/${name}`;
  return fetch(url).then((res) => res.json());
}

async function fetchGetServers(config) {
  const url = `${config.apiUrl}/servers`;
  return fetch(url).then((res) => res.json());
}

async function fetchCreateComponent(config, data) {
  const url = `${config.apiUrl}/workflows`;
  return fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then((res) => res.json());
}

async function fetchRemoveComponent(config, id) {
  const url = `${config.apiUrl}/workflows/${id}`;
  return fetch(url, {
    method: "DELETE",
  }).then((res) => res.json());
}

async function fetchUpdateComponent(config, id, data) {
  const url = `${config.apiUrl}/workflows/${id}`;
  return fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  }).then((res) => res.json());
}

async function initConfig() {
  const defaultConfig = {
    apiUrl: "https://cycle-16-dev-api-openstudio.emprops.ai",
  };
  await fs.ensureDir(path.dirname(configPath));
  await fs.writeJson(configPath, defaultConfig, { spaces: 2 });
  console.log(chalk.green("Configuration file created successfully!"));
}

async function newComponent() {
  const config = await fs.readJson(configPath);

  const { data: servers, error: fetchServersError } =
    await fetchGetServers(config);
  if (fetchServersError != null) {
    console.error(chalk.red(`Failed to fetch servers: ${fetchServersError}`));
    return;
  }
  const serverChoices = servers.map((server) => ({
    name: server.name,
    value: server.id,
  }));

  const componentData = {
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

  // Check if the component already exists
  const componentPath = path.join(componentsDir, componentData.name);
  const { error: createComponentError } = await fetchCreateComponent(
    config,
    componentData
  );
  if (createComponentError != null) {
    console.createComponentError(
      chalk.red(`Failed to create component: ${createComponentError}`)
    );
    return;
  }

  if (!(await fs.pathExists(componentPath))) {
    await fs.ensureDir(componentPath);
    await fs.mkdir(path.join(componentPath, "ref"));
    await fs.writeFile(path.join(componentPath, "api.json"), "{}");
    await fs.writeFile(path.join(componentPath, "form.json"), "{}");
    await fs.writeFile(
      path.join(componentPath, "credits.js"),
      `function computeCost(context) {
  return 1;
}`
    );
  }

  console.log(
    chalk.green(`Component "${componentData.name}" added successfully!`)
  );
}

async function removeComponent(componentName) {
  const config = await fs.readJson(configPath);
  const { data: component, error: getComponentError } = await fetchGetComponent(
    config,
    componentName
  );
  if (getComponentError != null) {
    console.error(chalk.red(`Failed to fetch component: ${getComponentError}`));
    return;
  }
  const { error: removeComponentError } = await fetchRemoveComponent(
    config,
    component.id
  );
  if (removeComponentError != null) {
    console.error(
      chalk.red(`Failed to remove component: ${removeComponentError}`)
    );
    return;
  }
  const componentPath = path.join(componentsDir, componentName);
  if (!(await fs.pathExists(componentPath))) {
    console.error(chalk.red(`Component "${componentName}" does not exist!`));
    return;
  }
  await fs.remove(componentPath);
  console.log(
    chalk.green(`Component "${componentName}" removed successfully!`)
  );
}

async function applyComponents(componentName) {
  const config = await fs.readJson(configPath);

  const { data: component, error: componentError } = await fetchGetComponent(
    config,
    componentName
  );
  if (componentError != null) {
    console.error(chalk.red(`Failed to fetch component: ${componentError}`));
    return;
  }

  if (!(await fs.pathExists(configPath))) {
    console.error(
      chalk.red("Configuration file not found! Please run `ecli init` first.")
    );
    return;
  }

  const formsFilePath = path.join(componentsDir, componentName, "form.json");
  const apiFilePath = path.join(componentsDir, componentName, "api.json");
  const creditsFilePath = path.join(componentsDir, componentName, "credits.js");

  if (!(await fs.pathExists(formsFilePath))) {
    console.error(
      chalk.red(`Forms file not found for component "${componentName}"!`)
    );
    return;
  }

  if (!(await fs.pathExists(apiFilePath))) {
    console.error(
      chalk.red(`API file not found for component "${componentName}"!`)
    );
    return;
  }

  const form = await fs.readJson(formsFilePath);
  const api = await fs.readJson(apiFilePath);

  let credits;
  if (await fs.pathExists(creditsFilePath)) {
    credits = fs.readFileSync(creditsFilePath, "utf8");
  }

  console.log(chalk.green(`Applying component "${componentName}"...`));

  const data = {
    form,
    inputs: api.inputs,
    workflow: api.workflow,
    credits_script: credits,
    output_node_id: api.output_node_id || null,
  };
  const { error: updateError } = await fetchUpdateComponent(
    config,
    component.id,
    {
      data,
    }
  );

  if (updateError != null) {
    console.error(chalk.red(`Failed to update component "${componentName}"!`));
    return;
  }

  console.log(
    chalk.green(`Component "${componentName}" applied successfully!`)
  );
}

async function getComponent(componentName, options) {
  console.log(`Getting details of component "${componentName}"...`);
  const config = await fs.readJson(configPath);
  const { data: component, error } = await fetchGetComponent(
    config,
    componentName
  );
  if (error != null) {
    console.error(chalk.red(`Failed to fetch component: ${error}`));
    return;
  }
  if (options.form) {
    console.log(
      chalk.magentaBright(
        JSON.stringify(component.data.form || "Not Found", null, 2)
      )
    );
  } else if (options.input) {
    console.log(
      chalk.magentaBright(
        JSON.stringify(component.data.inputs || "Not Found", null, 2)
      )
    );
  } else if (options.workflow) {
    console.log(
      chalk.magentaBright(
        JSON.stringify(component.data.workflow || "Not Found", null, 2)
      )
    );
  } else if (options.credits) {
    console.log(chalk.magenta(component.data.credits_script || "Not Found"));
  } else {
    console.log(JSON.stringify(component, null, 2));
  }
}

async function displayComponents(componentName) {
  const config = await fs.readJson(configPath);
  const { data: components, error: getComponentError } =
    await fetchGetComponent(config, componentName);
  if (getComponentError != null) {
    console.error(
      chalk.red(`Failed to fetch components: ${getComponentError}`)
    );
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
      if (error != null) {
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
      if (error != null) {
        console.error(chalk.red(`Failed to update component: ${error}`));
        return;
      }
      console.log(chalk.green("Component hidden successfully!"));
      break;
    }
    case "abort":
      break;
  }
}

const program = new Command();

program
  .command("init")
  .description("Initialize the configuration file")
  .action(initConfig);

const componentsCommand = program
  .command("component")
  .arguments("<name>")
  .description("Manage components");

componentsCommand
  .command("new")
  .description("Add a new component")
  .action(newComponent);

componentsCommand
  .command("remove")
  .description("Remove a component")
  .arguments("<name>")
  .action(removeComponent);

componentsCommand
  .command("apply")
  .description("Apply the components")
  .arguments("<name>")
  .action(applyComponents);

componentsCommand
  .command("display")
  .description("Display the components")
  .arguments("<name>")
  .action(displayComponents);

componentsCommand
  .command("get")
  .description("Get details of a component")
  .arguments("<name>")
  .option("-f, --form", "Get form of the component")
  .option("-i, --input", "Get form of the component")
  .option("-w, --workflow", "Get API of the component")
  .option("-c, --credits", "Get credits of the component")
  .action(getComponent);

program.parse(process.argv);
