/*
===============================================================
File: jest.config.js
Location: repository root
Author: Mark J. Latsha
Created: 2026-05-27
Description: Jest configuration for tests and coverage thresholds.
===============================================================
*/
module.exports = {
  testEnvironment: 'node',
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageThreshold: {
    global: {
      branches: 60,
      functions: 60,
      lines: 70,
      statements: 70
    }
  }
};
