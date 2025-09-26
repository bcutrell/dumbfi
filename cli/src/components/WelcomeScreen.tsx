import React from 'react';
import {Box, Text} from 'ink';
import {ASCII_LOGO} from '../utils.js';

export function WelcomeScreen({onContinue}: {onContinue: () => void}) {
	React.useEffect(() => {
		const timer = setTimeout(() => {
			onContinue();
		}, 2000);

		return () => clearTimeout(timer);
	}, [onContinue]);

	return (
		<Box flexDirection="column" alignItems="center">
			<Text color="cyan">{ASCII_LOGO}</Text>
			<Text color="yellow">
				Guaranteed to make returns!* (*not actually guaranteed)
			</Text>
			<Box marginTop={1}>
				<Text color="gray">
					[CASH REGISTER NOISE] 💵 [STONKS GOING UP NOISE] 📈
				</Text>
			</Box>
			<Box marginTop={2}>
				<Text color="green">Loading your financial destiny...</Text>
			</Box>
		</Box>
	);
}