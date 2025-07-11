import json
from website import create_app

configdata = ''
with open("config.json", "r") as jsonfile:
    configdata = json.load(jsonfile)

app = create_app()

if __name__ == '__main__':    app.run ( host='192.168.0.13', port='5001')#app.run(debug=True)