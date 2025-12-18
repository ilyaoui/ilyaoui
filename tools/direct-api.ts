/**
 * Direct API Caller
 *
 * Use this when you know the API endpoint
 */

import fetch from 'node-fetch';
import fs from 'fs';

interface APIConfig {
  url: string;
  method?: 'GET' | 'POST';
  headers?: Record<string, string>;
  body?: any;
}

async function callAPI(config: APIConfig) {
  console.log(`\n🌐 Calling API: ${config.method || 'GET'} ${config.url}`);

  try {
    const response = await fetch(config.url, {
      method: config.method || 'GET',
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ...config.headers,
      },
      body: config.body ? JSON.stringify(config.body) : undefined,
    });

    console.log(`✅ Status: ${response.status}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`✅ Response received`);
    console.log(`   Data keys: ${Object.keys(data).join(', ')}`);

    return data;
  } catch (error) {
    console.error(`❌ Error: ${error}`);
    throw error;
  }
}

function parseMatches(data: any): any[] {
  const matches: any[] = [];

  // Try common JSON structures
  const possiblePaths = [
    'games',
    'matches',
    'schedule',
    'data.games',
    'data.matches',
    'data.schedule',
    'results',
    'data',
  ];

  let gamesArray: any[] | null = null;

  // Try to find the games array
  for (const path of possiblePaths) {
    const parts = path.split('.');
    let current: any = data;

    for (const part of parts) {
      if (current && typeof current === 'object' && part in current) {
        current = current[part];
      } else {
        current = null;
        break;
      }
    }

    if (Array.isArray(current)) {
      gamesArray = current;
      console.log(`\n✅ Found games array at: ${path} (${current.length} items)`);
      break;
    }
  }

  if (!gamesArray) {
    console.log('\n⚠️ Could not find games array. Data structure:');
    console.log(JSON.stringify(data, null, 2).slice(0, 500));
    return [];
  }

  // Parse each game
  for (const game of gamesArray) {
    try {
      const match = {
        home: game.homeTeam || game.home_team || game.team1 || game.teamA || '',
        away: game.awayTeam || game.away_team || game.team2 || game.teamB || '',
        date: game.date || game.datetime || game.startTime || game.start_time || '',
        time: game.time || '',
        location: game.location || game.venue || game.court || game.field || '',
        competition: game.competition || game.division || game.pool || '',
        raw: game,
      };

      if (match.home || match.away) {
        matches.push(match);
      }
    } catch (error) {
      console.error(`Error parsing game:`, error);
    }
  }

  console.log(`✅ Parsed ${matches.length} matches`);
  return matches;
}

async function main() {
  // Example usage - replace with actual API endpoint
  const apiUrl = process.argv[2] || 'PASTE_API_URL_HERE';

  if (apiUrl === 'PASTE_API_URL_HERE') {
    console.log('\n❌ Please provide API URL:');
    console.log('   npx tsx tools/direct-api.ts "https://api.example.com/schedules/123"');
    console.log('\nOr edit the script and replace PASTE_API_URL_HERE with your API endpoint');
    return;
  }

  console.log('🚀 Direct API Scraper\n');

  // Call API
  const data = await callAPI({ url: apiUrl });

  // Save raw response
  const rawFile = 'api-response-raw.json';
  fs.writeFileSync(rawFile, JSON.stringify(data, null, 2));
  console.log(`\n💾 Raw API response saved to: ${rawFile}`);

  // Parse matches
  const matches = parseMatches(data);

  if (matches.length > 0) {
    // Save parsed matches
    const matchesFile = 'api-matches-parsed.json';
    fs.writeFileSync(matchesFile, JSON.stringify(matches, null, 2));
    console.log(`💾 Parsed matches saved to: ${matchesFile}`);

    // Display summary
    console.log('\n📊 Summary:');
    console.log(`   Total matches: ${matches.length}`);
    console.log('\n📋 First 3 matches:');
    matches.slice(0, 3).forEach((match, i) => {
      console.log(`\n   ${i + 1}. ${match.home} vs ${match.away}`);
      console.log(`      Date: ${match.date} ${match.time}`);
      console.log(`      Location: ${match.location || 'N/A'}`);
    });

    // Save as CSV
    const csv = [
      'Home,Away,Date,Time,Location,Competition',
      ...matches.map(m =>
        `"${m.home}","${m.away}","${m.date}","${m.time}","${m.location}","${m.competition}"`
      )
    ].join('\n');

    const csvFile = 'api-matches.csv';
    fs.writeFileSync(csvFile, csv);
    console.log(`\n💾 CSV exported to: ${csvFile}`);
  } else {
    console.log('\n❌ No matches found. Check the data structure in api-response-raw.json');
  }
}

main().catch(console.error);
