# Dokku Dashboard
Simple, open-source UI for Dokku powered by React and FastAPI.

# Note: work in progress
This is a work in progress. The project will be an open-source UI for dokku. Learn more at [indiehost.io](https://indiehost.io) and follow [@stubgreen](https://twitter.com/stubgreen) on X for updates.

# Steps to deploy

## 1. Install dokku-daemon

Must install and start dokku-daemon following the steps below (or from https://github.com/dokku/dokku-daemon).

```
# ensure you have build essentials installed
sudo apt-get install build-essential

# clone and install dokku-daemon
git clone https://github.com/dokku/dokku-daemon
cd dokku-daemon
sudo make install

# start the daemon
systemctl start dokku-daemon
```

## 2. Deploy dokku-api

Run the following commands to deploy dokku-api to your server running dokku

```
# create the app
dokku apps:create dokku-api

# add and mount persistent storage dir for the app
dokku storage:ensure-directory dokku-api
dokku storage:mount dokku-api /var/lib/dokku/storage/dokku-api:/app/data

# mount dokku-daemon to the app
# NOTE: must install dokku-daemon first
dokku storage:mount dokku-api /var/run/dokku-daemon/dokku-daemon.sock:/var/run/dokku-daemon/dokku-daemon.sock

# set required env vars (dokku-api uses sqlite to store config)
dokku config:set dokku-api DATABASE_URL=sqlite:////app/data/dokku-api.db
dokku config:set dokku-api DOKKU_API_URL={YOUR_URL_HERE}

# Use the url for your dokku-app e.g. https://dokku-api.37.27.231.172.sslip.io

# set build directory
dokku builder:set dokku-api build-dir dokku-api

# clone and deploy api from git repo
# will automatically build and deploy the dokku-api subdirectory
dokku git:sync --build-if-changes dokku-api https://github.com/indiehost/dokku-dashboard.git

# optionally enable letsencrypt for https
dokku letsencrypt:enable dokku-api
```

## 3. Run dokku-ui
Now that the api is running, we can connect to it using dokku-ui.

```
# clone this repo locally
git clone https://github.com/indiehost/dokku-dashboard.git

# navigate to dokku-ui
cd dokku-dashboard/dokku-ui

# install npm packages
npm install

# start UI
npm run dev 
```

Lastly, set the `VITE_DOKKU_API_URL` in your .env or .env.local:

```
# use your dokku-api url from step 1, e.g. https://dokku-api.37.27.231.172.sslip.io
VITE_DOKKU_API_URL={YOUR_URL_HERE}
```
