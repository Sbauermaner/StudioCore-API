import os


def clean(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".py"):
                full = os.path.join(root, f)
                with open(full, "r", encoding="utf-8") as fp:
                    lines = fp.readlines()
                new = [line.rstrip() + "\n" for line in lines]
                with open(full, "w", encoding="utf-8") as fp:
                    fp.writelines(new)


clean(".")
