#!/usr/bin/env node
/**
 * Test two agents connecting and syncing
 * Uses shared Gun instance to simulate relay/persistence
 */

const Gun = require('../scripts/gun-loader');
const GunAdapter = require('../scripts/gun-adapter');

const NAMESPACE = 'test-sync';
const KEY = 'test-key-123';

async function main() {
  console.log('🔗 Testing two-agent sync...\n');
  
  // Create shared Gun instance (simulates relay peer)
  const sharedGun = Gun({ localStorage: false, radisk: false, axe: false });
  
  // Create Agent 1
  const agent1 = new GunAdapter({ localStorage: false, radisk: false });
  agent1.gun = sharedGun;
  await agent1.connect(NAMESPACE, KEY, {
    instanceId: 'legion-main',
    name: 'Legion',
    owner: 'drac'
  });
  console.log('✅ Agent 1 (Legion) connected');
  
  // Create Agent 2 using same shared Gun
  const agent2 = new GunAdapter({ localStorage: false, radisk: false });
  agent2.gun = sharedGun;
  await agent2.connect(NAMESPACE, KEY, {
    instanceId: 'clawd-phone',
    name: 'Clawd-Phone',
    owner: 'drac'
  });
  console.log('✅ Agent 2 (Clawd-Phone) connected');
  
  // Agent 1 logs activity
  console.log('\n📝 Agent 1 logging activity...');
  const act1 = await agent1.logActivity({
    action: 'completed',
    summary: 'Helped with gun-sync skill development',
    tags: 'development,gun,sync'
  });
  console.log('   Entry ID:', act1.id);
  
  // Agent 2 logs activity
  console.log('📝 Agent 2 logging activity...');
  const act2 = await agent2.logActivity({
    action: 'started',
    summary: 'Monitoring notifications',
    tags: 'monitoring'
  });
  console.log('   Entry ID:', act2.id);
  
  // Agent 1 shares a memory
  console.log('\n🧠 Agent 1 sharing memory...');
  const mem = await agent1.shareMemory({
    content: 'Gun.js requires flat keys for Node v25+ compatibility',
    tags: 'technical,gun,node'
  });
  console.log('   Memory ID:', mem.id);
  
  // Wait for Gun to propagate
  console.log('\n⏳ Waiting for sync...');
  await new Promise(r => setTimeout(r, 800));
  
  // Agent 2 reads activity (should see both)
  console.log('\n📖 Agent 2 reading network activity:');
  const activities = await agent2.getActivity(10);
  if (activities.length === 0) {
    console.log('   (no activities found)');
  } else {
    activities.forEach(a => {
      console.log(`   • [${a.agent}] ${a.action}: ${a.summary}`);
    });
  }
  
  // Agent 1 reads memories (should see shared memory)
  console.log('\n📖 Agent 1 reading shared memories:');
  const memories = await agent1.getMemories(10);
  if (memories.length === 0) {
    console.log('   (no memories found)');
  } else {
    memories.forEach(m => {
      console.log(`   • [${m.learned_by}] ${m.content}`);
    });
  }
  
  // Check peers from each perspective
  console.log('\n👥 Agent 1 sees agents:');
  const agents1 = await agent1.getAgents();
  if (agents1.length === 0) {
    console.log('   (no agents found)');
  } else {
    agents1.forEach(a => {
      console.log(`   • ${a.name || a.id}`);
    });
  }
  
  console.log('\n👥 Agent 2 sees agents:');
  const agents2 = await agent2.getAgents();
  if (agents2.length === 0) {
    console.log('   (no agents found)');
  } else {
    agents2.forEach(a => {
      console.log(`   • ${a.name || a.id}`);
    });
  }
  
  // Cleanup
  await agent1.disconnect();
  await agent2.disconnect();
  
  console.log('\n' + (activities.length > 0 ? '✅' : '⚠️') + ' Two-agent sync test complete!');
  process.exit(activities.length > 0 ? 0 : 1);
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
