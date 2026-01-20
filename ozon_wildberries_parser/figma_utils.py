# figma_utils.py

import requests
from configs.config import FIGMA_HEADERS


def extract_node_ids(node: dict, result: dict | None = None) -> dict:
    """
    Рекурсивно обходит дерево Figma и собирает {layer_name: node_id}
    """
    if result is None:
        result = {}

    if 'id' in node and 'name' in node:
        result[node['name'].strip()] = node['id']

    for child in node.get('children', []):
        extract_node_ids(child, result)

    return result


def get_figma_nodes(file_key: str) -> dict:
    """
    Получает все слои Figma файла и их node_id

    Возвращает:
        dict: {layer_name: node_id}
    """
    url = f"https://api.figma.com/v1/files/{file_key}"
    response = requests.get(url, headers=FIGMA_HEADERS, timeout=15)
    response.raise_for_status()

    data = response.json()

    return extract_node_ids(data['document'])


if __name__ == "__main__":
    FILE_KEY = "HTIHXlH98E6OuMIixvArtp"
    nodes = get_figma_nodes(FILE_KEY)

    for name, node_id in nodes.items():
        print(f"{name}: {node_id}")
