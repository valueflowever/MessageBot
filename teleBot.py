import requests
import telegram
import time
import configparser
import datetime

from params import proxies


def get_config(filepath: str) -> dict:
    config = configparser.ConfigParser()
    config.read(filepath, encoding='utf-8')
    items = config._sections
    items = dict(items)
    for item in items:
        items[item] = dict(items[item])
    return items


def get_ethereum_gas_now(authorization: str) -> dict:
    """
    数据API：https://docs.blocknative.com/gas-platform
    数据每 15s 更新一次，请勿发送请求过于频繁
    """
    url = 'https://api.blocknative.com/gasprices/blockprices'
    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
    }
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {}


def get_eth_price() -> float:
    """
    api_doc https://www.coingecko.com/en/api/documentation
    :return: eth price
    """
    api_url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
    resp = requests.get(api_url, proxies=proxies)
    if resp.status_code == 200:
        return resp.json()['ethereum']['usd']
    else:
        raise Exception('error')


def get_pool_token_price(pair_address: str) -> dict:
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    url = f'https://www.dextools.io/chain-ethereum/api/uniswap/poolx?pairSelected={pair_address}'
    resp = requests.get(url, headers=headers)
    resp = resp.json()
    eth_amount = resp['data']['pair']['reserve1']
    eth_price_amount = eth_amount * get_eth_price()
    tgt_amount = resp['data']['pair']['reserve0']
    token_price_now = eth_price_amount / tgt_amount
    message = {
        'symbol': resp['data']['pair']['token0']['symbol'],
        'price': token_price_now,
        'time': str(datetime.datetime.now())
    }
    return message


def send_message(config: dict, remind_type: str, threshold: float):
    bot_token = config['CONF']['bot_token']
    group_chat_id = config['CONF']['group_chat_id']
    proxy = telegram.utils.request.Request(proxy_url='socks5://127.0.0.1:10808')
    bot = telegram.Bot(bot_token, request=proxy)
    if remind_type == 'gas':
        authorization = config['GAS']['authorization']
        gas = get_ethereum_gas_now(authorization)['blockPrices'][0]['estimatedPrices'][2]['price']
        if gas < int(threshold):
            bot.send_message(chat_id=group_chat_id, text=F"当前gas为{gas}")

    if remind_type == 'price':
        pair_address = config['PRICE']['pair_address']
        token_message = get_pool_token_price(pair_address)
        if float(token_message['price']) >= float(threshold):
            bot.send_message(chat_id=group_chat_id,
                             text=F"当前时间: {token_message['time']}, 关注的{token_message['symbol']} 价格为{token_message['price']}")


def main():
    config = get_config('config.ini')
    interval_time = int(config['CONF']['interval_time'])
    while 1:
        open_gas_remind = config['GAS']['open']
        open_price_remind = config['PRICE']['open']
        if open_gas_remind:
            gas_threshold = config['GAS']['remind_gas']
            send_message(config, 'gas', gas_threshold)
        if open_price_remind:
            price_threshold = config['PRICE']['remind_price']
            send_message(config, 'price', price_threshold)
        time.sleep(interval_time)


if __name__ == '__main__':
    main()
