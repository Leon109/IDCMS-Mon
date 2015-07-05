#coding=utf-8

import os
import ConfigParser

work_path = os.path.dirname(os.path.realpath(__file__))
conf_path = "%s/%s" % (work_path, '../config')

def config(conf_file, conf_name=None):
    '''confg_file 配置文件的名称
    conf_name  配置文件中项目的名称,如果为空择显示文件中有哪些配置
    名称
    '''
    cf = ConfigParser.ConfigParser()
    cf.optionxform = str
    conf_file = "%s/%s" % (conf_path, conf_file)
    cf.read(conf_file)
    if conf_name:
        conf = cf.items(conf_name)
        return dict(conf)
    return cf.sections()

if __name__ == "__main__":
    f = config('nbnet', 'trans')
    print f
    print f['ff_l'].split(';')
