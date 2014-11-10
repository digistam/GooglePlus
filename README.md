Google Plus API
===============

[https://developers.google.com/+/api/](https://developers.google.com/+/api/)

**Acquiring API Key**

[https://developers.google.com/+/api/oauth](https://developers.google.com/+/api/oauth) 

**To create an API key**

* Go to the [Google Developers Console](https://console.developers.google.com/project)
* Create or select a project
* In the sidebar on the left, select APIs & auth.
* In the displayed list of APIs, find the Google+ API and set its status to *ON*
* In the sidebar on the left, select Credentials
* Create an API key by clicking *Create New Key* 
* Select the appropriate kind of key: Server key, Browser key, Android key, or iOS key
* click Create

create a file named client_secrets.json, containing:

```
 {
  "installed": {
  "client_id": "*****.apps.googleusercontent.com",   
  "client_secret":"*****",
  "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}
```

