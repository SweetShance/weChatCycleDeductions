官方文档
https://pay.weixin.qq.com/wiki/doc/api/wxpay_v2/papay/chapter3_2.shtml

config.py # 配置文件，默认参数
sign_req_data # 对每个接口所需数据进行整理
cycleDeductions.py # 周期扣款主函数
signStrategy.py # 多种签约方式的实现
utils.py # 相关工具 xml <-> dict 转换， 签名和验签

使用：
    直接调用 cycleDeductions 里的类方法即可
    配置：
        config 文件， 如果你的config 是在项目根目录，且写在 __init__.py, 那直接配置即可


