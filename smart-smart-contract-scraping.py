# This script uses jq to format json and prepare it for BigQuery manual table creation through JSONL data
# If successful, BigQuery should auto-detect the schema
# To manually create a table with multiple rows, upload your files to Storage and import in bulk using *

import os
import time
import json
from socket import socket
from urllib.request import urlopen

# Your Etherscan API key here
apiKey: str = ''
# Your Linux json file path
contractsFilePathJson: str = ''
# Your Linux dir path - where to save new files
targetDirPath: str = ""
# counter for number of addresses scraped + test address
count: int = 1
# file extensions
solE: str = '.sol'
jsonE: str = '.json'
jsonlE: str = '.jsonl'

# test connection to Etherscan API
try:
    urlopen('https://api.etherscan.io/api?module=contract&action=getsourcecode&address='
            '0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae' + '&apikey=' + apiKey, timeout=1)
    print('{0}\n'.format(count) + 'Test address for Etherscan API connection test ' +
          '0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae' + '\n')
except socket.timeout:
    print("connection's timeout expired")

# import from json file

# Load json
with open(contractsFilePathJson) as f:
    content = json.load(f)
    # print(content)

# send a request to Etherscan API with each smart contract address
for address in content:
    count += 1
    if (count - 1) % 5 == 0:
        print('{0} addresses scraped - sleep 1 second'.format(count - 1) + '\n')
        time.sleep(1)

    # form and send request to Etherscan API
    with urlopen('https://api.etherscan.io/api?module=contract&action=getsourcecode&address='
                 + address['address'] + '&apikey=' + apiKey, timeout=5) as response:
        if socket.timeout == 5:
            print("timeout")
        # read json response
        data = response.read()

    # load json response
    jload = json.loads(data)

    # scrape the Contract Name and create 3 files with it appending the .sol, .json, and .jsonl extensions
    for code in jload['result']:
        contract_name = code['ContractName']
        if len(contract_name) == 0:
            contract_name = "noName"

        # use this to delete key-values inside the Result key
        del code['CompilerVersion']
        del code['OptimizationUsed']
        del code['Runs']
        del code['ConstructorArguments']
        del code['EVMVersion']
        del code['Library']
        del code['LicenseType']
        del code['SwarmSource']

        # write source code to .sol file and prepend contract address and contract name
        with open(targetDirPath + contract_name + '_' + address['address'] + solE, 'w', encoding='UTF-8') as f1:
            f1.writelines('/// ' + address['address'] + '\n' + '/// ' + contract_name + '\n\n' + code['SourceCode'])
        print('{0}\n'.format(count) + contract_name + '_' + address['address'] + ' written as ' + solE)

        # write source code to .json file
        with open(targetDirPath + contract_name + '_' + address['address'] + jsonE, 'w', encoding='UTF-8') as f2:
            json.dump(jload['result'], f2, indent=2, sort_keys=True)  # or code['SourceCode'] just for source code
        print(contract_name + '_' + address['address'] + ' written as ' + jsonE)

        # convert json to jsonl
        path = targetDirPath + contract_name + '_' + address['address'] + jsonE
        newContractName = contract_name + '_' + address['address'] + jsonlE
        # The JQ command is used
        os.system("bash -c 'cat " + path + " | jq -c '.[]' > " + targetDirPath + newContractName + "'")
        print(contract_name + '_' + address['address'] + ' written as ' + jsonlE + '\n')
print("Smart contracts scraped = {0}".format(count - 1))
