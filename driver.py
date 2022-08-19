import settings

app_name = settings.APP

if app_name == "blinker":
    from apps.blinker import app
    app_init = app.init
    app_tick = app.tick
    
def connect_to_wifi():
    import time, machine, network, gc
    time.sleep(1)
    print('Memory free', gc.mem_free())

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(settings.WIFI_SSID, settings.WIFI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def run():
    import time, machine
    import update
    
    connect_to_wifi()
    
    import update
    git_repo = "serpis/ota-updater"
    git_tag = settings.TAG
    target_dir = "cloned"
    has_update = update.check_if_has_update(git_repo, git_tag, target_dir)
    
    print("Has update?", has_update)
    if has_update:
        update.download_and_apply_update(git_repo, git_tag, target_dir)
        print("Resetting in 10 seconds...")
        time.sleep(10)
        machine.reset()
    
    print(app_name)
    app_init()
    while True:
        app_tick()
