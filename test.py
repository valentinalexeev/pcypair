import pcypair
import json

data = pcypair.getMarkersDataParsed("NICRES")
print(json.dumps(data, indent=4))

for param in data["data"].keys():
	print(param + " = " + data["data"][param]["value"])

print(data["data"]["CO"]["value"])
