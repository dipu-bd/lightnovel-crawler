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
