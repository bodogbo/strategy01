import math
from decimal import Decimal
import requests


# 币对设置
# 最小下单price精度
minPrice = 0.001
# 最小下单量
minQty = 0.1

# 4h BOLL
# todo 如何选择设置BOLL指标

class BOLL:
    # 上线
    UB = 3.3072
    # 中线  中线附近可以增加机会，减少网格幅度
    MB = 3.0542
    # 下线
    LB = 2.8013

# 小网格点差百分比
smalGridGapPecent = 0.02
# 中网格点差百分比
midGridGapPecent = 0.056

# 网格最低下限位置
lowLimitPrice = 0
# 网格最高上限位置
highLimitPrice = 99999999999

def roundTo(value: float, target: float) -> float:
    """
    Round price to price tick value.
    """
    value = Decimal(str(value))
    target = Decimal(str(target))
    rounded = float(int(round(value / target)) * target)
    return rounded

# price价格转换为最小精度
def priceRoundToMinPrice(value: float) -> float:
    return roundTo(value, minPrice)

# qty最小下单量转换为最小精度
def qtyRoundToMinQty(value: float) -> float:
    return roundTo(value, minQty)

def calLowLimitPrice(rate=0):
    global lowLimitPrice
    lowLimitPrice = priceRoundToMinPrice(BOLL.LB * (1-rate))

def calHighLimitPrice(rate=0):
    global highLimitPrice
    highLimitPrice = priceRoundToMinPrice(BOLL.UB * (1+rate))

# 每个格子的定义
class Grid(object):
    # # 买入价格
    # openPrice = 0
    # # 卖出价格
    # closePrice = 0
    # # 买入机会 == 买入基币的数量
    # openChance = 0
    # # 卖出机会
    # closeChance = 0
    # # 每次买入基币的数量 (暂时默认等于买入机会)
    # qty = openChance

    def __init__(self, openPrice=0, closePrice=0, openChance=0, closeChance=0, qty=0):
        self.openPrice = openPrice
        self.closePrice = closePrice
        self.openChance = openChance
        self.closeChance = closeChance
        self.qty = qty
        pass

    @property
    def open_chance(self):
        return self.openChance

    def print(self):
        print(f"{self.openPrice},{self.closePrice},{self.openChance},{self.closeChance},{self.qty},0,0,0")
        pass

gGrids = [
]


def genMinGrids(curPrice, rate=0.02, qty=5):
    calHighLimitPrice()
    calLowLimitPrice()
    global lowLimitPrice, highLimitPrice

    # 进入网格的最近买价
    enterOpenPrice = priceRoundToMinPrice(curPrice * (1-rate*0.5))
    realLowLimitPrice = enterOpenPrice
    while realLowLimitPrice > lowLimitPrice:
        realLowLimitPrice = priceRoundToMinPrice(realLowLimitPrice*(1-rate))

    print(f"realLowLimitPrice:{realLowLimitPrice}, lowLimitPrice:{lowLimitPrice}")
    openPrice = lowLimitPrice
    cnt = 0
    curMinQty = qtyRoundToMinQty(qty*0.65)
    while openPrice < highLimitPrice:
        closePrice = priceRoundToMinPrice(openPrice * (1+rate))
        openChance = qtyRoundToMinQty(qty - cnt*0.1)
        if openChance < curMinQty:
            openChance = curMinQty

        closeChance = 0
        grid = Grid(openPrice, closePrice, openChance, closeChance, openChance)
        gGrids.append(grid)
        # openPrice = priceRoundToMinPrice(closePrice * (1-0.005))
        openPrice = priceRoundToMinPrice(closePrice*(1-0.0005))
        cnt += 1
        pass
    pass

def getMarketTradeFromFtx(symbol):
    # https://ftx.com/api/markets/UNI-PERP/trades?limit=1
    """
    获取实时的最新交易数据 by symbol
    :param symbol:
    :return:
    {
"result": [
{
"id": 150681574,
"liquidation": false,
"price": 3.062,
"side": "buy",
"size": 49,
"time": "2020-10-23T07:32:14.365435+00:00"
}
],
"success": true
}
    """

    headers = {}
    payload = {
        'limit': 1,
    }

    url = f"https://ftx.com/api/markets/{symbol}/trades"
    timeout = 10

    try:
        with requests.Session() as sess:
            # try to do at least once
            for i in range(2):
                # do handle http requests
                resp = sess.get(url, params=payload, headers=headers, timeout=timeout)
                if resp.status_code != requests.codes.ok:
                    continue

                json_resp = resp.json()
                if resp.raise_for_status() is not None:
                    continue

                print(json_resp)
                if not json_resp.get('success') or not json_resp.get('success'):
                    print("1")
                    break

                if not json_resp.get('result'):
                    print("2")
                    break

                datas = json_resp.get('result')
                if len(datas) < 1:
                    print("getMarketTradeFromFtx failed datas empty")
                    return

                return datas[0]
    except:
        raise Exception('get market trade failed')

    return None


if __name__ == '__main__':
    lastTrade = getMarketTradeFromFtx("UNI-PERP")
    # 最大累计买入个数
    maxTotalQtyForBuy = 0

    curPrice = lastTrade["price"]
    print(f"lastTradePrice: {curPrice}")

    genMinGrids(curPrice)
    print(f"UNI-PERP,UNI-PERP,,,,,,")
    print(f"openPrice,closePrice,openChance,closeChance,qty,closeOnly,openOnly,oneShoot")
    for grid in gGrids:
        grid.print()
        maxTotalQtyForBuy += grid.open_chance



    print(f"")
    print(f"")
    print(f"")
    print(f"maxTotalQtyForBuy: {maxTotalQtyForBuy}")


