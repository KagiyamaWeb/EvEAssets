import urllib, urllib.parse
secret_key = '' #paste secret key here
client_params = {
'response_type' : 'code',
'redirect_uri' : 'http://localhost:5000/oauth-callback',
'client_id' : '', #paste client id here
'scope' : 'esi-skills.read_skillqueue.v1 esi-skills.read_skills.v1 esi-characterstats.read.v1 esi-wallet.read_character_wallet.v1 esi-characters.read_blueprints.v1 esi-assets.read_assets.v1',
'state' : '' #paste state here
}
#SSO_URL = 'https://login.eveonline.com/oauth/authorize?response_type=code&redirect_uri={}&client_id={}&scope={}'.format(urllib.parse.quote_plus(redirect_uri), client_id, urllib.parse.quote_plus(scopes))
SSO_URL = 'https://login.eveonline.com/v2/oauth/authorize?{}'.format(urllib.parse.urlencode(client_params))
AUTH_URL = 'https://login.eveonline.com/v2/oauth/token'
VERIFY_URL = 'https://esi.evetech.net/verify/'
