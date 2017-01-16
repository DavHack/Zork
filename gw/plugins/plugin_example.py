import pluginManager as plugin

@plugin.matcher
def default_matcher(client_data):
    if not client_data.name.startswith('david'):
        return 'test'

@plugin.command('test')
def activate_foo(client_data):
    return {'command': 'run_eval', 'args': 'foo()'}

@plugin.reactor('test')
def process_foo(client_data, output):
    if output == 'foo':
        return 'Big success, Client return foo as expected.'
    return 'Failure, Client return {} instead of foo'.format(output)

print('Load complete')
