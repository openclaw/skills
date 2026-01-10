const { AthomCloudAPI } = require('homey-api');
const fuzzy = require('./fuzzy');
const { cliError } = require('./errors');

/**
 * Homey API client wrapper
 */
class HomeyClient {
  constructor(token) {
    this.token = token;
    this.api = null;
    this.homeyApi = null;
    this.homey = null;
  }

  /**
   * Connect to Homey Cloud API and authenticate
   */
  async connect() {
    if (!this.token) {
      throw new Error('No token provided. Set HOMEY_TOKEN env var or write ~/.homey/config.json');
    }

    // Create Cloud API instance
    this.api = new AthomCloudAPI({ token: this.token });

    // Get authenticated user and their first Homey
    const user = await this.api.getAuthenticatedUser();
    this.homey = await user.getFirstHomey();

    // Create session
    this.homeyApi = await this.homey.authenticate();

    return this.homeyApi;
  }

  async _ensureConnected() {
    if (!this.homeyApi) await this.connect();
  }

  _pickDevice(id, device, options = {}) {
    const capabilitiesObj = device.capabilitiesObj || {};
    const values = Object.fromEntries(
      Object.entries(capabilitiesObj).map(([capabilityId, cap]) => [capabilityId, cap?.value])
    );

    const picked = {
      id,
      name: device.name,
      // Both are useful: zoneId for lookups, zoneName for display
      zoneId: device.zone || null,
      zoneName: device.zoneName || null,
      zone: device.zoneName || device.zone || null,
      class: device.class,
      driverId: device.driverId || null,
      uri: device.uri || null,
      capabilities: device.capabilities || [],
      capabilitiesObj,
      values,
      available: device.available,
      ready: device.ready,
    };

    if (options.raw) {
      picked.raw = device;
    }

    return picked;
  }

  _pickFlow(id, flow, options = {}) {
    const picked = {
      id,
      name: flow.name,
      enabled: flow.enabled,
      folder: flow.folder || null,
    };

    if (options.raw) {
      picked.raw = flow;
    }

    return picked;
  }

  /**
   * Get all devices
   * @returns {Promise<Array>} Array of devices
   */
  async getDevices(options = {}) {
    await this._ensureConnected();

    const devicesObj = await this.homeyApi.devices.getDevices();
    return Object.entries(devicesObj).map(([id, device]) => this._pickDevice(id, device, options));
  }

  /**
   * Get device by ID or name (fuzzy)
   * @param {string} nameOrId Device name or ID
   * @returns {Promise<object>} Device object
   */
  async getDevice(nameOrId, options = {}) {
    await this._ensureConnected();

    const devicesObj = await this.homeyApi.devices.getDevices();

    // Try direct ID lookup first
    if (devicesObj[nameOrId]) {
      return this._pickDevice(nameOrId, devicesObj[nameOrId], options);
    }

    const query = String(nameOrId).trim();
    const queryLower = query.toLowerCase();

    const entries = Object.entries(devicesObj).map(([id, device]) => ({
      id,
      name: device.name,
      nameLower: (device.name || '').toLowerCase(),
      device,
    }));

    // 1) Exact match(es)
    const exactMatches = entries.filter(e => e.nameLower === queryLower);
    if (exactMatches.length === 1) {
      const m = exactMatches[0];
      return this._pickDevice(m.id, m.device, options);
    }
    if (exactMatches.length > 1) {
      throw cliError(
        'AMBIGUOUS',
        `ambiguous device query '${query}' (matched ${exactMatches.length} devices). Use an id.`,
        { candidates: exactMatches.map(m => ({ id: m.id, name: m.name })) }
      );
    }

    // 2) Substring match(es)
    const substringMatches = entries.filter(e =>
      e.nameLower.includes(queryLower) || queryLower.includes(e.nameLower)
    );
    if (substringMatches.length === 1) {
      const m = substringMatches[0];
      return this._pickDevice(m.id, m.device, options);
    }
    if (substringMatches.length > 1) {
      throw cliError(
        'AMBIGUOUS',
        `ambiguous device query '${query}' (matched ${substringMatches.length} devices). Use an id.`,
        { candidates: substringMatches.slice(0, 20).map(m => ({ id: m.id, name: m.name })) }
      );
    }

    // 3) Levenshtein best match (only if uniquely best)
    const threshold = Number.isFinite(options.threshold) ? options.threshold : 5;
    const distances = entries
      .map(e => ({ e, d: fuzzy.levenshteinDistance(queryLower, e.nameLower) }))
      .sort((a, b) => a.d - b.d);

    const best = distances[0];
    if (!best || best.d > threshold) {
      const suggestions = fuzzy.fuzzySearch(query, entries, 5)
        .map(e => ({ id: e.id, name: e.name }))
        .filter(e => e.name);
      throw cliError(
        'NOT_FOUND',
        `device not found: '${query}'`,
        suggestions.length ? { candidates: suggestions } : undefined
      );
    }

    const bestTied = distances.filter(x => x.d === best.d && x.d <= threshold);
    if (bestTied.length !== 1) {
      throw cliError(
        'AMBIGUOUS',
        `ambiguous device query '${query}' (matched ${bestTied.length} devices at distance ${best.d}). Use an id.`,
        { candidates: bestTied.slice(0, 20).map(x => ({ id: x.e.id, name: x.e.name })) }
      );
    }

    return this._pickDevice(best.e.id, best.e.device, options);
  }

  /**
   * Set device capability value
   * @param {string} deviceId Device ID
   * @param {string} capability Capability ID
   * @param {any} value Value to set
   */
  async setCapability(deviceId, capability, value) {
    await this._ensureConnected();

    const device = await this.homeyApi.devices.getDevice({ id: deviceId });
    await device.setCapabilityValue({
      capabilityId: capability,
      value,
    });
  }

  /**
   * Get device capability value
   * @param {string} deviceId Device ID
   * @param {string} capability Capability ID
   * @returns {Promise<any>} Capability value
   */
  async getCapability(deviceId, capability) {
    await this._ensureConnected();

    const device = await this.homeyApi.devices.getDevice({ id: deviceId });
    return device.capabilitiesObj[capability]?.value;
  }

  /**
   * Get all flows
   * @returns {Promise<Array>} Array of flows
   */
  async getFlows(options = {}) {
    await this._ensureConnected();

    const flowsObj = await this.homeyApi.flow.getFlows();
    return Object.entries(flowsObj).map(([id, flow]) => this._pickFlow(id, flow, options));
  }

  /**
   * Search devices by query (returns multiple matches)
   */
  async searchDevices(query, options = {}) {
    await this._ensureConnected();

    const devicesObj = await this.homeyApi.devices.getDevices();
    const entries = Object.entries(devicesObj).map(([id, device]) => ({
      id,
      name: device.name,
      device,
    }));

    const q = String(query || '').trim();
    if (!q) {
      return Object.entries(devicesObj).map(([id, device]) => this._pickDevice(id, device, options));
    }

    const matches = fuzzy.fuzzySearch(q, entries, options.limit ?? 50);
    return matches.map(m => this._pickDevice(m.id, m.device, options));
  }

  /**
   * Search flows by query (returns multiple matches)
   */
  async searchFlows(query, options = {}) {
    await this._ensureConnected();

    const flowsObj = await this.homeyApi.flow.getFlows();
    const entries = Object.entries(flowsObj).map(([id, flow]) => ({
      id,
      name: flow.name,
      flow,
    }));

    const q = String(query || '').trim();
    if (!q) {
      return Object.entries(flowsObj).map(([id, flow]) => this._pickFlow(id, flow, options));
    }

    const matches = fuzzy.fuzzySearch(q, entries, options.limit ?? 50);
    return matches.map(m => this._pickFlow(m.id, m.flow, options));
  }

  /**
   * Trigger a flow by ID or name
   * @param {string} nameOrId Flow name or ID
   */
  async triggerFlow(nameOrId, options = {}) {
    await this._ensureConnected();

    const flowsObj = await this.homeyApi.flow.getFlows();

    // Direct ID lookup
    if (flowsObj[nameOrId]) {
      await flowsObj[nameOrId].trigger();
      return this._pickFlow(nameOrId, flowsObj[nameOrId], options);
    }

    const query = String(nameOrId).trim();
    const queryLower = query.toLowerCase();

    const entries = Object.entries(flowsObj).map(([id, flow]) => ({
      id,
      name: flow.name,
      nameLower: (flow.name || '').toLowerCase(),
      flow,
    }));

    // 1) Exact match(es)
    const exactMatches = entries.filter(e => e.nameLower === queryLower);
    if (exactMatches.length === 1) {
      const m = exactMatches[0];
      await m.flow.trigger();
      return this._pickFlow(m.id, m.flow, options);
    }
    if (exactMatches.length > 1) {
      throw cliError(
        'AMBIGUOUS',
        `ambiguous flow query '${query}' (matched ${exactMatches.length} flows). Use an id.`,
        { candidates: exactMatches.map(m => ({ id: m.id, name: m.name })) }
      );
    }

    // 2) Substring match(es)
    const substringMatches = entries.filter(e =>
      e.nameLower.includes(queryLower) || queryLower.includes(e.nameLower)
    );
    if (substringMatches.length === 1) {
      const m = substringMatches[0];
      await m.flow.trigger();
      return this._pickFlow(m.id, m.flow, options);
    }
    if (substringMatches.length > 1) {
      throw cliError(
        'AMBIGUOUS',
        `ambiguous flow query '${query}' (matched ${substringMatches.length} flows). Use an id.`,
        { candidates: substringMatches.slice(0, 20).map(m => ({ id: m.id, name: m.name })) }
      );
    }

    // 3) Levenshtein best match (only if uniquely best)
    const threshold = Number.isFinite(options.threshold) ? options.threshold : 5;
    const distances = entries
      .map(e => ({ e, d: fuzzy.levenshteinDistance(queryLower, e.nameLower) }))
      .sort((a, b) => a.d - b.d);

    const best = distances[0];
    if (!best || best.d > threshold) {
      const suggestions = fuzzy.fuzzySearch(query, entries, 5)
        .map(e => ({ id: e.id, name: e.name }))
        .filter(e => e.name);
      throw cliError(
        'NOT_FOUND',
        `flow not found: '${query}'`,
        suggestions.length ? { candidates: suggestions } : undefined
      );
    }

    const bestTied = distances.filter(x => x.d === best.d && x.d <= threshold);
    if (bestTied.length !== 1) {
      throw cliError(
        'AMBIGUOUS',
        `ambiguous flow query '${query}' (matched ${bestTied.length} flows at distance ${best.d}). Use an id.`,
        { candidates: bestTied.slice(0, 20).map(x => ({ id: x.e.id, name: x.e.name })) }
      );
    }

    await best.e.flow.trigger();
    return this._pickFlow(best.e.id, best.e.flow, options);
  }

  /**
   * Get all zones
   * @returns {Promise<Array>} Array of zones
   */
  async getZones(options = {}) {
    await this._ensureConnected();

    const zonesObj = await this.homeyApi.zones.getZones();
    return Object.entries(zonesObj).map(([id, zone]) => {
      const picked = {
        id,
        name: zone.name,
        parent: zone.parent,
        icon: zone.icon,
      };
      if (options.raw) picked.raw = zone;
      return picked;
    });
  }

  /**
   * Get Homey status/info
   * @returns {Promise<object>} Homey info
   */
  async getStatus() {
    await this._ensureConnected();

    const system = await this.homeyApi.system.getInfo();

    return {
      name: this.homey.name,
      platform: system.platform,
      platformVersion: system.platformVersion,
      hostname: system.hostname,
      cloudId: this.homey.id,
      connected: true,
    };
  }
}

module.exports = HomeyClient;
