import yaml


def load_paths_from_yaml(yaml_file_path):
    """import paths from yaml file."""
    with open(yaml_file_path, 'r') as file:
        paths_data = yaml.safe_load(file)
    return paths_data


def replace_base_path(data, base_path):
    """Replace '{base_path}' placeholders with the actual base_path."""
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = replace_base_path(value, base_path)
    elif isinstance(data, str):
        data = data.format(base_path=base_path)
    elif isinstance(data, list):
        data = [replace_base_path(item, base_path) for item in data]
    return data
