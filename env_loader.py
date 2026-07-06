import os


def load_env(filename: str = ".env.localrunner") -> str:
    """
    Load credentials from a .env-style file located in the PARENT folder
    (your notebooks folder, one level above this repo) into os.environ.

    Keeping the file one level up means every cloned copy of this repo shares
    the same credentials file, in the same location.

    Params:
    -------
    filename: str
        Name of the env file to look for in the parent folder.

    Returns:
    --------
    str
        The resolved path to the env file that was loaded.

    Raises:
    -------
    FileNotFoundError
        If the env file is not found in the parent folder.
    """
    repo_dir = os.getcwd()
    env_path = os.path.join(os.path.dirname(repo_dir), filename)

    if not os.path.isfile(env_path):
        raise FileNotFoundError(
            f"{filename} not found at {env_path} — place it in your notebooks "
            f"folder (one level up from this repo)."
        )

    with open(env_path) as f:
        for line in f.readlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                # Remove surrounding quotes (single or double) from shell-style values
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                os.environ[key] = value

    return env_path
