import json

config_file = open('./state_machine.json', 'r')
config = config_file.read()
config_file.close()
config = json.loads(config)

def format(v):
    (name, value) = v
    arr = value['StepsTo']
    return "\n".join(list(map(
        lambda to: f'   "{name}" -> "{to}"',
        arr
    )))


x = map(format, config.items())
x = '\n'.join(list(x))
x = 'digraph {\n' + x + '\n}'

fo = open('graph.dot', "w")
fo.write(x)
