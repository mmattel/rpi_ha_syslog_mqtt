# Syslog to MQTT

Listen to syslog for patterns and write to MQTT

Though this is specific for NetApp with ONTAP 7, it can be adapted for any other syslog/message source.

* Copy the `.env.example` file, rename it to `.env` and configure it.
* Copy the `syslog_mqtt.service` file to /etc/syslogd/syslog and adapt the path to the source.

```bash
sudo systemd-analyze verify /etc/systemd/system/syslog_mqtt.service

sudo systemctl daemon-reload
sudo systemctl enable syslog_mqtt.service
sudo systemctl start syslog_mqtt.service
sudo systemctl status syslog_mqtt.service
```
