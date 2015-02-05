from jawbone import Jawbone
import webbrowser

jb= Jawbone('nEXyCKO3F3s', 'c9a66fc619ccb0e7c2c4e90e59200dfba8aea5de', 'http://localhost/login/jawbone', scope='basic_read extended_read')

redirect = jb.auth()

response = jb.api_call('r5ZHAAV8pCXUBg2Qya-xrn74bRKrSrIWj29SxzFeRjN0HCKkcBV4krGIYeF7UShXRPaV1mvF5JRRAnYEZaPxlCzIBmUT', 'nudge/api/v.1.0/sleep')

token = access_token('jF_LbmL3sgAtppKeiXW_-M_1H33wGhYwvLzEKq4NpEuSc5-fiPxYrjQ7b97G101kASfWbIWY51xp7CT9C2hu5vXgJbBeGENBqbKHdHLQYmK3BFnpMtk_v_1iHbrzUzvK8aEpsIodBknNWzhLq6VsNHIg8qpbXhP6-Bq-_TO0iJnk8lNHm2EhXXMmcJ9fyPcu')
print token


