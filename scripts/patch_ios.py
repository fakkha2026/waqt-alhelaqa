import plistlib, glob, shutil, os, re
A = 'ios/App/App'
# الإشعارات
with open(f'{A}/App.entitlements', 'wb') as f:
    plistlib.dump({'aps-environment': 'production'}, f)
# Info.plist
p = f'{A}/Info.plist'
with open(p, 'rb') as f: d = plistlib.load(f)
d['CFBundleDisplayName'] = 'وقت الحلاقة'
d['UIBackgroundModes'] = ['remote-notification']
d['ITSAppUsesNonExemptEncryption'] = False
d['NSPhotoLibraryUsageDescription'] = 'عشان ترفق صورة قائمة الأسعار في رسالتك للإدارة'
d['NSCameraUsageDescription'] = 'عشان تصوّر قائمة الأسعار وترفقها في رسالتك للإدارة'
d['CFBundleDevelopmentRegion'] = 'ar'
d['UIUserInterfaceStyle'] = 'Light'
d['UISupportedInterfaceOrientations'] = ['UIInterfaceOrientationPortrait']
with open(p, 'wb') as f: plistlib.dump(d, f)
# AppDelegate
ad = f'{A}/AppDelegate.swift'
s = open(ad, encoding='utf-8').read()
if 'import FirebaseCore' not in s:
    s = s.replace('import Capacitor', 'import Capacitor\nimport FirebaseCore', 1)
if 'FirebaseApp.configure' not in s:
    s = re.sub(r'(didFinishLaunchingWithOptions[^{]*\{)', r'\1\n        if FirebaseApp.app() == nil { FirebaseApp.configure() }', s, count=1)
if 'didRegisterForRemoteNotificationsWithDeviceToken' not in s:
    add = '''
    func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        NotificationCenter.default.post(name: .capacitorDidRegisterForRemoteNotifications, object: deviceToken)
    }
    func application(_ application: UIApplication, didFailToRegisterForRemoteNotificationsWithError error: Error) {
        NotificationCenter.default.post(name: .capacitorDidFailToRegisterForRemoteNotifications, object: error)
    }
'''
    i = s.rstrip().rfind('}')
    s = s[:i] + add + s[i:]
open(ad, 'w', encoding='utf-8').write(s)
# الأيقونة وشاشة البداية
for f in glob.glob(f'{A}/Assets.xcassets/AppIcon.appiconset/*.png'):
    shutil.copy('icon.png', f)
for f in glob.glob(f'{A}/Assets.xcassets/Splash.imageset/*.png'):
    shutil.copy('splash.png', f)
print('patch_ios done')
# Privacy Manifest (شرط أبل)
pm = {
  'NSPrivacyTracking': False, 'NSPrivacyTrackingDomains': [],
  'NSPrivacyCollectedDataTypes': [
    {'NSPrivacyCollectedDataType': t, 'NSPrivacyCollectedDataTypeLinked': True, 'NSPrivacyCollectedDataTypeTracking': False,
     'NSPrivacyCollectedDataTypePurposes': ['NSPrivacyCollectedDataTypePurposeAppFunctionality']}
    for t in ['NSPrivacyCollectedDataTypeName', 'NSPrivacyCollectedDataTypePhoneNumber', 'NSPrivacyCollectedDataTypeUserID',
              'NSPrivacyCollectedDataTypePurchaseHistory', 'NSPrivacyCollectedDataTypeOtherUserContent', 'NSPrivacyCollectedDataTypePhotosorVideos']],
  'NSPrivacyAccessedAPITypes': [
    {'NSPrivacyAccessedAPIType': 'NSPrivacyAccessedAPICategoryUserDefaults', 'NSPrivacyAccessedAPITypeReasons': ['CA92.1']},
    {'NSPrivacyAccessedAPIType': 'NSPrivacyAccessedAPICategoryFileTimestamp', 'NSPrivacyAccessedAPITypeReasons': ['C617.1']},
    {'NSPrivacyAccessedAPIType': 'NSPrivacyAccessedAPICategorySystemBootTime', 'NSPrivacyAccessedAPITypeReasons': ['35F9.1']},
    {'NSPrivacyAccessedAPIType': 'NSPrivacyAccessedAPICategoryDiskSpace', 'NSPrivacyAccessedAPITypeReasons': ['E174.1']}]}
with open(f'{A}/PrivacyInfo.xcprivacy', 'wb') as f: plistlib.dump(pm, f)
print('privacy manifest done')
