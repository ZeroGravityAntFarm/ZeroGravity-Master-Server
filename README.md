# ZeroGravity-Master-Server
A lightweight Eldewrito Master Server implemented in python. 


## Usage:


#### Build:
```
sudo docker build . -t masterserver
```

#### Launch
```
docker run --name edmaster -p 80:8080 -d masterserver
```

##### Launch with Traefik
Set proxy variable to True if behind a reverse proxy. Currently needs some modification to work with traefik, see https://github.com/ZeroGravityAntFarm/ZeroGravity-Master-Server/issues/1
```
docker run --name edmaster -p 80:8080 --label "traefik.frontend.rule=Host:master.yourdomain.com" -d masterserver
```
