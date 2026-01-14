import React, {useState, useEffect} from 'react';
import {Box, Text, useInput} from 'ink';
import type {Command, CommandRegistry} from '../commands.js';
import {findCommand, fuzzySearchCommands} from '../commands.js';
import {ASCII_LOGO} from '../utils.js';

type Props = {
	registry: CommandRegistry;
	onExecute: (command: Command) => void;
};

export function CommandPrompt({registry, onExecute}: Props) {
	const [input, setInput] = useState('');
	const [suggestions, setSuggestions] = useState<Command[]>([]);
	const [selectedIndex, setSelectedIndex] = useState(0);
	const [showSuggestions, setShowSuggestions] = useState(false);

	useEffect(() => {
		if (input.startsWith('/')) {
			const matches = fuzzySearchCommands(registry, input.slice(1));
			setSuggestions(matches);
			setShowSuggestions(matches.length > 0);
			setSelectedIndex(0);
		} else {
			setShowSuggestions(false);
		}
	}, [input, registry]);

	useInput((inputChar, key) => {
		if (key.return) {
			// If suggestions are showing, execute the selected suggestion
			if (showSuggestions && suggestions.length > 0) {
				const selected = suggestions[selectedIndex];
				if (selected) {
					onExecute(selected);
					setInput('');
					setShowSuggestions(false);
				}
			} else if (input.startsWith('/')) {
				// Otherwise, try to execute the typed command
				const command = findCommand(registry, input.slice(1));
				if (command) {
					onExecute(command);
					setInput('');
					setShowSuggestions(false);
				}
			}
		} else if (key.tab && showSuggestions && suggestions.length > 0) {
			// Tab to autocomplete
			const selected = suggestions[selectedIndex];
			if (selected) {
				setInput(`/${selected.name}`);
				setShowSuggestions(false);
			}
		} else if (key.upArrow && showSuggestions) {
			setSelectedIndex(Math.max(0, selectedIndex - 1));
		} else if (key.downArrow && showSuggestions) {
			setSelectedIndex(Math.min(suggestions.length - 1, selectedIndex + 1));
		} else if (key.backspace || key.delete) {
			setInput(input.slice(0, -1));
		} else if (key.escape) {
			setInput('');
			setShowSuggestions(false);
		} else if (inputChar && !key.ctrl && !key.meta) {
			setInput(input + inputChar);
		}
	});

	return (
		<Box flexDirection="column">
			{/* ASCII Logo Header */}
			<Box flexDirection="column" marginBottom={1}>
				<Text color="cyan">{ASCII_LOGO}</Text>
				<Text dimColor>Type / to see available commands</Text>
			</Box>

			{/* Prompt with full-width separator lines */}
			<Box flexDirection="column" marginBottom={1}>
				<Text dimColor>{'─'.repeat(80)}</Text>
				<Box>
					<Text color="green">{'> '}</Text>
					<Text>{input}</Text>
					<Text inverse> </Text>
				</Box>
				<Text dimColor>{'─'.repeat(80)}</Text>
			</Box>

			{/* Suggestions */}
			{showSuggestions && suggestions.length > 0 && (
				<Box
					flexDirection="column"
					paddingX={2}
					paddingY={1}
					borderStyle="round"
					borderColor="gray"
					marginBottom={1}
				>
					<Box marginBottom={1}>
						<Text dimColor>
							Suggestions (Enter to run, Tab to autocomplete, ↑↓ to navigate):
						</Text>
					</Box>
					{suggestions.map((cmd, index) => (
						<Box key={cmd.name} paddingLeft={1}>
							<Text
								color={index === selectedIndex ? 'cyan' : undefined}
								bold={index === selectedIndex}
							>
								{index === selectedIndex ? '▶ ' : '  '}
								/{cmd.name}
							</Text>
							<Text dimColor> - {cmd.description}</Text>
						</Box>
					))}
				</Box>
			)}

		</Box>
	);
}
