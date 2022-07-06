# scrapeth
# Scrape Ethereum smart contracts (including source code) through the Etherscan API.

Uses a list of addresses stored in a local JSON file. The output is stored locally in 3 files with the extensions: .sol, .json, and .jsonl. The output JSON file is converted into JSONL with the help of the JQ command. The JSONL file can be used in a BigQuery import with auto-detect schema.