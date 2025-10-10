import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import type {GameState} from './types.js';

const STATE_FILE = path.join(os.homedir(), 'definitely_not_gambling.json');

export function saveState(state: GameState): void {
	try {
		fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
	} catch (error) {
		console.error('Failed to save state:', error);
	}
}

export function loadState(): GameState | null {
	try {
		if (fs.existsSync(STATE_FILE)) {
			const data = fs.readFileSync(STATE_FILE, 'utf8');
			return JSON.parse(data) as GameState;
		}
	} catch (error) {
		console.error('Failed to load state:', error);
	}

	return null;
}

export function clearState(): void {
	try {
		if (fs.existsSync(STATE_FILE)) {
			fs.unlinkSync(STATE_FILE);
		}
	} catch (error) {
		console.error('Failed to clear state:', error);
	}
}