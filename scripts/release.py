import argparse
import subprocess


def point_release(version):
    parts = version.split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    return '.'.join(parts)


def main():
    parser = argparse.ArgumentParser(description='Bump version number')
    parser.add_argument('version')
    args = parser.parse_args()

    branch = subprocess.check_output(['git', 'branch']).strip()

    if not "* master" in branch:
        raise Exception("Must be on master branch to release")

    if len(subprocess.check_output(["git", "status", "-s"]).strip()) > 0:
        raise Exception("Uncommitted changes, please commit or stash")

    subprocess.call(["git", "tag", args.version])
    subprocess.call(["git", "push", "origin", "master"])
    subprocess.call(["git", "push", "--tags"])
    subprocess.call(["python", "setup.py", "sdist", "upload"])


if __name__ == "__main__":
    main()
