# leggo la configurazione da secret/secret.conf
def read_config():
    config = {}
    with open( 'secret/secret.conf', 'r' ) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    return config

