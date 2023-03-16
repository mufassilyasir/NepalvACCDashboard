import requests


def avatardownload(first_name, last_name, cid):
    if first_name == "CID":
        r = requests.get(f"https://ui-avatars.com/api/?name={cid}&bold=true")
    elif first_name != "CID":
        r = requests.get(f"https://ui-avatars.com/api/?name={first_name}+{last_name}&bold=true")

    if r.status_code == 200:

        save_image = "website/static/public/Initials" + "/" + str(cid) + ".png"
        with open(save_image, 'wb') as file:
            file.write(r.content)
        file.close()

    return
