# Dokku Dashboard
Simple, open-source UI for Dokku powered by React and FastAPI.

# Note: work in progress
This is a work in progress. The project will be an open-source UI for dokku. Learn more at [indiehost.io](https://indiehost.io) and follow [@stubgreen](https://twitter.com/stubgreen) on X for updates.

# Steps to deploy

Pre-req: must install and start dokku-daemon following these steps: https://github.com/dokku/dokku-daemon

Then run the following commands to deploy dokku-api to your server running dokku

```
# create the app
dokku apps:create dokku-api

# add and mount persistent storage dir for the app
dokku storage:ensure-directory dokku-api
dokku storage:mount dokku-api /var/lib/dokku/storage/dokku-api:/app/data

# mount dokku-daemon to the app
dokku storage:mount dokku-api /var/run/dokku-daemon/dokku-daemon.sock:/var/run/dokku-daemon/dokku-daemon.sock

# set required env vars
dokku config:set dokku-api DATABASE_URL=sqlite:////app/data/dokku-api.db
dokku config:set dokku-api DOKKU_API_URL={YOUR_URL_HERE} # e.g. https://dokku-api.37.27.221.172.sslip.io

# deploy the api from git repo
# will automatically build and deploy the dokku-api subdirectory
dokku git:sync --build-if-changes dokku-api https://github.com/indiehost/dokku-dashboard.git

```
