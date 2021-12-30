import requests
import json
import telegram
import time
import configparser


def get_config(filepath: str) -> dict:
    config = configparser.ConfigParser()
    config.read(filepath, encoding='utf-8')
    items = config._sections
    items = dict(items)
    for item in items:
        items[item] = dict(items[item])
    return items


def ethereum_gas_now(authorization: str) -> dict:
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




def main():
    config = get_config('config.ini')
    bot_token = config['CONF']['bot_token']
    group_chat_id = config['CONF']['group_chat_id']
    set_gas = config['CONF']['set_gas']
    interval_time = int(config['CONF']['interval_time'])

    while 1:
        gas = gas_now()
        fast_gas = gas['data']['fast'] // 1000000000
        if fast_gas < int(set_gas):
            proxy = telegram.utils.request.Request(proxy_url='socks5://127.0.0.1:10808')
            bot = telegram.Bot(bot_token, request=proxy)
            bot.send_message(chat_id=group_chat_id, text=F"当前以太坊的gas为 {fast_gas} gwei")
            time.sleep(interval_time)


if __name__ == '__main__':
    main()
