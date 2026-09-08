import requests
import config


# 获取 access_token
token_url = (
    "https://api.weixin.qq.com/cgi-bin/token"
    "?grant_type=client_credential"
    f"&appid={config.WECHAT_APPID}"
    f"&secret={config.WECHAT_APPSECRET}"
)

token_data = requests.get(token_url).json()

if "access_token" not in token_data:
    print("获取token失败:")
    print(token_data)
    exit()

access_token = token_data["access_token"]


# 自定义菜单
menu = {
    "button": [
        {
            "name": "公司官网",
            "sub_button": {
                "list": [
                    {
                        "type": "view",
                        "name": "网站入口",
                        "url": "https://ty.xiaoshang88.meibu.net/"
                    },
                    {
                        "type": "view",
                        "name": "彤愿app下载",
                        "url": "https://ty.xiaoshang88.meibu.net/apk/shangji.apk"
                    },
                    {
                        "type": "view",
                        "name": "激活说明",
                        "url": "https://mp.weixin.qq.com/s/Xtp_qnfq0ZgjtjsbhsjjoQ"
                    }
                ]
            }
        },
        {
            "name": "上线广告",
            "sub_button": {
                "list": [
                    {
                        "type": "view",
                        "name": "外卖新出路",
                        "url": "https://mp.weixin.qq.com/s/ed-QM6mIryW2gSoEmUbaaA"
                    },
                    {
                        "type": "view",
                        "name": "投放广告",
                        "url": "https://mp.weixin.qq.com/s/AAb7nFTDYbOXD9iWutGsNw"
                    }
                ]
            }
        },
        {
            "name": "商集广场",
            "sub_button": {
                "list": [
                    {
                        "type": "view",
                        "name": "卡密激活介绍",
                        "url": "https://mp.weixin.qq.com/s/AAb7nFTDYbOXD9iWutGsNw"
                    }
                ]
            }
        }
    ]
}


url = (
    "https://api.weixin.qq.com/cgi-bin/menu/create"
    f"?access_token={access_token}"
)

r = requests.post(url, json=menu)

print(r.text)
