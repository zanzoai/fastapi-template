# fastapi-template

### Generate evironment for the project
```python3 -m venv venv```
### Enable the Environment
```source venv/bin/activate
# For PowerShell
~ .\venv\Scripts\Active
```
### If cloned install requirements
```pip install -r requirements.txt```
### Run the server locally
```uvicorn main:app --reload```
### Lock the downloaded packages once installed
```pip freeze > requirements.txt```