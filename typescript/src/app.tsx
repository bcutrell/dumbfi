import React, {useState, useMemo, useCallback} from 'react';
import {Box, useInput} from 'ink';
import type {Command} from './commands.js';
import {createCommandRegistry} from './commands.js';
import {CommandPrompt} from './components/CommandPrompt.js';
import {HelpScreen} from './components/HelpScreen.js';
import {DemoApp} from './components/DemoApp.js';

type AppMode = 'PROMPT' | 'HELP' | 'DEMO';

export default function App() {
	const [mode, setMode] = useState<AppMode>('PROMPT');

	const handleDemo = useCallback(() => {
		setMode('DEMO');
	}, []);

	const handleHelp = useCallback(() => {
		setMode('HELP');
	}, []);

	const handleBackToPrompt = useCallback(() => {
		setMode('PROMPT');
	}, []);

	const registry = useMemo(
		() => createCommandRegistry(handleDemo, handleHelp),
		[handleDemo, handleHelp],
	);

	const handleExecuteCommand = useCallback((command: Command) => {
		command.execute();
	}, []);

	// Handle any key press to go back from help screen
	useInput(() => {
		if (mode === 'HELP') {
			handleBackToPrompt();
		}
	});

	return (
		<Box>
			{mode === 'PROMPT' && (
				<CommandPrompt
					registry={registry}
					onExecute={handleExecuteCommand}
				/>
			)}

			{mode === 'HELP' && (
				<HelpScreen registry={registry} onBack={handleBackToPrompt} />
			)}

			{mode === 'DEMO' && <DemoApp onExit={handleBackToPrompt} />}
		</Box>
	);
}