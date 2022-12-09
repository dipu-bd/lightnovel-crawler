import json
import logging

from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

add_script_to_evaluate_on_new_document = "Page.addScriptToEvaluateOnNewDocument"
set_user_agent_override = "Network.setUserAgentOverride"

scroll_into_view_if_needed = r"""
window.scrollTo(0, 0);
arguments[0].scrollIntoViewIfNeeded();
"""

remove_element = "arguments[0].remove()"

hide_webdriver_from_navigator_script = r"""
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

remove_extra_objects_from_window_script = r"""
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

override_for_navigator_script = r"""
Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 1 })
Object.defineProperty(navigator.connection, 'rtt', {get: () => 100});

// https://github.com/microlinkhq/browserless/blob/master/packages/goto/src/evasions/chrome-runtime.js
window.chrome = {
    app: {
        isInstalled: false,
        InstallState: {
            DISABLED: 'disabled',
            INSTALLED: 'installed',
            NOT_INSTALLED: 'not_installed'
        },
        RunningState: {
            CANNOT_RUN: 'cannot_run',
            READY_TO_RUN: 'ready_to_run',
            RUNNING: 'running'
        }
    },
    runtime: {
        OnInstalledReason: {
            CHROME_UPDATE: 'chrome_update',
            INSTALL: 'install',
            SHARED_MODULE_UPDATE: 'shared_module_update',
            UPDATE: 'update'
        },
        OnRestartRequiredReason: {
            APP_UPDATE: 'app_update',
            OS_UPDATE: 'os_update',
            PERIODIC: 'periodic'
        },
        PlatformArch: {
            ARM: 'arm',
            ARM64: 'arm64',
            MIPS: 'mips',
            MIPS64: 'mips64',
            X86_32: 'x86-32',
            X86_64: 'x86-64'
        },
        PlatformNaclArch: {
            ARM: 'arm',
            MIPS: 'mips',
            MIPS64: 'mips64',
            X86_32: 'x86-32',
            X86_64: 'x86-64'
        },
        PlatformOs: {
            ANDROID: 'android',
            CROS: 'cros',
            LINUX: 'linux',
            MAC: 'mac',
            OPENBSD: 'openbsd',
            WIN: 'win'
        },
        RequestUpdateCheckStatus: {
            NO_UPDATE: 'no_update',
            THROTTLED: 'throttled',
            UPDATE_AVAILABLE: 'update_available'
        }
    }
}

// https://github.com/microlinkhq/browserless/blob/master/packages/goto/src/evasions/navigator-permissions.js
if (!window.Notification) {
    window.Notification = {
        permission: 'denied'
    }
}
const originalQuery = window.navigator.permissions.query
window.navigator.permissions.__proto__.query = parameters =>
    parameters.name === 'notifications'
        ? Promise.resolve({ state: window.Notification.permission })
        : originalQuery(parameters)
const oldCall = Function.prototype.call
function call() {
    return oldCall.apply(this, arguments)
}
Function.prototype.call = call
const nativeToStringFunctionString = Error.toString().replace(/Error/g, 'toString')
const oldToString = Function.prototype.toString
function functionToString() {
    if (this === window.navigator.permissions.query) {
        return 'function query() { [native code] }'
    }
    if (this === functionToString) {
        return nativeToStringFunctionString
    }
    return oldCall.call(oldToString, this)
}

// eslint-disable-next-line
Function.prototype.toString = functionToString
"""


def __send_cdp(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({"cmd": cmd, "params": params})
    response = driver.command_executor._request("POST", url, body)
    return response.get("value")


def _override_get(driver: WebDriver):
    get_original = driver.get

    def get_wrapped(*args, **kwargs):
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
                {"source": override_for_navigator_script},
            )
        __send_cdp(
            driver,
            add_script_to_evaluate_on_new_document,
            {"source": remove_extra_objects_from_window_script},
        )
        get_original(*args, **kwargs)

    driver.get = get_wrapped
