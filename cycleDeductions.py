import requests
from utils import Utils, SignUtils
from signStrategy import OfficialAccountsSign, AppSign, H5Sign
from sign_req_data import ( PreSignData, ApWithholdData, BeWithholdNotice, 
                           TerminationData, QueryOrderData, QuerySignData)


class CycleDeductions:
    """
        周期扣款服务
        1. 预签约
        2. 申请扣款
        3. 预扣费通知
        4. 商户侧解约
    """
   
    @staticmethod
    def to_pre_sign(sign_type: str, contract_code: str, contract_display_account: str, notify_url: str, **kwargs) -> dict:
        """
            预期签约接口
            @ sign_type: 签约方式
            @ contract_code: 签约协议号, 商户侧生成
            @ contract_display_account: 用户账户展示名称
            @ notify_url: 回调url
            @ kwargs： 附加数据， to_pre_sign_data默认缺少的数据，通过此参数加入
        """
        # 整理数据， 增加签名
        PreSignData.formate_data(contract_code, contract_display_account, notify_url, **kwargs)
        # 获取xml 格式， 带有签名的数据
        xml_data = PreSignData.get_data("xml", to_sign=True)
        # 将dict 类型数据转换为 xml 格式
        # 公众号签约
        if sign_type == "OA":
            res_data = OfficialAccountsSign.sign_method(xml_data)
        # App签约
        elif sign_type == "APP":
            res_data = AppSign.sign_method(xml_data)
        # h5 签约
        elif sign_type == "H5":
            res_data = H5Sign.sign_method(xml_data)
        else:
            res_data = {'return_code': False, 'return_msg': '没有该方式'}
        return res_data
    
    @staticmethod    
    def apply_for_withhold(body: str, out_trade_no: str, total_fee: int, notify_url: str, contract_id: str, **kwargs) -> dict:
        """
            申请扣款: 所有签约方式，申请扣款都会采用这种方式
            @ body:  商品或支付单简要描述
            @ out_trade_no: 订单号
            @ total_fee: 金额， 必须int否则会失败， 单位为 分
            @ notify_url: 扣款结果回调
            @ contract_id: 委托代扣id， 签约成功后返回到 签约回调里的
        """
         # 整理数据， 增加签名
        ApWithholdData.formate_data(body, out_trade_no, total_fee, notify_url, contract_id, **kwargs)
        # 获取 xml 带有签名的数据
        xml_data = ApWithholdData.get_data("xml", to_sign=True)
        url = "https://api.mch.weixin.qq.com/pay/pappayapply"
        res_data = SignUtils.request_ft(url, xml_data)
        return res_data
    
    @staticmethod
    def before_withhold_notify(contract_id: str, amount: int) -> dict:
        """
            预扣费通知
            @ contract_id: 委托代扣协议id
            @ amount: 扣款金额必须int， 单位 分
        """
        # 整理数据
        BeWithholdNotice.formate_data(contract_id, amount)
        # 获取 dict 不带签名的数据
        data = BeWithholdNotice.get_data("dict", to_sign=False)
        url = f"https://api.mch.weixin.qq.com/v3/papay/contracts/{contract_id}/notify"
        res_data = SignUtils.request_ft(url, data)
        return res_data
    
    @staticmethod
    def termination(contract_id: str, contract_termination_remark: str) -> dict:
        """
            商户侧解约
            @ contract_id: 委托代扣协议id
            @ contract_termination_remark:  解约备注
        """
         # 签名
        TerminationData.formate_data(contract_id, contract_termination_remark)
        # 获取 xml 带有签名的数据
        xml_data = TerminationData.get_data("xml", to_sign=True)
        url = "https://api.mch.weixin.qq.com/papay/deletecontract"
        res_data = SignUtils.request_ft(url, xml_data)
        return res_data
        

class SignOperation:
    """
        签约相关操作
        1. 查询订单
        2. 查询签约状态
    """
    @staticmethod
    def query_order(out_trade_no: str) -> dict:
        """ 
            查询订单 
            @ out_trade_no:  商户侧支付订单号
        """
        # 整理数据
        QueryOrderData.formate_data(out_trade_no)
         # 获取 xml 带有签名的数据
        xml_data = QueryOrderData.get_data("xml", to_sign=True)
        url = "https://api.mch.weixin.qq.com/pay/paporderquery"
        res_data = SignUtils.request_ft(url, xml_data)
        return res_data

    @staticmethod
    def query_sign_status(out_trade_no: str) -> dict:
        """
            查询签约状态， 使用模板id 和 签约协议号查询
            @ out_trade_no:  商户侧支付订单号
        """
        # 整理数据
        QuerySignData.formate_data(out_trade_no)
         # 获取 xml 带有签名的数据
        xml_data = QuerySignData.get_data("xml", to_sign=True)
        url = "https://api.mch.weixin.qq.com/papay/querycontract"
        res_data = SignUtils.request_ft(url, xml_data)
        return res_data



if __name__ == "__main__":
    # 调用app预期签约
    rt_data = CycleDeductions.to_pre_sign("APP", "010101010", "小明", "http://127.0.0.1", **{"return_app": "Y"})
    print(rt_data)
    # 申请扣款
    rt_data = CycleDeductions.apply_for_withhold("测试", "010101010", 5,  "http://127.0.0.1", "Wx15463511252015071056489715")
    print(rt_data)
    # 预扣费通知
    rt_data = CycleDeductions.before_withhold_notify("Wx15463511252015071056489715", 5)
    print(rt_data)
    