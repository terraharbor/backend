<h1 align="center" style="margin-top: 0px;">backend</h1>

<p align="center">Backend of the TerraHarbor application written in Python and using FastAPI</p>

<div align="center">

![Version](https://img.shields.io/github/v/release/terraharbor/backend?sort=semver&style=for-the-badge&label=Version&color=%2325c2a0&link=https%3A%2F%2Fgithub.com%2Fterraharbor%2Fbackend%2Freleases) ![License](https://img.shields.io/github/license/terraharbor/backend?style=for-the-badge&logo=gplv3&label=License) ![Build](https://img.shields.io/github/actions/workflow/status/terraharbor/backend/docker-build.yaml?event=push&style=for-the-badge&logo=docker&label=Build&link=https%3A%2F%2Fgithub.com%2Fterraharbor%2Fbackend%2Factions%2Fworkflows%2Fdocker-build.yaml%3Fquery%3Devent%253Apush)

![Unit Tests](https://img.shields.io/github/actions/workflow/status/terraharbor/backend/python-unit-tests.yaml?event=push&style=for-the-badge&logo=python&label=Unit%20Tests&link=https%3A%2F%2Fgithub.com%2Fterraharbor%2Fbackend%2Factions%2Fworkflows%2Fpython-unit-tests.yaml%3Fquery%3Devent%253Apush) ![Terraform Tests](https://img.shields.io/github/actions/workflow/status/terraharbor/backend/terraform-tests.yaml?event=push&style=for-the-badge&logo=terraform&label=Terraform%20Tests&link=https%3A%2F%2Fgithub.com%2Fterraharbor%2Fbackend%2Factions%2Fworkflows%2Fterraform-tests.yaml%3Fquery%3Devent%253Apush)

</div>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Local Development](#local-development)
  - [Unit Tests](#unit-tests)
    - [Add a unit test](#add-a-unit-test)
- [Endpoints](#endpoints)
  - [Unauthenticated Endpoints](#unauthenticated-endpoints)
    - [Request example](#request-example)
    - [Request example](#request-example-1)
  - [Authenticated Endpoints](#authenticated-endpoints)
    - [Request example (with LOCK)](#request-example-with-lock)
    - [Request example](#request-example-2)
    - [Request example](#request-example-3)
    - [Request example](#request-example-4)
    - [Request example](#request-example-5)
    - [Request example](#request-example-6)
    - [Request example](#request-example-7)
    - [Request example](#request-example-8)
    - [Request example](#request-example-9)
    - [Request example](#request-example-10)
    - [Request example](#request-example-11)
    - [Request example](#request-example-12)

## Local Development

In order to locally test this repository, clone this repo locally and the [infrastructure](https://github.com/terraharbor/infrastructure). Comment the services you don't want to test or you did not download (ex: frontend). Then, go into `infrastructure/docker-compose/` and execute:

```bash
docker-compose -f docker-compose-local.yaml build && docker-compose -f docker-compose-local.yaml up
```

When the app is running, visit `http://localhost:8000/docs/`. This page displays forms allowing to test the different endpoints.

> [!TIP]
> The [*Running Docker Compose locally*](https://github.com/terraharbor/infrastructure?tab=readme-ov-file#running-docker-compose-locally) in the [`terraharbor/infrastructure`](https://github.com/terraharbor/infrastructure) repository provides more details on how to set up your local environment.

### Unit Tests

In order to execute the unit tests, create a virtual env and use it:

```bash
python3 -m venv test-venv
source ./test-venv/bin/activate
```

Then install the dependencies:

```bash
pip install pytest
pip install -r requirements.txt
```

Then you can execute the tests:

```bash
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

### Unauthenticated Endpoints

* `POST`:`/register`: registers a user thanks to a username and a password. Returns the creds for debug reasons for the moment.

#### Request example

```bash
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

The password hash is for test purposes. It's temporary.

* `POST`:`/token`: Send a username and a password to this endpoints, and this user's token will be returned. A new one can be created here. Validity for one hour (user token for the frontend).
* `POST`:`/login`: Same as `/token`. It's an alias. No more utility.

#### Request example

```bash
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

```bash
curl -X LOCK http://localhost:8000/state/foo_project/state.tfstate \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

* `GET`:`/state/{project}/{state}`: Returns a state file. TODO: Won't work if the state file was locked by anyone else.

#### Request example

```bash
curl -X GET http://localhost:8000/state/foo_project/state.tfstate?version=1 \
  -H "Authorization: Bearer 3f5a358bf3da167a82e621f23a124751a902dd15541efb4aa551abeec96ee21f"
```

You don't need the "?version=1". It is used only to choose what version of the state we want to get.

* `POST`:`/state/{project}/{state}`: Uploads a state.

#### Request example

```bash
curl -X POST http://localhost:8000/state/foo_project/state.tfstate \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a" \
  --data-binary @state_v1.tfstate
```

* `DELETE`:`/state/{project}/{state}`: Deletes a state.

#### Request example

```bash
curl -X DELETE http://localhost:8000/state/foo_project/state.tfstate\?version=1 \
  -H "Authorization: Bearer 3f5a358bf3da167a82e621f23a124751a902dd15541efb4aa551abeec96ee21f"
```

* `GET`:`/me`: Returns current user session (must be authenticated).

#### Request example

```bash
curl -X GET http://localhost:8000/me \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

* `POST`:`/logout`: Logs out user

#### Request example

```bash
curl -X POST http://localhost:8000/logout \
    -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

Please note that, for the moment, no organization nor project notions have been implemented.

* `GET`:`/token/project/{project_id}`: Generates a new token, if meeting permissions

#### Request example

```bash
curl -X GET http://localhost:8000/token/project/1 \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

* `DELETE`:`/token/{project_id}/{project_token}`: Deletes the provided token, if meeting permissions

#### Request example

```bash
curl -X DELETE http://localhost:8000/token/project/1/43o5u234ru23482354bvcew3424543ef923rfvd3rkdv3jcv0welrk94523fdset \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

* `GET`:`/state/{project_id}/{project_token}/canRead`: Gets whether the given token can read the data or not

#### Request example

```bash
curl -X GET http://localhost:8000/state/1/43o5u234ru23482354bvcew3424543ef923rfvd3rkdv3jcv0welrk94523fdset/canRead \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

* `GET`:`/state/{project_id}/{project_token}/canWrite`: Gets whether the given token can write the data or not

#### Request example

```bash
curl -X GET http://localhost:8000/state/1/43o5u234ru23482354bvcew3424543ef923rfvd3rkdv3jcv0welrk94523fdset/canWrite \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

* `GET`:`/teams/list`: Gets the teams the currently logged user has access to

#### Request example

```bash
curl -X GET http://localhost:8000/teams/list \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```

* `GET`:`/state/list`: Gets the projects the currently logged user has access to

#### Request example

```bash
curl -X GET http://localhost:8000/state/list \
  -H "Authorization: Bearer 87807c4be294bcd2ada8730fbfcf5e51a6742f3836650e5741f188d80e29a95a"
```
