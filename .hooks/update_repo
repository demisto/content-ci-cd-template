#!/bin/bash

output_paths=(
    "CommonServerPython.py"
    "CommonServerPowerShell.ps1"
    "demistomock.py"
    "demistomock.ps1"
    "dev_envs/pytest/conftest.py"
    "pyproject.toml"
    "poetry.lock"
    "package.json"
    "package-lock.json"
    ".hooks/pre-commit"
    ".hooks/bootstrap"
)

url_to_fetch_from=(
    "https://raw.githubusercontent.com/demisto/content/master/Packs/Base/Scripts/CommonServerPython/CommonServerPython.py"
    "https://raw.githubusercontent.com/demisto/content/master/Packs/Base/Scripts/CommonServerPowerShell/CommonServerPowerShell.ps1"
    "https://raw.githubusercontent.com/demisto/content/master/Tests/demistomock/demistomock.py"
    "https://raw.githubusercontent.com/demisto/content/master/Tests/demistomock/demistomock.ps1"
    "https://raw.githubusercontent.com/demisto/content/master/Tests/scripts/dev_envs/pytest/conftest.py"
    "https://raw.githubusercontent.com/demisto/content/master/pyproject.toml"
    "https://raw.githubusercontent.com/demisto/content/master/poetry.lock"
    "https://raw.githubusercontent.com/demisto/content/master/package.json"
    "https://raw.githubusercontent.com/demisto/content/master/package-lock.json"
    "https://raw.githubusercontent.com/demisto/content/master/.hooks/pre-commit"
    "https://raw.githubusercontent.com/demisto/content/master/.hooks/bootstrap"
)

mkdir -p dev_envs/pytest
mkdir -p .hooks

is_failed=0


for i in ${!output_paths[@]};
do
    output_path=${output_paths[$i]}
    url=${url_to_fetch_from[$i]}

    $(curl -o "$output_path" $url --fail)
    exit_code=$?
    is_failed=$(($is_failed+$exit_code))

    if [ $exit_code -ne 0 ]
    then
        echo Failed to download $url
    fi
done

if [ $is_failed -ne 0 ]
then
    exit 1
fi

exit 0
