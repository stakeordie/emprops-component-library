# EmProps Component Library

## Component UI Configuration

This documents outlines how to write the `forms.js` JSON file for describing Component's UI.

### JSON Structure Overview

The configuration JSON follows this primary structure:

- **`name`**: The name of the configuration (e.g., `"Text to Image"`).
- **`fields`**: An object containing grouped fields, commonly organized as `"main"` and `"advanced"`. Each group contains an array of field objects.

Each field object has several potential properties:

- **`id`**: A unique identifier for the field.
- **`name`**: Display name of the field.
- **`type`**: Specifies the component type, such as `select`, `prompt_editor`, `aspect_ratio`, `slider`, or `image_loader`.
- **`conf_file`**: (Optional) Specifies a configuration file (usually JSON) that contains additional options or settings for the component.
- **`display`**: Boolean that indicates whether the field should be visible to the user.
- **`default`**: (Optional) The field's default value, where applicable.
- **`constraints`**: (Optional) An object that defines minimum, maximum, and step values for components like `slider`.

### UI Component Types

### `select`

The `select` component provides a dropdown menu for users to choose from a list of predefined options.

```json
{
  "id": "model",
  "name": "Model",
  "type": "select",
  "conf_file": "sd_models.json",
  "display": true
}
```

- `conf_file`: Refers to an external JSON file (e.g., sd_models.json) that defines the available options.
  > **Usage**: Primarily for selecting from a list of static options, such as models, samplers, or schedulers.

### `prompt_editor`

The `prompt_editor` component provides a textarea for users to enter text-based prompts.

```json
{
  "id": "prompt",
  "name": "Prompt",
  "type": "prompt_editor",
  "display": true
}
```

> **Usage**: Primarily for text prompts that will guide the model's generation, as in fields for "Prompt" and "Negative Prompt".

### `aspect_ratio`

The `aspect_ratio` component provides predefined aspect ratio options, usually loaded from a configuration file.

```json
{
  "id": "aspect_ratio",
  "name": "Aspect Ratio",
  "type": "aspect_ratio",
  "conf_file": "aspect_ratio.json",
  "display": true
}
```

- **`conf_file`**: Specifies a JSON file (e.g., `aspect_ratio.json`) that defines the possible aspect ratio options.

> **Usage**: Useful for choosing specific image dimensions, such as 16:9, 4:3, etc.

### `slider`

The `slider` component provides a range slider for numerical input.

```json
{
  "id": "steps",
  "name": "Steps",
  "type": "slider",
  "default": 20,
  "constraints": {
    "min": 1,
    "max": 60,
    "step": 20
  },
  "display": true
}
```

- **`default`**: Sets the default starting value for the slider.
- **`constraints`**: Defines the minimum, maximum, and step values for the slider.

> **Usage**: Best for parameters like "Steps" or "CFG" where a numeric value within a range is needed.

### `image_loader`

The `image_loader` component provides an interface for users to upload or select an image.

```json
{
  "name": "Select Image",
  "id": "image",
  "type": "image_loader",
  "display": true
}
```

> **Usage**: Primarily for allowing users to load images into the application.

## Server Setup

Clone the repo, cd into the directory, and run the following command:

```bash
cd ~
git clone https://github.com/stakeordie/emprops_component_library.git
cd emprops_component_library/server_scripts
./basic.sh && source ~/.bashrc


eval "docker buildx build $(sed 's/^/--build-arg /' ../global/.env) --builder cloud-emprops-comfy-servers --platform linux/amd64 -t emprops/comfy-basic:v1 --output type=cacheonly --push ."
```
