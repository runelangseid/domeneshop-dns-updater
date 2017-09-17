# domeneshop-dns-updater

As domeneshop is missing an dyndns API, this small util provides an automated way to
update subdomains.

# 1. Run from host

## Install
```sh
pip install -r requirements.txt
```

## Configure
```sh
cp config.yml-default config.yml
```

Add username and password, id for domain (7 digits) and the domains to update.

## Run

For help
```sh
./domeneshop.py -h
```

Run this to update DNS
```sh
./domeneshop.py [config]
```
# 2. Run from docker

@todo

# Credit

A similar implementation in NodeJS https://github.com/maccyber/auto-add-dns-domeneshop
