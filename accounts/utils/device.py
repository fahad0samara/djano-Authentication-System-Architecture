from django.http import HttpRequest
import user_agents

def parse_user_agent(request: HttpRequest) -> dict:
    """Parse user agent string into device info."""
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = user_agents.parse(ua_string)
    
    return {
        'browser': user_agent.browser.family,
        'browser_version': user_agent.browser.version_string,
        'os': user_agent.os.family,
        'device': user_agent.device.family,
        'is_mobile': user_agent.is_mobile,
        'is_tablet': user_agent.is_tablet,
        'is_bot': user_agent.is_bot
    }