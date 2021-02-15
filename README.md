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
```
docker run --name edmaster -p 80:8080 --label "traefik.frontend.rule=Host:master.yourdomain.com" -d masterserver
```
