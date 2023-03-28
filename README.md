Demo
====

TODO: Write better and a more thorough explanation of the demo.

* pip install .
* PYTHONPATH=src python -msso init
* PYTHONPATH=src python -msso add-user bob@example.com
  * Enter `secret` as password
* PYTHONPATH=src python -msso add-audience bob@example.com application-service-1
* In one terminal run:
  * python -muvicorn --app-dir=src sso.app:app --port 5000
* In another terminal run
  * FLASK_DEBUG=1 FLASK_APP=src/application-service/application.py flask run --port 5001
* In another terminal run
  * python src/application-client/client.py --client-id bob@example.com --client-secret secret


TODO
====

* pytest
* Docker compose file
* sqladmin
* write documentation and tutorial
* python-social integration
* SAML/OpenID Connect
* JavaScript example
* Ensure OpenAPI looks good