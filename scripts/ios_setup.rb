require 'xcodeproj'
p = Xcodeproj::Project.open('ios/App/App.xcodeproj')
t = p.targets.find { |x| x.name == 'App' }
g = p.main_group.children.find { |c| c.display_name == 'App' }
unless g.files.any? { |f| f.path == 'GoogleService-Info.plist' }
  f = g.new_reference('GoogleService-Info.plist')
  t.resources_build_phase.add_file_reference(f)
end
unless g.files.any? { |f| f.path == 'PrivacyInfo.xcprivacy' }
  pf = g.new_reference('PrivacyInfo.xcprivacy')
  t.resources_build_phase.add_file_reference(pf)
end
g.new_reference('App.entitlements') unless g.files.any? { |f| f.path == 'App.entitlements' }
t.build_configurations.each do |c|
  c.build_settings['CODE_SIGN_ENTITLEMENTS'] = 'App/App.entitlements'
  c.build_settings['CURRENT_PROJECT_VERSION'] = ENV['BUILD_NUMBER'] || '1'
  c.build_settings['MARKETING_VERSION'] = ENV['APP_VERSION'] || '1.0'
  c.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '15.0'
  c.build_settings['TARGETED_DEVICE_FAMILY'] = '1'
end
p.save
puts 'ios_setup done'
