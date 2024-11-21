Content CI/CD Template

This repository demonstrates how to create your own repository in which to create your content and configure your CI/CD process.

Follow [XSOAR CI/CD](https://xsoar.pan.dev/docs/reference/packs/content-management) Article.

# Getting Started

## Setting up the repository in Github

### Creating new private repository

Press the `Use this Template` button and choose to `Create a new repository` in your own GitHub account.

### Clone the repository

Clone the private repository to your local machine, so you can start working on it.

```bash
git clone https://github.com/yourname/private-repo.git
cd private-repo
```

## Setup the repository

### Install dependencies

This repository uses [poetry](https://python-poetry.org/) to manage dependencies.
To install the dependencies, run the following command:

```bash
poetry install
```

This command will create a virtual environment and install all the dependencies.

To activate the virtual environment, run the following command:

```bash
poetry shell
```

## Create a new content item

### Create a new pack

To create a new pack, run the following command:

```bash
demisto-sdk init --name <pack_name>
```

### Create a new Integration or Script

To create a new Integration or Script, run the following command:

```bash
cd Packs/<pack_name>
demisto-sdk init <--integration|--script> --name <integration_or_script_name>
```

Or you can download custom items from your XSOAR instance.  
To do that, you need to set the `DEMISTO_BASE_URL` and `DEMISTO_API_KEY` (and `XSIAM_AUTH_ID` for XSOAR 8) environment variables in your terminal or in the `.env` file. see [Demisto SDK](https://github.com/demisto/demisto-sdk/?tab=readme-ov-file#installation) for more information.

Then run the following command:

```bash
demisto-sdk download -i <item_id> -o <path_to_the_pack>
```

## Deploying to XSOAR

We have two options to deploy our content to XSOAR:

1. Via an artifact server.
2. Directly to XSOAR.

See [XSOAR CI/CD](https://xsoar.pan.dev/docs/reference/packs/content-management#deployment) Article for more information.

In this repository, we have an example of [GitHub Action file](.github/workflows/config.yml) that contains the two options.  
Under the `Upload Packs to Artifacts Server` job, you can see the two options.  
Delete the one you don't want to use.

### Deploying to XSOAR via artifact server

In the `Upload Packs to Artifacts Server` job, you can choose to upload the modified packs to an artifact server.  
Use the following scripts to upload the modified packs to the artifact server:

#### Google Cloud Storage

Use the `bucket_upload.py` script to upload the modified packs to a Google Cloud Storage bucket.

#### AWS S3

Use the `bucket_upload_aws.py` script to upload the modified packs to an AWS S3 bucket.

### Deploying to XSOAR directly

To upload the modified packs directly to XSOAR, you need to add the following environment variables to your repository:  
`DEMISTO_BASE_URL` and `DEMISTO_API_KEY` as secret.  
`XSIAM_AUTH_ID` as variable.
See [Creating secrets for a repository](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) for more information.
