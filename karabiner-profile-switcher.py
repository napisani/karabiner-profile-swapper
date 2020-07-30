import sys
import os
import json

from os.path import expanduser

try:
    from AppKit import NSWorkspace, NSObject, NSObject, NSApplication, NSLog, \
        NSWorkspaceDidActivateApplicationNotification, NSWorkspaceApplicationKey, NSBundle
except ImportError:
    print('AppKit module not found, script should be run using system-default Python installations')
    sys.exit(1)


# from PyObjCTools import AppHelper
# from threading import Thread


def kill_handler(sig, frame):
    print('exiting')
    sys.exit(0)


class ProfileIdentifier:
    _default_profile_key = 'default'

    def __init__(self):
        self._home_dir = expanduser("~")
        self._profile_map = self.load_profile_map()
        self._available_profiles = self.load_available_profiles()
        NSLog('loaded up available profiles: %@', self._available_profiles)
        NSLog('loaded up profile map: %@', self._profile_map)

    def load_available_profiles(self):
        with open(self._home_dir + '/.config/karabiner/karabiner.json') as karabiner_config:
            cnf = json.load(karabiner_config)
            profiles = cnf['profiles']
            profile_names = list(map(lambda profile: profile['name'], profiles))
            return profile_names

    def load_profile_map(self):
        with open(self._home_dir + '/.config/karabiner/karabiner-profile-swap.json') as swap_config:
            return json.load(swap_config)

    def get_profile_for_bundle_name(self, bundle_name):
        if bundle_name is None or bundle_name not in self._profile_map:
            return self._profile_map[self._default_profile_key]
        return self._profile_map[bundle_name]


class ProfileSwitcher:
    _karabiner_cmd = '/Library/Application Support/org.pqrs/Karabiner-Elements/bin/karabiner_cli'

    def __init__(self, profile_ider):
        self.current_profile = ''
        self.profile_ider = profile_ider

    def switch_to_profile(self, bundle_name):
        NSLog('switching profile %@', bundle_name)
        profile = self.profile_ider.get_profile_for_bundle_name(bundle_name)
        if profile != self.current_profile:
            self._run_switch_command(profile)
            self.current_profile = profile

    def _run_switch_command(self, bundle_name):
        with os.popen("'{}' --select-profile '{}'".format(self._karabiner_cmd, bundle_name)) as cmdStream:
            NSLog("Switch CMD Output: %@", cmdStream.read())


class FrontAppListener(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        workspace = NSWorkspace.sharedWorkspace()
        note_center = workspace.notificationCenter()
        note_center.addObserver_selector_name_object_(
            self,
            self.didActivateApplicationNotification_,
            NSWorkspaceDidActivateApplicationNotification,
            None
        )

    def didActivateApplicationNotification_(self, notification):
        NSLog("didActivateApplicationNotification notification: %@", notification)
        try:
            user_info = notification.userInfo()
            app_info = user_info.objectForKey_(NSWorkspaceApplicationKey)
            NSLog("activated app_info: %@", app_info)

            for name in ["bundleIdentifier", "localizedName", "bundleURL", "executableURL", "launchDate"]:
                value = app_info.valueForKey_(name)
                NSLog("activated app_info attribute -- %@ : %@", name, value)

            bundle_name = app_info.valueForKey_("bundleIdentifier")
            self.profile_switcher.switch_to_profile(bundle_name)
        except:
            NSLog("failed to get foreground app name")


def startAppListener(profile_switcher):
    sharedapp = NSApplication.sharedApplication()
    app = FrontAppListener.alloc().init()
    app.profile_switcher = profile_switcher
    sharedapp.setDelegate_(app)
    sharedapp.run()
    # AppHelper.runEventLoop()

def hideDockIcon():
    bundle = NSBundle.mainBundle()
    info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
    info['LSUIElement'] = '1'


if __name__ == '__main__':
    profile_identifier = ProfileIdentifier()
    profile_switcher = ProfileSwitcher(profile_identifier)
    hideDockIcon()
    startAppListener(profile_switcher)
