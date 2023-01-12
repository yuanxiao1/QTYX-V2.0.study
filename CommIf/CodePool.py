#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

from CommIf.SysFile import Base_File_Oper

class ManageSelfPool:

    def __init__(self, syslog_obj):
        self.syslog = syslog_obj

    def load_self_pool(self):
        # 加载自选股票池
        self_pool = Base_File_Oper.load_sys_para("stock_self_pool.json")
        self.syslog.re_print("从Json文件获取自选股票池成功...\n")
        return self_pool

    def save_self_pool(self, total_code):
        Base_File_Oper.save_sys_para("stock_self_pool.json", total_code)
        self.syslog.re_print("保存自选股票池至Json文件成功...\n")

    def load_pool_stock(self):
        # 加载自选股票池-个股
        return self.load_self_pool()["股票"]

    def load_pool_index(self):
        # 加载自选股票池-指数
        return self.load_self_pool()["指数"]

    def convert_code_format(self, codes):
        # 自适应转换代码格式成baostock格式

        for k, v in codes.items():
            if v.find('.') == 6: # tushare的代码格式
                code_split = v.lower().split(".")
                bs_code = code_split[1] + "." + code_split[0]  # tushare转baostock
                codes[k] = bs_code
            elif v.find('.') == -1:  # 正常代码格式
                codes[k] = "sh." + v if v[0] == '6' else "sz." + v # 行情转baostock
            else:
                codes[k] = v
        return codes

    def update_increase_st(self, new_code):
        # 增量更新
        st_code = self.load_self_pool()
        st_code['股票'].update(self.convert_code_format(new_code))
        self.save_self_pool(st_code)
        self.syslog.re_print("增量更新自选股票池成功...\n")

    def update_replace_st(self, new_code):
        # 完全替换
        st_code = self.load_self_pool()
        st_code['股票'].clear()
        st_code['股票'].update(self.convert_code_format(new_code))
        self.save_self_pool(st_code)
        self.syslog.re_print("完全替换自选股票池成功...\n")

    def delete_one_st(self, one_code):
        # 删除股票
        st_code = self.load_self_pool()
        st_code['股票'].pop(one_code)
        self.save_self_pool(st_code)
        self.syslog.re_print("删除自选股票池中{0}...\n".format(one_code))


class ManageTradePool:

    def __init__(self, syslog_obj, poolname="交易股票池", filename="trade_para.json"):
        self.syslog = syslog_obj
        self.filename = filename
        self.poolname = poolname

    def load_total_info(self):
        # 加载交易股票池
        self_trade = Base_File_Oper.load_sys_para(self.filename)
        self.syslog.re_print(f"从Json文件获取{self.poolname}成功...\n")
        return self_trade

    def load_name_code(self):
        # 返回股票名称和代码-字典

        name_code_dict = dict()
        trade_info = self.load_total_info()

        for k, v in trade_info.items():
            name_code_dict[k] = v['code']

        return name_code_dict

    def save_trade_pool(self, total_code):
        Base_File_Oper.save_sys_para(self.filename, total_code)
        self.syslog.re_print(f"保存{self.poolname}至Json文件成功...\n")

    def load_trade_stock(self, name):
        # 加载自选股票池-个股
        return self.load_total_info()[name]

    def convert_code_format(self, codes):
        # 自适应转换代码格式成baostock格式

        for k, v in codes.items():
            if v.find('.') == 6: # tushare的代码格式
                code_split = v.lower().split(".")
                bs_code = code_split[1] + "." + code_split[0]  # tushare转baostock
                codes[k] = bs_code
            elif v.find('.') == -1:  # 正常代码格式
                codes[k] = "sh." + v if v[0] == '6' else "sz." + v # 行情转baostock
            else:
                codes[k] = v
        return codes

    def update_increase_st(self, new_stock):
        # 增量更新
        st_code = self.load_total_info()
        st_code.update(new_stock)
        self.save_trade_pool(st_code)
        self.syslog.re_print(f"增量更新{self.poolname}成功...\n")

    def update_replace_st(self, new_name):
        # 完全替换
        st_code = self.save_trade_pool()
        st_code.clear()
        st_code.update(self.convert_code_format(new_name))
        self.save_trade_pool(st_code)
        self.syslog.re_print(f"完全替换{self.poolname}成功...\n")

    def delete_one_st(self, one_name):
        # 删除股票
        code_info = self.load_total_info()
        code_info.pop(one_name)

        self.save_trade_pool(code_info)
        self.syslog.re_print(f"删除{self.poolname}中{one_name}...\n")
