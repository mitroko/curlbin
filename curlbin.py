# Curl pastebin.
# License: GPLv2
# Author: Dmitriy Stremkovskiy: mitya@stremki.net
# Version: 13 Jul 2020

from cgi import parse_qs, escape
import magic
import random
import os

dic = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
store = '/var/spool/curlbin'
cycles = 20
hash_len = 4
upload_limit = 33554432
curlbins_limit = 100


def return_200(response,reason=''):

  headers = [
    ('Content-Type', 'text/plain'),
    ('Content-Length', '0'),
  ]
  if reason:
    headers.append(('X-Reason', '{0}'.format(reason)))
  response('200 OK', headers)
  return []


def return_302(responce,where,reason=''):

  headers = [
    ('Content-Type', 'text/plain'),
    ('Content-Length', '0'),
    ('Location', '{0}'.format(where)),
  ]
  if reason:
    headers.append(('X-Reason', '{0}'.format(reason)))
  responce('302 Found', headers)
  return []


def return_code(response,file_id):

  response('200 OK', [
    ('Content-Type', 'text/plain'),
    ('X-URL', '{0}'.format(file_id)),
  ])
  return ['%s\n' % file_id]


def return_data(response,url_f):

  if get_magic(url_f)[0:10] == 'ASCII text':
    ct = 'text/plain'
  else:
    ct = 'application/octet-stream'
  response('200 OK', [ ('Content-Type', ct) ])
  return [open(url_f).read()]


def build_site_url(environ, file_id):

  if 'APP_URL' in environ:
    return '%s/%s' % (environ['APP_URL'], file_id)

  scheme = 'http'
  server_name = 'localhost'
  server_port = ''

  if 'HTTPS' in environ and environ['HTTPS'] == 'on':
    scheme = 'https'
  if 'REQUEST_SCHEME' in environ:
    scheme = environ['REQUEST_SCHEME']
  if 'SERVER_PORT' in environ:
    if str(environ['SERVER_PORT']) == '80' and scheme == 'http':
      server_port = ''
    elif str(environ['SERVER_PORT']) == '443' and scheme == 'https':
      server_port = ''
    else:
      server_port = ':%s' % environ['SERVER_PORT']
  if 'SERVER_NAME' in environ:
    server_name = environ['SERVER_NAME']
  if 'HTTP_HOST' in environ:
    server_name = environ['HTTP_HOST']

  return '%s://%s%s/%s' % (scheme, server_name, server_port, file_id)


def get_magic(file_path):

  ms = magic.open(magic.NONE)
  ms.load()
  tp = ms.file(file_path)
  ms.close()
  return tp


def gen_id(length):

  global dic
  global store
  global cycles
  not_found = True
  i = 0
  while not_found and i < cycles:
    new = ''.join(random.sample(dic, length))
    new_f = '%s/%s' % (store, new)
    if os.path.isfile(new_f):
      i += 1
      continue
    else:
      open(new_f, 'w').close()
      not_found = False
  if i == cycles:
    return ''

  return new 


def check_file(environ):

  global store
  global hash_len

  lc = str(environ.get('REQUEST_URI', ''))[1:]

  lcal = len(lc.split('/'))
  lc = lc.split('/', lcal - 1)[-1]

  if not len(lc) == hash_len:
    return [False, 'Wrong url']

  url_f = '%s/%s' % (store, lc)
  if not os.path.isfile(url_f):
    return [False, 'No such file']

  return [True, url_f]


def application(environ, start_response):

  try:
    Method = str(environ.get('REQUEST_METHOD', ''))

  except:
    Method = 'GET'

  if Method == 'PUT':

    request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    if request_body_size > upload_limit:
      return return_200(start_response, 'Upload is limited to %s bytes' % str(upload_limit))

    if len(os.listdir(store)) >= curlbins_limit:
      return return_200(start_response, 'Upload is limited to %s elements' % str(curlbins_limit))

    request_body = environ['wsgi.input'].read(request_body_size)

    if request_body == None or request_body == '':
      return return_200(start_response, 'No data posted')

    new_id = gen_id(hash_len)
    if new_id:
      new_f = '%s/%s' % (store, new_id)
    else:
      return return_200(start_response, 'No free slots available, sorry')

    with open(new_f, 'w') as f:
      f.write(request_body)

    full_url = build_site_url(environ, new_id)
    return return_code(start_response, full_url)

  elif Method == 'DELETE':
    state, msg_or_f = check_file(environ)
    if not state:
      return return_200(start_response, msg_or_f)
    try:
      os.remove(msg_or_f)
    except:
      pass
    return return_200(start_response, 'OK. File deleted')

  elif Method != 'GET':
    return return_200(start_response, 'Wrong method')

  state, msg_or_f = check_file(environ)
  if not state:
    return return_200(start_response, msg_or_f)

  return return_data(start_response, msg_or_f)
