# BlockContinuity
链节点区块连续性监控服务。



## 依赖

该服务使用python-sdk与链交互，在运行前，请先安装[Python-Middleware](https://github.com/Cocos-BCX/Python-Middleware)

## 配置

### 1. 配置链参数

将需要监控的链配置到[Python-Middleware](https://github.com/Cocos-BCX/Python-Middleware)中PythonMiddlewarebase/chains.py，默认已经配置了主网和测试网。

```python
default_prefix = "COCOS"

known_chains = {
    "prod": {
        "chain_id": "6057d856c398875cac2650fe33caef3d5f6b403d184c5154abbff526ec1143c4",
        "core_symbol": "COCOS",
        "prefix": "COCOS"
    },
    "testnet": {
        "chain_id": "1ae3653a3105800f5722c5bda2b55530d0e9e8654314e2f3dc6d2b010da641c5",
        "core_symbol": "COCOS",
        "prefix": "COCOS"
    }
}
```

### 2. 监控的链节点

> 这里只说明multi_nodes分支多节点版本，master分支单节点比较简单，可以类比，不再叙述。

​示例：

``` python
node_address_dict = {
    "mainnet-fn": "wss://api.cocosbcx.net",
    "testnet-fn": "wss://test.cocosbcx.net"
}
```

> 建议一个ws url对应一个节点。若一个ws url路由到多个节点，会发生混乱。

### 3. 配置钉钉消息推送地址

示例：

``` python
token = "00fe2e1e62a1db837133d5078fb5c5c4053c1383b20ac1b1d773458a096d9df0"
alert_address = "https://oapi.dingtalk.com/robot/send?access_token="+token
```



## 运行

```shell
python main.py
```

或执行脚本**start_d.sh**


