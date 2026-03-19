import argparse
import json
import logging
import os
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from azure.storage.blob import BlobServiceClient, ContainerClient
from prettytable import PrettyTable

MAIN_CONTAINER_PACK_PATH_FORMAT = "content/packs/{pack_name}/{pack_version}/{pack_zip_name}"
BRANCH_CONTAINER_PACK_PATH_FORMAT = "builds/{branch_name}/packs/{pack_name}/{pack_version}/{pack_zip_name}"


def dir_path(path: str) -> Path:
    if os.path.isdir(path):
        return Path(path)
    raise argparse.ArgumentTypeError(f"{path} is not a valid path.")


def option_handler() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload packs to Azure Blob Storage.")
    parser.add_argument("-a", "--account_url", required=True, help="Azure Storage account URL.")
    parser.add_argument("-c", "--container_name", required=True, help="Target container name.")
    parser.add_argument("-d", "--packs_directory", required=True, type=dir_path, help="Directory that contains zipped packs to upload.")
    parser.add_argument("-b", "--branch_name", required=True, help="Branch name running the upload.")
    parser.add_argument("--default_branch", default="main", help="Name of the default branch (default: main).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    return parser.parse_args()


def ensure_sas_token(verbose: bool) -> str:
    try:
        token = os.environ["AZURE_STORAGE_SAS_TOKEN"].strip()
    except KeyError:
        raise RuntimeError("Required environment variable AZURE_STORAGE_SAS_TOKEN is not set.") from None
    if not token:
        raise RuntimeError("AZURE_STORAGE_SAS_TOKEN is set but empty.")
    if verbose:
        preview = f"{token[:6]}...{token[-6:]}" if len(token) > 12 else "***"
        logging.info("Using SAS token (redacted preview: %s)", preview)
    return token


def init_container_clients(
    account_url: str,
    container_name: str,
    sas_token: str,
    verbose: bool,
) -> Tuple[Optional[ContainerClient], Optional[ContainerClient]]:
    sas_with_prefix = sas_token if sas_token.startswith("?") else f"?{sas_token}"
    primary_client: Optional[ContainerClient] = None
    fallback_client: Optional[ContainerClient] = None
    errors = []

    try:
        service = BlobServiceClient(account_url=f"{account_url}{sas_with_prefix}")
        primary_client = service.get_container_client(container_name)
        if verbose:
            logging.info("Initialized account-level client for container %s", container_name)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"account-level: {exc}")
        if verbose:
            logging.info("Failed to initialize account-level client: %s", exc)

    try:
        container_url = f"{account_url}/{container_name}{sas_with_prefix}"
        fallback_client = ContainerClient.from_container_url(container_url)
        if verbose:
            logging.info("Initialized container-level client for container %s", container_name)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"container-level: {exc}")
        if verbose:
            logging.info("Failed to initialize container-level client: %s", exc)

    if not primary_client and not fallback_client:
        details = "; ".join(errors) if errors else "no additional details"
        raise RuntimeError(f"Failed to initialize Azure Blob container clients: {details}")

    return primary_client, fallback_client


def get_pack_metadata(pack_path: Path, verbose: bool) -> Dict[str, str]:
    if verbose:
        logging.info("Reading metadata from %s", pack_path)
    try:
        with zipfile.ZipFile(pack_path, "r") as zip_ref:
            metadata_content = zip_ref.read("metadata.json")
            return json.loads(metadata_content)
    except zipfile.BadZipFile as exc:
        raise ValueError(f"{pack_path} is not a valid zip file.") from exc
    except KeyError as exc:
        raise FileNotFoundError(f"metadata.json not found in {pack_path}.") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in metadata.json for {pack_path}: {exc}") from exc


def format_blob_path(pack_name: str, pack_version: str, pack_zip_name: str, branch_name: str, default_branch: str) -> str:
    if branch_name == default_branch:
        return MAIN_CONTAINER_PACK_PATH_FORMAT.format(
            pack_name=pack_name,
            pack_version=pack_version,
            pack_zip_name=pack_zip_name,
        )
    return BRANCH_CONTAINER_PACK_PATH_FORMAT.format(
        branch_name=branch_name.replace("/", "_"),
        pack_name=pack_name,
        pack_version=pack_version,
        pack_zip_name=pack_zip_name,
    )


def _is_authorization_error(error: Exception) -> bool:
    message = str(error).lower()
    return "authorizationfailure" in message or "not authorized" in message or "authenticationfailed" in message


def upload_blob_with_fallback(
    primary_client: Optional[ContainerClient],
    fallback_client: Optional[ContainerClient],
    blob_name: str,
    pack_path: Path,
    verbose: bool,
) -> ContainerClient:
    last_error: Optional[Exception] = None
    for label, client in (("account-level", primary_client), ("container-level", fallback_client)):
        if not client:
            continue
        try:
            with pack_path.open("rb") as data:
                client.upload_blob(blob_name, data, overwrite=True)
            if verbose:
                logging.info("%s upload succeeded for %s", label, blob_name)
            return client
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if verbose:
                logging.info("%s upload failed for %s: %s", label, blob_name, exc)
            if label == "account-level" and fallback_client and _is_authorization_error(exc):
                continue
            raise
    raise RuntimeError(f"Upload failed for {blob_name}: {last_error}")


def verify_upload(client: ContainerClient, blob_name: str, verbose: bool) -> None:
    if not client:
        return
    try:
        blob_client = client.get_blob_client(blob_name)
        if blob_client.exists():
            properties = blob_client.get_blob_properties()
            if verbose:
                logging.info("Verified blob %s (%s bytes)", blob_name, properties.size)
        elif verbose:
            logging.info("Blob %s uploaded but verification skipped (no read permission).", blob_name)
    except Exception as exc:  # noqa: BLE001
        if verbose:
            logging.info("Verification skipped for %s: %s", blob_name, exc)


def upload_pack_file(
    pack_path: Path,
    primary_client: Optional[ContainerClient],
    fallback_client: Optional[ContainerClient],
    branch_name: str,
    default_branch: str,
    verbose: bool,
) -> Tuple[str, bool]:
    pack_label = pack_path.stem
    try:
        metadata = get_pack_metadata(pack_path, verbose)
        pack_label = metadata["id"]
        pack_version = metadata["currentVersion"]
        blob_name = format_blob_path(pack_label, pack_version, pack_path.name, branch_name, default_branch)
        print(f"Uploading '{pack_path.name}' to '{blob_name}'...", end="", flush=True)
        used_client = upload_blob_with_fallback(primary_client, fallback_client, blob_name, pack_path, verbose)
        verify_upload(used_client, blob_name, verbose)
        print(" done.")
        return pack_label, True
    except Exception as exc:  # noqa: BLE001
        print(" failed.")
        logging.error("Failed to upload pack '%s': %s", pack_label, exc)
        return pack_label, False


def upload_packs(
    primary_client: Optional[ContainerClient],
    fallback_client: Optional[ContainerClient],
    packs_directory: Path,
    branch_name: str,
    default_branch: str,
    verbose: bool,
) -> Dict[str, bool]:
    logging.info("Uploading packs from %s", packs_directory)
    results: Dict[str, bool] = {}
    for pack_zip_path in sorted(packs_directory.iterdir()):
        if not pack_zip_path.is_file() or pack_zip_path.suffix.lower() != ".zip":
            continue
        pack_name, upload_result = upload_pack_file(
            pack_zip_path,
            primary_client,
            fallback_client,
            branch_name,
            default_branch,
            verbose,
        )
        results[pack_name] = upload_result
    return results


def print_uploads_results_table(packs_results: Dict[str, bool]) -> None:
    table = PrettyTable()
    table.field_names = ["Pack Name", "Upload Status"]
    for pack_name, status in packs_results.items():
        table.add_row([pack_name, "Success" if status else "Failed"])
    print(table)


def main() -> None:
    options = option_handler()
    logging.basicConfig(level=logging.INFO if options.verbose else logging.WARNING, format="%(levelname)s: %(message)s")

    try:
        sas_token = ensure_sas_token(options.verbose)
        primary_client, fallback_client = init_container_clients(
            options.account_url,
            options.container_name,
            sas_token,
            options.verbose,
        )
        packs_results = upload_packs(
            primary_client,
            fallback_client,
            options.packs_directory,
            options.branch_name,
            options.default_branch,
            options.verbose,
        )
        if packs_results:
            print_uploads_results_table(packs_results)
    except Exception as exc:  # noqa: BLE001
        logging.error("Pack upload process failed: %s", exc)
        if options.verbose:
            import traceback

            traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
