export type Command = {
	name: string;
	description: string;
	aliases?: string[];
	execute: () => void;
};

export type CommandRegistry = {
	[key: string]: Command;
};

export const createCommandRegistry = (
	onDemo: () => void,
	onHelp: () => void,
): CommandRegistry => {
	return {
		demo: {
			name: 'demo',
			description: 'Launch the Portfolio Rebalancer 3000™ demo',
			aliases: ['d', 'portfolio'],
			execute: onDemo,
		},
		help: {
			name: 'help',
			description: 'Show all available commands',
			aliases: ['h', '?'],
			execute: onHelp,
		},
	};
};

export const findCommand = (
	registry: CommandRegistry,
	input: string,
): Command | null => {
	const normalized = input.toLowerCase().replace(/^\/+/, '');

	// Exact match
	if (registry[normalized]) {
		return registry[normalized];
	}

	// Check aliases
	for (const command of Object.values(registry)) {
		if (command.aliases?.includes(normalized)) {
			return command;
		}
	}

	return null;
};

export const fuzzySearchCommands = (
	registry: CommandRegistry,
	input: string,
): Command[] => {
	const normalized = input.toLowerCase().replace(/^\/+/, '');

	if (!normalized) {
		return Object.values(registry);
	}

	const commands = Object.values(registry);
	const matches: Array<{command: Command; score: number}> = [];

	for (const command of commands) {
		const searchTargets = [
			command.name,
			command.description.toLowerCase(),
			...(command.aliases || []),
		];

		let bestScore = 0;

		for (const target of searchTargets) {
			const score = calculateFuzzyScore(target, normalized);
			bestScore = Math.max(bestScore, score);
		}

		if (bestScore > 0) {
			matches.push({command, score: bestScore});
		}
	}

	return matches
		.sort((a, b) => b.score - a.score)
		.map(match => match.command);
};

function calculateFuzzyScore(target: string, query: string): number {
	if (target === query) return 100;
	if (target.startsWith(query)) return 80;
	if (target.includes(query)) return 60;

	// Character matching
	let score = 0;
	let queryIndex = 0;

	for (let i = 0; i < target.length && queryIndex < query.length; i++) {
		if (target[i] === query[queryIndex]) {
			score += 10;
			queryIndex++;
		}
	}

	return queryIndex === query.length ? score : 0;
}
