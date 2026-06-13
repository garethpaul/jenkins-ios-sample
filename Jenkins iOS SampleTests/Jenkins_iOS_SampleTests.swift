//
//  Jenkins_iOS_SampleTests.swift
//  Jenkins iOS SampleTests
//
//  Created by Gareth Jones on 5/13/15.
//  Copyright (c) 2015 Gareth Jones. All rights reserved.
//

import UIKit
import XCTest
@testable import Jenkins_iOS_Sample

final class Jenkins_iOS_SampleTests: XCTestCase {

    func testFabricAPIKeyValidationRejectsMissingOrBlankValues() {
        XCTAssertFalse(isConfiguredFabricAPIKey(nil))
        XCTAssertFalse(isConfiguredFabricAPIKey(""))
        XCTAssertFalse(isConfiguredFabricAPIKey(" \n\t "))
    }

    func testFabricAPIKeyValidationRejectsPlaceholders() {
        XCTAssertFalse(isConfiguredFabricAPIKey("$(FABRIC_API_KEY)"))
        XCTAssertFalse(isConfiguredFabricAPIKey("prefix-$(FABRIC_API_KEY)"))
        XCTAssertFalse(isConfiguredFabricAPIKey("YOUR_FABRIC_API_KEY"))
        XCTAssertFalse(isConfiguredFabricAPIKey("your_fabric_api_key"))
        XCTAssertFalse(isConfiguredFabricAPIKey("YOUR_FABRIC_API_KEY_HERE"))
        XCTAssertFalse(isConfiguredFabricAPIKey("prefix-FABRIC_API_KEY"))
        XCTAssertFalse(isConfiguredFabricAPIKey("YOUR_CRASHLYTICS_BUILD_SECRET"))
        XCTAssertFalse(isConfiguredFabricAPIKey("REPLACE_WITH_FABRIC_API_KEY"))
        XCTAssertFalse(isConfiguredFabricAPIKey("replace_with_fabric_api_key"))
    }

    func testFabricAPIKeyValidationRejectsEmbeddedWhitespace() {
        XCTAssertFalse(isConfiguredFabricAPIKey("abc 123"))
        XCTAssertFalse(isConfiguredFabricAPIKey("abc\t123"))
        XCTAssertFalse(isConfiguredFabricAPIKey("abc\n123"))
    }

    func testFabricAPIKeyValidationRejectsControlCharacters() {
        XCTAssertFalse(isConfiguredFabricAPIKey("abc\u{0000}123"))
        XCTAssertFalse(isConfiguredFabricAPIKey("abc\u{202E}123"))
    }

    func testFabricAPIKeyValidationAcceptsTrimmedRealValues() {
        XCTAssertTrue(isConfiguredFabricAPIKey(" abc123 "))
    }
}
