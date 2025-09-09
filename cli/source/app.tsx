import React, {useState, useCallback, useEffect, useMemo} from 'react';
import {Box, Text, useInput, useApp} from 'ink';
import {exec} from 'child_process';
import {promisify} from 'util';

const execAsync = promisify(exec);

type Command = {
	name: string;
	description: string;
	handler: () => Promise<void>;
};

type Props = {
	name?: string;
};

export default function App({name}: Props) {
	const [input, setInput] = useState('');
	const [output, setOutput] = useState<string[]>([]);
	const [isExecuting, setIsExecuting] = useState(false);
	const [suggestions, setSuggestions] = useState<string[]>([]);
	const {exit} = useApp();

	const addOutput = useCallback((text: string) => {
		setOutput(prev => {
			const lines = text.split('\n').filter(line => line.trim() !== '');
			return [...prev, ...lines];
		});
	}, []);

	const commands = useMemo((): Command[] => [
		{
			name: '/ls',
			description: 'List files in current directory',
			handler: async () => {
				try {
					const {stdout} = await execAsync('ls -la');
					addOutput(stdout.trim());
				} catch (error) {
					addOutput(`Error: ${error instanceof Error ? error.message : String(error)}`);
				}
			},
		},
		{
			name: '/pwd',
			description: 'Show current working directory',
			handler: async () => {
				try {
					const {stdout} = await execAsync('pwd');
					addOutput(stdout.trim());
				} catch (error) {
					addOutput(`Error: ${error instanceof Error ? error.message : String(error)}`);
				}
			},
		},
		{
			name: '/date',
			description: 'Show current date and time',
			handler: async () => {
				try {
					const {stdout} = await execAsync('date');
					addOutput(stdout.trim());
				} catch (error) {
					addOutput(`Error: ${error instanceof Error ? error.message : String(error)}`);
				}
			},
		},
	], [addOutput]);

	const executeCommand = useCallback(async (commandName: string) => {
		const command = commands.find(cmd => cmd.name === commandName);
		if (command) {
			setIsExecuting(true);
			addOutput(`$ ${commandName}`);
			await command.handler();
			setIsExecuting(false);
		} else {
			addOutput(`Unknown command: ${commandName}`);
			addOutput('Available commands:');
			commands.forEach(cmd => {
				addOutput(`  ${cmd.name} - ${cmd.description}`);
			});
		}
	}, [commands, addOutput]);

	const handleTabCompletion = useCallback(() => {
		const matchingCommands = commands.filter(cmd => 
			cmd.name.startsWith(input)
		);
		
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
				executeCommand(input.trim());
				setInput('');
			}
		} else if (key.tab) {
			handleTabCompletion();
		} else if (key.backspace || key.delete) {
			setInput(prev => prev.slice(0, -1));
		} else if (!key.ctrl && !key.meta && char) {
			setInput(prev => prev + char);
		}
	});

	useEffect(() => {
		addOutput(`Welcome to My CLI${name ? `, ${name}` : ''}!`);
		addOutput('Type a command to get started (use Tab for autocompletion):');
		commands.forEach(cmd => {
			addOutput(`  ${cmd.name} - ${cmd.description}`);
		});
		addOutput('  /exit - Exit the CLI');
		addOutput('');
	}, [name, commands, addOutput]);

	const renderedOutput = useMemo(() => {
		return output.slice(-50).map((line, index) => (
			<Text key={`${index}-${line.slice(0, 10)}`}>{line}</Text>
		));
	}, [output]);

	return (
		<Box flexDirection="column" height="100%">
			{/* Scrollable output area */}
			<Box flexDirection="column" flexGrow={1} overflow="hidden" marginBottom={1}>
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
					<Text color="blue">❯ </Text>
					<Text>{input}</Text>
					{isExecuting && <Text color="yellow"> (executing...)</Text>}
				</Box>
				
				{/* Autocomplete suggestions */}
				{suggestions.length > 0 && (
					<Box flexDirection="column" marginTop={1}>
						<Text color="gray">Suggestions:</Text>
						{suggestions.slice(0, 5).map((suggestion, index) => (
							<Text key={index} color="gray">  {suggestion}</Text>
						))}
					</Box>
				)}
			</Box>
		</Box>
	);
}
