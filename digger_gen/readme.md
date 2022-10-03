# Digger Gen

The `digger_gen` filter allows you to quickly and easily generate the `minecraft:digger` component, to satisfy your tool-building needs.

## Using the Filter

1. Install via `regolith install digger_gen`
2. Place the `digger_gen` filter into your profile

## Configuration

Configuration for this filter is contained within `data/digger_gen/dig_types.json

The structure looks like this:

```json
{
	"wood": [
		"minecraft:chest",
		{
			"tags": "q.any_tag('wood', 'pumpkin', 'plant')"
		}
	],
	"example_two": [
		"example:custom_block"
	]
}
```