from pathlib import Path
import subprocess
import time
from typing import Dict
from dotenv import load_dotenv
import os

# Example Command:
# command = 'timeout 60 cargo run --release -- --cores 1-10 on-chain -a "0x983EFCA0Fd5F9B03f75BbBD41F4BeD3eC20c96d8" -b "latest"'


def get_contracts(directory: Path):
    contracts = []

    for file in directory.glob("**/*.txt"):
        with file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("https://etherscan.io/"):
                    contracts.append(
                        {
                            "address": line.split("/")[4].split("?")[0],
                            "blocknum": "22320135",  # Latest as of 2025-04-21 23:57 GMT+2
                        }
                    )
    for file in directory.glob("**/defihacklabs_list.txt"):
        with file.open("r", encoding="utf-8") as f:
            for line in f:
                temp = [s.strip() for s in line.split(",")]
                contracts.append(
                    {
                        "address": temp[0],
                        "blocknum": temp[1],
                    }
                )

    return contracts


def run_contract_analysis(contract: Dict, etherscan_key):
    address = contract["address"]
    blocknum = contract["blocknum"]
    contract_path = Path(address)

    if contract_path.is_dir():
        print(f"Skipping existing directory: {address}")
        return

    contract_path.mkdir(parents=True, exist_ok=True)
    output_file = contract_path / "output.txt"

    # timeout 60
    # cargo run --release
    # -- evm
    # -t "0x983EFCA0Fd5F9B03f75BbBD41F4BeD3eC20c96d8"
    # -c eth
    # -b "22126698"
    # -u "http://192.168.122.253:8545/"
    # -w "0x983EFCA0Fd5F9B03f75BbBD41F4BeD3eC20c96d8/"
    # --run-forever
    # -e "http://192.168.122.253:8545"
    # --onchain-etherscan-api-key D8IX374FJNCA2UKF51XI9TYQA9TD8IKJGE
    command = f'timeout 60 \
        cargo run --release -- evm \
        -t "{address}" \
        -c eth \
        -o \
        --onchain-block-number "{blocknum}" \
        --onchain-url "http://192.168.122.253:8545/" \
        --work-dir "{contract_path}" \
        --onchain-etherscan-api-key "{etherscan_key}"'
    # cargo run --release -- evm -t "0x983EFCA0Fd5F9B03f75BbBD41F4BeD3eC20c96d8" -c eth -o --onchain-block-number "22461918" --onchain-url "http://192.168.122.253:8545/" --work-dir "0x983EFCA0Fd5F9B03f75BbBD41F4BeD3eC20c96d8/"  --onchain-etherscan-api-key "D8IX374FJNCA2UKF51XI9TYQA9TD8IKJGE"
    with open(contract_path / "command.txt", "w") as f:
        f.write(command)

    print(f"Running command: {command}")

    start_time = time.time()

    try:
        with output_file.open("wb") as out:
            subprocess.run(
                command, shell=True, stdout=out, stderr=subprocess.STDOUT, check=True
            )
    except subprocess.CalledProcessError as e:
        print(f"Error processing {contract}: {e}")
    finally:
        elapsed_time = time.time() - start_time
        print(f"Completed {contract} in {elapsed_time:.2f} seconds")


def run_cargo_build_release():
    try:
        result = subprocess.run(
            ["cargo", "build", "--release"],
            cwd=os.getcwd(),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.output
    except Exception as e:
        return False, str(e)


def main():
    run_cargo_build_release()
    load_dotenv()
    contract_dir = Path("_contracts/online/")
    contracts = get_contracts(contract_dir)
    etherscan_key = os.getenv("ETHERSCAN_KEY")

    for contract in contracts:
        run_contract_analysis(contract, etherscan_key)


if __name__ == "__main__":
    main()
