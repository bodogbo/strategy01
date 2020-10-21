package main

import (
	"fmt"
	"time"

	"github.com/sirupsen/logrus"
	"github.com/tidwall/gjson"

	"github.com/gorilla/websocket"
)

type WebsocketClient struct {
	conn       *websocket.Conn
	authed     int
	secret     []byte
	apiKey     string
	subAccount string

	onOrderChange func(body []byte)
}

func (client *WebsocketClient) loop() {
	conn := client.conn
	defer conn.Close()

	for {
		conn.SetReadDeadline(time.Now().Add(time.Minute))
		_, b, err := conn.ReadMessage()
		if err != nil {
			logrus.WithError(err).Errorln("conn.ReadMessage")
			break
		}

		type_ := gjson.GetBytes(b, "type").String()
		channel := gjson.GetBytes(b, "channel").String()

		logrus.Printf("websocket: %s", string(b))
		switch type_ {
		case "update":
			switch channel {
			case "orders":
				if client.onOrderChange != nil {
					client.onOrderChange(b)
				}
			}
		}
	}
}

func (client *WebsocketClient) ping() error {
	body := `{"op": "ping"}`
	if err := client.send(websocket.TextMessage, []byte(body)); err != nil {
		client.authed = -1
		return err
	}
	return nil
}

func (client *WebsocketClient) close() {
	client.conn.Close()
}

func (client *WebsocketClient) login() error {
	ts := time.Now().UnixNano() / int64(time.Millisecond)
	signature := sign(fmt.Sprintf("%dwebsocket_login", ts), client.secret)
	body := fmt.Sprintf(`{"op": "login", "args": {"key": "%s", "sign": "%s", "time": %d, "subaccount":"%s"}}`, client.apiKey, signature, ts, client.subAccount)
	if err := client.send(websocket.TextMessage, []byte(body)); err != nil {
		client.authed = -1
		return err
	}
	return nil
}

func (client *WebsocketClient) send(t int, body []byte) error {
	logrus.Println("send", string(body))
	if err := client.conn.WriteMessage(t, body); err != nil {
		return err
	}
	return nil
}

func (client *WebsocketClient) subOrder() error {
	if err := client.send(websocket.TextMessage, []byte(`{"op": "subscribe", "channel": "orders"}`)); err != nil {
		return err
	}

	return nil
}

func (client *WebsocketClient) subDepths(market string) error {
	body := fmt.Sprintf(`{"op": "subscribe", "channel": "orderbook", "market": "BTC-PERP"}`)
	if err := client.send(websocket.TextMessage, []byte(body)); err != nil {
		return err
	}
	return nil
}

func (client *WebsocketClient) dial(auth bool) error {
	c, _, err := websocket.DefaultDialer.Dial("wss://ftx.com/ws/", nil)
	if err != nil {
		return err
	}
	logrus.Println("connected")
	client.conn = c
	go client.loop()
	go func() {
		defer client.close()
		for {
			time.Sleep(time.Second * 15)
			if client.ping() != nil {
				break
			}
		}
	}()

	if auth {
		client.login()

		time.Sleep(time.Millisecond * 100)
		deadline := time.Now().Add(time.Second * 10)
		for time.Now().Before(deadline) && client.authed == 0 {
			time.Sleep(time.Millisecond * 100)
		}
		logrus.Println("auth result", client.authed)

		if client.authed == 0 {
			return fmt.Errorf("auth timeout")
		}

		if client.authed < 0 {
			return fmt.Errorf("auth failed")
		}
	}

	return nil
}
