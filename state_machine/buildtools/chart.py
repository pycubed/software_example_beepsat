from StateMachineConfig import config


def format(v):
    (name, value) = v
    arr = value['StepsTo']
    return "\n".join(list(map(
        lambda to: f'   "{name}" -> "{to}"',
        arr
    )))


x = map(format, config.items())
x = '\n'.join(list(x))
x = 'digraph {\n'+x+'\n}'
print(x)

fo = open('graph.dot', "w")
fo.write(x)