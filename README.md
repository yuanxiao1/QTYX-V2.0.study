为了帮助书籍《Python股票量化交易从入门到实践》读者建立一座从书本知识到实战应用之间的“桥梁”，我们会赠送股票量化分析工具QTYX学习版(V2.0)。

目的是提供给大家一个配套书籍的学习模版，帮助大家更好地掌握书籍的知识点，并且可以以这个模板为基础去搭建适合自己的量化系统！

需要注意版本号为V2.0.study。移植指南可参考如下链接：https://blog.csdn.net/hangzhouyx/article/details/113774922

同时，我们在知识星球中一直在迭代更新可供实战的QTYX版本，感兴趣的小伙伴可以关注我的微信公众号(元宵大师带你用Python量化交易)了解。 
最新版的使用攻略介绍，请点击: https://mp.weixin.qq.com/mp/homepage?__biz=MzUxMjU4NDAwNA==&hid=6&sn=81038d128b4ef94b01a1382e51359903

注意：
baostock 和 wxpython搭配不好会出现“日期格式不正确”报错，建议的版本搭配为：
Python3.7+wxpython4.0.4+baostock 0.8.8  

如果使用Python3.8，可参考如下配置【简单粗暴把baostock库的\site-packages\baostock\security\history.py文件的175至187行注释掉，重启Pycharm即可】：
Python3.8+wxpython4.1.1+baostock 0.8.8

2.3之后的版本已经增加第三方库tabulate，需要pip安装一下。Windows环境pip安装winreg库

在tushare官网注册账号获取token码（填写个人信息后有120积分）， 拷贝后填写到ConfigFiles/token.txt 文件中。从2.2.1版本开始，也可以不提供，随便填写字符即可。

Windows用户在启动后先点击【配置】页面，配置当前系统为Windows，点击保存。顶部的状态条可以返回到主菜单，然后再点击【量化】界面。

