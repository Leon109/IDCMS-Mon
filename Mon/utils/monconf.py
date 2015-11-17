#coding=utf-8

import ConfigParser

# 配置文件目录
conf_path = '../config'

def config(conf_file, conf_name=None):
    '''confg_file 配置文件的名称
    conf_name  配置文件中项目的名称,如果为空择显示文件中有哪些配置
    名称
    '''
    # 使用ConfigParser读取ini配置文件
    cf = ConfigParser.ConfigParser()
    # 在构造对象之后设置 optionxform 属性为 str 即可区别保留大小写
    cf.optionxform = str
    # 获取配置文件路径
    conf_file = "%s/%s" % (conf_path, conf_file)
    # cls表示自身类这里也就是config
    cf.read(conf_file)
    if conf_name:
    # 获取数据的项目的数据（字典）注意这样ini和bool值等类型，会默认认为是字符串
        conf = cf.items(conf_name)
        return dict(conf)
    # 获取原始配置文件
    return cf

if __name__ == "__main__":
    # 使用方法举例
    all_conf = config('mon.conf')
    # 获取所有项目
    print all_conf.sections()
    # get方法总是返回字符串，类似的有getint，getfloat，getboolean分别返回整型，浮点值和布尔值
    # 获取log项目的debug 布尔值
    print all_conf.getboolean('nbnet', 'debug')
    # 获取特定项目所有参数
    trans = config('mon.conf', 'trans')
    print trans

