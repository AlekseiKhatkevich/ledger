**Keycloak auth:**

 - Fetch openID token, an example:

```shell
curl --location 'http://localhost:8000/user/login' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'grant_type=password' \
--data-urlencode 'client_id=fastapi-keycloak' \
--data-urlencode 'username=qwerty12345@disroot.org' \
--data-urlencode 'password=1q2w3e' \
--data-urlencode 'scope=openid'
```