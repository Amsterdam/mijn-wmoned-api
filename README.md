# WMO Ned API Client

## Introduction

A REST API which discloses the WMO Ned REST API.

Swagger is exposed on '/api/wmo' and provides all required API info.

Request roundtrip:

       +--------------+
       |              |
       |   Frontend   |
       |              |
       +--------------+
           ^      |
           |      | req       +------------------------+
           |      |           |                        |
           |      +---------> |   TMA                  |
     res   |                  |   (adds a SAML token   |
           |                  |   holding the BSN)     |
           |      +---------+ |                        |
           |      |           +------------------------+
           |      v
       +----------------------------------+
       |                                  |
       |   API                            |
       |   (Get voorzieningen from the    |
       |   WMO Ned API)                   |
       |                                  |
       +----------------------------------+
           ^      |
           |      |
           |      |
     res   |      |   req
           |      |
           |      |
           |      v
       +----------------------+
       |                      |
       |   WMO Ned API        |
       |   (responds with     |
       |   voorzieningen)     |
       |                      |
       +----------------------+

### Requirements

- Access to the Amsterdam secure Gitlab
- Access to Rattic

### Local development

1. Clone repo and `cd` in
2. Create a virtual env and activate
3. Run `pip install -r app/requirements.txt`
4. Set environment variables:
   - `export FLASK_APP=app/api/server.py`
   - `export TMA_CERTIFICATE=<path to certificate>` (rattic: "TMA certificaat local") you can put this line your shell rc file
   - `export WMO_NED_API_KEY=<Find on Rattic -> WMO Ned API key>`
   - NOTE: Make sure you wrap the key in single quotes. There are some chars in
     the key which can be seen as commands.
5. Run `flask run`

### Deployment

1. Run `docker-compose up --build`
2. Get '/status/health' to check if the API is up and running

### Testing

1. Clone repo and `cd` in
2. Create a virtual env and activate
3. Run `pip install -r app/requirements.txt`
4. `export TMA_CERTIFICATE=<path to certificate>` (rattic: "TMA certificaat local") you can put this line your shell rc file
5. Run `python -m unittest`

### Updating dependencies
Direct dependencies are specified in `requirements-root.txt`. These should not have pinned a version (except when needed)

* `pip install -r requirements-root.txt`
* `pip freeze > requirements.txt`
* Add back at the top in requirements.txt
 `--extra-index-url https://nexus.secure.amsterdam.nl/repository/pypi-hosted/simple`
