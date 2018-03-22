# This command will grab json and display an array of all domain entries at one place in the cert array object (0 in this case).
# Further iteration of the objects is needed to get all the dns_names from every cert entry
# curl -s 'https://certspotter.com/api/v0/certs?domain=rockstargames.com' |     python -c "import sys, json; obj=json.load(sys.stdin); print '\n'.join(obj[0]['dns_names'])"

#!/usr/bin/python
import sys, json, argparse
from subprocess import Popen, PIPE

# arguments and usage
parser = argparse.ArgumentParser(description='Domain recon tool that leverages the Cert Spotter API', usage='%(prog)s domain')
parser.add_argument('domain', help="Extract domains for the given domain and all sub-domains")
args = parser.parse_args()


def getcertificates(domain):
    # fetch cert(s) for domain. returns json
    obj = Popen(['curl', '-s', 'https://certspotter.com/api/v0/certs?domain=' + domain], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = obj.communicate("")
    rc = obj.returncode
    
    # decode and return json
    return json.loads(output)

def getdomainlist(certs):
    dns_names = []
    domainlist = []
    i = 0

    while i < len(certs):
        # iterate certs and extract the dns_names node from each
        dns_names.append(certs[i]['dns_names'])

        # each dns_names node contains a list of domains
        for domains in dns_names:
            # extract each domain from the list
            for domain in domains:
                domainlist.append(domain)

        i += 1

    return domainlist

def reduceandsortdomainlist(domainlist):
    # converting to a set eliminates duplicates
    domainset = set(domainlist)

    # converting back to a list will allow sorting
    domainlist = list(domainset)
    domainlist.sort()
    return domainlist

def getrecursivedomainlist(domainlist):
    mergedlist = []
    for domain in domainlist:
        mergedlist += run(domain)
    return mergedlist

def run(domain):
    certs = getcertificates(domain)
    return reduceandsortdomainlist(getdomainlist(certs))

domainlist = run(args.domain)
recursivedomainlist = reduceandsortdomainlist(getrecursivedomainlist(domainlist))

for domain in recursivedomainlist:
    print domain

print '\n::DIAGNOSTICS::'
print 'Non-recursive domain list length\t\t{}'.format(len(domainlist))
print 'Recursive domain list length\t\t\t{}'.format(len(recursivedomainlist))
print 'Additional domains found by being recursive\t{}\n'.format(len(recursivedomainlist) - len(domainlist))

## TODO: Make iterative list building optional.  
## It adds a lot of overhead and in some cases it doesn't
## provide any benefit such as with small businesses
