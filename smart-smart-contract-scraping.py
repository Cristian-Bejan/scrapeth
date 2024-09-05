# This script uses jq to format json and prepare it for BigQuery manual table creation through JSONL data
# If successful, BigQuery should auto-detect the schema
# To manually create a table with multiple rows, upload your files to Storage and import in bulk using *

import os
import time
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# Your Etherscan API key here
apiKey = ''
# Your Linux json file path
contractsFilePathJson = ''
# Your Linux directory path - where to save new files
targetDirPath = ""
# counter for number of addresses scraped + test address
count = 1
# file extensions
solE = '.sol'
jsonE = '.json'
jsonlE = '.jsonl'

# Test connection to Etherscan API
try:
    urlopen(f'https://api.etherscan.io/api?module=contract&action=getsourcecode&address='
            '0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae' + '&apikey=' + apiKey, timeout=1)
    print(f'{count}\nTest address for Etherscan API connection test '
          '0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae\n')
except URLError as e:
    print(f"Connection failed: {e.reason}")

# Load json
with open(contractsFilePathJson) as f:
    content = json.load(f)

# Send a request to Etherscan API with each smart contract address
for address in content:
    count += 1
    if (count - 1) % 5 == 0:
        print(f'{count - 1} addresses scraped - sleeping for 1 second\n')
        time.sleep(1)  # Sleep for 1 second after every 5 addresses

    # Form and send request to Etherscan API
    try:
        with urlopen(f'https://api.etherscan.io/api?module=contract&action=getsourcecode&address='
                     f'{address["address"]}&apikey={apiKey}', timeout=5) as response:
            # Read json response
            data = response.read()
    except HTTPError as e:
        print(f'HTTP error: {e.code}')
        continue
    except URLError as e:
        print(f'Failed to reach server: {e.reason}')
        continue

    # Load json response
    jload = json.loads(data)

    # Scrape the Contract Name and create 3 files with it appending the .sol, .json, and .jsonl extensions
    for code in jload['result']:
        contract_name = code['ContractName'] or "noName"  # Use "noName" if contract name is empty

        # Delete unnecessary keys in a more efficient way
        keys_to_delete = ['CompilerVersion', 'OptimizationUsed', 'Runs', 'ConstructorArguments', 'EVMVersion', 'Library', 'LicenseType', 'SwarmSource']
        for key in keys_to_delete:
            code.pop(key, None)

        # Write source code to .sol file
        sol_file_path = os.path.join(targetDirPath, f'{contract_name}_{address["address"]}{solE}')
        with open(sol_file_path, 'w', encoding='UTF-8') as f1:
            f1.write(f'/// {address["address"]}\n/// {contract_name}\n\n{code["SourceCode"]}')
        print(f'{contract_name}_{address["address"]} written as {solE}')

        # Write source code to .json file
        json_file_path = os.path.join(targetDirPath, f'{contract_name}_{address["address"]}{jsonE}')
        with open(json_file_path, 'w', encoding='UTF-8') as f2:
            json.dump(jload['result'], f2, indent=2, sort_keys=True)
        print(f'{contract_name}_{address["address"]} written as {jsonE}')

        # Convert json to jsonl
        jsonl_file_path = os.path.join(targetDirPath, f'{contract_name}_{address["address"]}{jsonlE}')
        os.system(f"bash -c 'cat {json_file_path} | jq -c \".[]\" > {jsonl_file_path}'")
        print(f'{contract_name}_{address["address"]} written as {jsonlE}\n')

print(f"Smart contracts scraped = {count - 1}")
