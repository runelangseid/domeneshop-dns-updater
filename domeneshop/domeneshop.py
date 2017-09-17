# -*- coding: utf-8 -*-
import requests
import yaml
from bs4 import BeautifulSoup
import re
import dns.resolver

__author__ = 'runelangseid'

# @todo Add support for advanced options, like ttl & type
# @todo Add support for Docker, Docker-compose

class Domeneshop(object):
    verbose = False
    # @todo Simplify headers
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.8,nb;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://domeneshop.no",
        "Pragma": "no-cache",
        "Referer": "https://domeneshop.no",
        "Upgrade-Insecure-Requests": "1",
    }

    config = {}
    cookies = {}

    ip = ''

    def __init__(self, config='config.yml', verbose=False):
        """
        Instance Domeneshop object
        """

        self.ip = self.get_ip()
        self.verbose = verbose

        with open(config) as f:
            self.config = yaml.load(f)

    def login(self):
        """
        Login
        """
        data = [
            ('username', self.config['login']),
            ('password', self.config['password']),
        ]

        # Get cookie
        response = requests.get(self.config['domeneshop']['login'])
        self.cookies = dict(response.cookies)

        response = requests.post(
            self.config['domeneshop']['login'],
            data=data,
            headers=self.headers,
            cookies=self.cookies,
        );

        # Check if login was successful
        soup = BeautifulSoup(response.text)
        logout = soup.findAll('a', href=re.compile('^http.*/logout'))
        if not logout:
            if self.verbose:
                print('Could not log in. Exiting.')
            # @todo Throw exception
            return False

        if self.verbose:
            print('Login successful')

        return True

    def update_records(self):
        """
        Update dns records from config
        """
        for record in self.config['record']:
            self.update_record(record)

    # @todo Add support for top domains - eg example.com. Only www.example.com is supported
    # @todo Add support for setting ttl
    def update_record(self, record):
        """
        Update single dns record from config
        """
        if self.verbose:
            print('record', record)

        # check ip
        changed = self.changed_ip(record['domain'])
        if changed:
            print('Detected changed ip for %s' % record['domain'])

            # @todo Throw exception
            if not self.cookies:
                login = self.login()
                if not login:
                    return False
        else:
            print('No changed detected for %s' % record['domain'])
            return

        url = '%s?edit=dns&id=%s' % (self.config['domeneshop']['admin'], record['id'])

        response = requests.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
        );

        form = self._get_form(response, record)
        host = self._get_host(record)

        if not form:
            print('Problem accessing domain page.')
            return

        auth = form.find('input', {'name': 'auth'})['value']
        olddata = form.find('input', {'name': 'olddata'})['value']
        oldtype = form.find('input', {'name': 'oldtype'})['value']

        params = (
            ('id', record['id']),
            ('edit', 'dns'),
            ('advanced', '0'),
        )

        payload = [
            ('auth', auth),
            ('advanced', '0'),
            ('id', record['id']),
            ('edit', 'dns'),
            ('host', host),
            ('oldtype', oldtype),
            ('olddata', olddata),
            ('data', self.ip),
            ('modify.x', '7'),
            ('modify.y', '6'),
        ]

        if self.verbose:
            print('Payload for update', payload)

        requests.post(
            url,
            params=params,
            data=payload,
            headers=self.headers,
            cookies=self.cookies,
        );

        # Add check if update was successful with issuing a new request
        response = requests.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
        );

        form = self._get_form(response, record)

        if form:
            host_updated = form.find('input', {'name': 'host'})['value']
            if host == host_updated:
                print('- Updated successfully')
                return True

        print('- Whoops! Updated was not successful!')
        return False

    def changed_ip(self, domain):
        """
        Checks if DNS record refers to current IP address
        """
        ip = self.get_ip()

        # Basic A query the host's DNS
        for rdata in dns.resolver.query(domain, 'A'):
            if ip == rdata.address:
                return False

        return True

    @staticmethod
    def _get_host(record):
        host = record['domain'].split('.')[0]
        return host

    @staticmethod
    def _get_form(response, record):
        soup = BeautifulSoup(response.text)
        forms = soup.findAll('form')

        for form in forms:
            search = '^%s.*' % (record['domain'])
            tds = form.findAll('td', text=re.compile(search))
            if tds:
                return form

        return False

    @staticmethod
    def get_ip():
        ip = requests.get('https://api.ipify.org').text
        return ip
