"""作用：定义httpbin接口响应的JSON Schema结构约束。"""


GET_RESPONSE_SCHEMA = {
    'type': 'object',
    'required': ['args', 'headers', 'origin', 'url'],
    'properties': {
        'args': {'type': 'object'},
        'headers': {'type': 'object'},
        'origin': {'type': 'string'},
        'url': {'type': 'string', 'format': 'uri'},
    },
}

HEADERS_RESPONSE_SCHEMA = {
    'type': 'object',
    'required': ['headers'],
    'properties': {
        'headers': {'type': 'object'},
    },
}

POST_RESPONSE_SCHEMA = {
    'type': 'object',
    'required': ['args', 'data', 'files', 'form', 'headers', 'json', 'origin', 'url'],
    'properties': {
        'args': {'type': 'object'},
        'data': {'type': 'string'},
        'files': {'type': 'object'},
        'form': {'type': 'object'},
        'headers': {'type': 'object'},
        'origin': {'type': 'string'},
        'url': {'type': 'string', 'format': 'uri'},
    },
}

AUTH_RESPONSE_SCHEMA = {
    'type': 'object',
    'required': ['authenticated', 'user'],
    'properties': {
        'authenticated': {'const': True},
        'user': {'type': 'string', 'minLength': 1},
    },
    'additionalProperties': True,
}
