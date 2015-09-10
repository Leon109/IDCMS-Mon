# IDCMS-Web

权限认证

使用 app.utils 中的 permission 模块
有一个权限认证Permisson 方法，获取用户属性对应的数字标志为值
可以讲将该方法传入模版中直接使用，方法参见 auth/__init__.py中的设置
用户权限属性通过 模型中的role 定义，用户登录后可以通过current_user.role获取

装饰器 参见 permission中的permission_validation  使用改装饰器如果没有权限认证会返回403错误

v0.5 一般注释都是 sales中,具体使用可以参考help
