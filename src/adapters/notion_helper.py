from typing import Dict, Any


def extract_property_value(properties: Dict, key: str) -> Any:
    """
    Extract a typed value from a Notion page's properties dict.
    Handles: title, rich_text, number, select, multi_select, checkbox, formula, relation.
    """
    prop = properties.get(key)
    if not prop:
        return None

    prop_type = prop.get('type')
    if not prop_type:
        if 'title' in prop: prop_type = 'title'
        elif 'rich_text' in prop: prop_type = 'rich_text'
        elif 'number' in prop: prop_type = 'number'
        elif 'select' in prop: prop_type = 'select'
        elif 'multi_select' in prop: prop_type = 'multi_select'
        elif 'checkbox' in prop: prop_type = 'checkbox'
        elif 'formula' in prop: prop_type = 'formula'
        elif 'relation' in prop: prop_type = 'relation'

    if prop_type == 'title':
        return prop['title'][0]['text']['content'] if prop['title'] else ""
    elif prop_type == 'rich_text':
        return prop['rich_text'][0]['text']['content'] if prop['rich_text'] else ""
    elif prop_type == 'number':
        return prop['number']
    elif prop_type == 'select':
        return prop['select']['name'] if prop['select'] else None
    elif prop_type == 'multi_select':
        return [item['name'] for item in prop['multi_select']]
    elif prop_type == 'checkbox':
        return prop['checkbox']
    elif prop_type == 'formula':
        if prop['formula']['type'] == 'number':
            return prop['formula']['number']
        elif prop['formula']['type'] == 'string':
            return prop['formula']['string']
    elif prop_type == 'relation':
        return [rel['id'] for rel in prop['relation']]

    return None
