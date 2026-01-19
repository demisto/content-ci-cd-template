import argparse
import json
import os
import zipfile
from pathlib import Path

from azure.storage.blob import BlobServiceClient

"""This script is made to upload a single content pack to Azure."""


def dir_path(path: str) -> Path:
    """Directory type module for argparse."""
    if Path.is_file(path):
        return Path(path)
    msg = f"{path} is not a valid path."
    raise argparse.ArgumentTypeError(msg)


def option_handler() -> argparse.Namespace:
    """Validates and parses script arguments.

    Returns:
        Namespace: Parsed arguments object.

    """
    parser = argparse.ArgumentParser(description="Upload packs to your bucket.")
    parser.add_argument("-a", "--account_url", required=True, help="Azure storage account URL")
    parser.add_argument("-c", "--container_name", required=True, help="Azure storage account URL")
    parser.add_argument("-i", "--input_file", required=True, help="Path to pack file in Zip format", type=dir_path)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    return parser.parse_args()


def get_pack_metadata(pack_path: Path):
    with zipfile.ZipFile(pack_path, "r") as zip_ref:
        return json.loads(zip_ref.read("metadata.json"))


def upload_pack(pack_path: Path, account_url: str, container_name: str):
    try:
        credential = os.environ["AZURE_STORAGE_SAS_TOKEN"]
    except KeyError:
        msg = "Required environment variable AZURE_STORAGE_SAS_TOKEN is not set."
        raise RuntimeError(msg)

    metadata = get_pack_metadata(pack_path)
    pack_id = metadata["id"]
    pack_version = metadata["currentVersion"]
    file_name = pack_path.name
    print(f"Uploading pack '{pack_path}'...", end="")
    try:
        service = BlobServiceClient(account_url=account_url, credential=credential)
        container_client = service.get_container_client("xsoar-artifacts")
        blob_name = f"content/packs/{pack_id}/{pack_version}/{file_name}"
        with Path(pack_path).open("rb") as data:
            container_client.upload_blob(blob_name, data)
    except Exception as ex:
        msg = f"failed: {str(ex)}"
    print("done.")


def main():
    options = option_handler()
    account_url = options.account_url
    pack_path = options.input_file
    container_name = options.container_name

    upload_pack(pack_path, account_url, container_name)


if __name__ == "__main__":
    main()
