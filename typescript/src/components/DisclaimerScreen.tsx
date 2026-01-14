import React from 'react';
import {Box, Text, useInput} from 'ink';

type DisclaimerScreenProps = {
	onPlayAgain: () => void;
	onExit: () => void;
};

export function DisclaimerScreen({
	onPlayAgain,
	onExit,
}: DisclaimerScreenProps) {
	useInput((input, key) => {
		if (key.return || input === ' ') {
			onPlayAgain();
		} else if (input === 'q' || key.escape) {
			onExit();
		}
	});

	return (
		<Box flexDirection="column" padding={1} alignItems="center">
			<Box marginBottom={1}>
				<Text bold color="red">
					⚠️  DISCLAIMER ⚠️
				</Text>
			</Box>

			<Box flexDirection="column" marginBottom={1} alignItems="center">
				<Text>This is not financial advice.</Text>
				<Text>It's not even good comedy.</Text>
				<Text>Please consult a real advisor or</Text>
				<Text>just buy index funds.</Text>
			</Box>

			<Box marginBottom={1}>
				<Text color="gray">
					Past performance does not guarantee
				</Text>
			</Box>
			<Box marginBottom={1}>
				<Text color="gray">
					future results. Mostly because this
				</Text>
			</Box>
			<Box marginBottom={1}>
				<Text color="gray">was all randomly generated.</Text>
			</Box>

			<Box marginTop={2} marginBottom={1}>
				<Text bold color="cyan">
					💰 Thanks for playing DumbFi! 💰
				</Text>
			</Box>

			<Box marginBottom={1}>
				<Text color="green">Press Enter to YOLO again...</Text>
			</Box>
			<Box>
				<Text color="gray">Press Q or ESC to exit</Text>
			</Box>
		</Box>
	);
}