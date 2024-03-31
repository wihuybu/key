import re
import json
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
	return jsonify({'msg': 'Hello World!'})


@app.route('/tracking')
def tracking():
	try:
		arguments = request.args
		orderId = arguments.get('orderId', None)
		emailAdr = arguments.get('emailAddress', None)
		orderId = re.sub(r'[-\s]', '', orderId)

		check_id = lambda s: bool(re.match(r'^\d{15}$', s))
		check_email = lambda s: bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', s))

		if not (check_id(orderId) and check_email(emailAdr)):
			return jsonify({'msg': 'Something went wrong!', 'ok': False})

		payload = {
			'orderId': orderId,
			'emailAddress': emailAdr
		}

		payload_string = json.dumps(payload)

		url = 'https://www.walmart.com/orchestra/home/graphql/getGuestOrder/'
		url += 'fa3c094e674591bc46e8c6102e30b202c58fde1302532f7bff7306e76977a9c5'
		params = {'variables': payload_string}

		headers = {
				'authority': 'www.walmart.com',
				'accept': 'application/json',
				'accept-language': 'en-US',
				'content-type': 'application/json',
				'downlink': '10',
				'dpr': '1.14',
				'referer': 'https://www.walmart.com/orders/',
				'sec-ch-ua-mobile': '?0',
				'sec-ch-ua-platform': '"Windows"',
				'sec-fetch-dest': 'empty',
				'sec-fetch-mode': 'cors',
				'sec-fetch-site': 'same-origin',
				'user-agent':
				'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
				'wm_mp': 'true',
				'wm_page_url': 'https://www.walmart.com/orders/',
				'x-apollo-operation-name': 'getGuestOrder',
				'x-enable-server-timing': '1',
				'x-latency-trace': '1',
				'x-o-bu': 'WALMART-US',
				'x-o-ccm': 'server',
				'x-o-gql-query': 'query getGuestOrder',
				'x-o-mart': 'B2C',
				'x-o-platform': 'rweb',
				'x-o-platform-version':
				'us-web-1.127.0-14ef2d4b4491be5938a5fa20df7d77ad9264e136-0321',
				'x-o-segment': 'oaoh'
		}

		response = requests.get(url, headers=headers, params=params)
		data = response.json()
		groups_2101 = data['data']['guestOrder']['groups_2101'][0]
		status_data = groups_2101['status']
		if status_data['wasDelayed']: status = {'status': 'DELAY'}
		if status_data['showStatusTracker']:
			shipment = groups_2101['shipment']
			status = {'status': 'SHIPED', 'trackingNumber': int(shipment['trackingNumber'])}
		else: status = {'status': status_data['statusType']}
		status |= {'ok': True}
		return status

	except:
		return jsonify({'msg': 'Something went wrong!', 'ok': False})

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
