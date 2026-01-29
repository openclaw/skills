/**
 * Basic tests for gun-sync skill
 */

const assert = require('assert');
const pairingCode = require('../scripts/utils/pairing-code');
const schema = require('../scripts/utils/schema');

console.log('🧪 Running gun-sync tests...\n');

// Test pairing code generation
console.log('Testing pairing code generation...');
const network = pairingCode.generateNewNetwork();
assert(network.namespaceId, 'Should generate namespace ID');
assert(network.encryptionKey, 'Should generate encryption key');
assert(network.pairingCode, 'Should generate pairing code');
assert(network.namespaceId.startsWith('cbot-'), 'Namespace should start with cbot-');
console.log('✅ Pairing code generation works');

// Test pairing code parsing
console.log('Testing pairing code parsing...');
const parsed = pairingCode.parsePairingCode(network.pairingCode);
assert(parsed, 'Should parse pairing code');
assert.strictEqual(parsed.namespaceId, network.namespaceId, 'Namespace should match');
assert.strictEqual(parsed.encryptionKey, network.encryptionKey, 'Key should match');
console.log('✅ Pairing code parsing works');

// Test invalid pairing code
console.log('Testing invalid pairing code...');
const invalid = pairingCode.parsePairingCode('not-a-valid-code');
assert.strictEqual(invalid, null, 'Should return null for invalid code');
console.log('✅ Invalid code handling works');

// Test schema helpers
console.log('Testing schema helpers...');

const identity = schema.createAgentIdentity({
  name: 'TestBot',
  instanceId: 'test-123',
  owner: 'testuser',
  channel: 'telegram'
});
assert(identity.name === 'TestBot', 'Identity name should match');
assert(identity.instance_id === 'test-123', 'Instance ID should match');
assert(identity.created, 'Should have created timestamp');
console.log('✅ Agent identity creation works');

const activity = schema.createActivityEntry({
  agent: 'TestBot',
  action: 'completed',
  summary: 'Test task completed',
  tags: ['test']
});
assert(activity.agent === 'TestBot', 'Activity agent should match');
assert(activity.id, 'Activity should have ID');
assert(activity.timestamp, 'Activity should have timestamp');
console.log('✅ Activity entry creation works');

const memory = schema.createMemoryEntry({
  content: 'Test memory',
  learnedBy: 'TestBot',
  tags: ['test']
});
assert(memory.content === 'Test memory', 'Memory content should match');
assert(memory.id.startsWith('mem-'), 'Memory ID should start with mem-');
console.log('✅ Memory entry creation works');

const decision = schema.createDecisionEntry({
  topic: 'Test topic',
  decision: 'Test decision',
  decidedBy: 'TestBot'
});
assert(decision.topic === 'Test topic', 'Decision topic should match');
assert(decision.id.startsWith('dec-'), 'Decision ID should start with dec-');
console.log('✅ Decision entry creation works');

console.log('\n✅ All tests passed!');
