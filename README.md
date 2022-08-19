# scrapeth
# Scrape Ethereum smart contracts (including source code) through the Etherscan API.

Uses as input a list of addresses stored in a JSON file. The output is written to three files with the extensions: **.sol, .json, and .jsonl**  
The output JSON file is converted into JSONL with the help of the **JQ** command:  
```sudo apt install jq```  

With JSONL data you could do a manual table creation in **BigQuery**. If successful, BigQuery should auto-detect the schema.
To manually create a table with multiple rows, upload your files to Storage and import in bulk using *

**Please do not pull requests for security issues. This project was intended to be used as a standalone script**
