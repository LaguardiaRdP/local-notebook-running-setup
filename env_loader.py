from __future__ import annotations

import os


# Filenames tried, in order, when a specific one isn't given. Both a plain
# .env.localrunner and a shell-style .env.localrunner.sh (with `export` lines)
# are supported.
_DEFAULT_CANDIDATES = (".env.localrunner", ".env.localrunner.sh")


def load_env(filename: str | None = None) -> str:
    """
    Load credentials from a .env-style file located in the PARENT folder
    (your notebooks folder, one level above this repo) into os.environ.

    Keeping the file one level up means every cloned copy of this repo shares
    the same credentials file, in the same location.

    Handles both plain `KEY=value` lines and shell-style `export KEY=value`
    lines, so the same file can be `source`d from a shell or loaded here.

    Params:
    -------
    filename: str | None
        Name of the env file to look for in the parent folder. If None, tries
        `.env.localrunner` then `.env.localrunner.sh`.

    Returns:
    --------
    str
        The resolved path to the env file that was loaded.

    Raises:
    -------
    FileNotFoundError
        If no matching env file is found in the parent folder.
    """
    parent_dir = os.path.dirname(os.getcwd())
    candidates = [filename] if filename else list(_DEFAULT_CANDIDATES)

    env_path = None
    for candidate in candidates:
        path = os.path.join(parent_dir, candidate)
        if os.path.isfile(path):
            env_path = path
            break

    if env_path is None:
        tried = " or ".join(candidates)
        raise FileNotFoundError(
            f"{tried} not found in {parent_dir} — place your credentials file in "
            f"your notebooks folder (one level up from this repo)."
        )

    with open(env_path) as f:
        for line in f.readlines():
            line = line.strip()
            # Drop shell `export ` prefix so `export KEY=value` parses correctly.
            if line.startswith("export "):
                line = line[len("export "):].strip()
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
