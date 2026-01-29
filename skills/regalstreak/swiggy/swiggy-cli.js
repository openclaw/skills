#!/usr/bin/env node

/**
 * Swiggy CLI - Wrapper for Swiggy MCP servers
 * Uses mcporter under the hood to connect to:
 * - https://mcp.swiggy.com/food
 * - https://mcp.swiggy.com/im (Instamart)
 * - https://mcp.swiggy.com/dineout
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const MCP_SERVERS = {
  food: 'https://mcp.swiggy.com/food',
  im: 'https://mcp.swiggy.com/im',
  dineout: 'https://mcp.swiggy.com/dineout'
};

function exec(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', stdio: 'pipe' });
  } catch (err) {
    console.error('Error:', err.message);
    if (err.stderr) console.error(err.stderr);
    process.exit(1);
  }
}

function callMCP(server, tool, args = {}) {
  const argsJson = JSON.stringify(args);
  const cmd = `mcporter call --server "${MCP_SERVERS[server]}" --tool "${tool}" --args '${argsJson}'`;
  return exec(cmd);
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
Swiggy CLI - Order food, groceries, and book restaurants

Usage:
  swiggy food search <query> [--location <loc>]
  swiggy food menu <restaurant-id>
  swiggy food cart add <item-id> [--quantity <n>]
  swiggy food cart show
  swiggy food cart clear
  swiggy food order --address <addr> --confirm

  swiggy im search <query> [--location <loc>]
  swiggy im cart add <item-id> [--quantity <n>]
  swiggy im cart show
  swiggy im cart clear
  swiggy im order --address <addr> --confirm

  swiggy dineout search <query>
  swiggy dineout details <restaurant-id>
  swiggy dineout slots <restaurant-id> --date <YYYY-MM-DD>
  swiggy dineout book <restaurant-id> --date <YYYY-MM-DD> --time <HH:MM> --guests <n> --confirm

Options:
  --location    Delivery location (for food/im search)
  --quantity    Item quantity (default: 1)
  --address     Delivery address (required for orders)
  --date        Booking date (YYYY-MM-DD)
  --time        Booking time (HH:MM)
  --guests      Number of guests
  --confirm     Required flag to confirm orders/bookings

Examples:
  swiggy food search "biryani" --location "Koramangala, Bengaluru"
  swiggy im search "eggs" --location "HSR Layout"
  swiggy dineout search "Italian Indiranagar"
`);
    process.exit(0);
  }

  const [service, action, ...rest] = args;

  if (!['food', 'im', 'dineout'].includes(service)) {
    console.error('Invalid service. Use: food, im, or dineout');
    process.exit(1);
  }

  // Parse flags
  const flags = {};
  let positional = [];
  for (let i = 0; i < rest.length; i++) {
    if (rest[i].startsWith('--')) {
      const key = rest[i].slice(2);
      const value = rest[i + 1] && !rest[i + 1].startsWith('--') ? rest[i + 1] : true;
      flags[key] = value;
      if (value !== true) i++; // Skip next arg
    } else {
      positional.push(rest[i]);
    }
  }

  // Route commands to appropriate MCP tools
  let result;

  switch (service) {
    case 'food':
      result = handleFood(action, positional, flags);
      break;
    case 'im':
      result = handleInstamart(action, positional, flags);
      break;
    case 'dineout':
      result = handleDineout(action, positional, flags);
      break;
  }

  console.log(result);
}

function handleFood(action, positional, flags) {
  switch (action) {
    case 'search':
      return callMCP('food', 'search_restaurants', {
        query: positional[0] || '',
        location: flags.location
      });
    
    case 'menu':
      return callMCP('food', 'get_menu', {
        restaurant_id: positional[0]
      });
    
    case 'cart':
      const cartAction = positional[0];
      if (cartAction === 'add') {
        return callMCP('food', 'add_to_cart', {
          item_id: positional[1],
          quantity: parseInt(flags.quantity || 1)
        });
      } else if (cartAction === 'show') {
        return callMCP('food', 'view_cart', {});
      } else if (cartAction === 'clear') {
        return callMCP('food', 'clear_cart', {});
      }
      break;
    
    case 'order':
      if (!flags.confirm) {
        console.error('⚠️  ERROR: --confirm flag required to place order');
        console.error('This is a safety check. Review cart first with: swiggy food cart show');
        process.exit(1);
      }
      if (!flags.address) {
        console.error('ERROR: --address required for order');
        process.exit(1);
      }
      return callMCP('food', 'place_order', {
        address: flags.address
      });
    
    default:
      console.error(`Unknown food action: ${action}`);
      process.exit(1);
  }
}

function handleInstamart(action, positional, flags) {
  switch (action) {
    case 'search':
      return callMCP('im', 'search_products', {
        query: positional[0] || '',
        location: flags.location
      });
    
    case 'cart':
      const cartAction = positional[0];
      if (cartAction === 'add') {
        return callMCP('im', 'add_to_cart', {
          product_id: positional[1],
          quantity: parseInt(flags.quantity || 1)
        });
      } else if (cartAction === 'show') {
        return callMCP('im', 'view_cart', {});
      } else if (cartAction === 'clear') {
        return callMCP('im', 'clear_cart', {});
      }
      break;
    
    case 'order':
      if (!flags.confirm) {
        console.error('⚠️  ERROR: --confirm flag required to place order');
        console.error('This is a safety check. Review cart first with: swiggy im cart show');
        process.exit(1);
      }
      if (!flags.address) {
        console.error('ERROR: --address required for order');
        process.exit(1);
      }
      return callMCP('im', 'checkout', {
        address: flags.address
      });
    
    default:
      console.error(`Unknown instamart action: ${action}`);
      process.exit(1);
  }
}

function handleDineout(action, positional, flags) {
  switch (action) {
    case 'search':
      return callMCP('dineout', 'search_restaurants', {
        query: positional[0] || '',
        location: flags.location
      });
    
    case 'details':
      return callMCP('dineout', 'get_details', {
        restaurant_id: positional[0]
      });
    
    case 'slots':
      if (!flags.date) {
        console.error('ERROR: --date required (format: YYYY-MM-DD)');
        process.exit(1);
      }
      return callMCP('dineout', 'check_availability', {
        restaurant_id: positional[0],
        date: flags.date
      });
    
    case 'book':
      if (!flags.confirm) {
        console.error('⚠️  ERROR: --confirm flag required to book table');
        console.error('This is a safety check. Review details first.');
        process.exit(1);
      }
      if (!flags.date || !flags.time || !flags.guests) {
        console.error('ERROR: --date, --time, and --guests required for booking');
        process.exit(1);
      }
      return callMCP('dineout', 'book_table', {
        restaurant_id: positional[0],
        date: flags.date,
        time: flags.time,
        guests: parseInt(flags.guests)
      });
    
    default:
      console.error(`Unknown dineout action: ${action}`);
      process.exit(1);
  }
}

main();
