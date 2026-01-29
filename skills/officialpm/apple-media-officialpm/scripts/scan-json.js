#!/usr/bin/env node
/*
Parse `atvremote scan` output into a compact JSON.
Works with pyatv/atvremote 0.17.x default scan formatting.
*/

const { execSync } = require('child_process')

function runScan(timeoutSec = 5) {
  const out = execSync(`atvremote scan -t ${Number(timeoutSec)}`, { encoding: 'utf8' })
  return out
}

function parseScan(text) {
  const lines = text.split(/\r?\n/)
  const devices = []

  let cur = null
  let inServices = false
  let inIdentifiers = false

  for (const raw of lines) {
    const line = raw.trim()

    // New device starts with "Name:"
    const nameMatch = line.match(/^Name:\s*(.+)$/)
    if (nameMatch) {
      if (cur) devices.push(cur)
      cur = { name: nameMatch[1].trim(), address: null, model: null, os: null, ids: [], services: [] }
      inServices = false
      inIdentifiers = false
      continue
    }

    if (!cur) continue

    const modelMatch = line.match(/^Model\/SW:\s*(.+)$/)
    if (modelMatch) {
      cur.model = modelMatch[1].trim()
      continue
    }

    const addrMatch = line.match(/^Address:\s*(.+)$/)
    if (addrMatch) {
      cur.address = addrMatch[1].trim()
      continue
    }

    if (line.startsWith('Identifiers:')) {
      inIdentifiers = true
      inServices = false
      continue
    }
    if (line.startsWith('Services:')) {
      inServices = true
      inIdentifiers = false
      continue
    }

    if (inIdentifiers) {
      const idMatch = line.match(/^-\s*(.+)$/)
      if (idMatch) cur.ids.push(idMatch[1].trim())
      continue
    }

    if (inServices) {
      // Example:
      // - Protocol: AirPlay, Port: 7000, Credentials: None, Requires Password: False, Password: None, Pairing: Disabled
      const svcMatch = line.match(/^-\s*Protocol:\s*([^,]+),\s*Port:\s*(\d+),\s*Credentials:\s*([^,]+),\s*Requires Password:\s*([^,]+),\s*Password:\s*([^,]+),\s*Pairing:\s*(.+)$/)
      if (svcMatch) {
        cur.services.push({
          protocol: svcMatch[1].trim(),
          port: Number(svcMatch[2]),
          credentials: svcMatch[3].trim(),
          requiresPassword: svcMatch[4].trim(),
          password: svcMatch[5].trim(),
          pairing: svcMatch[6].trim(),
        })
      }
      continue
    }
  }

  if (cur) devices.push(cur)
  return devices
}

const timeout = process.argv[2] ? Number(process.argv[2]) : 5
const raw = runScan(timeout)
const devices = parseScan(raw)
console.log(JSON.stringify({ scannedAt: new Date().toISOString(), timeoutSec: timeout, devices }, null, 2))
