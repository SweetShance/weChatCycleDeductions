from abc import ABCMeta, abstractstaticmethod
import requests
from utils import Utils


class SignStrategy(metaclass=ABCMeta):
    @abstractstaticmethod
    def sign_method():
        pass
    

class OfficialAccountsSign(SignStrategy):
    """ 公众号签约 """
    @staticmethod
    def sign_method(xml_data: str) -> dict:
        """
            @data: xml 格式
        """
        url = "https://api.mch.weixin.qq.com/papay/entrustweb"
        res_data = requests.get(url, data=xml_data)
        if res_data.status_code == 200:
            return {"return_code": "SUCCESS", 'return_msg': "无返回值"}
        return {"return_code": False, 'return_msg': "请求失败"}
        
    

class AppSign(SignStrategy):
    """ app 签约 """
    @staticmethod
    def sign_method(xml_data):
        """
            @ xml_data: xml格式数据
        """
        url = "https://api.mch.weixin.qq.com/papay/preentrustweb"
        # 请求接口
        res_data = requests.post(url, data=xml_data)
        if res_data.status_code == 200:
            dict_data = Utils.xml_to_dict(res_data.content)
            return dict_data
        else:
            return {"return_code": False, "return_msg": "接口请求失败"}
    

class H5Sign(SignStrategy):
    """ H5 签约 """
    @staticmethod
    def sign_method(xml_data):
        """
            @data: xml 格式
        """
        url = "https://api.mch.weixin.qq.com/papay/entrustweb"
        res_data = requests.get(url, data=xml_data)
        if res_data.status_code == 200:
            dict_data = Utils.xml_to_dict(res_data.content)
            return dict_data
        return {"return_code": False, 'return_msg': "请求失败"}
    