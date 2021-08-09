from configparser import ConfigParser


class Config():
    def __init__(self):
        self.token = self.get_param('bot', 'token')
        self.webhook_host = self.get_param('bot', 'webhook_host')
        self.webhook_path = self.get_param('bot', 'webhook_path')

    def get_param(self, section, param):
        """ Get parameter in section
        """
        config_file = "config.ini"
        conf = ConfigParser()
        conf.read(config_file)
        value = conf.get(section, param)
        return value
