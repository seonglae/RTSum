from aiohttp import ClientSession


class OpenIE5:
  def __init__(self, server_url):
    if server_url[-1] == '/':
      server_url = server_url[:-1]
    self.server_url = server_url
    self.extract_context = '/getExtraction'

  async def extract(self, text, session: ClientSession, properties=None):
    assert isinstance(text, str)
    if properties is None:
      properties = {}
    else:
      assert isinstance(properties, dict)

    try:
      data = text.encode('utf-8')
      async with session.post(self.server_url + self.extract_context,  params={
          'properties': str(properties)
      }, data=data, headers={'Connection': 'close'}) as response:
        res = await response.json(content_type=None)
        return res
    except Exception as e:
      print(e)
      raise Exception('Check whether you have started the OpenIE5 server')
