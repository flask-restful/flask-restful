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
        raise Exception("Uncommited changes, please commit or stash")

    new_version = point_release(args.version)
    option = "version='{}'"

    setup = open('setup.py').read()
    
    with open('setup.py', 'w') as f:
        f.write(setup.replace(option.format(args.version),
                              option.format(new_version)))

    #subprocess.call(["git", "add", "setup.py"])
    #subprocess.call(["git", "commit", "-am",
    #                 "Bump to version {}".format(new_version)])
    #subprocess.call(["git", "tag", new_version])
    #subprocess.call(["git", "push", "origin", "master"])
    #subprocess.call(["git", "push", "--tags"])
    #subprocess.call(["python", "setup.py", "sdist", "upload"])


if __name__ == "__main__":
    main()
