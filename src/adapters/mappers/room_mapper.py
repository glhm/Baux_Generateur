from typing import Dict
from src.domain.entities.room import Room
from src.adapters.notion_helper import extract_property_value


def map_rooms(raw_chambres) -> Dict[str, Room]:
    """Map raw Notion room/chambre data to a dict of Room entities keyed by Notion ID."""
    mapping = {}
    for item in raw_chambres.get('results', []):
        props = item['properties']
        r_id = item['id']

        builder = Room.Builder()\
            .with_name(extract_property_value(props, "{NOM_CHAMBRE}"))\
            .with_surface(extract_property_value(props, "{SURFACE_CHAMBRE}"))\
            .with_floor(extract_property_value(props, "{ETAGE}"))\
            .with_description(extract_property_value(props, "{DESCRIPTION_CHAMBRE}"))

        mapping[r_id] = builder.build()
    return mapping
