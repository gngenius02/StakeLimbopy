#!/usr/bin/env python3
 
import json
import os
import signal
import urllib



############### Settings
#######################################################################################
currency = 'xrp'
betcountstop = 0                # stop rolling after x (set to 0 for unlimited)
amount = 0.00000001
maxbet = 0.1
betmulti = 1.01                 # multiplier to increase your bet amount by on loss
multiplierTarget = 1.01         # game hunt multtipler
api_token = ""
#######################################################################################


class GraphQLClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.token = None
        self.headername = None
 
    def execute(self, query, variables=None):
        return self._send(query, variables)
 
    def inject_token(self, token, headername='Authorization'):
        self.token = token
        self.headername = headername
 
    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}
        headers = {'Accept': 'application/json',
                   'Connection': 'keep-alive',
                   'Content-Type': 'application/json'}
 
        if self.token is not None:
            headers[self.headername] = '{}'.format(self.token)
 
        req = urllib.request.Request(self.endpoint, json.dumps(data).encode('utf-8'), headers)
 
        try:
            response = urllib.request.urlopen(req)
            return response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            print((e.read()))
            print('')
            return False

class Stake:
    def __init__(self):
        self.user = self.getBalance()
        
    def request(self, query, variables=None):
        client = GraphQLClient('https://api.stake.com/graphql')
        client.inject_token(api_token, 'x-access-token')
        result = client.execute(query, variables)
        return result

    def getBalance(self, currency=None):
        balances = self._getAllBalances()
        if currency == None:
            for balance in balances:
                current = balance['available']['currency']
                amount = balance['available']['amount']
                print("{:<10}{:<10}".format( '{}:'.format(current), "{:.8f}".format(amount)))
        else:
            for balance in balances:
                current = balance['available']['currency']
                if current == currency:
                    amount = balance['available']['amount']
                    print("{:<10}{:<10}".format( '{}:'.format(current), "{:.8f}".format(amount)))
                else:
                    continue
                
    def _getAllBalances(self):
        res = self._getUser()
        return res['data']['user']['balances']

    def _getUser(self):
        query = "query Balances($available: Boolean = false, $vault: Boolean = false) {user { id balances {available @include(if: $available) { currency amount} vault @include(if: $vault) { currency amount}}}}"
        res = self.request(query, variables = {"available": True})
        user = json.loads(res)
        print('{:<10}{}'.format('userid:',user['data']['user']['id']))
        return user

    def limboBet(self, betamount=0.0, currency='xrp', multiplierTarget=3.0):
        query = "mutation LimboBet($amount: Float!, $multiplierTarget: Float!, $currency: CurrencyEnum!) { limboBet(amount: $amount, currency: $currency, multiplierTarget: $multiplierTarget) { ...CasinoBetFragment state { ...LimboStateFragment }}} fragment CasinoBetFragment on CasinoBet { id payoutMultiplier amountMultiplier amount payout currency game user { id name } } fragment LimboStateFragment on CasinoGameLimbo { result multiplierTarget }"
        res = self.request(query, variables={ "amount": betamount , "currency": currency, "multiplierTarget": multiplierTarget })
        return res

## Counters
losscount = 0
betcount = 0
wincount = 0
worstLoss = 0
bestWin = 0

x100count = 138
x1000count = 265
x10000count = 265

lastx100 = 0
lastx1000 = 0
lastx10000 = 0


def play( betamount ):
    res = s.limboBet(betamount,currency,multiplierTarget)
    bet = json.loads(res)['data']['limboBet']
    result = bet['state']['result']
    user = bet['user']['name']
    target = bet['state']['multiplierTarget']
    lastbet = bet['amount']
    if result > target:
        win = True
    else:
        win = False
    print("BETAMOUNT: {:<10} | RESULT: {:<10} | WIN: {:<10} | USER: {:<15}".format("{:.8f}".format(lastbet),"{:.2f}".format(result), win, user))
    checkResults(result)
    if win:
        return amount
    else:
        if betamount >= maxbet:
            return maxbet
        else:
            return betamount * betmulti




def checkResults(result):
    global x10000count,x1000count,x100count,running,lastx100,lastx1000,lastx10000
    result = float(result)
    if result > 10000:
        lastx10000 = result
        x100count = 0
        x1000count = 0
        x10000count = 0
    elif result > 1000:
        lastx1000 = result
        x100count = 0
        x1000count = 0
        x10000count +=1
    elif result > 100:
        lastx100 = result
        x100count = 0
        x1000count +=1
        x10000count +=1
    else:
        x100count +=1
        x1000count +=1
        x10000count +=1
    if x100count >= 750 or x1000count >= 7500 or x10000count >= 75000:
        running = False
        print('we got a wild fuckin turkey, {} {} {}'.format(x100count,x1000count,x10000count))
    else:
        print('')
        print('x100: {:<10}|{:<10}|x1k: {:<10}|{:<10}| x10k: {:<10}|{:<10}'.format(x100count,'{:.2f}'.format(lastx100),x1000count,'{:.2f}'.format(lastx1000),x10000count,'{:.2f}'.format(lastx10000)))
        print('')
        print('')
        print('')
    

running = True;
s = Stake()
s.getBalance(currency)
nextamount = play(amount)

while running:
    nextamount = play(nextamount)

