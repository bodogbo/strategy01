package main

import "github.com/sirupsen/logrus"

func recoverGridFromOpenOrdersOnInit() (err error) {
	// 定时刷新订单状态
	orders, err := client.getOrders(perpName)
	if err != nil {
		logrus.WithError(err).Errorln("recoverGridFromOpenOrdersOnInit GetOpenOrders")
		return
	}

	for _, order := range orders {
		if order.Side == "sell" {
			// 找到 orderPrice 的卖单对应的grid
			grid := getTradeGridByClosePrice(order.Price)
			if nil == grid {
				// todo senddingding
				continue
			}

			grid.CloseChance += order.RemainingSize

		} else {

		}
	}

	return
}

func getTradeGridByOpenPrice(openPrice float64) (grid *TradeGrid) {
	for _, grid := range gGrids {
		if grid.OpenAt != openPrice {
			continue
		}

		return grid
	}

	return
}

func getTradeGridByClosePrice(openPrice float64) (grid *TradeGrid) {
	for _, grid := range gGrids {
		if grid.CloseAt != openPrice {
			continue
		}

		return grid
	}

	return
}
