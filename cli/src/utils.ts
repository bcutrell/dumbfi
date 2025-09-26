import type {Mood} from './types.js';

export function createAsciiBar(
	percentage: number,
	width: number = 20,
): string {
	const filled = Math.round((percentage / 100) * width);
	const empty = width - filled;
	return '█'.repeat(filled) + '░'.repeat(empty);
}

export function formatCurrency(amount: number): string {
	if (amount === 350) return '$tree.fiddy';
	if (Math.abs(amount - 420.69) < 0.01) return '$420.69 (nice)';

	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	}).format(amount);
}

export function formatPercent(decimal: number): string {
	const percent = decimal * 100;
	const sign = percent >= 0 ? '+' : '';
	return `${sign}${percent.toFixed(1)}%`;
}

export function getMoodFromReturn(returnValue: number): Mood {
	if (returnValue > 0.15) return '😊';
	if (returnValue > 0) return '😐';
	if (returnValue > -0.1) return '😰';
	return '🤬';
}

export function getRiskLevel(equityPercent: number): string {
	if (equityPercent <= 20) return 'SLEEPY 😴';
	if (equityPercent <= 40) return 'MILD 🌶️';
	if (equityPercent <= 60) return 'SPICY 🌶️🌶️';
	if (equityPercent <= 80) return 'VERY SPICY 🌶️🌶️🌶️';
	return 'NUCLEAR 🌶️🌶️🌶️🌶️';
}

export function randomBetween(min: number, max: number): number {
	return Math.random() * (max - min) + min;
}

export function randomChoice<T>(array: T[]): T {
	return array[Math.floor(Math.random() * array.length)]!;
}

export function gaussianRandom(mean: number = 0, stdDev: number = 1): number {
	let u = 0;
	let v = 0;
	while (u === 0) u = Math.random();
	while (v === 0) v = Math.random();
	const num = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
	return num * stdDev + mean;
}

export function sleep(ms: number): Promise<void> {
	return new Promise(resolve => setTimeout(resolve, ms));
}

export const ASCII_LOGO = `
  ____                  _     _____ _
 |  _ \\ _   _ _ __ ___ | |__ |  ___(_)
 | | | | | | | '_ \` _ \\| '_ \\| |_  | |
 | |_| | |_| | | | | | | |_) |  _| | |
 |____/ \\__,_|_| |_| |_|_.__/|_|   |_|

 💰  PORTFOLIO REBALANCER 3000™  💰
`;

export const LOADING_MESSAGES = [
	'Consulting the oracle...',
	'Mining bitcoins...',
	'Reticulating splines...',
	'Asking ChatGPT for advice...',
	'Rolling dice...',
	'Calling Jim Cramer...',
	'Reading tea leaves...',
	'Checking Mercury retrograde...',
	'Summoning the spirit of Benjamin Graham...',
	'Sacrificing to the market gods...',
];

export function getRandomLoadingMessage(): string {
	return randomChoice(LOADING_MESSAGES);
}

export function checkEasterEgg(input: string): boolean {
	return input.toLowerCase().includes('diamond hands');
}