# -*- coding: utf-8 -*-

import json


class Result:

    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data

    def __str__(self):
        return 'Result{code=%s, message=%s, data=%s}' % (self.code, self.message, self.data)

    def standard_format(self):
        dict = {'code': self.code, 'message': self.message, 'data': self.data}
        return json.dumps(dict)


if __name__ == '__main__':
    result = Result(0, 'success', {'1': 1, '2': True, '3': ['a', 'b', 'c']})
    print(result.standard_format())
    print(len(' '))
    print(' '.isspace())
    print(''.isspace())
