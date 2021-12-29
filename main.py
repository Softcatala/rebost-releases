from flavors import __init__
import json


if __name__ == '__main__':
    u = flavor.get('ubuntu')
    print(
        json.dumps(u, indent=4)
    )

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


# https://cdimage.ubuntu.com/$flavor/releases/main-version/release/