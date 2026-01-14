import React from 'react';
import {Box, Text} from 'ink';
import type {CommandRegistry} from '../commands.js';

type Props = {
	registry: CommandRegistry;
	onBack: () => void;
};

export function HelpScreen({registry}: Props) {
	const commands = Object.values(registry);

	return (
		<Box flexDirection="column" paddingX={2} paddingY={1}>
			{/* Header */}
			<Box
				marginBottom={2}
				paddingY={1}
				paddingX={2}
				borderStyle="round"
				borderColor="cyan"
			>
				<Text bold color="cyan">
					📚 Available Commands
				</Text>
			</Box>

			{/* Commands list */}
			<Box flexDirection="column" marginBottom={2}>
				{commands.map(cmd => (
					<Box key={cmd.name} flexDirection="column" marginBottom={1}>
						<Box>
							<Text color="green" bold>
								/{cmd.name}
							</Text>
							{cmd.aliases && cmd.aliases.length > 0 && (
								<Text dimColor>
									{' '}
									(aliases: {cmd.aliases.map(a => `/${a}`).join(', ')})
								</Text>
							)}
						</Box>
						<Box paddingLeft={2}>
							<Text>{cmd.description}</Text>
						</Box>
					</Box>
				))}
			</Box>

			{/* Tips */}
			<Box
				flexDirection="column"
				paddingX={2}
				paddingY={1}
				borderStyle="round"
				borderColor="gray"
				marginBottom={2}
			>
				<Box marginBottom={1}>
					<Text bold>💡 Tips:</Text>
				</Box>
				<Text>• Type / to see autocomplete suggestions</Text>
				<Text>• Use Tab to autocomplete commands</Text>
				<Text>• Use ↑↓ arrows to navigate suggestions</Text>
				<Text>• Press Esc to clear input</Text>
			</Box>

			{/* Back button */}
			<Box>
				<Text dimColor>Press any key to return...</Text>
			</Box>
		</Box>
	);
}
