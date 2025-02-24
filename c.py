# a. 请给出发现该问题的思路 需要分析哪些数据 可以⽤ SQL 或 Python 代码表达核⼼思路
"""
理论上应该有游戏指标去监控这个事情，在相应的监控报表上就能发现这个问题；
夏目假设目前是原始的情况，只有常规的时长、留存、付费等指标，并且只有操作数据表如下：
ods
{
  user_id:xx
  level_id:xx
  event_name: start/fail/success
  timestamp:xx
}
首先肯定是从留存/时长/付费上体现出来，比如7留/第7日人均时长/7日付费率等指标突然有个明显的跌落;
有两张方法发现关卡异常
1.直接统计各个关卡的通关率、流失率/崩溃率等信息，找到有某个关卡存在明显异常；
2.统计用户自新增后每天的平均关卡数，找到平均关卡出现明显下滑的天次，进一步定位到某个关卡

以统计通关率为例，sql如下：
select level_id, 
       sum(if(b.user_id is not null ,1 ,0)) AS game_start, AS game_success,
       count(a.user_id) AS game_start,
      sum(if(b.user_id is not null ,1 ,0)) /count(a.user_id) AS pass_rate
from ods a left join ods b on a.user_id = b.user_id
where a.event_name = "start" and b.event_name = "success"
group BY 1 order by 4;
"""


# b.根据你⾃⼰玩游戏的经验 提出 2~3 个优化该游戏关卡的假设 并设计 A/B 实验⽅案进⾏验证
"""
以Match类游戏为例

假设1：难度问题
A/B 实验方案：
将玩家随机分为三组：对照组、A组、B组
对照组维持原样，A组减少关卡物品种类，B组增加物品种类
对比AB两组玩家的留存、时长等关键指标是否对比对照组显著，从而得知关卡设计是否存在过难/过简单情况；

如果是偏新手关，可以设计增加/减少引导
操作类似假设1；
"""

# c.讨论如何捕捉和响应玩家反馈 持续优化游戏体验 提⾼⽤户留存
"""
捕捉反馈：
1.核心指标监控，如时长、开局等是否出现异常；
2.问卷调查，收集玩家直接反馈；
3.舆情关注，收集玩家评论、客服反馈等信息

响应反馈：
1.画饼；
2.增加版本更新频次，修复；
3.根据反馈进行大量AB测找到真正的增长点；
"""

