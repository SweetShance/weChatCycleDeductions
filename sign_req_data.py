import time
import string
import random
from abc import ABCMeta, abstractclassmethod
from utils import SignUtils, Utils
import config

class SignReqDataAbstract(metaclass=ABCMeta):
    """
        相关接口数据整理， 抽象方法， 所有具体接口重写 format_data 方法， 然后通过 get_data() 方法获取相应数据
        0. 重置data数据
        1. 获取时间戳
        2. 获取请求序列号
        3. 随机字符串
        4. 数据整理
        5. 获取正确数据
    """
    data = {} # 存各个接口的所需数据
    
    @classmethod
    def set_default_data(cls):
        """ 重置data数据 因为类属性，内容不断添加，所以重置一下 """
        cls.data = {
        "appid": config.appid,
        "mch_id": config.mch_id,
    }
    
    @staticmethod
    def get_time() -> str:
        """ 时间戳 """
        time_str = str(time.time())[:10]
        return time_str
    
    @staticmethod
    def serial_number() -> str:
        """ 请求序列号  13 + 3"""
        serial_ = str(time.time()*1000)[:-5] + ''.join(random.sample(string.digits, 3))
        return serial_
    
    @staticmethod
    def nonce_str() -> str:
        """ 随机字符串 """
        nonce_str_ = "".join(random.sample(string.ascii_letters + string.digits, 16))
        return nonce_str_
    
    @abstractclassmethod
    def formate_data(cls):
        pass
    
    @classmethod
    def get_data(cls, data_type: str, to_sign=True):
        """
            获取数据
            @ data_type: 所需数据样式， xml / dict
            @ to_sign: 是否需要签名
        """
        # 如果需要签名
        if to_sign:
            cls.data["sign"] = SignUtils.create_sign(cls.data)
        if data_type == "xml":
            xml_data = Utils.dict_to_xml(cls.data)
            return xml_data
        else:
            return cls.data
    
    
class PreSignData(SignReqDataAbstract):
    """ 预签约数据整理 """
    @classmethod
    def formate_data(cls, contract_code: str, contract_display_account: str, notify_url: str, **kwargs) -> bytes:
        """
            @ contract_code: 签约协议号， 由客户端生成
            @ contract_display_account： 用户账户展示名称不支持UTF8非3字节编码的字符
            @ notify_url: 签约回调
            @ kwargs: 附加数据， 例如 return_app, return_web, return_appid, 书写的时候根据文档，看下少些什么传过来
        """
        # 重置data数据
        cls.set_default_data()
        cls.data["plan_id"] = config.plan_id
        cls.data["contract_code"] = contract_code
        cls.data["request_serial"] = cls.serial_number()
        cls.data["contract_display_account"] = contract_display_account
        cls.data["notify_url"] = notify_url
        cls.data["version"] = "1.0"
        cls.data["sign_type"] = "MD5"
        cls.data["timestamp"] = cls.get_time()
        for key, value in kwargs.items():
            cls.data[key] = value


class ApWithholdData(SignReqDataAbstract):
    @classmethod
    def formate_data(cls, body: str, out_trade_no: str, total_fee: int, notify_url: str, contract_id: str, **kwargs) -> bytes: 
        """ 
            申请扣款数据
            数据文档 https://pay.weixin.qq.com/wiki/doc/api/wxpay_v2/papay/chapter3_8.shtml
            @ body:  商品或支付单简要描述
            @ out_trade_no: 订单号
            @ total_fee: 金额， 必须int否则会失败， 单位为 分
            @ notify_url: 扣款结果回调
            @ contract_id: 委托代扣id， 签约成功后返回到 签约回调里的
            
            return : xml 格式数据
        """
        # 重置data数据
        cls.set_default_data()
        cls.data["nonce_str"] = cls.nonce_str()  #随机字符串
        cls.data["body"] =  body   # 商品或支付单简要描述
        cls.data["out_trade_no"] = out_trade_no  # 订单号
        cls.data["total_fee"] = total_fee  # 总金额
        cls.data["fee_type"] = "CNY" 
        cls.data["notify_url"] = notify_url  # 扣款回调
        cls.data["trade_type"] = "PAP"
        cls.data["contract_id"] = contract_id # 委托代扣id 
        for key, value in kwargs.items():
            cls.data[key] = value
            

class BeWithholdNotice(SignReqDataAbstract):
    """ 预扣费通知数据 """
    @classmethod
    def formate_data(cls, contract_id: str, amount: int):
        """ v3 接口 不需要xml
            数据文档：
            https://pay.weixin.qq.com/wiki/doc/api/wxpay_v2/papay/chapter3_10.shtml
            @ contract_id: 委托代扣协议id
            @ amount: 扣款金额必须int， 单位 分
            return 字典
        """
        # 重置data数据
        cls.set_default_data()

        cls.data["mchid"] = config.mch_id,
        cls.data["appid"] = config.appid,
        cls.data["contract_id"] = contract_id,
        cls.data["estimated_amount"] = {"amount": amount, "currency": "CNY"}
        

class TerminationData(SignReqDataAbstract):
    """ 商户申请解约数据 """
    @classmethod
    def formate_data(cls, contract_id: str, contract_termination_remark: str):
        """
            @ contract_id: 委托代扣协议id
            @ contract_termination_remark:  解约备注
        """
        # 重置data数据
        cls.set_default_data()
        
        cls.data["appid"] = config.appid,
        cls.data["mch_id"] = config.mch_id,
        cls.data["contract_id"] = contract_id,
        cls.data["contract_termination_remark"] = contract_termination_remark,
        cls.data["version"] = "1.0"
        
        
class QueryOrderData(SignReqDataAbstract):
    """ 查询订单所需数据 """
    @classmethod
    def formate_data(cls, out_trade_no: str):
        """
            @ out_trade_no:  商户侧支付订单号
        """
        # 重置data数据
        cls.set_default_data()

        cls.data["out_trade_no"] = out_trade_no  # 支付订单号
        cls.data["nonce_str"] = cls.nonce_str


class QuerySignData(SignReqDataAbstract):
    """ 查询签约状态 """
    @classmethod
    def formate_data(cls, contract_id: str):
        """
            @ out_trade_no:  商户侧支付订单号
        """
        cls.data["contract_id"]: contract_id  # 支付订单号
        cls.data["nonce_str"]: cls.nonce_str


if __name__ == "__main__":
    PreSignData.formate_data( "010101010", "小明", "http://127.0.0.1", **{"return_app": "Y"})
    print(PreSignData.get_data("xml", to_sign=True))