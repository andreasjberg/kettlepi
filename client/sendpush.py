from pushbullet import Pushbullet

# https://pypi.python.org/pypi/pushbullet.py
api_key = 'o.ygFXCfO9qBn8hBLzVdabvGOE04Rly5fB'
pb = Pushbullet(api_key)


def send_notification(title, body):
    push_title = str(title)
    push_body = str(body)
    pb.push_note("%s" % push_title, "%s" % push_body)


if __name__ == "__main__":
    # hops = ['East Kent Golding', 'Saaz']
    # time = 15
    # title = "Add hops!"
    # body = "Add HOPS!", "Add Hops: %s" % hops + "Boiltime: %s" % time
    # send_notification(title,body)
    send_notification("HEJ KOMPIS", "JAG pra! so!")
