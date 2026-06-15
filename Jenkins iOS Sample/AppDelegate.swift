//
//  AppDelegate.swift
//  Jenkins iOS Sample
//
//  Created by Gareth Jones on 5/13/15.
//  Copyright (c) 2015 Gareth Jones. All rights reserved.
//

import UIKit
import Fabric
import Crashlytics

func isConfiguredFabricAPIKey(_ apiKey: String?) -> Bool {
    guard let apiKey = apiKey else {
        return false
    }

    let trimmedAPIKey = apiKey.trimmingCharacters(in: .whitespacesAndNewlines)
    if apiKey != trimmedAPIKey {
        return false
    }
    if trimmedAPIKey.rangeOfCharacter(from: .whitespacesAndNewlines) != nil {
        return false
    }
    if trimmedAPIKey.rangeOfCharacter(from: .controlCharacters) != nil {
        return false
    }

    let normalizedAPIKey = trimmedAPIKey.uppercased()
    let placeholderFragments = ["FABRIC_API_KEY", "CRASHLYTICS_BUILD_SECRET"]
    let hexadecimalCharacters = CharacterSet(charactersIn: "0123456789abcdefABCDEF")

    for placeholderFragment in placeholderFragments {
        if normalizedAPIKey.range(of: placeholderFragment) != nil {
            return false
        }
    }

    return !trimmedAPIKey.isEmpty &&
        trimmedAPIKey.count == 40 &&
        trimmedAPIKey.unicodeScalars.allSatisfy { hexadecimalCharacters.contains($0) } &&
        trimmedAPIKey.range(of: "$(") == nil &&
        normalizedAPIKey != "YOUR_FABRIC_API_KEY" &&
        !normalizedAPIKey.hasPrefix("REPLACE_")
}

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?


    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Override point for customization after application launch.
        if hasConfiguredFabricAPIKey() {
            Fabric.with([Crashlytics.sharedInstance()])
        }

        return true
    }

    func hasConfiguredFabricAPIKey() -> Bool {
        if let fabric = Bundle.main.object(forInfoDictionaryKey: "Fabric") as? [String: Any],
            let apiKey = fabric["APIKey"] as? String {
                return isConfiguredFabricAPIKey(apiKey)
        }

        return false
    }

    func applicationWillResignActive(_ application: UIApplication) {
        // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
        // Use this method to pause ongoing tasks, disable timers, and throttle down OpenGL ES frame rates. Games should use this method to pause the game.
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        // Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later.
        // If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
        // Called as part of the transition from the background to the inactive state; here you can undo many of the changes made on entering the background.
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
        // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
    }

    func applicationWillTerminate(_ application: UIApplication) {
        // Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.
    }


}
