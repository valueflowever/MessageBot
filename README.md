# 消息提醒机器人

## 功能如下：

1. 以太坊GAS提醒
    * 使用到的[GAS API文档](https://docs.blocknative.com/gas-platform)

2. coin价格提醒
    * 当大于或者小于设定价格时，tg发送提醒信息
    * coin实时价格使用了[coingecko API](https://www.coingecko.com/en/api/documentation) 
    * 查询ERC20代币在DEX中的实时价格，需要提供类uniswap合约的配对合约地址