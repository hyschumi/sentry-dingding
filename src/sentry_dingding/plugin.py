# -*- coding:utf-8 -*-

import json

import requests
from datetime import datetime
from sentry.plugins.bases.notify import NotificationPlugin

import sentry_dingding
from .forms import DingDingOptionsForm

DingTalk_API = "https://oapi.dingtalk.com/robot/send?access_token={token}"


class DingDingPlugin(NotificationPlugin):
    """
    Sentry plugin to send error counts to DingDing.
    """
    author = 'ansheng'
    author_url = 'https://github.com/anshengme/sentry-dingding'
    version = sentry_dingding.VERSION
    description = 'Send error counts to DingDing.'
    slug = 'DingDing'
    title = 'DingDing'
    conf_key = slug
    conf_title = title
    resource_links = [
        ('Source', 'https://github.com/anshengme/sentry-dingding'),
        ('Bug Tracker', 'https://github.com/anshengme/sentry-dingding/issues'),
        ('README', 'https://github.com/anshengme/sentry-dingding/blob/master/README.md'),
    ]
    project_conf_form = DingDingOptionsForm

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('access_token', project))

    def notify(self, notification):
        event = notification.event
        self.notify_users(event.group, event)

    def notify_users(self, group, event, fail_silently=False):
        self.post_process(group, event)

    def post_process(self, group, event, is_new=True, is_sample=False, **kwargs):
        if not self.is_configured(group.project):
            return
        project = event.project
        metadata = event.get_event_metadata()
        type = metadata.get('type')
        level = group.get_level_display().upper()
        link = group.get_absolute_url()
        server_name = event.get_tag('server_name')
        ips = event.get_tag('ips')
        msg = event.error().encode('utf-8')
        data = {
            'msgtype': 'markdown',
            'markdown': {
                'title': '{project_name}:{type}:{level}'.format(project_name=project, level=level, type=type),
                'text': '##### {project_name} \n > type: {type} \n\n > level:{level} \n\n > time: {time}\
                        \n\n > server: {server_name} \n\n > ip:{ips} \n\n > msg:{msg} \n\n >[view]({link})'.format(
                            project_name=project, level=level, type=type, server_name=server_name, ips=ips,
                            link=link, msg=msg, time=datetime.now().strftime('%H:%M:%S')),
            },
        }

        requests.post(
            url=self.get_send_url(group),
            headers={"Content-Type": "application/json"},
            data=json.dumps(data).encode("utf-8")
        )

    def get_send_url(self, group):
        access_token = self.get_option('access_token', group.project)
        return DingTalk_API.format(token=access_token)
