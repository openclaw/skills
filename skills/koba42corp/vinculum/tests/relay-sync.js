#!/usr/bin/env node
/**
 * Test two agents syncing through the relay daemon
 */

const Gun = require('../scripts/gun-loader');
const GunAdapter = require('../scripts/gun-adapter');

const NAMESPACE = 'cbot-7fd646e13ed6';
const KEY = 'b95c1bf703b41aea11f0c950b19fa8ec51df70a0c944afb9c8abae76ca7e5461';
const RELAY = 'http://localhost:8765/gun';

async function main() {
  console.log('🔗 Testing two-agent sync via relay...\n');
  
  // Create Agent 1 - connects to relay
  const agent1 = new GunAdapter({ peers: [RELAY] });
  await agent1.init({ peers: [RELAY] });
  await agent1.connect(NAMESPACE, KEY, {
    instanceId: 'legion-main',
    name: 'Legion',
    owner: 'drac'
  });
  console.log('✅ Agent 1 (Legion) connected to relay');
  
  // Create Agent 2 - also connects to relay
  const agent2 = new GunAdapter({ peers: [RELAY] });
  await agent2.init({ peers: [RELAY] });
  await agent2.connect(NAMESPACE, KEY, {
    instanceId: 'clawd-mobile',
    name: 'Clawd-Mobile',
    owner: 'drac'
  });
  console.log('✅ Agent 2 (Clawd-Mobile) connected to relay');
  
  // Wait for peer discovery
  await new Promise(r => setTimeout(r, 1000));
  
  // Agent 1 logs activity
  console.log('\n📝 Agent 1 sharing memory...');
  const mem = await agent1.shareMemory({
    content: 'Relay sync test - ' + new Date().toISOString(),
    tags: 'test,relay'
  });
  console.log('   Memory ID:', mem.id);
  
  // Agent 2 logs activity  
  console.log('📝 Agent 2 logging activity...');
  const act = await agent2.logActivity({
    action: 'tested',
    summary: 'Verified relay sync works',
    tags: 'test'
  });
  console.log('   Activity ID:', act.id);
  
  // Wait for relay sync
  console.log('\n⏳ Waiting for relay sync...');
  await new Promise(r => setTimeout(r, 2000));
  
  // Agent 2 reads memories (should see Agent 1's)
  console.log('\n📖 Agent 2 reading memories:');
  const memories = await agent2.getMemories(10);
  if (memories.length === 0) {
    console.log('   (no memories found)');
  } else {
    memories.forEach(m => {
      console.log(`   • [${m.learned_by}] ${m.content}`);
    });
  }
  
  // Agent 1 reads activity (should see Agent 2's)
  console.log('\n📖 Agent 1 reading activity:');
  const activities = await agent1.getActivity(10);
  if (activities.length === 0) {
    console.log('   (no activities found)');
  } else {
    activities.forEach(a => {
      console.log(`   • [${a.agent}] ${a.summary}`);
    });
  }
  
  // Check agents
  console.log('\n👥 Agent 1 sees:');
  const agents1 = await agent1.getAgents();
  agents1.forEach(a => console.log(`   • ${a.name || a.id}`));
  
  console.log('\n👥 Agent 2 sees:');
  const agents2 = await agent2.getAgents();
  agents2.forEach(a => console.log(`   • ${a.name || a.id}`));
  
  // Cleanup
  await agent1.disconnect();
  await agent2.disconnect();
  
  const success = agents1.length >= 2 && agents2.length >= 2;
  console.log('\n' + (success ? '✅' : '⚠️') + ' Relay sync test complete!');
  process.exit(success ? 0 : 1);
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
