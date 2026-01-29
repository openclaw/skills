#!/usr/bin/env node
/**
 * Lightning CLI - Send and receive Bitcoin over Lightning Network
 * Uses LNI (Lightning Node Interface) for multi-backend support
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// QR code generation (uses qrencode CLI if available)
function printQRCode(data, outputFile = null) {
  try {
    if (outputFile) {
      // Generate PNG file
      execSync(`echo -n "${data}" | qrencode -t PNG -o "${outputFile}" -m 2 -s 8`, {
        stdio: ['pipe', 'pipe', 'ignore']
      });
      console.log(`QR_IMAGE:${outputFile}`);
      return outputFile;
    }
    // Try qrencode (common on Linux/macOS)
    const qr = execSync(`echo -n "${data}" | qrencode -t UTF8 -m 2`, { 
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'ignore']
    });
    console.log(qr);
  } catch (e) {
    // Try Python qrcode as fallback
    try {
      if (outputFile) {
        execSync(`python3 -c "import qrcode; qr=qrcode.make('${data}'); qr.save('${outputFile}')"`, {
          stdio: ['pipe', 'pipe', 'ignore']
        });
        console.log(`QR_IMAGE:${outputFile}`);
        return outputFile;
      }
      const qr = execSync(`python3 -c "import qrcode; qr=qrcode.QRCode(border=1); qr.add_data('${data}'); qr.print_ascii(invert=True)"`, {
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'ignore']
      });
      console.log(qr);
    } catch (e2) {
      console.log('📱 Scan with wallet app (install qrencode for QR display)');
    }
  }
  return null;
}

// Config paths
const CONFIG_PATH = path.join(process.env.HOME, '.lightning-config.json');
const CONTACTS_PATH = path.join(process.env.HOME, '.lightning-contacts.json');
const LNI_PATH = path.join(__dirname, '..', 'lib');

// Load contacts
function loadContacts() {
  if (!fs.existsSync(CONTACTS_PATH)) {
    return { contacts: [] };
  }
  return JSON.parse(fs.readFileSync(CONTACTS_PATH, 'utf8'));
}

// Save contacts
function saveContacts(data) {
  fs.writeFileSync(CONTACTS_PATH, JSON.stringify(data, null, 2));
}

// Resolve contact name to destination
function resolveContact(nameOrDest) {
  const contacts = loadContacts();
  const contact = contacts.contacts.find(c => c.name.toLowerCase() === nameOrDest.toLowerCase());
  if (contact) {
    return { destination: contact.destination, contact };
  }
  return { destination: nameOrDest, contact: null };
}

// Add a contact
function addContact(name, destination, type) {
  const data = loadContacts();
  // Remove existing with same name
  data.contacts = data.contacts.filter(c => c.name.toLowerCase() !== name.toLowerCase());
  data.contacts.push({
    name,
    destination,
    type,
    added: new Date().toISOString().split('T')[0]
  });
  saveContacts(data);
  return data;
}

// List contacts
function listContacts() {
  const data = loadContacts();
  return data.contacts;
}

// Load LNI
let lni;
try {
  lni = require(LNI_PATH);
} catch (e) {
  console.error('❌ LNI binary not found. Run: cd ~/workspace/skills/lightning && npm run download');
  console.error('Error:', e.message);
  process.exit(1);
}

// Load config
function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
}

// Create node instance based on backend
function createNode(config) {
  switch (config.backend) {
    case 'lnd':
      return {
        type: 'lnd',
        node: new lni.LndNode({
          url: config.url,
          macaroon: config.macaroon,
          socks5Proxy: config.socks5Proxy,
          acceptInvalidCerts: config.acceptInvalidCerts,
          httpTimeout: config.httpTimeout
        })
      };
    
    case 'cln':
      return {
        type: 'cln',
        node: new lni.ClnNode({
          url: config.url,
          rune: config.rune,
          socks5Proxy: config.socks5Proxy,
          acceptInvalidCerts: config.acceptInvalidCerts,
          httpTimeout: config.httpTimeout
        })
      };
    
    case 'phoenixd':
      return {
        type: 'phoenixd',
        node: new lni.PhoenixdNode({
          url: config.url,
          password: config.password,
          socks5Proxy: config.socks5Proxy,
          acceptInvalidCerts: config.acceptInvalidCerts,
          httpTimeout: config.httpTimeout
        })
      };
    
    case 'nwc':
      return {
        type: 'nwc',
        node: new lni.NwcNode({
          nwcUri: config.nwcUri,
          socks5Proxy: config.socks5Proxy,
          acceptInvalidCerts: config.acceptInvalidCerts,
          httpTimeout: config.httpTimeout
        })
      };
    
    case 'strike':
      return {
        type: 'strike',
        node: new lni.StrikeNode({
          apiKey: config.apiKey,
          baseUrl: config.baseUrl,
          socks5Proxy: config.socks5Proxy,
          acceptInvalidCerts: config.acceptInvalidCerts,
          httpTimeout: config.httpTimeout
        })
      };
    
    case 'blink':
      return {
        type: 'blink',
        node: new lni.BlinkNode({
          apiKey: config.apiKey,
          baseUrl: config.baseUrl,
          socks5Proxy: config.socks5Proxy,
          acceptInvalidCerts: config.acceptInvalidCerts,
          httpTimeout: config.httpTimeout
        })
      };
    
    case 'speed':
      return {
        type: 'speed',
        node: new lni.SpeedNode({
          apiKey: config.apiKey,
          baseUrl: config.baseUrl,
          socks5Proxy: config.socks5Proxy,
          acceptInvalidCerts: config.acceptInvalidCerts,
          httpTimeout: config.httpTimeout
        })
      };
    
    case 'spark':
      const sparkNode = new lni.SparkNode({
        mnemonic: config.mnemonic,
        passphrase: config.passphrase,
        apiKey: config.apiKey,
        storageDir: config.storageDir,
        network: config.network || 'mainnet'
      });
      return {
        type: 'spark',
        node: sparkNode,
        needsConnect: true
      };
    
    default:
      throw new Error(`Unknown backend: ${config.backend}`);
  }
}

// Commands
async function getInfo(node) {
  try {
    const info = await node.node.getInfo();
    console.log('⚡ Lightning Node Info');
    console.log('='.repeat(40));
    console.log(`Backend: ${node.type.toUpperCase()}`);
    if (info.alias) console.log(`Alias: ${info.alias}`);
    if (info.pubkey) console.log(`Pubkey: ${info.pubkey}`);
    if (info.blockHeight) console.log(`Block Height: ${info.blockHeight}`);
    
    // Handle different balance formats
    let balanceSats = info.balanceSat || 0;
    if (info.sendBalanceMsat !== undefined) {
      balanceSats = Math.floor(info.sendBalanceMsat / 1000);
    }
    
    console.log(`Balance: ${balanceSats.toLocaleString()} sats`);
    
    // Spark-specific: show receive capacity
    if (info.receiveBalanceMsat !== undefined) {
      const receiveSats = Math.floor(info.receiveBalanceMsat / 1000);
      console.log(`Receive Capacity: ${receiveSats.toLocaleString()} sats`);
    }
    
    return info;
  } catch (e) {
    console.error(`❌ Failed to get info: ${e.message}`);
    throw e;
  }
}

async function getBalance(node) {
  try {
    const info = await node.node.getInfo();
    const balance = info.balanceSat || 0;
    console.log(`⚡ Balance: ${balance.toLocaleString()} sats`);
    return balance;
  } catch (e) {
    console.error(`❌ Failed to get balance: ${e.message}`);
    throw e;
  }
}

// Watch for invoice payment (polls with lookupInvoice)
async function watchInvoice(node, paymentHash, amountSats, intervalMs = 3000, maxMs = 300000) {
  const startTime = Date.now();
  console.log(`\n👀 Watching for payment (${maxMs / 1000}s timeout, polling every ${intervalMs/1000}s)...`);
  
  while (Date.now() - startTime < maxMs) {
    try {
      const invoice = await node.node.lookupInvoice({ paymentHash });
      
      if (invoice.settledAt && invoice.settledAt > 0) {
        console.log('\n' + '='.repeat(40));
        console.log('✅ PAYMENT RECEIVED!');
        console.log('='.repeat(40));
        console.log(`Amount: ${amountSats} sats`);
        console.log(`Preimage: ${invoice.preimage}`);
        
        // Execute callback command if provided
        if (global.onPaidCallback) {
          try {
            const callbackCmd = global.onPaidCallback
              .replace('{amount}', amountSats)
              .replace('{hash}', paymentHash)
              .replace('{preimage}', invoice.preimage);
            execSync(callbackCmd, { stdio: 'inherit' });
          } catch (e) {
            console.error('Callback failed:', e.message);
          }
        }
        
        // Write to file if specified
        if (global.onPaidFile) {
          fs.writeFileSync(global.onPaidFile, JSON.stringify({
            paid: true,
            amount: amountSats,
            paymentHash,
            preimage: invoice.preimage,
            settledAt: invoice.settledAt
          }, null, 2));
        }
        
        // Send notification via clawdbot
        if (global.notifyTarget) {
          try {
            const msg = `✅ PAYMENT RECEIVED!\n\n⚡ Amount: ${amountSats} sats\n\n🔑 Preimage:\n\\\`${invoice.preimage}\\\`\n\n🔗 Payment Hash:\n\\\`${paymentHash}\\\``;
            const channel = global.notifyChannel || 'telegram';
            execSync(`clawdbot message send --channel ${channel} --target "${global.notifyTarget}" --message "${msg}"`, {
              stdio: 'ignore'
            });
            console.log('📨 Notification sent!');
          } catch (e) {
            console.error('Notification failed:', e.message);
          }
        }
        
        return { paid: true, invoice };
      }
    } catch (e) {
      // Ignore lookup errors, keep polling
    }
    await new Promise(r => setTimeout(r, intervalMs));
  }
  
  console.log('\n⏰ Watch timeout - invoice may still be paid later');
  return { paid: false };
}

async function createInvoice(node, amountSats, memo = '') {
  try {
    const params = {
      invoiceType: 'Bolt11',
      amountMsats: amountSats * 1000,
      description: memo || 'Lightning payment',
      expiry: Math.floor(Date.now() / 1000) + 3600 // 1 hour
    };
    
    const invoice = await node.node.createInvoice(params);
    const bolt11 = invoice.serialized || invoice.invoice; // Spark uses 'invoice', others use 'serialized'
    
    console.log('⚡ Invoice Created');
    console.log('='.repeat(40));
    console.log(`Amount: ${amountSats} sats`);
    console.log(`Memo: ${memo || '(none)'}`);
    console.log(`Payment Hash: ${invoice.paymentHash}`);
    console.log('');
    console.log('Invoice:');
    console.log(bolt11);
    console.log('');
    
    // Generate QR code (image file if qrImagePath provided)
    const qrPath = printQRCode(bolt11.toUpperCase(), global.qrImagePath);
    
    return { ...invoice, bolt11, qrPath };
  } catch (e) {
    console.error(`❌ Failed to create invoice: ${e.message}`);
    throw e;
  }
}

async function payInvoice(node, bolt11, feeLimitPct = 1.0, confirmed = false) {
  try {
    // If not confirmed, just decode and return details for approval
    if (!confirmed) {
      const decoded = decodeInvoiceLocal(bolt11);
      console.log('⚡ Invoice Details (CONFIRM BEFORE PAYING)');
      console.log('='.repeat(40));
      console.log(`Amount: ${decoded.amountSats.toLocaleString()} sats`);
      console.log(`Invoice: ${bolt11.substring(0, 50)}...`);
      console.log('');
      console.log('⚠️  To confirm payment, run:');
      console.log(`/lightning confirm ${bolt11}`);
      return { needsConfirmation: true, ...decoded };
    }
    
    // Confirmed - actually pay
    console.log('⚡ Paying invoice...');
    
    const params = {
      invoice: bolt11,
      feeLimitPercentage: feeLimitPct,
      allowSelfPayment: false
    };
    
    const result = await node.node.payInvoice(params);
    const amountSats = result.amountSat || Math.floor((result.amountMsats || 0) / 1000);
    const feeSats = result.routingFeeSat || Math.floor((result.feesPaid || 0) / 1000);
    
    console.log('✅ Payment Successful!');
    console.log('='.repeat(40));
    console.log(`Amount: ${amountSats.toLocaleString()} sats`);
    console.log(`Fee: ${feeSats} sats`);
    console.log(`Preimage: ${result.preimage}`);
    return result;
  } catch (e) {
    console.error(`❌ Payment failed: ${e.message}`);
    throw e;
  }
}

// Pay any destination (Lightning Address, LNURL, or BOLT11)
// Uses native LNI resolution
async function payAnyDestination(node, destination, amountSats, confirmed = false) {
  try {
    const amountMsats = amountSats ? amountSats * 1000 : null;
    
    // Check if needs resolution (Lightning Address or LNURL)
    if (lni.needsResolution(destination)) {
      // Get payment info for confirmation
      if (!confirmed) {
        console.log(`🔍 Fetching payment info: ${destination}`);
        const info = await lni.getPaymentInfo(destination, amountMsats);
        
        const minSats = info.minSendableMsats ? Math.ceil(info.minSendableMsats / 1000) : null;
        const maxSats = info.maxSendableMsats ? Math.floor(info.maxSendableMsats / 1000) : null;
        
        console.log('');
        console.log(`⚡ ${info.destinationType === 'lightning_address' ? 'Lightning Address' : 'LNURL'} Payment (CONFIRM BEFORE PAYING)`);
        console.log('='.repeat(40));
        console.log(`To: ${destination}`);
        console.log(`Amount: ${amountSats.toLocaleString()} sats`);
        if (info.description) {
          try {
            const meta = JSON.parse(info.description);
            const desc = meta.find(m => m[0] === 'text/plain');
            if (desc) console.log(`Description: ${desc[1]}`);
          } catch (e) {
            console.log(`Description: ${info.description.substring(0, 50)}`);
          }
        }
        if (minSats && maxSats) {
          console.log(`Min: ${minSats} sats | Max: ${maxSats.toLocaleString()} sats`);
        }
        console.log('');
        console.log('⚠️  To confirm payment, run:');
        console.log(`/lightning confirm ${destination} ${amountSats}`);
        return { needsConfirmation: true, destination, amountSats };
      }
      
      // Confirmed - resolve to BOLT11 and pay
      console.log(`📥 Resolving ${destination} to invoice...`);
      const bolt11 = await lni.resolveToBolt11(destination, amountMsats);
      
      console.log(`⚡ Paying (${amountSats} sats)...`);
      
      const params = {
        invoice: bolt11,
        feeLimitPercentage: 1.0,
        allowSelfPayment: false
      };
      
      const result = await node.node.payInvoice(params);
      const paidSats = result.amountSat || Math.floor((result.amountMsats || 0) / 1000);
      const feeSats = result.routingFeeSat || Math.floor((result.feesPaid || 0) / 1000);
      
      console.log('✅ Payment Successful!');
      console.log('='.repeat(40));
      console.log(`To: ${destination}`);
      console.log(`Amount: ${paidSats.toLocaleString()} sats`);
      console.log(`Fee: ${feeSats} sats`);
      if (result.preimage) console.log(`Preimage: ${result.preimage}`);
      return result;
    } else {
      // Direct BOLT11 - use existing payInvoice flow
      return await payInvoice(node, destination, 1.0, confirmed);
    }
  } catch (e) {
    console.error(`❌ Payment failed: ${e.message}`);
    throw e;
  }
}

// Pay BOLT12 offer
async function payBolt12Offer(node, offer, amountSats, confirmed = false) {
  try {
    if (!confirmed) {
      console.log('⚡ BOLT12 Offer Payment (CONFIRM BEFORE PAYING)');
      console.log('='.repeat(40));
      console.log(`Amount: ${amountSats.toLocaleString()} sats`);
      console.log(`Offer: ${offer.substring(0, 50)}...`);
      console.log('');
      console.log('⚠️  To confirm payment, run:');
      console.log(`/lightning confirm ${offer} ${amountSats}`);
      return { needsConfirmation: true, amountSats, offer };
    }
    
    // Confirmed - actually pay the offer
    console.log(`⚡ Paying BOLT12 offer (${amountSats} sats)...`);
    
    const result = await node.node.payOffer(offer, amountSats * 1000, 'Payment via Clawdbot');
    
    const paidSats = result.amountSat || Math.floor((result.amountMsats || 0) / 1000);
    const feeSats = result.routingFeeSat || Math.floor((result.feesPaid || 0) / 1000);
    
    console.log('✅ Payment Successful!');
    console.log('='.repeat(40));
    console.log(`Amount: ${paidSats.toLocaleString()} sats`);
    console.log(`Fee: ${feeSats} sats`);
    if (result.preimage) console.log(`Preimage: ${result.preimage}`);
    return result;
  } catch (e) {
    console.error(`❌ BOLT12 payment failed: ${e.message}`);
    throw e;
  }
}

// Local invoice decoder (no node connection needed)
function decodeInvoiceLocal(bolt11) {
  let amountSats = 0;
  
  // Parse amount from BOLT11 prefix
  const amountMatch = bolt11.toLowerCase().match(/^ln(bc|tb|tbs)(\d+)([munp]?)/);
  if (amountMatch) {
    const num = parseInt(amountMatch[2]);
    const unit = amountMatch[3] || '';
    switch (unit) {
      case 'm': amountSats = num * 100000; break;  // milli-bitcoin
      case 'u': amountSats = num * 100; break;      // micro-bitcoin  
      case 'n': amountSats = num / 10; break;       // nano-bitcoin
      case 'p': amountSats = num / 10000; break;    // pico-bitcoin
      default: amountSats = num * 100000000;        // full bitcoin
    }
  }
  
  return { amountSats: Math.round(amountSats), invoice: bolt11 };
}

async function decodeInvoice(node, destination) {
  try {
    // Detect type using LNI
    let payType;
    try {
      payType = lni.detectPaymentType(destination);
    } catch (e) {
      payType = 'unknown';
    }

    // Try native node decode first (works for BOLT11, BOLT12, and more)
    try {
      const decoded = await node.node.decode(destination);
      const result = typeof decoded === 'string' ? JSON.parse(decoded) : decoded;

      console.log('⚡ Decoded Payment');
      console.log('='.repeat(40));
      console.log(`Type: ${result.type || payType}`);
      console.log(`Valid: ${result.valid ? '✅' : '❌'}`);

      if (result.offer_id) console.log(`Offer ID: ${result.offer_id}`);
      if (result.offer_description) console.log(`Description: ${result.offer_description}`);
      if (result.offer_node_id) console.log(`Node ID: ${result.offer_node_id}`);
      if (result.offer_amount_msat) {
        const sats = Math.floor(parseInt(result.offer_amount_msat) / 1000);
        console.log(`Amount: ${sats.toLocaleString()} sats`);
      }
      if (result.invreq_amount_msat) {
        const sats = Math.floor(parseInt(result.invreq_amount_msat) / 1000);
        console.log(`Requested Amount: ${sats.toLocaleString()} sats`);
      }
      if (result.invoice_amount_msat) {
        const sats = Math.floor(parseInt(result.invoice_amount_msat) / 1000);
        console.log(`Invoice Amount: ${sats.toLocaleString()} sats`);
      }
      if (result.invoice_payment_hash) console.log(`Payment Hash: ${result.invoice_payment_hash}`);

      // Blinded paths info
      if (result.offer_paths && result.offer_paths.length > 0) {
        console.log(`Blinded Paths: ${result.offer_paths.length}`);
        for (let i = 0; i < result.offer_paths.length; i++) {
          const p = result.offer_paths[i];
          const hops = p.path ? p.path.length : 0;
          console.log(`  Path ${i + 1}: ${hops} hop${hops !== 1 ? 's' : ''}, first node: ${(p.first_node_id || '').substring(0, 20)}...`);
        }
      }

      return result;
    } catch (e) {
      // Fall back to local BOLT11 regex parsing
      if (payType === 'bolt11') {
        const decoded = decodeInvoiceLocal(destination);
        console.log('⚡ Invoice Details');
        console.log('='.repeat(40));
        console.log(`Type: BOLT11`);
        console.log(`Amount: ~${decoded.amountSats.toLocaleString()} sats`);
        console.log(`Invoice: ${destination.substring(0, 40)}...`);
        return decoded;
      }
      throw e;
    }
  } catch (e) {
    console.error(`❌ Failed to decode: ${e.message}`);
    throw e;
  }
}

async function listTransactions(node, limit = 10) {
  try {
    const params = {
      from: 0,
      limit: limit
      // Don't pass paymentHash if we want all transactions
    };
    
    const txns = await node.node.listTransactions(params);
    
    // Sort by settledAt descending (newest first), unsettled at the end
    txns.sort((a, b) => {
      if (a.settledAt && b.settledAt) return b.settledAt - a.settledAt;
      if (a.settledAt && !b.settledAt) return -1;
      if (!a.settledAt && b.settledAt) return 1;
      return 0;
    });
    
    console.log(`⚡ Recent Transactions (${txns.length})`);
    console.log('='.repeat(40));
    
    if (txns.length === 0) {
      console.log('No transactions yet.');
      return txns;
    }
    
    for (const tx of txns) {
      const direction = tx.type === 'incoming' ? '📥' : '📤';
      const amountSats = tx.amountSat || Math.floor((tx.amountMsats || 0) / 1000);
      const settled = tx.settledAt > 0 ? '✅' : '⏳';
      console.log(`${direction} ${settled} ${amountSats.toLocaleString()} sats - ${tx.description || '(no memo)'}`);
    }
    
    return txns;
  } catch (e) {
    console.error(`❌ Failed to list transactions: ${e.message}`);
    throw e;
  }
}

// Main
async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'info';
  
  // Load config
  const config = loadConfig();
  if (!config) {
    console.error('❌ No config found. Create ~/.lightning-config.json');
    console.log(`
Example config:
{
  "backend": "phoenixd",
  "url": "http://127.0.0.1:9740",
  "password": "your-password"
}
`);
    process.exit(1);
  }
  
  // Create node
  let node;
  try {
    node = createNode(config);
    
    // Spark requires explicit connect
    if (node.needsConnect) {
      console.log('🔌 Connecting to Spark/Breez...');
      await node.node.connect();
      console.log('✅ Connected!\n');
    }
  } catch (e) {
    console.error(`❌ Failed to create/connect node: ${e.message}`);
    process.exit(1);
  }
  
  // Execute command
  try {
    switch (command) {
      case 'info':
        await getInfo(node);
        break;
      
      case 'balance':
        await getBalance(node);
        break;
      
      case 'invoice':
      case 'receive':
      case 'create':
        const amount = parseInt(args[1]);
        if (!amount || amount <= 0) {
          console.error('Usage: lightning.js invoice <amount_sats> [memo]');
          process.exit(1);
        }
        const memo = args.slice(2).join(' ');
        const invoiceResult = await createInvoice(node, amount, memo);
        
        // Watch for payment if --watch flag is set
        if (global.watchPayment) {
          await watchInvoice(node, invoiceResult.paymentHash, amount, 3000, 300000);
        }
        break;
      
      case 'contacts':
        const contactsList = listContacts();
        if (contactsList.length === 0) {
          console.log('No contacts saved yet.');
          console.log('Add one: /lightning add <name> <destination>');
        } else {
          console.log('⚡ Lightning Contacts');
          console.log('='.repeat(40));
          for (const c of contactsList) {
            console.log(`${c.name} (${c.type})`);
            console.log(`  ${c.destination.substring(0, 50)}...`);
          }
        }
        break;
      
      case 'add':
        const addName = args[1];
        const addDest = args[2];
        if (!addName || !addDest) {
          console.error('Usage: lightning.js add <name> <destination>');
          process.exit(1);
        }
        try {
          const addType = lni.detectPaymentType(addDest);
          addContact(addName, addDest, addType);
          console.log(`✅ Saved "${addName}" (${addType})`);
        } catch (e) {
          console.error(`❌ Invalid destination: ${e.message}`);
          process.exit(1);
        }
        break;
      
      case 'pay':
        let invoicePay = args[1];
        if (!invoicePay) {
          console.error('Usage: lightning.js pay <invoice|address|contact> [amount_sats]');
          process.exit(1);
        }
        
        // Check if it's a contact name
        const payResolved = resolveContact(invoicePay);
        if (payResolved.contact) {
          console.log(`📇 Contact: ${payResolved.contact.name}`);
          invoicePay = payResolved.destination;
        }
        
        // Use native LNI detection
        let payType;
        try {
          payType = lni.detectPaymentType(invoicePay);
        } catch (e) {
          console.error(`❌ Unknown destination: ${invoicePay}`);
          process.exit(1);
        }
        const payAmount = parseInt(args[2]) || null;
        
        if (payType === 'lightning_address' || payType === 'lnurl') {
          if (!payAmount || payAmount <= 0) {
            console.log(`⚡ ${payType === 'lightning_address' ? 'Lightning Address' : 'LNURL'} Detected`);
            console.log('='.repeat(40));
            console.log(`Destination: ${invoicePay}`);
            console.log('You need to specify the amount to send.');
            console.log('');
            console.log('Usage: /lightning pay <destination> <amount_sats>');
            console.log(`Example: /lightning pay ${invoicePay.substring(0, 30)}${invoicePay.length > 30 ? '...' : ''} 100`);
            break;
          }
          await payAnyDestination(node, invoicePay, payAmount, false);
        } else if (payType === 'bolt12') {
          if (!payAmount || payAmount <= 0) {
            console.log('⚡ BOLT12 Offer Detected');
            console.log('='.repeat(40));
            console.log('This is a reusable BOLT12 offer.');
            console.log('You need to specify the amount to send.');
            console.log('');
            console.log('Usage: /lightning pay <offer> <amount_sats>');
            break;
          }
          await payBolt12Offer(node, invoicePay, payAmount, false);
        } else if (payType === 'bolt11') {
          await payInvoice(node, invoicePay, 1.0, false);
        } else {
          console.error('Unknown payment type. Supported: BOLT11, BOLT12, LNURL, Lightning Address');
          process.exit(1);
        }
        break;
      
      case 'confirm':
        let invoiceConfirm = args[1];
        if (!invoiceConfirm) {
          console.error('Usage: lightning.js confirm <invoice|address|contact> [amount]');
          process.exit(1);
        }
        
        // Check if it's a contact name
        const confirmResolved = resolveContact(invoiceConfirm);
        if (confirmResolved.contact) {
          console.log(`📇 Contact: ${confirmResolved.contact.name}`);
          invoiceConfirm = confirmResolved.destination;
        }
        
        let confirmType;
        try {
          confirmType = lni.detectPaymentType(invoiceConfirm);
        } catch (e) {
          console.error(`❌ Unknown destination: ${invoiceConfirm}`);
          process.exit(1);
        }
        const confirmAmount = parseInt(args[2]) || null;
        
        if (confirmType === 'lightning_address' || confirmType === 'lnurl') {
          if (!confirmAmount || confirmAmount <= 0) {
            console.error(`${confirmType === 'lightning_address' ? 'Lightning Address' : 'LNURL'} requires an amount: /lightning confirm <destination> <amount_sats>`);
            process.exit(1);
          }
          await payAnyDestination(node, invoiceConfirm, confirmAmount, true);
        } else if (confirmType === 'bolt12') {
          if (!confirmAmount || confirmAmount <= 0) {
            console.error('BOLT12 offers require an amount: /lightning confirm <offer> <amount_sats>');
            process.exit(1);
          }
          await payBolt12Offer(node, invoiceConfirm, confirmAmount, true);
        } else if (confirmType === 'bolt11') {
          await payInvoice(node, invoiceConfirm, 1.0, true);
        } else {
          console.error('Unknown payment type.');
          process.exit(1);
        }
        break;
      
      case 'decode':
        let decodeDest = args[1];
        if (!decodeDest) {
          console.error('Usage: lightning.js decode <bolt11|bolt12|contact>');
          process.exit(1);
        }
        // Resolve contact name
        const decodeResolved = resolveContact(decodeDest);
        if (decodeResolved.contact) {
          console.log(`📇 Contact: ${decodeResolved.contact.name}`);
          decodeDest = decodeResolved.destination;
        }
        await decodeInvoice(node, decodeDest);
        break;
      
      case 'history':
        const limit = parseInt(args[1]) || 10;
        await listTransactions(node, limit);
        break;
      
      default:
        console.log(`
⚡ Lightning CLI

Commands:
  info              Show node info & balance
  balance           Show balance only
  invoice <sats> [memo]  Create invoice (aliases: receive, create)
  pay <bolt11>      Decode & request confirmation
  confirm <bolt11>  Actually pay (after review)
  decode <bolt11>   Decode invoice
  history [limit]   List transactions

Examples:
  lightning.js invoice 1000 "Coffee"
  lightning.js pay lnbc1000n1pj...    # Shows amount, asks to confirm
  lightning.js confirm lnbc1000n1pj... # Actually sends payment
  lightning.js balance
`);
    }
  } catch (e) {
    process.exit(1);
  }
}

// Parse flags before running
const qrImageIdx = process.argv.indexOf('--qr-image');
if (qrImageIdx !== -1) {
  global.qrImagePath = process.argv[qrImageIdx + 1] || '/tmp/lightning-qr.png';
  process.argv.splice(qrImageIdx, 2);
}

const watchIdx = process.argv.indexOf('--watch');
if (watchIdx !== -1) {
  global.watchPayment = true;
  process.argv.splice(watchIdx, 1);
}

const callbackIdx = process.argv.indexOf('--on-paid');
if (callbackIdx !== -1) {
  global.onPaidCallback = process.argv[callbackIdx + 1];
  process.argv.splice(callbackIdx, 2);
}

const fileIdx = process.argv.indexOf('--on-paid-file');
if (fileIdx !== -1) {
  global.onPaidFile = process.argv[fileIdx + 1] || '/tmp/lightning-paid.json';
  process.argv.splice(fileIdx, 2);
}

const notifyIdx = process.argv.indexOf('--notify');
if (notifyIdx !== -1) {
  global.notifyTarget = process.argv[notifyIdx + 1];
  process.argv.splice(notifyIdx, 2);
}

const notifyChannelIdx = process.argv.indexOf('--notify-channel');
if (notifyChannelIdx !== -1) {
  global.notifyChannel = process.argv[notifyChannelIdx + 1];
  process.argv.splice(notifyChannelIdx, 2);
}

main();
