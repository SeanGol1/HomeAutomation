import json
from website import create_app

configdata = ''
with open("config.json", "r") as jsonfile:
    configdata = json.load(jsonfile)

app = create_app()

if __name__ == '__main__':    app.run(host=configdata['Pi_IP'], port=configdata['Pi_port'])#app.run(debug=True)