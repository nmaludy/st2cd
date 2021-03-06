#!/usr/bin/env python

"""
Python script which submits data to installer and triggers installer setup
aka puppet run
"""

import time
import httplib
import argparse

import requests


DEFAULT_PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAtwTLsIVC5pMfga9DOByva+5uZ3bArmaJtB8ArtfUCsq7TmC6
cyLU3CPQfWGPmRyxiNBQ5PtC4TdB2bI5NpA0LUReqhhOT+ceXAUj4cSeXgVz3AoW
Wg4JBy0xvsZsq3t83ukVEyCiv2LEWsOa1AjnDZJthmTbkLkCOUytb+t7BR+XIpcP
wAMCaSVwdM7SHkPIhUfOQmb50w0VsVDvHY1m2D8Y5LiuxFfLyA+3xZI9bzapRtMK
TkdBI7TyWJUd+jdHhwmF2pL7QD2rKlxHWurCaN6pRMhfDJR7cHImpEqVLeuDH1bM
6dnQ8rdJXdqxNCTB6J65g8ydE0/jvWBz1OCE5QIDAQABAoIBAFgy4HKGFhKGLjXS
H4PIFyXddqk3ym2BjrUWB7861b4JqzB/Xvsjew9H1y7FOG2iLVBwi7t99uIQPhTK
VdYcsnhqLXCtW/gXukLAW2Vu2p8W45nT5qepgeJKfmGgwDf3v9qw2u4n2SaAU34m
K9QpIighO9T7f/CDqDWy5RY9lkCGASxrEbEvYCRUglpMKIjP3+YV1C+8R442WpTB
wQC3gzUSmoA8HmeTfx3jBKb322chZJ+pRflI2Jmew1C7OWUI5CEEAFmpZfPXKByn
s+5GIm0yLnXp3ifYyvnv0pJgASyUhBaiIpLxh0Lm5xZjQbmiiJXn3Sw8IHLPA24X
EwftAxUCgYEAvGShv1npb1MGhl16rJ3M9LxGs+yam9+yrekJ6RrearNIT+cE7yqk
cNnSC4nETf48koGpywt+A1w5g9SZxlYOn3MtbiGmCCfWUJ4u2sMz3GcFtSg/Wamr
C2aREYyp6n4gJnXR81U0sDQ1UX4udWEgxSY/zuA1NM7WO6PlhjPSIVcCgYEA+LJu
Gmvg8BnR21coB2fmmzEn3J1FGyXsxTcJwUdwe6pcHfScV6HKc1ud/NHiU3kTek6L
Ue6FftTJ5QpFfdlcoOWRREP4tseIcwlD1N0U9WWp0GOil/7CWHxfceqUeK+7Z5hw
RrKs8Kh5qw3pn/IjmwjFyNA+LuFSze+NxdjB+iMCgYBgJ9TOv+t/oJbR+eBlPl2g
BIDp0LfRG0otraYbTlV7jGo6LiW8lL09xE+LCBQj4sGz3W52bjUxLd9FRDwAmWf5
RmZHsfD2dK7UkwhDLCLKOeMV5ab/8rOUrBMbK/qF7z4lozk3w6OS0/Lq10aLLrn1
JmKnCpTdkTyTUEIUT1rPHQKBgEKbBwHsgoHLaHjmDsJtAUXvFE3xkOCEd7UZ2HL7
PxTfu2wKZxTRL/dVQirDy2mvs5e+EXIP/5DITIobBiF+ZWByG0W9Lo9FQTYN9Sy9
SS+v2psFFDbA9Cveo3FO8hSgfABywx8sG0UY2f0F7Nv5ba/H2bC+lOjZT+P3lHC4
bLshAoGAMvb3qbMM+a07HerbYAyalk4FQvI2jyjxOjCeRq7MfKuWx+REvLgAFl2b
nhfve6kCARIexb2KEJ6CL7hVShb+8vRe/MiPfAVMjLnIAsiuqPOhKbAmb8VnSNro
pijm5DDq2EQk3QLA4Lo/iZz3s1Qbw/pJM21w8jY1nvUdb5UmaMQ=
-----END RSA PRIVATE KEY-----
""".strip()

DEFAULT_PUBLIC_KEY = """
AAAAB3NzaC1yc2EAAAADAQABAAABAQC3BMuwhULmkx+Br0M4HK9r7m5ndsCuZom0HwCu19QKyrtOYLpzItTcI9B9YY+ZHLGI0FDk+0LhN0HZsjk2kDQtRF6qGE5P5x5cBSPhxJ5eBXPcChZaDgkHLTG+xmyre3ze6RUTIKK/YsRaw5rUCOcNkm2GZNuQuQI5TK1v63sFH5cilw/AAwJpJXB0ztIeQ8iFR85CZvnTDRWxUO8djWbYPxjkuK7EV8vID7fFkj1vNqlG0wpOR0EjtPJYlR36N0eHCYXakvtAPasqXEda6sJo3qlEyF8MlHtwciakSpUt64MfVszp2dDyt0ld2rE0JMHonrmDzJ0TT+O9YHPU4ITl
""".strip()

HUBOT_PASSWORD = 'fyeahubot'


def run_installer(installer_url, hostname, admin_username, system_username,
                  enterprise_key):

    # 1. Hit "data_save" to save username and hubot password
    params = {'hostname': hostname, 'password': HUBOT_PASSWORD}
    url = '%sdata_save' % (installer_url)

    print('Sending params %s to %s' % (params, url))
    response = requests.get(url=url, params=params, verify=False)
    print('Response status: %s' % (response.status_code))

    if response.status_code not in [httplib.OK, httplib.NO_CONTENT]:
        print('Response body: %s' % (response.text))
        raise Exception('GET to /data_save failed')

    # 2. Hit "root" endpoint with all the necessary data
    data = {}
    data['hostname'] = hostname

    # Admin account info
    # Note: We use static password
    data['admin-username'] = admin_username
    data['password-1'] = 'StackStorm1'
    data['password-1'] = 'StackStorm2'

    # System account info
    data['username'] = system_username

    # We use static public and private key for testing
    data['sshgen'] = '1'
    data['gen-public'] = DEFAULT_PUBLIC_KEY
    data['gen-private'] = DEFAULT_PRIVATE_KEY

    # We use self signed cert generated by installer
    data['selfsigned'] = '1'

    # ChatOps / Hubot info
    # Note: We use invalid / random token
    data['check-chatops'] = '1'
    data['chatops'] = 'slack'
    data['slack-token'] = 'INVALID-YES'
    data['hubot-password'] = HUBOT_PASSWORD

    if enterprise_key:
        data['ch-enterprise'] = '1'
        data['enterprise'] = enterprise_key

    url = installer_url
    print('Sending data %s to %s' % (data, url))
    params = {'skip_lock_check': 'true'}
    response = requests.post(url=installer_url, params=params, data=data,
                             verify=False, allow_redirects=True)
    print('Response status: %s' % (response.status_code))

    if response.status_code != httplib.OK:
        print('Response body: %s' % (response.text))
        raise Exception('POST to /setup/ failed')

    # Note: We manually poll "/puppet" endpoint here since that is what
    # the client does and puppet is run lazily so this endpoint actually
    # triggers the puppet run
    puppet_url = '%spuppet' % (installer_url)
    print('Polling /puppet/...')
    while True:

        try:
            response = requests.get(url=puppet_url, params={'line': 1000},
                                    verify=False)
        except requests.exceptions.ConnectionError:
            # This indicates the cert change after the sucessful run which
            # indicates completion
            break

        text = response.text

        if '--terminate--' in text:
            break

        print('Sleeping between polls...')
        time.sleep(5)

    print('All done!')


def main(installer_url, hostname, admin_username, system_username,
         enterprise_key):
    # Note: Our Nginx setup makes trailing slash mandatory
    if not installer_url.endswith('/'):
        installer_url = installer_url + '/'

    run_installer(installer_url=installer_url,
                  hostname=hostname, admin_username=admin_username,
                  system_username=system_username,
                  enterprise_key=enterprise_key)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Submit data to installer')

    parser.add_argument('--installer_url', default=None, required=True,
                        help='Installer URL')

    parser.add_argument('--hostname', default='localhost',
                        help='Server hostname / IP')

    parser.add_argument('--admin_username', default='admin',
                        help='Admin username')
    parser.add_argument('--system_username', default='stanley',
                        help='System account username')

    parser.add_argument('--enterprise_key', default=None,
                        help='Enterprise license key')
    args = parser.parse_args()

    main(installer_url=args.installer_url,
         hostname=args.hostname,
         admin_username=args.admin_username,
         system_username=args.system_username,
         enterprise_key=args.enterprise_key)
