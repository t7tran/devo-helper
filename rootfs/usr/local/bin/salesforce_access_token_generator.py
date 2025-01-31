#!/usr/bin/env python

import webbrowser
import requests
import json
import urllib.parse as urlparse
import click as click

def authorize_login_url(auth_site, authorization_url,  client_id, redirect_uri):
    """
    URL to login through Salesforce
    :return: Redirect URL for Oauth2 authentication
    """

    return "{site}{authorize_url}" \
            "?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&prompt=login".format(
                site=auth_site,
                authorize_url=authorization_url,
                client_id=client_id,
                redirect_uri=urlparse.quote(redirect_uri)
            )

def get_access_token(redirect_uri, code, client_id, client_secret, auth_site, token_url):
    """
    Sets the body of the POST request
    :return: POST response
    """
    body = {
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = _request_token(body, auth_site, token_url)

    return response

def _request_token(data, auth_site, token_url):
    """
    Sends a POST request to Salesforce to authenticate credentials
    :param data: body of the POST request
    :return: POST response
    """
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(
        "{site}{token_url}".format(
            site=auth_site,
            token_url=token_url
        ),
        data=data,
        headers=headers
    )

    return response    

@click.command()
@click.option('--client_id', 
              'client_id', 
              help='Salesforce OAuth client ID', 
              required=True
              )
@click.option('--client_secret', 
              'client_secret', 
              help='Salesforce OAuth client secret', 
              required=True
              )
@click.option('--redirect_uri', 
              'redirect_uri', 
              help='Salesforce OAuth client redirect URI',
              required=True
              )
@click.option('--domain', 
              'salesforce_domain', 
              help='Salesforce domain, default: \"login\"'
              )

def cli(client_id, client_secret, redirect_uri, salesforce_domain):
    
    auth_site = "https://{salesforce_domain}.salesforce.com".format(salesforce_domain=(salesforce_domain if salesforce_domain else "login"))
    authorization_url = '/services/oauth2/authorize'
    token_url = '/services/oauth2/token'

    oauth_redirect = authorize_login_url(auth_site, authorization_url, client_id, redirect_uri)
    #webbrowser.open(oauth_redirect)

    # Sample: https://www.enter-url-here.com/?code=aPrxILdoIUt7J4zOidrhMRBqhwgwsTAh7expE53Qeh2KhelBXIzspDZ8nPV8t7uADsOHeWXz5g%3D%3D
    callback_url = input('\nOpen the URL below in your browser:\n' + oauth_redirect + '\nCopy-Paste your callback URL and press ENTER\n')
    print("\n")

    # Extract the code from the URL
    extract_code = urlparse.urlparse(callback_url)
    code = urlparse.parse_qs(extract_code.query)['code'][0]
    # print(code)
    # Sample: aPrxILdoIUt7J4zOidrhMRBqhwgwsTAh7expE53Qeh2KhelBXIzspDZ8nPV8t7uADsOHeWXz5g==

    # Retrieve access_token from Salesforce by sending authenticated code
    sf_authentication = get_access_token(redirect_uri, code, client_id, client_secret, auth_site, token_url)

    print("Access Token JSON:\n")
    print(json.dumps(sf_authentication.json()))
    print("\n")
 
    # with open("access_token.json", "w") as f:
    #     f.write(json.dumps(sf_authentication.json()))

    # print("\"access_token.json\" file has been generated. Please, check the folder")


if __name__ == "__main__":
    cli()
