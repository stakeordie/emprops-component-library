import { z } from 'zod';

// Base schemas for common field properties
const baseFieldSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.string(),
  display: z.boolean(),
  default: z.any().optional(),
});

// Schema for slider constraints
const sliderConstraintsSchema = z.object({
  min: z.number(),
  max: z.number(),
  step: z.number(),
});

// Schema for different field types
const selectFieldSchema = baseFieldSchema.extend({
  type: z.literal('select'),
  conf_file: z.string(),
});

const promptEditorFieldSchema = baseFieldSchema.extend({
  type: z.literal('prompt_editor'),
  placeholder: z.string().optional(),
});

const sliderFieldSchema = baseFieldSchema.extend({
  type: z.literal('slider'),
  constraints: sliderConstraintsSchema,
});

const imageLoaderFieldSchema = baseFieldSchema.extend({
  type: z.literal('image_loader'),
});

const aspectRatioFieldSchema = baseFieldSchema.extend({
  type: z.literal('aspect_ratio'),
  conf_file: z.string(),
});

// Union type for all field types
const fieldSchema = z.discriminatedUnion('type', [
  selectFieldSchema,
  promptEditorFieldSchema,
  sliderFieldSchema,
  imageLoaderFieldSchema,
  aspectRatioFieldSchema,
]);

// Schema for form.json
export const formConfigSchema = z.object({
  main: z.array(fieldSchema),
  advanced: z.array(fieldSchema),
});

// Schema for inputs.json
export const inputConfigSchema = z.array(
  z.object({
    id: z.string(),
    pathJq: z.string(),
  })
);

// Schema for api.json
export const apiConfigSchema = z.object({
  url: z.string().url(),
  method: z.enum(['GET', 'POST', 'PUT', 'DELETE']),
  headers: z.record(z.string()),
  successResponseCode: z.array(z.number()),
  fetchType: z.enum(['wait', 'poll']),
  wait: z.object({
    outputExprJq: z.string(),
  }).optional(),
  poll: z.object({
    interval: z.number(),
    timeout: z.number(),
    statusExprJq: z.string(),
    outputExprJq: z.string(),
  }).optional(),
});

// Schema for workflow.json (comfy_workflow type)
export const workflowConfigSchema = z.object({
  nodes: z.record(z.any()),
  output_node_id: z.string(),
}).optional();

// Function to validate component files
export async function validateComponent(componentPath, type) {
  const errors = [];
  
  try {
    // Validate form.json (required for all types)
    const formPath = path.join(componentPath, 'form.json');
    if (await fs.pathExists(formPath)) {
      const formData = await fs.readJson(formPath);
      try {
        formConfigSchema.parse(formData);
      } catch (e) {
        errors.push(`form.json validation failed: ${e.message}`);
      }
    } else {
      errors.push('form.json is required but missing');
    }

    // Validate type-specific files
    if (type === 'fetch_api') {
      // Validate api.json
      const apiPath = path.join(componentPath, 'api.json');
      if (await fs.pathExists(apiPath)) {
        const apiData = await fs.readJson(apiPath);
        try {
          apiConfigSchema.parse(apiData);
        } catch (e) {
          errors.push(`api.json validation failed: ${e.message}`);
        }
      } else {
        errors.push('api.json is required for fetch_api type but missing');
      }

      // Validate inputs.json
      const inputsPath = path.join(componentPath, 'inputs.json');
      if (await fs.pathExists(inputsPath)) {
        const inputsData = await fs.readJson(inputsPath);
        try {
          inputConfigSchema.parse(inputsData);
        } catch (e) {
          errors.push(`inputs.json validation failed: ${e.message}`);
        }
      }
    } else if (type === 'comfy_workflow') {
      // Validate workflow.json
      const workflowPath = path.join(componentPath, 'workflow.json');
      if (await fs.pathExists(workflowPath)) {
        const workflowData = await fs.readJson(workflowPath);
        try {
          workflowConfigSchema.parse(workflowData);
        } catch (e) {
          errors.push(`workflow.json validation failed: ${e.message}`);
        }
      } else {
        errors.push('workflow.json is required for comfy_workflow type but missing');
      }
    }

    return errors.length > 0 ? { valid: false, errors } : { valid: true };
  } catch (error) {
    return { valid: false, errors: [`Validation failed: ${error.message}`] };
  }
}
