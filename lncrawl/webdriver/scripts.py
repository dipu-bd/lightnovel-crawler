import json
import logging

from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

add_script_to_evaluate_on_new_document = "Page.addScriptToEvaluateOnNewDocument"
set_user_agent_override = "Network.setUserAgentOverride"

hide_webdriver_from_navigator_script = """
Object.defineProperty(window, 'navigator', {
    value: new Proxy(navigator, {
        has: (target, key) => {
            return (key === 'webdriver' ? false : key in target);
        },
        get: (target, key) => {
            if (key === 'webdriver') return false;
            return (typeof target[key] === 'function' ? target[key].bind(target) : target[key]);
        },
    }),
});
"""

return_webdriver_script = "return navigator.webdriver"

return_user_agent_script = "return navigator.userAgent"

override_touch_points_for_navigator_script = """
Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 1 })
"""

remove_extra_objects_from_window_script = """
let objectToInspect = window;
let result = [];
while(objectToInspect !== null) {
    result = result.concat(Object.getOwnPropertyNames(objectToInspect));
    objectToInspect = Object.getPrototypeOf(objectToInspect);
}
result.forEach((p) => {
    if (p.match(/.+_.+_(Array|Promise|Symbol)/ig)) {
        delete window[p];
    }
});
"""


def __send_cdp(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({"cmd": cmd, "params": params})
    response = driver.command_executor._request("POST", url, body)
    return response.get("value")


def _override_get(driver: WebDriver):
    original = driver.get

    def override(*args, **kwargs):
        if driver.execute_script(return_webdriver_script):
            logger.info("patch navigator.webdriver")
            __send_cdp(
                driver,
                add_script_to_evaluate_on_new_document,
                {"source": hide_webdriver_from_navigator_script},
            )
            logger.info("patch user-agent string")
            user_agent = driver.execute_script(return_user_agent_script)
            __send_cdp(
                driver,
                set_user_agent_override,
                {"userAgent": user_agent.replace("Headless", "")},
            )
            __send_cdp(
                driver,
                add_script_to_evaluate_on_new_document,
                {"source": override_touch_points_for_navigator_script},
            )
        __send_cdp(
            driver,
            add_script_to_evaluate_on_new_document,
            {"source": remove_extra_objects_from_window_script},
        )
        original(*args, **kwargs)

    driver.get = override
