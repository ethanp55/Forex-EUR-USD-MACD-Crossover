from os import environ

config_vars = {
    'host_name': environ['HOST_NAME'],
    'streaming_host_name': environ['STREAMING_HOST_NAME'],
    'port': environ['PORT'],
    'ssl': environ['SSL'],
    'api_token': environ['API_TOKEN'],
    'username': environ['USER_NAME'],
    'date_format': environ['DATE_FORMAT'],
    'time_zone': environ['TIME_ZONE'],
    'account': environ['ACCOUNT']
}


class Config(object):

    @staticmethod
    def get_host_name():
        return config_vars['host_name']

    @staticmethod
    def get_streaming_host_name():
        return config_vars['streaming_host_name']

    @staticmethod
    def get_port():
        return config_vars['port']

    @staticmethod
    def get_ssl():
        return config_vars['ssl']

    @staticmethod
    def get_api_token():
        return config_vars['api_token']

    @staticmethod
    def get_username():
        return config_vars['username']

    @staticmethod
    def get_date_format():
        return config_vars['date_format']

    @staticmethod
    def get_time_zone():
        return config_vars['time_zone']

    @staticmethod
    def get_account():
        return config_vars['account']
