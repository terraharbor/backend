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

## Endpoints

There are currently several basic endpoints:

> doc format: `METHOD`:`ENDPOINT` 

* `POST`:`/register`: registers a user thanks to a username and a password. Returns the creds for debug reasons for the moment.
* `POST`:`/token`: Send a username and a password to this endpoints, and this user's token will be returned. A new one can be created here. Validity for one hour (user token for the frontend).
* `LOCK`:`/state/{state}`: Locks a state file.
* `UNLOCK`:`/state/{state}`: Unlocks a state file.
* `GET`:`/state/{state}`: Returns a state file. TODO: Won't work if the state file was locked by anyone else.
* `POST`:`/state/{state}`: Uploads a state.
* `DELETE`:`/state/{state}`: Deletes a state.
* `GET`:`/me`: Returns current user session (must be authenticated).

Please note that for the moment, no organization nor project notions have been implemented.