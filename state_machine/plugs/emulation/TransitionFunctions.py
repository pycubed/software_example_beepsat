def announcer(source, destination, cubesat):
    print(f'We are transitioning from {source} -> {destination}!!!')
    print(f'We also have access to the cubesat object: {cubesat}')


def low_power_on(source, destination, cubesat):
    print('We should be turning off most of the cubesat\'s power hungry devices')


def low_power_off(source, destination, cubesat):
    print('We should be returning to normal opperations')
