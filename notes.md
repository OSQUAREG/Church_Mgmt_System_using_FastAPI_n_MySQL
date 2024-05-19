# Application

## Hashing Password in terminal

1. In the project folder, use command: `python` and press enter.
2. ```
   from api.authentication.services.auth import AuthService  
   AuthService().get_password_hash("<your password>")
   ```

## Create your Secret Key in three steps

1. Type `python` and enter
2. Type `import secrets` and enter
3. Type `secrets.token_hex(32)` and enter

# Postman

## Setting JWT Token as Env Variable

### Login Route => test code:

var jsonData = pm.response.json();

var token = jsonData.access_token;

pm.globals.set("access_token", token);

pm.environment.set("access_token", token);

### Select Church Level => test code:

var jsonData = pm.response.json();

var token = jsonData.access_token;

pm.globals.unset("access_token");

pm.environment.unset("access_token");

pm.globals.set("access_token", token);

pm.environment.set("access_token", token);

# Client App

```
py --list-paths  # To see the installed Python versions
set npm_config_python=C:\path\to\python.exe  # CMD
$Env:npm_config_python="C:\path\to\python.exe"  # PowerShell
```
