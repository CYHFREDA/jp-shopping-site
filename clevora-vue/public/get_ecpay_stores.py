import requests
import hashlib
import urllib.parse
import json

def gen_check_mac_value(params, hash_key, hash_iv):
    sorted_params = sorted(params.items())
    encode_str = f"HashKey={hash_key}&" + "&".join(f"{k}={v}" for k, v in sorted_params) + f"&HashIV={hash_iv}"
    encode_str = urllib.parse.quote_plus(encode_str).lower()
    check_mac = hashlib.md5(encode_str.encode('utf-8')).hexdigest().upper()
    return check_mac

merchant_id = "2000132"  # 綠界測試帳號
hash_key = "5294y06JbISpM5x9"
hash_iv = "v77hoKGq4kWxNNIS"

cvs_types = {
    "7-11": "UNIMART",
    "全家": "FAMI",
    "萊爾富": "HILIFE",
    "OK超商": "OKMART"
}

url = "https://logistics-stage.ecpay.com.tw/Helper/GetStoreList"
all_stores = []

for cvs_name, cvs_type in cvs_types.items():
    params = {
        "MerchantID": merchant_id,
        "CvsType": cvs_type,
        "PlatformID": ""
    }
    params["CheckMacValue"] = gen_check_mac_value(params, hash_key, hash_iv)
    resp = requests.post(url, data=params)
    data = resp.json()
    for store in data["StoreList"]:
        if store["CvsType"] == cvs_type:
            for info in store["StoreInfo"]:
                all_stores.append({
                    "cvs": cvs_name,
                    "id": info["StoreId"],
                    "store": info["StoreName"],
                    "address": info["StoreAddr"],
                    "phone": info["StorePhone"]
                })
    print(f"{cvs_name} 門市數量：{len(all_stores)}")

with open("all_cvs_stores.json", "w", encoding="utf-8") as f:
    json.dump(all_stores, f, ensure_ascii=False, indent=2)

print(f"已儲存所有超商門市到 all_cvs_stores.json，總數：{len(all_stores)}")