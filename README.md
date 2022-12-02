# ZeroGravity-Master-Server
A lightweight Eldewrito Master Server and Banlist API implemented in python. Example banlist file provided.


## Usage:


#### Build:
```
sudo docker build . -t masterserver
```

#### Launch
```
docker run --name edmaster -p 80:8080 -d masterserver
```

#### View Flask Requests
```
 sudo docker logs masterserver
 ```

#### Routes
```
/list
```
```
/announce
```
```
/banlist
```
##### Launch with Traefik
Set proxy variable to True if behind a reverse proxy. Currently needs some modification to work with traefik, see https://github.com/ZeroGravityAntFarm/ZeroGravity-Master-Server/issues/1
```
docker run --name edmaster -p 80:8080 --label "traefik.http.routers.$name.rule=Host(\`$domain\`)" -d masterserver
```
