# backend
Backend of the TerraHarbor application written in Python and using FastAPI

## Test in Local

In order to locally test this repository, clone this repo locally and the [infrastructure](https://github.com/terraharbor/infrastructure). Comment the services you don't want to test or you did not download (ex: frontend). <br>
Execute
```zsh
docker-compose -f docker-compose-local.yaml build && docker-compose -f docker-compose-local.yaml up
```
in `infrastructure/docker-compose/ in order to start the containers.<br>
when the app is running, visit `http://localhost:8000/docs/<br>
This page displays forms allowing to test the different endpoints.

### Unit Tests

In order to execute the unit tests, create a virtual env and use it:

```zsh
python3 -m venv test-venv
source ./test-venv/bin/activate
```

Then install the dependencies:

```zsh
pip install pytest
pip install -r requirements.txt
```

Then you can execute the tests:

```zsh
pytest
```

#### Add a unit test

Go to `/tests/python/unit_tests/`.

To add a test, you can add a file or go to an existing file, and create a new function. The function will be the test, and the function's name must be explicit about what is tested, and what should be returned. Ex: `test_hello_world__should_return_true`. The end of the test must be an `assert <condition>` and not a return.

A unit test is supposed to be executing within a fraction of second, and only test the function that is tested's behavior. Meaning that another non-default function call should be mocked, in order to control its output, and test the sole tested function behavior. Especially if the other function makes call requests.

**Basic Example Format:**

```python
def test_hello_world__should_return_true():
  expected_result: str = "hello world"
  output: str = hello_world()
  assert expected_result == output
```

## Endpoints

There are currently several basic endpoints:

> doc format: `METHOD`:`ENDPOINT`

### Not Authenticated endpoimts

* `POST`:`/register`: registers a user thanks to a username and a password. Returns the creds for debug reasons for the moment.

#### Request example
```zsh
curl -X 'POST' \
  'http://localhost:8000/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user&password=password'
```
**Returns:**

```json
{
  "message": "User registered successfully",
  "user": {
    "username": "user",
    "disabled": true,
    "sha512_hash": "35b104625d3fa93a9bb2ea089a300434c902ae51a33b838242a3aa0eb6ea3a6e86c973c1a09088b7489ec39adf21ce3baf9f1aaaf05a265f01882fba4d904f06",
    "salt": "28ba555d23d8e8ab3b16f8bc9efd1cb9f413e61a450560028b0e9c3297ff39d3",
    "token": null,
    "token_validity": null
  }
}
```
the password hash is for test purposes. It's temporary.

* `POST`:`/token`: Send a username and a password to this endpoints, and this user's token will be returned. A new one can be created here. Validity for one hour (user token for the frontend).
* `POST`:`/login`: Same as /token. It's an alias. No more utility.

#### Request example

```zsh
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user&password=password'
```

**Returns:**

```json
{
  "access_token": "416bc3a7fb0ed25cbb2c526c15a5f1cc8ef39c154dc52acd47dcd4b68b5ce4cf",
  "token_type": "bearer"
}
```

### Authenticated Endpoints

* `LOCK`:`/state/{project}/{state}`: Locks a state file.
* `UNLOCK`:`/state/{project}/{state}`: Unlocks a state file.

#### Request example (with LOCK)

```zsh
curl -X LOCK http://localhost:8000/state/foo_project/state.tfstate \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

* `GET`:`/state/{project}/{state}`: Returns a state file. TODO: Won't work if the state file was locked by anyone else.

#### Request Example

```zsh
curl -X GET http://localhost:8000/state/foo_project/state.tfstate?version=1 \
  -H "Authorization: Bearer 3f5a358bf3da167a82e621f23a124751a902dd15541efb4aa551abeec96ee21f"
```

You don't need the "?version=1". It is used only to choose what version of the state we want to get.

* `POST`:`/state/{project}/{state}`: Uploads a state.

#### Request Example
```zsh
curl -X POST http://localhost:8000/state/foo_project/state.tfstate \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a" \
  --data-binary @state_v1.tfstate
```

* `DELETE`:`/state/{project}/{state}`: Deletes a state.

#### Request Example

```zsh
curl -X DELETE http://localhost:8000/state/foo_project/state.tfstate\?version=1 \
  -H "Authorization: Bearer 3f5a358bf3da167a82e621f23a124751a902dd15541efb4aa551abeec96ee21f"
```

* `GET`:`/me`: Returns current user session (must be authenticated).

#### Request Example
```zsh
curl -X GET http://localhost:8000/me \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

* `POST`:`/logout/`: Logs out user

#### Request Example

```zsh
curl -X POST http://localhost:8000/logout \
    -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

Please note that for the moment, no organization nor project notions have been implemented.