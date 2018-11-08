#                                                django的一些用法笔记
view:	
	 请求体 a.request.body()  
	 源碼中post files等这些方法都是在request.body中去取相应的内容
		request.POST(request.body)     
		request.FILES(request.body)  
		request.GET


	在django中没有 request.put  request.delete 这些方法 如果想用怎么办呢？
	依靠request.body 自己去取相应的数据 

	b.request.Meta()
		request.method(POST,GET,PUT)
		request.path_info
		request.COOKIES




知识点概要
    - Session
    - CSRF
    - Model操作
    - Form验证（ModelForm）
    - 中间件
    - 缓存
    - 信号


内容详细：

1. Session  
	使用session时要创建表结构  python manage.py makemigrations migrate
	django 默认将session保存在数据库中

	基于Cookie做用户验证时：敏感信息不适合放在cookie中
	

    a. Session原理
		Cookie是保存在用户浏览器端的键值对
		Session是保存在服务器端的键值对
	
    b. Cookie和Session对比
    
    c. Session配置(缺少cache)
    
    d. 示例：实现两周自动登陆
            - request.session.set_expiry(60*10)
            - SESSION_SAVE_EVERY_REQUEST = True

    PS: cookie中不设置超时时间，则表示关闭浏览器自动清除
	
	
    session 的使用：
 
	    def index(request):
	        # 获取、设置、删除Session中数据
	        request.session['k1']
	        request.session.get('k1',None)
	        request.session['k1'] = 123
	        request.session.setdefault('k1',123) # 存在则不设置
	        del request.session['k1']
	 
	        # 所有 键、值、键值对
	        request.session.keys()
	        request.session.values()
	        request.session.items()
	        request.session.iterkeys()
	        request.session.itervalues()
	        request.session.iteritems()
	 
	 
	        # 用户session的随机字符串
	        request.session.session_key
	 
	        # 将所有Session失效日期小于当前日期的数据删除
	        request.session.clear_expired()
	 
	        # 检查 用户session的随机字符串 在数据库中是否
	        request.session.exists("session_key")
	 
	        # 删除当前用户的所有Session数据
	        request.session.delete("session_key")
	 
	        request.session.set_expiry(value)
	            * 如果value是个整数，session会在些秒数后失效。
	            * 如果value是个datatime或timedelta，session就会在这个时间后失效。
	            * 如果value是0,用户关闭浏览器session就会失效。
	            * 如果value是None,session会依赖全局session失效策略。


	- session依赖于cookie
	- 服务器session
		获取当前用户随机字符串，根据随机字符串获取对应信息
		request.session['is_login']

		在session中设置值：
		request.session["username"]=user

		request.session.get()
		request.session[x] = x
		
		request.session.clear()
		
	- 配置文件中设置默认操作（通用配置）：
		SESSION_COOKIE_NAME ＝ "sessionid"                       # Session的cookie保存在浏览器上时的key，即：sessionid＝随机字符串（默认）
		SESSION_COOKIE_PATH ＝ "/"                               # Session的cookie保存的路径（默认）
		SESSION_COOKIE_DOMAIN = None                             # Session的cookie保存的域名（默认）
		SESSION_COOKIE_SECURE = False                            # 是否Https传输cookie（默认）
		SESSION_COOKIE_HTTPONLY = True                           # 是否Session的cookie只支持http传输（默认）
		SESSION_COOKIE_AGE = 1209600                             # Session的cookie失效日期（2周）（默认）
		SESSION_EXPIRE_AT_BROWSER_CLOSE = False                  # 是否关闭浏览器使得Session过期（默认）
		# set_cookie('k',123)
		SESSION_SAVE_EVERY_REQUEST = False                       # 是否每次请求都保存Session，默认修改之后才保存（默认） 	
																 # 可以保证在最后一次操作时间之后的2周时间都保存session

	- 引擎的配置
	 	缓存Session   将session存在缓存中
	 		配置 settings.py
			SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # 引擎
    		SESSION_CACHE_ALIAS = 'default'                            # 使用的缓存别名（默认内存缓存，也可以是memcache），此处别名依赖缓存的设置

    		 CACHES = {
		        'default': {
		            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
		            'LOCATION': '127.0.0.1:11211',
		        			}
		    			}

    	文件Session
    		配置 settings.py

    		SESSION_ENGINE = 'django.contrib.sessions.backends.file'    # 引擎
    		SESSION_FILE_PATH = None                                    
    		# 缓存文件路径，如果为None，则使用tempfile模块获取一个临时地址tempfile.gettempdir()                                                    # 如：/var/folders/d3/j9tj0gz93dg06bmwxmhh6_xm0000gn/T

    	缓存+数据库Session
    		配置 settings.py
 
    		SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'        # 引擎

2. CSRF
    a. CSRF原理

    b. 无CSRF时存在隐患

    c. Form提交（CSRF）

    d. Ajax提交（CSRF）
       CSRF请求头 X-CSRFToken

	       请求头中不能有_ 例如  
		       $.ajax({
		       		url:'/login/',
		       		type:'POST',
		       		data{'user':'root','pwd':'123'}
		       		headers:{'x_csrftoken'}     带有_后台会视为非法字符，后台会取不到值
		       })
		   
		   	   开启csrf之后正确写法：
		   	    $.ajax({
		       		url:'/login/',
		       		type:'POST',
		       		data{'user':'root','pwd':'123'}
		       		headers:{'X-CSRFtoken':$.cookie('csrftoken')},      之后就可以不用每个都定义这个请求头了
		       		succeed:function(arg){
		       			...
		       		}
		       })

		       在全局定义ajax的请求头 属性：
			       	$.ajaxSetup({
			       		beforeSend:function(xhr,settings){
			       		xhr.setRequestHeader('X-CSRFtoken',$.cookie('csrftoken'));
			       		}
			       	});

			       	请求头发送的token和前端显示的token不是一个token 我们要拿cookie中的token

	   
6. 中间件
	django的中間件定义在settiongs中的MIDDLEWARE中

		中间件的定义路径：
			在settings加上 如：在Middle下的m1.py中有一个class1 如果想要引用class这个中间件 即在setting中的middleware字段中加上'Middle.m1.class1'

		在django的中间件函数中 请求函数和返回函数 process_request process_response的函数名是固定的不可变

		请求顺序：  请求函数(process_request)
			请求端(process_request) --> 

			中间件{..}(按照中间件中定义的中间件的顺序逐一经过，如果其中有一项中间件直接返回(process_response)或报错，后面的中间件就不会再经过) --> 

			请求目标地址(process_request)
		
		返回顺序:   返回函数(process_response)

			请求端(process_response) --> 中间件{..} (按照中间件中定义的中间件的顺序逐一经过) --> 请求目标地址(process_response)

		例子：

			在django项目目录中创建一个Middle(名字叫自己命名) 里面创建一个py文件

				from django.utils.deprecation import MiddlewareMixin

				class Middle1(MiddlewareMixin):
				    def process_request(self,request):
				        print("hello my name is Middle1 request")
				    def process_response(self,request,response):
				        print("hello my name is Middle1 response")
				        return response
				class Middle2(MiddlewareMixin):
				    def process_request(self,request):
				        print("hello my name is Middle2 request")
				    def process_response(self,request,response):
				        print("hello my name is Middle2 response")
				        return response

				class Middle3(MiddlewareMixin):
				    def process_request(self,request):
				        print("hello my name is Middle3 request")
				    def process_response(self,request,response):
				        print("hello my name is Middle3 response")
				        return response



		    引用：
		    	在settings中引用：

		    	MIDDLEWARE = [
				    'django.middleware.security.SecurityMiddleware',
				    'django.contrib.sessions.middleware.SessionMiddleware',
				    'django.middleware.common.CommonMiddleware',
				    'django.middleware.csrf.CsrfViewMiddleware',
				    'django.contrib.auth.middleware.AuthenticationMiddleware',
				    'django.contrib.messages.middleware.MessageMiddleware',
				    'django.middleware.clickjacking.XFrameOptionsMiddleware',
				    'Middle.m1.Middle1',
				    'Middle.m1.Middle2',
				    'Middle.m1.Middle3',
				]

7. 缓存
	5种配置
		1.开发调试： 

		# 此为开始调试用，实际内部不做任何操作
    	# 配置：
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',     # 引擎
                'TIMEOUT': 300,                                               # 缓存超时时间（默认300，None表示永不过期，0表示立即过期）
                'OPTIONS':{
                    'MAX_ENTRIES': 300,                                       # 最大缓存个数（默认300）
                    'CULL_FREQUENCY': 3,                                      # 缓存到达最大个数之后，剔除缓存个数的比例，即：1/CULL_FREQUENCY（默认3）
                },
                'KEY_PREFIX': '',                                             # 缓存key的前缀（默认空）
                'VERSION': 1,                                                 # 缓存key的版本（默认1）
                'KEY_FUNCTION' 函数名                                         # 生成key的函数（默认函数会生成为：【前缀:版本:key】）
            }
        }


	    # 自定义key
	    def default_key_func(key, key_prefix, version):
	        """
	        Default function to generate keys.

	        Constructs the key used by all other methods. By default it prepends
	        the `key_prefix'. KEY_FUNCTION can be used to specify an alternate
	        function with custom key making behavior.
	        """
	        return '%s:%s:%s' % (key_prefix, version, key)

	    def get_key_func(key_func):
	        """
	        Function to decide which key function to use.

	        Defaults to ``default_key_func``.
	        """
	        if key_func is not None:
	            if callable(key_func):
	                return key_func
	            else:
	                return import_string(key_func)
	        return default_key_func


	    2.内存

	    # 此缓存将内容保存至内存的变量中
    	# 配置：
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        }

    # 注：其他配置同开发调试版本


    	3.文件：
    	 # 此缓存将内容保存至文件
   		 # 配置：

	        CACHES = {
	            'default': {
	                'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
	                'LOCATION': '/var/tmp/django_cache',
	            }
	        }
	    # 注：其他配置同开发调试版本



    	4.数据库

    	# 此缓存将内容保存至数据库

	    # 配置：
	        CACHES = {
	            'default': {
	                'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
	                'LOCATION': 'my_cache_table', # 数据库表
	            }
	        }

	    # 注：执行创建表命令 python manage.py createcachetable


	    5.Memcache缓存（python-memcached模块）

	    # 此缓存使用python-memcached模块连接memcache

	    CACHES = {
	        'default': {
	            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
	            'LOCATION': '127.0.0.1:11211',
	        }
	    }

	    CACHES = {
	        'default': {
	            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
	            'LOCATION': 'unix:/tmp/memcached.sock',
	        }
	    }   

	    CACHES = {
	        'default': {
	            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
	            'LOCATION': [
	                ('172.19.26.240:11211',15),
	                ('172.19.26.242:11211',10),     mamecahe模块 支持加权重
	            ] 
	        }
	    }


	3种应用：

		优先级：全局 > 视图 > 模板   这个和请求周期有关

		一：全局
			在中间件中定义
			 使用中间件，经过一系列的认证等操作，如果内容在缓存中存在，则使用FetchFromCacheMiddleware获取内容并返回给用户，当返回给用户之前，判断缓存中是否已经存在，如果不存在则UpdateCacheMiddleware会将缓存保存至缓存，从而实现全站缓存

	    MIDDLEWARE = [
	        'django.middleware.cache.UpdateCacheMiddleware',
	        # 其他中间件...
	        'django.middleware.cache.FetchFromCacheMiddleware',
	    ]

	    CACHE_MIDDLEWARE_ALIAS = ""
	    CACHE_MIDDLEWARE_SECONDS = ""
	    CACHE_MIDDLEWARE_KEY_PREFIX = ""

		二：视图函数：

			 方式一：
		        from django.views.decorators.cache import cache_page

		        @cache_page(60 * 15)
		        def my_view(request):
		            ...

	    	方式二：
		        from django.views.decorators.cache import cache_page

		        urlpatterns = [
		            url(r'^foo/([0-9]{1,2})/$', cache_page(60 * 15)(my_view)),
		        ]

		三：模板：在html中 定义 

			 a. 引入TemplateTag

	        	{% load cache %}

	    	b. 使用缓存

		        {% cache 5000 缓存key %}
		            缓存内容
		        {% endcache %}

8. 信号
    - 内置信号

    	在django中有很多内置的信号：
    		Model signals
		    pre_init                    # django的modal执行其构造方法前，自动触发
		    post_init                   # django的modal执行其构造方法后，自动触发
		    pre_save                    # django的modal对象保存前，自动触发
		    post_save                   # django的modal对象保存后，自动触发
		    pre_delete                  # django的modal对象删除前，自动触发
		    post_delete                 # django的modal对象删除后，自动触发
		    m2m_changed                 # django的modal中使用m2m字段操作第三张表（add,remove,clear）前后，自动触发
		    class_prepared              # 程序启动时，检测已注册的app中modal类，对于每一个类，自动触发
		Management signals
		    pre_migrate                 # 执行migrate命令前，自动触发
		    post_migrate                # 执行migrate命令后，自动触发
		Request/response signals
		    request_started             # 请求到来前，自动触发
		    request_finished            # 请求结束后，自动触发
		    got_request_exception       # 请求异常后，自动触发
		Test signals
		    setting_changed             # 使用test测试修改配置文件时，自动触发
		    template_rendered           # 使用test测试渲染模板时，自动触发
		Database Wrappers
		    connection_created          # 创建数据库连接时，自动触发

		定义和触发信号：

			from django.core.signals import request_finished
		    from django.core.signals import request_started
		    from django.core.signals import got_request_exception

		    from django.db.models.signals import class_prepared
		    from django.db.models.signals import pre_init, post_init
		    from django.db.models.signals import pre_save, post_save
		    from django.db.models.signals import pre_delete, post_delete
		    from django.db.models.signals import m2m_changed
		    from django.db.models.signals import pre_migrate, post_migrate

		    from django.test.signals import setting_changed
		    from django.test.signals import template_rendered

		    from django.db.backends.signals import connection_created

		    在信号中定义函数：

		    def callback(sender, **kwargs):
		        print("xxoo_callback")
		        print(sender,kwargs)

		    触发信号：
		    xxoo.connect(callback)   如pre_init.connect(callback)  此时在django的modal执行其构造方法前，会自动触发callback函数
		    # xxoo指上述导入的内容



	- 自定义
		 - 定义信号

		 	import django.dispatch
			pizza_done(自定义信号名) = django.dispatch.Signal(providing_args=["toppings", "size"])
 
		 - 触发信号   在view中触发   sender为发送者的名字 

		 	from 路径 import pizza_done
 
			pizza_done.send(sender='seven',toppings=123, size=456)

		 - 信号中注册函数

			 def callback(sender, **kwargs):
			    print("callback")
			    print(sender,kwargs)
			 
			pizza_done.connect(callback)

			
3. Model操作
    
    a. 字段类型 + 参数

    b. 连表字段 + 参数

    c. Meta

    d. SQL操作：
        - 基本增删改查
        - 进阶操作
        - 正反查询
        - 其他操作

    e. 验证（弱）

4. Form操作
	
	在form表单验证时  
		1.如果不使用django的内置标签，前端传入的name和后端接受的要一致 

			如 

			前端 html：<input type="text" name="user"> 
			
			后端 view：

			from django import forms
			'''widgets是form的插件'''
			from django.forms import widgets
			from django.forms import fields

			class FM(forms.Form):
		   
		    user=fields.EmailField(
		        error_messages={"required": "邮箱不能为空", "invalid": "邮箱不符合规范"},

		    )
			password=fields.CharField(
		        max_length=16,
		        min_length=6,
		        error_messages={"required":"密码不能为空","max_length":"长度不能超过16个字符","min_length":"长度不能短于6个字符"},
		        label="密码 ",
		        widget=widgets.PasswordInput(attrs={"class":"c2"})

	    	)

	完成：
		- 验证用户请求

		- 生成HTML
			1.django内部就可以自動生成标签  
				如： 在view中生成像上面一样的FM {{ obj.user }}  

			2.在view中设定如果认证失败 让其重新return render本页面，此时请求方法变为GET 此时在GET中定义返回obj
				例子
				def sign_up(request):
			    if request.method=="GET":
			        obj=FM()
			        return render(request,'sign_up.html',{"obj":obj})

			    if request.method=="POST":
			        obj=FM(request.POST)
			        r1=obj.is_valid()

			        if r1:
			            print(obj.cleaned_data.get('user')) #获取user
			            # info="新增一条用户数据{}".format(obj.user)
			            print(type(obj.cleaned_data))
			            # post_save.send(sender="Account",info=obj.cleaned_data)
			            print(132)
			            try:
			                models.Account.objects.create(**obj.cleaned_data)

			                return redirect('/temp/')
			            except:
			                return HttpResponse("输入的邮箱已存在")
			            # return HttpResponse("200")
			        else:
			            # print(obj.errors.as_json())
			            print(obj.errors)
			            return render(request,'sign_up.html',{"obj":obj})
		  	
		  	（这样可以保留上一次提交的数据）
		
	自定义：
		- 类
		- 字段（校验）
		- 插件（生成HTML）
		
	初始化操作：
		











