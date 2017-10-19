## 说明
此模块只处理爬虫相关的业务，网络监测、任务确定等任务不在这里处理。

## 开发约定

### 抓取需要初始化的东西
1、将项目目录trivest_spider设置为Sources Root
2、GlobleConfig.py存储的是当前项目的部分配置
    1、projectIdentify:
        项目唯一标识，分布式，不同的项目思考(规则：项目名称!@项目部署位置!@部署时间!@ 1000-9999的随机数）
        案例: 'news spider!@xiamen!@2017-9-30 15:59!@7699'
    2、spiderDetails 为对应爬虫下的基本信息
        table_name: 存储表的英文
        table_name_zh: 存储表的中文
        spider_name: spider的英文
        spider_name_zh: spider的中文
        注意：每添加一种spider，就在这spiderDetails对象内部添加一个对象，key为spider的英文名


### 抓取状态存储
在重新启动爬虫时候，需要全部清除clearAllStatus()

### Spider开发模式
开发Spider时，抓取的数据都是用标准的字典存储，也就是不在items.py里定义Item类。
Item处理统一在pipeline中进行，Spider中不处理相关的逻辑，启用哪一些Pipeline通过在每个Spider的个性化配置中指定。

###Spider划分
一个Spider只处理特定的爬取任务，例如新浪科技滚动新闻与新浪股票，应该划分为不同的Spider

###Spider命名
Spider的文件名命名统一为: ```数据源_版本.py``` 的模式，相应的Spider类采用相应的驼峰格式,并加上Spider后缀，spider名称同文件名。