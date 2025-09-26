import {exec} from 'node:child_process';
import {promisify} from 'node:util';
import React, {useState, useCallback, useEffect, useMemo} from 'react';
import {Box, Text, useInput, useApp} from 'ink';

const execAsync = promisify(exec);

type Command = {
	name: string;
	description: string;
	handler: () => Promise<void>;
};

export default function App() {
	const [input, setInput] = useState('');
	const [output, setOutput] = useState<string[]>([]);
	const [isExecuting, setIsExecuting] = useState(false);
	const [suggestions, setSuggestions] = useState<string[]>([]);
	const {exit} = useApp();

	const addOutput = useCallback((text: string) => {
		setOutput(previous => {
			const lines = text.split('\n').filter(line => line.trim() !== '');
			return [...previous, ...lines];
		});
	}, []);

	const commands = useMemo(
		(): Command[] => [
			{
				name: '/ls',
				description: 'List files in current directory',
				async handler() {
					try {
						const {stdout} = await execAsync('ls -la');
						addOutput(stdout.trim());
					} catch (error: unknown) {
						addOutput(
							`Error: ${
								error instanceof Error ? error.message : String(error)
							}`,
						);
					}
				},
			},
			{
				name: '/pwd',
				description: 'Show current working directory',
				async handler() {
					try {
						const {stdout} = await execAsync('pwd');
						addOutput(stdout.trim());
					} catch (error: unknown) {
						addOutput(
							`Error: ${
								error instanceof Error ? error.message : String(error)
							}`,
						);
					}
				},
			},
			{
				name: '/date',
				description: 'Show current date and time',
				async handler() {
					try {
						const {stdout} = await execAsync('date');
						addOutput(stdout.trim());
					} catch (error: unknown) {
						addOutput(
							`Error: ${
								error instanceof Error ? error.message : String(error)
							}`,
						);
					}
				},
			},
		],
		[addOutput],
	);

	const executeCommand = useCallback(
		async (commandName: string) => {
			const command = commands.find(cmd => cmd.name === commandName);
			if (command) {
				setIsExecuting(true);
				addOutput(`$ ${commandName}`);
				await command.handler();
				setIsExecuting(false);
			} else {
				addOutput(`Unknown command: ${commandName}`);
				addOutput('Available commands:');
				for (const cmd of commands) {
					addOutput(`  ${cmd.name} - ${cmd.description}`);
				}
			}
		},
		[commands, addOutput],
	);

	const handleTabCompletion = useCallback(() => {
		const matchingCommands = commands.filter(cmd => cmd.name.startsWith(input));

		if (matchingCommands.length === 1) {
			setInput(matchingCommands[0]!.name);
			setSuggestions([]);
		}
	}, [input, commands]);

	const updateSuggestions = useCallback(() => {
		if (input.startsWith('/') && input.length > 1) {
			const matchingCommands = commands
				.filter(cmd => cmd.name.startsWith(input))
				.map(cmd => `${cmd.name} - ${cmd.description}`);
			setSuggestions(matchingCommands);
		} else if (input.startsWith('/') && input.length === 1) {
			setSuggestions(commands.map(cmd => `${cmd.name} - ${cmd.description}`));
		} else {
			setSuggestions([]);
		}
	}, [input, commands]);

	useEffect(() => {
		updateSuggestions();
	}, [updateSuggestions]);

	useInput((char, key) => {
		if (key.return) {
			if (input === '/exit' || input === '/quit') {
				exit();
				return;
			}

			if (input.trim()) {
				void executeCommand(input.trim());
				setInput('');
			}
		} else if (key.tab) {
			handleTabCompletion();
		} else if (key.backspace || key.delete) {
			setInput(previous => previous.slice(0, -1));
		} else if (!key.ctrl && !key.meta && char) {
			setInput(previous => previous + char);
		}
	});

	useEffect(() => {
		addOutput('Welcome to DumbFi CLI!');
		addOutput('Type a command to get started (use Tab for autocompletion):');
		for (const cmd of commands) {
			addOutput(`  ${cmd.name} - ${cmd.description}`);
		}

		addOutput('  /exit - Exit the CLI');
		addOutput('');
	}, [commands, addOutput]);

	const renderedOutput = useMemo(() => {
		return output
			.slice(-50)
			.map((line, index) => (
				<Text key={`${output.length - 50 + index}-${line.slice(0, 10)}`}>
					{line}
				</Text>
			));
	}, [output]);

	return (
		<Box flexDirection="column" height="100%">
			{/* Scrollable output area */}
			<Box
				flexDirection="column"
				flexGrow={1}
				overflow="hidden"
				marginBottom={1}
			>
				{renderedOutput}
			</Box>

			{/* Input box with border */}
			<Box flexDirection="column">
				<Box
					borderStyle="round"
					borderColor="blue"
					paddingX={1}
					paddingY={0}
					flexDirection="row"
					alignItems="center"
				>
					<Text color="blue">{'>'} </Text>
					<Text>{input}</Text>
					{isExecuting && <Text color="yellow"> (executing...)</Text>}
				</Box>

				{/* Autocomplete suggestions */}
				{suggestions.length > 0 && (
					<Box flexDirection="column" marginTop={1}>
						<Text color="gray">Suggestions:</Text>
						{suggestions.slice(0, 5).map(suggestion => (
							<Text key={suggestion} color="gray">
								{' '}
								{suggestion}
							</Text>
						))}
					</Box>
				)}
			</Box>
		</Box>
	);
}
