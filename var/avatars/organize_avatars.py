from max.rest.utils import get_avatar_folder
import os
import re
import shutil


OBJECT_ID_REGEX = re.compile(r'([abcdefABCDEF\d]{24}).png')
SHA1_REGEX = re.compile(r'([abcdefABCDEF\d]{40}).png')
USER_REGEX = re.compile(r'(.*?)(?:-(large))?\.png')

exclusions = []


def excluded(name):
    if 'missing' in name.lower():
        return True
    if 'readme' in name.lower():
        return True
    if name.lower().endswith('.py'):
        return True
    if name.lower().endswith('.pyc'):
        return True
    if name.lower().endswith('.jpg'):
        return True
    if filename in ['contexts', 'people', 'conversations']:
        return True
    return False

for filename in os.listdir('.'):
    if not excluded(filename):
        name = ''
        context = ''
        if SHA1_REGEX.match(filename):
            name = SHA1_REGEX.match(filename).groups()[0]
            context = 'contexts'
            size = ''
        elif OBJECT_ID_REGEX.match(filename):
            name = OBJECT_ID_REGEX.match(filename).groups()[0]
            context = 'conversations'
            size = ''
        elif USER_REGEX.match(filename):
            name, size = USER_REGEX.match(filename).groups()
            context = 'people'
            size = '' if size is None else size

        if name:
            avatar_folder = get_avatar_folder(os.getcwd(), context, name, size)
            new_filename = os.path.join(avatar_folder, name)

            shutil.move(filename, new_filename)
            print "MOVED {} --> {}".format(filename, new_filename)
        else:
            exclusions.append(filename)
    else:
        exclusions.append(filename)

print
for filename in exclusions:
    print 'EXCLUDED {}'.format(filename)
