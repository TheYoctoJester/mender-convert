#! /usr/bin/env python3

# Update clones of the repositories we need in KAS_REPO_REF_DIR to speed up fetches

import sys
import os
import subprocess
import pathlib

images = [
    {
        "url": "https://downloads.raspberrypi.com/raspios_lite_armhf/images/raspios_lite_armhf-2024-07-04/2024-07-04-raspios-bookworm-armhf-lite.img.xz",
        "name": "2024-07-04-raspios-bookworm-armhf-lite.img.xz",
        "checksum": "df9c192d66d35e1ce67acde33a5b5f2b81ff02d2b986ea52f1f6ea211d646a1b",
        "image_name": "2024-07-04-raspios-bookworm-armhf-lite.img",
        "image_checksum": "5cbfbf12490d852cb2e0bbae912399a9e0785f6c0a8cf95a0676cbc0a9e146ed"
    },
   {
        "url": "https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2024-07-04/2024-07-04-raspios-bookworm-arm64-lite.img.xz",
        "name": "2024-07-04-raspios-bookworm-arm64-lite.img.xz",
        "checksum": "43d150e7901583919e4eb1f0fa83fe0363af2d1e9777a5bb707d696d535e2599",
        "image_name": "2024-07-04-raspios-bookworm-arm64-lite.img",
        "image_checksum": "2746d9ff409c34de471f615a94a3f15917dca9829ddbc7a9528f019e97dc4f03"
    },
    {
        "url": "https://downloads.raspberrypi.com/raspios_oldstable_lite_armhf/images/raspios_oldstable_lite_armhf-2024-07-04/2024-07-04-raspios-bullseye-armhf-lite.img.xz",
        "name": "2024-07-04-raspios-bullseye-armhf-lite.img.xz",
        "checksum": "10a44eeb5f5bfd000b755425b93914add6c8f0590294189abdf7a9ac7297dc3b",
        "image_name": "2024-07-04-raspios-bullseye-armhf-lite.img",
        "image_checksum": "1829ce6d8adbc21d7fad72c4be2066e0fe0fbb38ae4b7c0266d32448e3468cc3"
    },
    {
        "url": "https://downloads.raspberrypi.com/raspios_oldstable_lite_arm64/images/raspios_oldstable_lite_arm64-2024-07-04/2024-07-04-raspios-bullseye-arm64-lite.img.xz",
        "name": "2024-07-04-raspios-bullseye-arm64-lite.img.xz",
        "checksum": "999437f8e1f3f31669deaaeb01aefb94303694e929d0f4c276379383e9169ac4",
        "image_name": "2024-07-04-raspios-bullseye-arm64-lite.img",
        "image_checksum": "0246fcc7074ff2ea293fd4af625dbf228a5db39c3083dd00c3db03a0f2c4f376"
    }
]

if __name__ == "__main__":
    if "GOLDEN_IMAGE_DIR" not in os.environ:
        print("GOLDEN_IMAGE_DIR needs to be set")
        sys.exit(1)

    base_imagedir = pathlib.Path(os.environ["GOLDEN_IMAGE_DIR"])
    failed = False

    for act in images:
        image = base_imagedir / act["image_name"]
        print(f'processing file {image}')

        def fail():
            sys.exit(128)

        def check_integrity(filename, hash):
            try:
                #result = subprocess.run(["echo", hash, filename, "|", "sha256sum", "-c", "--quiet", "--status"], stdout=subprocess.PIPE)
                result = subprocess.run(["sha256sum", filename], stdout=subprocess.PIPE)
                output = result.stdout.decode()
                if result.returncode == 0 and output.split()[0] == hash:
                    return True
                return False
            except: # technically this could hide some valid exceptions to handle, but lets move forward for now.
                return False

        needs_download = False
        if not image.exists():
            print(f'image {act["image_name"]} not found, downloading')
            needs_download = True
        elif not check_integrity(image, act["image_checksum"]):
            print(f'image {act["image_name"]} checksum invalid, downloading')
            needs_download = True
        else:
            print(f'image {act["image_name"]} found and valid')
        
        if needs_download:
            comp_image = base_imagedir / act["name"]
            try:
                print(f'Downloading {act["url"]}')
                subprocess.run(["wget", act["url"], "-O", comp_image], check=True)
            except subprocess.CalledProcessError as e:
                print(e)
                fail()
            print(f'Checking {act["name"]}')
            if not check_integrity(comp_image, act["checksum"]):
                fail()
            try:
                print(f'Unpacking {act["name"]}')
                subprocess.run(["unxz", "-f", comp_image], check=True) # needs -f to overwrite and eventually existing corrupt file
            except subprocess.CalledProcessError as e:
                print(e)
                fail()
            print(f'Checking {act["image_name"]}')
            if not check_integrity(image, act["image_checksum"]):
                fail()
