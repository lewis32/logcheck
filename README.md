>  如果在使用过程中出现问题请提供all.log文件，邮件或信鸿与@liuchangchun沟通，谢谢~

## 串口模式

- 仅适用于外销业务，在使用该模式前，需要修改日志策略定时定量阈值为极大值，使日志数据写入同一个文件，便于串口长时间读取数据。

- 外销机尽量避免通过修改云端配置更新策略，避免互相影响测试，请使用以下命令修改本地策略：

  ```shell
  log.off
  sed -i "s/\(<serduration>\).*\(<\/serduration><serfileSize>\).*\(<\/serfileSize><dotduration>\).*\(<\/dotduration><dotfileSize>\).*\(<\/dotfileSize><excduration>\).*\(<\/excduration><excfileSize>\).*\(<\/excfileSize>\)/\1999999\2999999\3999999\4999999\5999999\6999999\7/g" /var/local/logservice/xml/report_obtained_policy_xml_file.xmlreboot
  reboot
  ```

- 配置信息保存在`conf/cfg.ini`的以`serial`打头的section下，针对不同平台请自行修改`start_cmd`等。

## Kafka模式

1. 适用于内销业务，在使用该模式前，需要修改日志策略定时定量阈值为0，使日志数据实时上报，便于Kafka实时消费数据。
2. 内销的Kafka通信不需要走SSH通道，直接选择topic然后连接即可。
3. 配置信息保存在`conf/cfg.ini`的以kafka打头的secion下，如果云端变动请自行修改server等。

## 手动模式



适用于单条或多条日志数据的验证。

【规则文件】
1. 规则文件保存在`conf/`路径下，`policy_common.json`文件保存公共字段，policy_module*.json文件保存业务模块事件字段，文件名中的版本号请和日志系统基线版本保持一致，便于跟踪对比。
2. 具体规则编写请仿照`example_common.json`和`example_module.json`，实际编写JSON时请不要添加备注，使用前先用JSON格式化工具先排除格式问题。

【结果文件】
测试结果数据保存在`result/`路径下。