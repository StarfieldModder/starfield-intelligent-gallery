/*
===============================================================
File: test/index.test.js
Location: test/
Author: Mark J. Latsha
Co-Author: Microsoft Copilot
Created: 2026-05-27
Description:
  Basic Jest smoke test for the CI stub. Verifies the exported
  projectIdentity function returns the expected string.
Notes:
  - Keeps CI fast and deterministic.
===============================================================
*/

const { projectIdentity } = require('../src/index');

test('projectIdentity returns expected string', () => {
  const id = projectIdentity();
  expect(typeof id).toBe('string');
  expect(id).toMatch(/Starfield Intelligent Gallery/);
});
