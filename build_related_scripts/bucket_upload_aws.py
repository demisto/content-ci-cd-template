import argparse
import boto3
import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional
import zipfile
from prettytable import PrettyTable

s3 = boto3.resource('s3')

MAIN_BUCKET_PACK_PATH_FORMAT = 'content/packs/{pack_name}/{pack_version}/{pack_zip_name}'
BRANCH_BUCKET_PACK_PATH_FORMAT = 'builds/{branch_name}/packs/{pack_name}/{pack_version}/{pack_zip_name}'


def dir_path(path: str):
    """Directory type module for argparse.
    """
    if os.path.isdir(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f'{path} is not a valid path.')


def option_handler() -> argparse.Namespace:
    """Validates and parses script arguments.

    Returns:
        Namespace: Parsed arguments object.

    """
    parser = argparse.ArgumentParser(description='Upload packs to your bucket.')
    parser.add_argument('--bucket_name', required=True, help='The bucket name to upload packs to.')
    parser.add_argument('-d', '--packs_directory', required=True, help='The path to the directory with the packs to upload.', type=dir_path)
    parser.add_argument('-b', '--branch_name', required=True, help='The branch name that the upload is running from.')
    parser.add_argument('--default_branch', default='main', help='The name of the default branch.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    return parser.parse_args()


def init_bucket(bucket_name: str) -> Optional[s3.Bucket]:
    """Initiate bucket connection.

    Args:
        service_account (str): The path to the service account file.

    Returns:
        Bucket. Initialized AWS S3 bucket object.
    """
    logging.info(f"Initializing bucket '{bucket_name}'.")
    try:
        bucket = s3.Bucket(bucket_name)
    except Exception as e:
        print(f'An error occurred while initiating bucket.\n{e}')
        return

    return bucket


def upload_to_bucket(bucket: s3.Bucket, pack_path: str, destination_path: str) -> bool:
    """Uploads a pack to the desired place in the bucket.

    Args:
        bucket (s3.Bucket): Initialized AWS S3 bucket object.
        pack_path (str): The path to the pack file to upload.
        destination_path (str): The path to upload the pack to.

    Returns:
        bool. Whether the upload succeeded or not.
    """
    try:
        bucket.upload_file(pack_path, destination_path)
        return True
    except Exception as e:
        print(f'An error occurred while uploading {pack_path} to bucket.\n{e}')
        return False


def upload_packs(bucket: s3.Bucket, packs_directory: Path, branch_name: str, default_branch: str) -> Dict[str, bool]:
    """

    Args:
        bucket (s3.Bucket): Initialized AWS S3 bucket object.
        packs_directory (Path): The path of the zipped packs to upload.
        branch_name (str): The branch name that the upload is running from.
        default_branch (str): The name of the default branch, used to determine bucket path format.

    Returns:
        Dict[str, bool]. Status for each required pack for upload.
    """
    packs_results: Dict[str, bool] = {}

    logging.info(f"Uploading packs from directory '{packs_directory}'...")
    os.chdir(packs_directory)
    for pack_zip_name in os.listdir():
        if not pack_zip_name.endswith('.zip'):
            continue

        # Removes the .zip suffix
        pack_name = pack_zip_name[:-4]

        upload_result = False
        try:
            pack_path = os.path.join(os.getcwd(), pack_zip_name)
            logging.info(f"Processing '{pack_name}'...")
            with zipfile.ZipFile(pack_path, 'r') as zip_ref:
                metadata_content = zip_ref.read('metadata.json')

            metadata_json = json.loads(metadata_content)
            pack_version = metadata_json['currentVersion']

            if branch_name == default_branch:
                destination_path = MAIN_BUCKET_PACK_PATH_FORMAT.format(
                    pack_name=pack_name,
                    pack_version=pack_version,
                    pack_zip_name=pack_zip_name,
                )
            else:
                destination_path = BRANCH_BUCKET_PACK_PATH_FORMAT.format(
                    branch_name=branch_name.replace('/', '_'),
                    pack_name=pack_name,
                    pack_version=pack_version,
                    pack_zip_name=pack_zip_name,
                )

            upload_result = upload_to_bucket(bucket, pack_path, destination_path)
            logging.info(f"Pack '{pack_path}' uploaded to '{destination_path}'.")

        except Exception as e:
            print(f'An error occurred while uploading {pack_zip_name} to the bucket.\n{e}')

        packs_results[pack_name] = upload_result

    return packs_results


def print_uploads_results_table(packs_results: Dict[str, bool]) -> None:
    """Parses the packs uploads result into a table and prints it.

    Args:
        packs_results (Dict[str, bool]). Status for each required pack for upload.
    """
    results_table = PrettyTable()
    results_table.field_names = ['Pack Name', 'Upload Status']

    for pack_name, upload_result in packs_results.items():
        results_table.add_row([pack_name, 'Success' if upload_result else 'Failed'])

    print(results_table)


def main():
    logging.basicConfig()

    options = option_handler()
    bucket_name: str = options.bucket_name
    packs_directory: Path = options.packs_directory
    branch_name: str = options.branch_name
    default_branch: str = options.default_branch
    verbose: bool = options.verbose

    if verbose:
        logging.getLogger().setLevel(logging.INFO)

    logging.info(f"Logging has been enabled with level '{logging.getLevelName(logging.root.level)}'.")

    bucket = init_bucket(bucket_name)
    if not bucket:
        exit(1)

    packs_results = upload_packs(bucket, packs_directory, branch_name, default_branch)

    if packs_results:
        print_uploads_results_table(packs_results)


if __name__ == '__main__':
    main()
