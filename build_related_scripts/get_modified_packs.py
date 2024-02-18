import argparse
import os
from pathlib import Path
from typing import List

from demisto_sdk.commands.common.git_util import GitUtil
from demisto_sdk.commands.common.tools import get_pack_names_from_files

PACK_PATH_REGEX = r"Packs/([a-zA-Z0-9_]+)/"

PACKS = "Packs"


def dir_path(path: str):
    """Directory type module for argparse."""
    if os.path.isdir(path):
        return Path(path)
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path.")


def option_handler() -> argparse.Namespace:
    """Validates and parses script arguments.

    Returns:
        Namespace: Parsed arguments object.

    """
    parser = argparse.ArgumentParser(description="Collect the packs that has changed.")
    parser.add_argument(
        "-rp", "--repo_path", help="The path to the required repo.", type=dir_path
    )
    parser.add_argument(
        '--prev-ver', default='master', help='Previous branch or SHA1 commit to run checks against.'
    )
    return parser.parse_args()


def get_changed_files(repo_path: Path, prev_ver: str) -> List[str]:
    """Uses the demisto-sdk's GitUtil to get all the changed files.

    Args:
        repo_path (Path): The path to the repo.

    Returns:
        List[str]. All the files that have changed.
    """
    git_util = GitUtil(repo_path)
    repo = git_util.repo

    try:
        active_branch = repo.active_branch
    except TypeError:
        active_branch = 'DETACHED_' + repo.head.object.hexsha

    if str(active_branch) == prev_ver:
        # Get the latest commit in master, prior the merge.
        prev_ver = str(repo.remote().refs[prev_ver].commit.parents[0])

    modified_files = git_util.modified_files(prev_ver=prev_ver)
    added_files = git_util.added_files(prev_ver=prev_ver)
    renamed_tuples = git_util.renamed_files(prev_ver=prev_ver)
    renamed_files = {new_file_path for _, new_file_path in renamed_tuples}

    all_changed_files = modified_files.union(added_files).union(renamed_files)
    return [str(changed_file) for changed_file in all_changed_files]


def main():
    options = option_handler()
    repo_path: Path = options.repo_path
    prev_ver: str = options.prev_ver

    changed_files = get_changed_files(repo_path, prev_ver)

    packs_changed = get_pack_names_from_files(changed_files)
    packs_changed_paths = [str(repo_path / PACKS / pack) for pack in packs_changed]
    changed_packs_paths_string = ",".join(packs_changed_paths)

    print(changed_packs_paths_string)


if __name__ == "__main__":
    main()
