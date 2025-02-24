# a. 基于Kafka的实时数据处理架构设计
"""
  玩家行为
    │
    ▼
+-----------+
| 游戏客户端 | --(JSON埋点数据)
+-----------+
    │
    ▼
+-----------------+
| Kafka生产者      | --(分区策略)--> TopicA[Partition0,1..N]
+-----------------+                TopicB[Partition0,1..N]
    │
    ▼
+-----------------+
| Kafka Broker集群 | --(消费组订阅)
+-----------------+
    │
    ▼
+-----------------+
| Flink消费者      | --(KeyBy+Window, 如实时在线时长指标可以用滑动窗口)
+-----------------+
    │
    ▼
+-----------------+
| 聚合结果存储      | --(如写入Redshifit)--> bi看板
+-----------------+
"""


# b. 选择合适的实时计算框架 如 Spark Streaming Flink 编写伪代码实现关键指标计算
"""

假设数据埋点收集Json格式如下
{
  "user_id": "123",
  "timestamp": 1620000000,
}

--Python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import KafkaSource, KafkaSink
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream.window import TumblingEventTimeWindows

# 初始化Flink环境
env = StreamExecutionEnvironment.get_execution_environment()

# 配置Kafka消费者
kafka_source = KafkaSource.builder()
    .set_bootstrap_servers("kafka-broker:9092")
    .set_topics("user_online_time", "payment_events")
    .set_group_id("metrics_group")
    .set_value_only_deserializer(SimpleStringSchema())
    .build()

# 定义数据处理逻辑
ds = env.from_source(kafka_source, WatermarkStrategy.for_monotonous_timestamps(), "Kafka Source")

# 解析JSON数据并提取事件时间
def parse_event(event):
    data = json.loads(event)
    return (data["user_id"],  data["timestamp"])

parsed_stream = ds.map(parse_event)

# 计算在线时长
online_time_stream = parsed_stream 
    .filter(lambda x: x[1] in ["login", "logout"]) 
    .key_by(lambda x: x[0]) 
    .window(TumblingEventTimeWindows.of(Time.minutes(5))) 
    .process(OnlineTimeCalculator())  # 自定义窗口函数，累加时间差

# 结果写入Kafka
kafka_sink = KafkaSink.builder() 
    .set_bootstrap_servers("kafka-broker:9092") 
    .set_record_serializer(SimpleStringSchema()) 
    .build()

online_time_stream.sink_to(kafka_sink, topic="metrics_online_time")
"""

# c. 低延迟、高可靠性及流量高峰应对策略
"""
低延迟：
Kafka端优化：
批量发送与压缩，减少网络开销
零拷贝传输：Broker使用sendfile系统调用直接传输磁盘数据，减少内存拷贝
Flink端优化：
基于事件时间处理乱序数据，设置合理的水位线延迟（如1秒），避免窗口延迟
启用增量检查点（RocksDB状态后端），减少计算停顿 

高可靠性保障
Kafka容错：
ISR机制
位移提交，结合Flink的Checkpoint机制实现精确一次语义
Flink容错：
状态快照：定期保存状态到持久化存储（如HDFS），故障时从最近快照恢复
Exactly-Once语义：通过Kafka事务和两阶段提交（2PC）确保端到端一致性

流量高峰应对
横向扩展：
1.扩容、加并行
2.使用消息队列的缓冲
3.抽样

"""
