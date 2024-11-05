#!/usr/bin/env node

import { Command } from "commander";
import chalk from "chalk";
import fs from "fs-extra";
import path from "path";

const program = new Command();
const configPath = path.join(process.env.HOME, ".ecli", "config.json");
const componentsDir = path.join(process.cwd(), "Components");

async function fetchComponent(config, componentName) {
  const url = `${config.apiUrl}/workflows/name/${componentName}`;
  return fetch(url).then((res) => res.json());
}

async function updateComponent(config, id, data) {
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

async function addComponent(componentName) {
  const componentPath = path.join(componentsDir, componentName);

  if (await fs.pathExists(componentPath)) {
    console.error(chalk.red(`Component "${componentName}" already exists!`));
    return;
  }

  await fs.ensureDir(componentPath);
  await fs.mkdir(path.join(componentPath, "ref"));
  await fs.writeFile(path.join(componentPath, "api.json"), "");
  await fs.writeFile(path.join(componentPath, "form.json"), "");
  await fs.writeFile(
    path.join(componentPath, "credits.js"),
    `function computeCredits(context) {
  return 1;
}`
  );

  console.log(chalk.green(`Component "${componentName}" added successfully!`));
}

async function removeComponent(componentName) {
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

  const { data: component, error: componentError } = await fetchComponent(
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
  };
  const { error: updateError } = await updateComponent(config, component.id, {
    data,
  });

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
  const { data: component, error } = await fetchComponent(
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
    console.log(chalk.magenta(component.data.credits_script) || "Not Found");
  } else {
    console.log(JSON.stringify(component, null, 2));
  }
}

program
  .command("init")
  .description("Initialize the configuration file")
  .action(initConfig);

const componentsCommand = program
  .command("component")
  .arguments("<name>")
  .description("Manage components");

componentsCommand
  .command("add")
  .description("Add a new component")
  .arguments("<name>")
  .action(addComponent);

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
  .command("get")
  .description("Get details of a component")
  .arguments("<name>")
  .option("-f, --form", "Get form of the component")
  .option("-i, --input", "Get form of the component")
  .option("-w, --workflow", "Get API of the component")
  .option("-c, --credits", "Get credits of the component")
  .action(getComponent);

program.parse(process.argv);
