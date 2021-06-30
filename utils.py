import hashlib
import requests
from bs4 import BeautifulSoup
import config


class Utils():
    @staticmethod
    def dict_to_xml(dict_data) -> str:
        """ 将字典转换为签约需要的xml格式 """
        xml = """<xml>{}</xml>"""
        content = ""
        for k, v in dict_data.items():
            content += "<{key}>{value}</{key}>".format(key=k, value=v)
        return xml.format(content).encode("utf-8")
    
    @staticmethod
    def xml_to_dict(xml_data) -> dict:
        """ 将微信接口返回xml数据的转为 dict格式 """
        soup = BeautifulSoup(xml_data, features="xml")
        xml = soup.find('xml')  # 解析xml
        data_dict = dict([(item.name, item.text) for item in xml.find_all()])
        return data_dict

class SignUtils:
    @staticmethod
    def create_sign(data: dict) -> str:
        stringA = ""
        # 参数名ASCII码从小到大排序（字典序）
        for k in sorted(data):
            stringA += "{k}={v}&".format(k=k, v=data.get(k))
        # 拼接API密钥
        stringSignTemp = stringA + "key=%s" % config.weixin_key  # 注：key为商户平台设置的密钥
        # 加密
        md5 = hashlib.md5()
        md5.update(stringSignTemp.encode("utf-8"))
        sign = md5.hexdigest().upper()
        return sign
        
    @classmethod
    def check_sign(cls, data: dict) -> bool:
        # 微信返回的签名
        res_sign = data.pop("sign")
        # 根据数据生成的签名
        this_sign = cls.check_sign(data)
        if this_sign == this_sign:
            return True
        else:
            return False
        
    @staticmethod
    def request_ft(url: str, xml_data: str) -> dict:
        # 请求接口
        res_data = requests.post(url, data=xml_data)
        if res_data.status_code == 200:
            # 将xml转换为dict
            res_data_dict = Utils.xml_to_dict(res_data.content)
            return res_data_dict
        else:
            return {"return_code": False, 'return_msg': "请求失败"}