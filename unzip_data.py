import os
import sys
import platform
from hashlib import md5


def execute(cmd: str) -> None:
    print(cmd)
    assert os.system(cmd) == 0


def check_md5(filename: str, gt_hashcode: str) -> None:
    """
    Check the MD5 of a file against the ground truth
    """
    print("Checking %s.." % filename)
    if not os.path.exists(filename):
        print(filename, "not exists")
        print("aborting..")
        sys.exit(-1)
    # The file could be large
    # See: https://stackoverflow.com/questions/48122798/oserror-errno-22-invalid-argument-when-reading-a-huge-file
    inp = open(filename, "rb")
    hasher = md5()
    while True:
        block = inp.read(64 * (1 << 20))
        if not block:
            break
        hasher.update(block)
    hashcode = hasher.hexdigest()

    if hashcode != gt_hashcode:
        print(filename, "has the wrong MD5 hashcode")
        print("Expect %s, but found %s" % (gt_hashcode, hashcode))
        print("Aborting..")
        sys.exit(-1)


def unzip(filename: str) -> None:
    if os.path.exists(filename[:-7]):
        remove = input(
            filename[:-7] + " already exists. Do you want to remove it? (y/N)"
        ).lower()
        if remove == "y":
            execute("rm -r " + filename[:-7])
        else:
            print("aborting..")
            sys.exit(-1)

    execute("tar -xvzf " + filename)


if __name__ == "__main__":
    check_md5("projs_split.json", "39eac2315532040f370ca4996862ef75")
    check_md5("data.tar.gz", "922937155a199605eb8067ccfbbdb81a")
    check_md5("sexp_cache.tar.gz", "2e8ff40a7dd0b6d0efc74480dd3dfc8d")
    unzip("data.tar.gz")
    unzip("sexp_cache.tar.gz")
    os.mkdir("sexp_cache")
    execute("mdb_load -f sexp_cache.lmdb sexp_cache")
    os.remove("sexp_cache.lmdb")

    print("Setting the absolute paths..")
    cwd = os.getcwd()
    if platform.system() == "Darwin":
        cmd = (
            "find ./data -type f -exec sed -i '' 's/TAPAS_ROOT_ABSOLUTE_PATH/%s/g' {} +"
            % cwd.replace(os.path.sep, "\/")
        )
    else:
        cmd = (
            "find ./data -type f -exec sed -i 's/TAPAS_ROOT_ABSOLUTE_PATH/%s/g' {} +"
            % cwd.replace(os.path.sep, "\/")
        )
    execute(cmd)
    print("The CoqGym dataset is ready!")
