"""

    Provenance class to create provenance metadata

"""

import secrets

PROVENANCE_DEP = 'dep'
PROVENANCE_ACTIVITY_TYPE_PUBLISH = 'publish'
PROVENANCE_ACTIVITY_TYPE_PUBLISH = 'import'
PROVENANCE_ACTIVITY_TYPE_OPERATION = 'operation'

PROVENANCE_AGENT_TYPE_ACCOUNT = 'account'


def create_publish(agent_id, activity_id=None):
    if activity_id is None:
        activity_id = secrets.token_hex(32)

    return {
        'prefix': create_prefix(),
        'activity': create_activity(activity_id, PROVENANCE_ACTIVITY_TYPE_PUBLISH),
        'entity': add_asset_entity('this'),
        'agent': create_agent(agent_id, PROVENANCE_AGENT_TYPE_ACCOUNT),
        'wasAssociatedWith': create_associated_with(agent_id, activity_id),
        'wasGeneratedBy': create_generated_by(activity_id)
    }


def create_invoke(activity_id, agent_id, asset_list, inputs_text, outputs_text):
    entities = add_asset_entity('this')
    for asset in asset_list:
        entities = add_asset_entity(asset, entities)

    dependencies = create_dependencies(inputs_text, outputs_text)
    return {
        'prefix': create_prefix(),
        'activity': create_activity(activity_id, PROVENANCE_ACTIVITY_TYPE_OPERATION, dependencies),
        'entity': entities,
        'agent': create_agent(agent_id, PROVENANCE_AGENT_TYPE_ACCOUNT),
        'wasAssociatedWith': create_associated_with(agent_id, activity_id),
        'wasDerivedFrom': create_derived_from(asset_list),
        'wasGeneratedBy': create_generated_by(activity_id)
    }


def create_prefix():
    return {
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'prov': 'http://www.w3.org/ns/prov#',
        PROVENANCE_DEP: 'http://dex.sg'
    }


def add_asset_entity(asset_id, entities=None):
    if entities is None:
        entities = {}
    entities[f'{PROVENANCE_DEP}:{asset_id}'] = {
        'prov:type': {
            '$': f'{PROVENANCE_DEP}:asset',
            'type': 'xsd:string'
        }
    }
    return entities


def create_activity(activity_id, activity_type, entries=None):
    items = {
        'prov:type': {
            '$': f'{PROVENANCE_DEP}:{activity_type}',
            'type': 'xsd:string'
        }
    }
    if entries:
        for name, value in entries.items():
            items[name] = value

    return {
        f'{PROVENANCE_DEP}:{activity_id}': items
    }


def create_agent(agent_id, agent_type):
    return {
        f'{PROVENANCE_DEP}:{agent_id}': {
            'prov:type': {
                '$': f'{PROVENANCE_DEP}:{agent_type}',
                'type': 'xsd:string'
            }
        }
    }


def create_associated_with(agent_id, activity_id):
    random_id = secrets.token_hex(32)
    return {
        f'_:{random_id}': {
            'prov:agent': agent_id,
            'prov:activity': activity_id
        }
    }


def create_generated_by(activity_id):
    entity_id = f'{PROVENANCE_DEP}:this'
    random_id = secrets.token_hex(32)
    return {
        f'_:{random_id}': {
            'prov:entity': entity_id,
            'prov:activity': activity_id
        }
    }


def create_derived_from(asset_list):
    entities = {}
    for asset in asset_list:
        random_id = secrets.token_hex(32)
        entities[f'_:{random_id}'] = {
            'prov:usedEntity': asset.asset_id,
            'prov:generatedEntity': f'{PROVENANCE_DEP}:this'
        }
    return entities


def create_dependencies(inputs_text, outputs_text):
    return {
        f'{PROVENANCE_DEP}:outputs': {
            '$': outputs_text,
            'type': 'xsd:string'
        },
        f'{PROVENANCE_DEP}:inputs': {
            '$': inputs_text,
            'type': 'xsd:string'
        }
    }
