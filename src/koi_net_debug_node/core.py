from slack_bolt import App
from koi_net.core import FullNode
from .config import DebugNodeConfig
from .dashboard_repoerter import DashboardReporter


class DebugNode(FullNode):
    config_schema = DebugNodeConfig
    slack_app = lambda config: App(
        token=config.env.slack_bot_token, 
        signing_secret=config.env.slack_signing_secret
    )
    
    dashboard_reporter = DashboardReporter
