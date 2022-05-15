为了帮助书籍《Python股票量化交易从入门到实践》读者建立一座从书本知识到实战应用之间的“桥梁”，我们会赠送股票量化分析工具QTYX V1.0和V2.0版本。

目的是提供给大家一个模版，可以以此为基础去搭建适合自己的量化系统！

同时，我们在知识星球中一直在迭代更新可供实战的QTYX版本，目前已经升级到了V2.4.2。在大家不断反馈和建议中，最新版QTYX不但增加了很多功能，还解决了很多V1.0和V2.0版本移植过程中所遇到的问题，在使用上也改进了很多。

为了帮助读者们更快地上手工具，同时我们也可以更集中精力在新版本的改进中，我们将最新版QTYX做了裁剪，除了未开放部分星球会员付费的功能外，其他的界面和操作方式上和最新版一致。

需要注意版本号为V2.0.study。

移植指南可参考如下链接：https://blog.csdn.net/hangzhouyx/article/details/113774922

最新版的视频介绍点击: https://zhuanlan.zhihu.com/p/467160411

感兴趣的小伙伴可以关注我的微信公众号：元宵大师带你用Python量化交易

注意：
baostock 和 wxpython搭配不好会出现“日期格式不正确”报错，建议的版本搭配为：
Python3.7+wxpython4.0.4+baostock 0.8.8  

如果使用Python3.8，可参考如下配置【简单粗暴把baostock库的\site-packages\baostock\security\history.py文件的175至187行注释掉，重启Pycharm即可】：
Python3.8+wxpython4.1.1+baostock 0.8.8

2.3之后的版本已经增加第三方库tabulate，需要pip安装一下。Windows环境pip安装winreg库

在tushare官网注册账号获取token码（填写个人信息后有120积分）， 拷贝后填写到ConfigFiles/token.txt 文件中。从2.2.1版本开始，也可以不提供，随便填写字符即可。

Windows用户在启动后先点击【配置】页面，配置当前系统为Windows，点击保存。顶部的状态条可以返回到主菜单，然后再点击【量化】界面。
