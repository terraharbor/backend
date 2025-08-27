# backend
Backend of the TerraHarbor application written in Python and using FastAPI

## Test in Local

In order to locally test this repository, clone this repo locally and the [infrastructure](https://github.com/terraharbor/infrastructure). Comment the services you don't want to test or you did not download (ex: frontend). <br>
Execute
```zsh
docker-compose -f docker-compose-local.yaml
```
in `infrastructure/docker-compose/ in order to start the containers.<br>
when the app is running, visit `http://localhost:8000/docs/<br>
This page displays forms allowing to test the different endpoints.
