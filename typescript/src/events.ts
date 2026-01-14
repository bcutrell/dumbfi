import type {MarketEvent} from './types.js';
import {randomChoice, randomBetween} from './utils.js';

const POSSIBLE_EVENTS: MarketEvent[] = [
	{
		name: 'Elon tweeted!',
		description: 'Something about crypto and memes',
		impact: {CRYPTO: randomBetween(-0.2, 0.2)},
		emoji: '🐦',
	},
	{
		name: 'Fed printer go BRRR',
		description: 'Money printer activated',
		impact: {
			VTI: 0.05,
			BND: 0.02,
			VXUS: 0.04,
			GOLD: 0.03,
			CRYPTO: 0.08,
		},
		emoji: '🖨️',
	},
	{
		name: 'Mercury is in retrograde',
		description: 'Planets doing weird stuff',
		impact: {VXUS: -0.1},
		emoji: '☿️',
	},
	{
		name: "It's Monday",
		description: 'Nobody likes Mondays',
		impact: {
			VTI: -0.02,
			BND: -0.01,
			VXUS: -0.02,
			GOLD: -0.01,
			CRYPTO: -0.03,
		},
		emoji: '📅',
	},
	{
		name: 'Quarterly earnings beat!',
		description: 'Line goes up!',
		impact: {VTI: 0.03, VXUS: 0.02},
		emoji: '📊',
	},
	{
		name: 'Inflation fears',
		description: 'Money becomes less money',
		impact: {BND: -0.05, GOLD: 0.08},
		emoji: '💸',
	},
	{
		name: 'China sneezed',
		description: 'Markets react accordingly',
		impact: {VXUS: -0.08, VTI: -0.02},
		emoji: '🤧',
	},
	{
		name: 'New variant dropped',
		description: 'COVID-23 just released',
		impact: {
			VTI: -0.06,
			BND: 0.02,
			VXUS: -0.08,
			GOLD: 0.04,
			CRYPTO: -0.05,
		},
		emoji: '🦠',
	},
	{
		name: 'Retail investors FOMO',
		description: 'Reddit found a new toy',
		impact: {VTI: 0.04, CRYPTO: 0.15},
		emoji: '📱',
	},
	{
		name: 'Hedge funds liquidating',
		description: 'Someone got margin called',
		impact: {
			VTI: -0.08,
			BND: -0.03,
			VXUS: -0.1,
			GOLD: -0.05,
			CRYPTO: -0.15,
		},
		emoji: '💀',
	},
	{
		name: 'Bank of Japan intervenes',
		description: 'Yen goes wild',
		impact: {VXUS: 0.06},
		emoji: '🏦',
	},
	{
		name: 'Oil prices spike',
		description: 'Gas is expensive again',
		impact: {VTI: -0.03, VXUS: -0.04, GOLD: 0.02},
		emoji: '⛽',
	},
	{
		name: 'Tech sector rotation',
		description: 'Money moving around',
		impact: {VTI: 0.02, CRYPTO: -0.08},
		emoji: '💻',
	},
	{
		name: 'Dividend announcement',
		description: 'Boomer bonds paid out!',
		impact: {BND: 0.005},
		emoji: '💰',
	},
	{
		name: 'Crypto exchange collapsed',
		description: 'Not your keys, not your coins',
		impact: {CRYPTO: -0.3},
		emoji: '🏚️',
	},
	{
		name: 'New meme stock',
		description: 'Apes together strong',
		impact: {VTI: 0.06},
		emoji: '🦍',
	},
	{
		name: 'Rate hike announced',
		description: 'Fed tightening',
		impact: {BND: -0.04, VTI: -0.05, CRYPTO: -0.1},
		emoji: '📈',
	},
	{
		name: 'Stimulus checks!',
		description: 'Free money from government',
		impact: {
			VTI: 0.04,
			BND: 0.01,
			VXUS: 0.03,
			GOLD: 0.02,
			CRYPTO: 0.12,
		},
		emoji: '💵',
	},
	{
		name: 'Gold rush',
		description: 'Shiny rocks in demand',
		impact: {GOLD: 0.15},
		emoji: '✨',
	},
	{
		name: 'CEO tweeted something dumb',
		description: 'Markets confused',
		impact: {VTI: -0.02},
		emoji: '🤡',
	},
	{
		name: 'Absolutely nothing happened',
		description: 'Market sideways',
		impact: {},
		emoji: '😴',
	},
];

const SPLIT_EVENT: MarketEvent = {
	name: 'Stock split announced!',
	description: 'Your Magic Money ETF just did a 10:1 split! (This changes nothing)',
	impact: {},
	emoji: '✂️',
};

const RENAME_EVENT: MarketEvent = {
	name: 'ETF rebranding',
	description: 'Foreign Mystery ETF changed its name to "Foreign Enigma ETF"',
	impact: {},
	emoji: '🏷️',
};

export function generateRandomEvent(day: number): MarketEvent | null {
	if (Math.random() > 0.3) {
		return null;
	}

	if (day === 100 && Math.random() > 0.5) {
		return SPLIT_EVENT;
	}

	if (day === 150 && Math.random() > 0.7) {
		return RENAME_EVENT;
	}

	return randomChoice(POSSIBLE_EVENTS);
}

export function generateEventDescription(event: MarketEvent): string {
	const impactSymbols = Object.keys(event.impact);

	if (impactSymbols.length === 0) {
		return `${event.emoji} ${event.name}\n   ${event.description}`;
	}

	let description = `${event.emoji} ${event.name}\n   ${event.description}\n   Impact: `;

	const impacts = impactSymbols.map(symbol => {
		const impact = event.impact[symbol as keyof typeof event.impact]!;
		const sign = impact >= 0 ? '+' : '';
		return `${symbol} ${sign}${(impact * 100).toFixed(1)}%`;
	});

	description += impacts.join(', ');

	return description;
}