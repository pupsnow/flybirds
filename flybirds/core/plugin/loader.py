# -*- coding: utf-8 -*-
"""
load event
"""
import base64

import flybirds.core.global_resource as gr
import flybirds.utils.flybirds_log as log
from flybirds.core.config_manage import DeviceConfig
from flybirds.core.config_manage import PluginConfig
from flybirds.core.global_context import GlobalContext
from flybirds.core.plugin.plugin_manager import DirectoryPluginManager
from flybirds.utils.dsl_helper import str2bool


class PluginManager:  # pylint: disable=too-few-public-methods
    """
    plugin load management
    """

    name = "PluginManager"
    order = 1

    @staticmethod
    def run(context):
        """
        load plugin from pkg
        """
        # initialize the global object module
        gr.init_glb()
        # get user-specified parameter value or custom parameter
        user_data = {}
        if context is not None and context.config is not None:
            user_data = (
                context.config.userdata
                if isinstance(context.config.userdata, dict)
                else {}
            )
            for key, value in user_data.items():
                user_data[key] = str(base64.b64decode(value), "utf-8")

        # check some specific values of the user_data
        if user_data.get('platform'):
            platform = user_data.get('platform').strip().lower()
            if platform not in ['ios', 'android', 'web']:
                log.warn(f'flybirds is not supports to run on {platform} '
                         f'platform. It will now run on Android by default.')
                platform = "android"
            user_data['platform'] = platform

        if user_data.get('headless'):
            headless = str2bool(user_data.get('headless').strip())
            user_data['headless'] = headless

        if user_data.get('browserType'):
            browser_type = user_data.get('browserType').strip().lower()
            browser_types = browser_type.split(',')
            browser_types = list(set(browser_types))
            temp = []
            [temp.append(i) for i in browser_types if
             i in ['chromium', 'firefox', 'webkit']]
            if len(temp) == 0:
                temp.append('chromium')
            user_data['browserType'] = ",".join(temp)

        log.info(f'[loader] user_data: {user_data}')
        gr.set_value("userData", user_data)

        cur_browser = "chromium"
        if user_data.get('cur_browser'):
            cur_browser = user_data.get('cur_browser')
        gr.set_value("cur_browser", cur_browser)

        p_info = PluginConfig(user_data).plugin_info
        if p_info is not None and p_info.__contains__("active"):
            GlobalContext.active_plugin = p_info.get("active")

        GlobalContext.plugin_info = p_info.get(GlobalContext.active_plugin)

        if GlobalContext.plugin_info is None:
            raise Exception(
                f"not exist this plugin {GlobalContext.active_plugin}"
            )
        GlobalContext.platform = DeviceConfig(user_data, None).platform
        log.info(
            f"[loader] run platform: {GlobalContext.platform}")
        plugin_manager = DirectoryPluginManager()
        plugin_manager.load_plugins()

        return plugin_manager


# add plugin load event to global processor
GlobalContext.join("plugin_processor", PluginManager, 1)
