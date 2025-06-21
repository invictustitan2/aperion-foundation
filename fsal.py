# fsal.py — File System Access Layer (stub, extensible for evil)
def list_files(path="."):
    import os
    return os.listdir(path)
