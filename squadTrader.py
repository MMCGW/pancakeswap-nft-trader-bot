from web3 import Web3
from web3.middleware import geth_poa_middleware
from config import MARKET_CONTRACT, MARKET_ABI
import time

# BSC NODE
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org/'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


marketContract = w3.eth.contract(address=MARKET_CONTRACT, abi=MARKET_ABI)


# YOU
ADDRESS = w3.toChecksumAddress('ADDRESS')
PRIVATE_KEY = str('PRIVATE_KEY').lower()


# TX SETTING
GAS = 400000
GAS_PRICE = 5000000000


def buyNFT(payableBNB, collection, tokenId):
    raw_tx = marketContract.functions.buyTokenUsingBNB(collection, tokenId).buildTransaction({
        'from': ADDRESS,
        'nonce': w3.eth.getTransactionCount(ADDRESS),
        'value': payableBNB,
        'gas': GAS,
        'gasPrice': GAS_PRICE,
    })
    signed_tx = w3.eth.account.signTransaction(raw_tx, private_key=PRIVATE_KEY)
    w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print('Bought! ')


def sellNFT(collection, tokenId, price):
    raw_tx = marketContract.functions.createAskOrder(collection, tokenId, price).buildTransaction({
        'from': ADDRESS,
        'nonce': w3.eth.getTransactionCount(ADDRESS),
        'value': 0,
        'gas': GAS,
        'gasPrice': GAS_PRICE,
    })
    signed_tx = w3.eth.account.signTransaction(raw_tx, private_key=PRIVATE_KEY)
    w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print('sell')


def handle_event(event):
    collection = event.args['collection']
    tokenId = event.args['tokenId']
    askPrice = event.args['askPrice']
    askPriceBNB = w3.fromWei(askPrice, "ether")

    if collection == '0x0a8901b0E25DEb55A87524f0cC164E9644020EBA':
        print(f'Listed: {tokenId} | {askPriceBNB} BNB')
        if askPriceBNB <= 5.8:  # if the price is bellow this value attempts to buy the nft
            print(f'{30*"="} Buying!! ==> | {askPriceBNB} BNB | {tokenId}')
            buyNFT(askPrice, collection, tokenId)


def log_loop(event_filter, poll_interval):
    while True:
        try:
            for event in event_filter.get_new_entries():
                handle_event(event)
            time.sleep(poll_interval)
        except Exception as e:
            print(e)


def main():
    event_filter = marketContract.events.AskNew.createFilter(fromBlock="latest")
    log_loop(event_filter, 5)


if __name__ == '__main__':
    main()
