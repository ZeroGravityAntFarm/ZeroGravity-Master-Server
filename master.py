import requests
import socket
import json
from datetime import datetime
from flask import Flask, request, make_response
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

#=============<CONFIG>==================
proxy=False
hostport=8080
KillTime=5000
#=============</CONFIG>=================

ServerList = []

class ohai(Resource):
    def get(self):
        banner = 'ZGAFv0.1'
        
        response = make_response(banner, 200)
        response.mimetype = "text/plain"

        return banner

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
                result: {
                    code: 5,
                    msg: "Invalid IP address."
                }
            }

        #Grab shutdown flag and validate as boolean 
        ShutdownFlag = request.args.get('shutdown')
        ValidParam = [1, 0, "true", "false"]
        if ShutdownFlag not in ValidParam:
            return {
                "result": {
                    "code": 1,
                    "msg": "Invalid parameters, valid parameters are 'port' (int) and 'shutdown' (bool)"
                }
            }
        
        #Grab port query parameter and validate as a real port number
        GameJsonPort = request.args.get('port')
        if not 1 <= int(GameJsonPort) <= 65535:
            return {
                "result": {
                    "code": 4,
                    "msg": "Invalid port. A valid port is in the range 1024-65535."
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=hostport, debug=True)
