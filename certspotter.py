#!/usr/bin/python
import sys, json, argparse
from subprocess import Popen, PIPE

# arguments and usage
parser = argparse.ArgumentParser(description='Domain recon tool that leverages the Cert Spotter API', usage='%(prog)s domain')
parser.add_argument('domain', help="Extract domains for the given domain and all sub-domains")
args = parser.parse_args()

# fetch cert(s) for domain. returns json
obj = Popen(['curl', '-s', 'https://certspotter.com/api/v0/certs?domain=' + args.domain], stdin=PIPE, stdout=PIPE, stderr=PIPE)
output, err = obj.communicate("")
rc = obj.returncode

# decode json
loaded = json.loads(output)

dns_names = []
domainlist = []
i = 0

while i < len(loaded):
    # iterate certs and extract the dns_names node from each
    dns_names.append(loaded[i]['dns_names'])

    # each dns_names node contains a list of domains
    for domains in dns_names:
        # extract each domain from the list
        for domain in domains:
            domainlist.append(domain)

    i += 1

# converting to a set eliminates duplicates
domainset = set(domainlist)

# converting back to a list will allow sorting
domainlist = list(domainset)
domainlist.sort()

# print output, save to a file, etc.
for domain in domainlist:
    print domain
