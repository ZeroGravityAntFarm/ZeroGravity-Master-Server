import requests
import socket
import json
import sys
from datetime import datetime
from collections import OrderedDict
from flask import Flask, request, make_response, jsonify, send_file
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS

#=============<CONFIG>==================
proxy=True
hostport=80
KillTime=300
banfile="banlist.json"
#=============</CONFIG>=================

app = Flask(__name__)
CORS(app)
api = Api(app)
ServerList = []



class ohai(Resource):
    #Simple healthcheck endpoint at the root url
    def get(self):
        banner = 'ZGAFv0.2'
        response = make_response(banner, 200)
        response.mimetype = "text/plain"

        return banner



class banlist(Resource):
    def get(self):
        #Check for existence of user agent header
        try:
            u_agent = request.headers.getlist("User-Agent")[0]
        except:
            return make_response("", 200)
       
        if proxy:
            IP = request.headers.getlist("X-Real-IP")[0]
        else:
            IP = request.remote_addr

        #Check for a valid ed server user agent, then quickly ping the game server api page for an extra layer of verification (could even go a step further and cross reference the json data with our master server api). 
        if u_agent == "ElDewrito/0.6.1":
            try:
                dew_request = requests.get('http://'+ IP + ':11775')
            except:
                return send_file("banlist.json")
                
            #If the game server api is up then return the banlist 
            if dew_request.status_code == 200:
                try:
                    banfile = json.load(open('banlist.json', 'r'), object_pairs_hook=OrderedDict)
                except:
                    return make_response("", 200)

                b_response = make_response(json.dumps(banfile, sort_keys=False), 200)
                b_response.mimetype = "application/json"

                return send_file("banlist.json")
                
            else:
                return send_file("banlist.json")
        else:
            return make_response("", 200)



class Announce(Resource):
    def get(self):
       
       #Proxy check, use x forwarder header for server ip
        if proxy:
            IP = request.headers.getlist("X-Forwarded-For")[0]
        else:
            IP = request.remote_addr

        #F your regex
        try:
            socket.inet_aton(IP)
        except:
            return {
                "result": {
                    "code": 5,
                    "msg": "🤡"
                }
            }


        #Validate server user agent
        try:
            userAgent = request.headers.get("User-Agent")
            
            if userAgent not in ("ElDewrito/0.6.1.0", "ElDewrito/0.5.1.1", "ElDewrito/0.7.0.0", "ElDewrito/0.7.1", "ElDewrito/0.7.2"):
                return {
                    "result": {
                        "code": 5,
                        "msg": "🤡"
                    }
                }
        
        except:
            return {
                "result": {
                    "code": 5,
                    "msg": "🤡"
                }
            }


        #Grab shutdown flag and validate as boolean 
        ShutdownFlag = request.args.get('shutdown')
        ValidParam = ["1", "0", "true", "false", None]
        if ShutdownFlag not in ValidParam:
            return {
                "result": {
                    "code": 1,
                    "msg": "🤡"
                }
            }
        
        #Grab port query parameter and validate as a real port number
        GameJsonPort = request.args.get('port')
        if not 1 <= int(GameJsonPort) <= 65535:
            return {
                "result": {
                    "code": 4,
                    "msg": "🤡"
                }
            }

        #Validate this is a real server
        try:
            resp = requests.get(url="http://" + IP + ":" + str(GameJsonPort), timeout=5)

        except:
             return {
                "result": {
                    "code": 1,
                    "msg": "🤡"
                }
            }

        if not resp:
             return {
                "result": {
                    "code": 1,
                    "msg": "🤡"
                }
            }

        #If the server sends a shutdown flag then we remove it from our db. No futher need to hit the game api.
        if ShutdownFlag == 1 or "true":
            for server in ServerList:
                if server[1] == IP:
                    ServerList.remove(server)

        #Add our new server to the server list
        DewritoServer = []
        DewritoServer.append(datetime.now())
        DewritoServer.append(IP)
        DewritoServer.append(GameJsonPort)

        #Find if our requesting server is in our master list. If so, update the entry.
        for server in ServerList:
            if DewritoServer[1] in server[1]:
                if DewritoServer[2] in server[2]:
                    index = ServerList.index(server)
                    ServerList[index] = DewritoServer
        else:
            ServerList.append(DewritoServer)

        return {
            "result": {
                "code": 0,
                "msg": "Added server to list"
            }
        }



class List(Resource):
    def get(self):
        MasterList = []
        
        #Find all servers in our list that are not outside the kill time then add them to a sperate list. 
        for server in ServerList:
            LifeTime = datetime.now() - server[0]
            if LifeTime.seconds < KillTime:
                ServerRecord = str(server[1]) + ":" + str(server[2])
                MasterList.append(ServerRecord)
        
        #Build our return data payload with the master server list. 
        data = {
            "listVersion": 1,
            "result": {
                    "code": 0,
                    "servers": MasterList,
                    "msg": "OK"
            },
            "cache": 30,
            "listVersion": 1
        }

        return data

api.add_resource(ohai, '/')
api.add_resource(Announce, '/announce')
api.add_resource(List, '/list')
api.add_resource(banlist, '/banlist')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=hostport)
