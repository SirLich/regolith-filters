"""
This filter allows you to quickly generate `minecraft:digger` component.
It's essentially a very narrow and single use template.
"""

from reticulator import *
import sys

def process_item(item: ItemFileBP, speed: int, dig_type: str):
    """ Takes in a single item, and injects the correct data """

    with open('./data/digger_gen/dig_types.json', 'r') as f:
        dig_types = json.load(f)
    
    component_data = {
        "use_efficiency": True,
        "destroy_speeds": [
            {
                "block": x,
                "speed": speed,
                "on_dig": {
                    "event": "gen:damage"
                }
            } for x in dig_types[dig_type]
        ]
    }

    item.add_component('minecraft:digger', component_data)

    # Last, we inject the event that will be used.
    event_data = {
        "damage": {
            "type": "none",
            "amount": 1,
            "target": "self"
        }
    }
    item.add_event("gen:damage", event_data)


def main():
    """ Entrypoint for the script """
    bp = BehaviorPack('./BP')

    for item in bp.items:
        item.get_component
        if item.jsonpath_exists('**/minecraft:digger'):
            print(f"Skipping '{item.identifier}' because it already contains 'minecraft:digger'.")
            continue

        if not item.jsonpath_exists('**/gen:digger'):
            continue # Skip if gen:digger doesn't exist
        
        gen_component = item.get_component('gen:digger')
        speed = gen_component.get_jsonpath('speed', 10)
        dig_type = gen_component.get_jsonpath('dig_type')
        gen_component.delete()

        process_item(item, speed, dig_type)

    # Last step is to save the project
    bp.save()

if __name__ == "__main__":
    main()